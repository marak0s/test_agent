from fastapi import APIRouter, HTTPException

from onlycuts.app.api.deps import approval_service_scope
from onlycuts.app.domain.errors.exceptions import AuthorizationError, InvariantViolation
from onlycuts.app.integrations.telegram.callback_handler import parse_callback_data
from onlycuts.app.integrations.telegram.command_parser import (
    extract_ids_from_approval_message,
    parse_approval_command,
)
from onlycuts.app.security.sanitization import sanitize_text

router = APIRouter(prefix="/telegram")


def _get(obj: dict | None, *path, default=None):
    cur = obj
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


@router.post("/callback")
def telegram_callback(payload: dict):
    """
    Handle native Telegram webhook updates for:
    - reply commands
    - inline callback queries

    Accept raw dict instead of strict Pydantic schema to avoid 422 on real Telegram updates.
    """
    try:
        with approval_service_scope() as (service, session):
            # --------------------------------------------------
            # Reply-command path
            # --------------------------------------------------
            message = payload.get("message")
            if isinstance(message, dict) and isinstance(message.get("reply_to_message"), dict):
                text = message.get("text")
                reply_text = _get(message, "reply_to_message", "text")
                actor_user_id = _get(message, "from", "id")
                actor_chat_id = _get(message, "chat", "id")
                message_id = message.get("message_id")

                if not text:
                    raise HTTPException(status_code=400, detail="reply command message has no text")
                if not reply_text:
                    raise HTTPException(status_code=400, detail="reply_to_message has no text")
                if actor_user_id is None or actor_chat_id is None or message_id is None:
                    raise HTTPException(status_code=400, detail="reply command message is missing actor/chat metadata")

                cmd = parse_approval_command(sanitize_text(text))
                draft_id, content_item_id = extract_ids_from_approval_message(reply_text)

                action = cmd.modifier if cmd.action == "regen" and cmd.modifier else cmd.action

                result = service.resolve_reply_command(
                    actor_user_id=int(actor_user_id),
                    actor_chat_id=int(actor_chat_id),
                    draft_id=draft_id,
                    content_item_id=content_item_id,
                    action=action,
                    source_id=f"reply:{message_id}:{action}",
                    queue_note=cmd.queue_note,
                )
                session.commit()
                return {
                    "ok": True,
                    "accepted": not result.idempotent_replay,
                    "action": action,
                    "effect": result.effect,
                    "idempotent": result.idempotent_replay,
                }

            # --------------------------------------------------
            # Inline button path
            # --------------------------------------------------
            callback = payload.get("callback_query")
            if isinstance(callback, dict):
                callback_id = callback.get("id")
                callback_data = callback.get("data")
                actor_user_id = _get(callback, "from", "id")
                message = callback.get("message") or {}
                actor_chat_id = _get(message, "chat", "id")
                message_text = message.get("text") or ""

                if not callback_id:
                    raise HTTPException(status_code=400, detail="callback query has no id")
                if not callback_data:
                    raise HTTPException(status_code=400, detail="callback query has no data")
                if actor_user_id is None or actor_chat_id is None:
                    raise HTTPException(status_code=400, detail="callback query missing actor/chat metadata")

                # Backward compatibility:
                # - old format: "post|draft_uuid|content_uuid"
                # - new short format: "post"
                if "|" in callback_data:
                    parsed = parse_callback_data(callback_data)
                    action = parsed.action
                    draft_id = parsed.draft_id
                    content_item_id = parsed.content_item_id
                else:
                    action = callback_data
                    draft_id, content_item_id = extract_ids_from_approval_message(message_text)

                result = service.resolve_action(
                    actor_user_id=int(actor_user_id),
                    actor_chat_id=int(actor_chat_id),
                    draft_id=draft_id,
                    content_item_id=content_item_id,
                    action=action,
                    source_type="callback",
                    source_id=str(callback_id),
                )
                session.commit()
                return {
                    "ok": True,
                    "accepted": not result.idempotent_replay,
                    "action": action,
                    "effect": result.effect,
                    "idempotent": result.idempotent_replay,
                }

        raise HTTPException(status_code=400, detail="unsupported Telegram update")

    except AuthorizationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except (InvariantViolation, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc