import time
import httpx

from onlycuts.app.api.deps import approval_service_scope
from onlycuts.app.config.settings import settings
from onlycuts.app.domain.errors.exceptions import AuthorizationError, InvariantViolation
from onlycuts.app.integrations.telegram.callback_handler import parse_callback_data
from onlycuts.app.integrations.telegram.command_parser import (
    extract_ids_from_approval_message,
    parse_approval_command,
)
from onlycuts.app.security.sanitization import sanitize_text


def tg_api(method: str, payload: dict | None = None) -> dict:
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/{method}"
    resp = httpx.post(url, json=payload or {}, timeout=40.0)
    resp.raise_for_status()
    return resp.json()


def get_updates(offset: int | None = None, timeout: int = 30) -> list[dict]:
    payload: dict = {
        "timeout": timeout,
        "allowed_updates": ["message", "callback_query"],
    }
    if offset is not None:
        payload["offset"] = offset
    data = tg_api("getUpdates", payload)
    return data.get("result", [])


def answer_callback_query(callback_query_id: str, text: str | None = None) -> None:
    payload = {"callback_query_id": callback_query_id}
    if text:
        payload["text"] = text
    try:
        tg_api("answerCallbackQuery", payload)
    except Exception as exc:
        print(f"answerCallbackQuery error: {exc}")


def process_reply_command(message: dict) -> None:
    text = message.get("text")
    reply_to_message = message.get("reply_to_message") or {}
    reply_text = reply_to_message.get("text")
    actor_user_id = ((message.get("from") or {}).get("id"))
    actor_chat_id = ((message.get("chat") or {}).get("id"))
    message_id = message.get("message_id")

    if not text or not reply_text:
        return

    cmd = parse_approval_command(sanitize_text(text))
    draft_id, content_item_id = extract_ids_from_approval_message(reply_text)
    action = cmd.modifier if cmd.action == "regen" and cmd.modifier else cmd.action

    with approval_service_scope() as (service, session):
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
        print(
            {
                "kind": "reply_command",
                "action": action,
                "effect": result.effect,
                "idempotent": result.idempotent_replay,
            }
        )


def process_callback(callback: dict) -> None:
    callback_id = callback.get("id")
    callback_data = callback.get("data")
    actor_user_id = ((callback.get("from") or {}).get("id"))
    message = callback.get("message") or {}
    actor_chat_id = ((message.get("chat") or {}).get("id"))
    message_text = message.get("text") or ""

    if not callback_id or not callback_data:
        return

    if "|" in callback_data:
        parsed = parse_callback_data(callback_data)
        action = parsed.action
        draft_id = parsed.draft_id
        content_item_id = parsed.content_item_id
    else:
        action = callback_data
        draft_id, content_item_id = extract_ids_from_approval_message(message_text)

    try:
        with approval_service_scope() as (service, session):
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

        answer_callback_query(callback_id, text=f"OK: {result.effect}")
        print(
            {
                "kind": "callback",
                "action": action,
                "effect": result.effect,
                "idempotent": result.idempotent_replay,
            }
        )

    except AuthorizationError as exc:
        answer_callback_query(callback_id, text="Unauthorized")
        print(f"AuthorizationError: {exc}")
    except (InvariantViolation, ValueError) as exc:
        answer_callback_query(callback_id, text=f"Error: {exc}")
        print(f"Business error: {exc}")
    except Exception as exc:
        answer_callback_query(callback_id, text="Unexpected error")
        print(f"Unexpected callback error: {exc}")


def main() -> None:
    print("telegram polling started")
    offset = None

    while True:
        try:
            updates = get_updates(offset=offset, timeout=30)
            for upd in updates:
                offset = upd["update_id"] + 1

                if "message" in upd:
                    msg = upd["message"]
                    if msg.get("reply_to_message"):
                        process_reply_command(msg)

                if "callback_query" in upd:
                    process_callback(upd["callback_query"])

        except Exception as exc:
            print(f"polling error: {exc}")
            time.sleep(3)


if __name__ == "__main__":
    main()