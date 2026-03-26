from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from onlycuts.app.api.deps import approval_service_scope
from onlycuts.app.domain.errors.exceptions import AuthorizationError, InvariantViolation
from onlycuts.app.integrations.telegram.callback_handler import parse_callback_data
from onlycuts.app.integrations.telegram.command_parser import (
    extract_ids_from_approval_message,
    parse_approval_command,
)
from onlycuts.app.security.sanitization import sanitize_text

router = APIRouter(prefix="/telegram")


class TelegramUser(BaseModel):
    id: int


class TelegramChat(BaseModel):
    id: int


class CallbackQuery(BaseModel):
    id: str
    data: str
    from_user: TelegramUser
    message_chat: TelegramChat


class MessageReply(BaseModel):
    message_id: int
    text: str


class MessageUpdate(BaseModel):
    message_id: int
    from_user: TelegramUser
    chat: TelegramChat
    text: str
    reply_to_message: MessageReply | None = None


class TelegramUpdateRequest(BaseModel):
    callback_query: CallbackQuery | None = None
    message: MessageUpdate | None = None


@router.post("/callback")
def telegram_callback(payload: TelegramUpdateRequest) -> dict:
    try:
        with approval_service_scope() as (service, session):
            if payload.callback_query is not None:
                parsed = parse_callback_data(payload.callback_query.data)
                result = service.resolve_action(
                    actor_user_id=payload.callback_query.from_user.id,
                    actor_chat_id=payload.callback_query.message_chat.id,
                    draft_id=parsed.draft_id,
                    content_item_id=parsed.content_item_id,
                    action=parsed.action,
                    source_type="callback",
                    source_id=payload.callback_query.id,
                )
                session.commit()
                return {"ok": True, "effect": result.effect, "idempotent": result.idempotent_replay}

            if payload.message is not None:
                cmd = parse_approval_command(sanitize_text(payload.message.text))
                if cmd.action == "help":
                    return {"ok": True, "effect": "help", "commands": ["post", "regen", "shorter", "stronger", "reject", "queue", "help"]}
                if payload.message.reply_to_message is None:
                    raise HTTPException(status_code=400, detail="command must reply to approval message")
                draft_id, content_item_id = extract_ids_from_approval_message(payload.message.reply_to_message.text)
                source_id = f"msg:{payload.message.message_id}:{cmd.action}:{cmd.modifier or ''}:{cmd.queue_note or ''}"
                result = service.resolve_action(
                    actor_user_id=payload.message.from_user.id,
                    actor_chat_id=payload.message.chat.id,
                    draft_id=draft_id,
                    content_item_id=content_item_id,
                    action=cmd.modifier if cmd.action == "regen" and cmd.modifier else cmd.action,
                    source_type="reply_command",
                    source_id=source_id,
                    queue_note=cmd.queue_note,
                )
                session.commit()
                return {"ok": True, "effect": result.effect, "idempotent": result.idempotent_replay}
    except AuthorizationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except (InvariantViolation, ValueError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    raise HTTPException(status_code=400, detail="unsupported telegram update payload")
