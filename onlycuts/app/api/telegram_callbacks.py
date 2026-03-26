from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from onlycuts.app.api.deps import approval_service_scope
from onlycuts.app.domain.errors.exceptions import AuthorizationError, InvariantViolation
from onlycuts.app.integrations.telegram.callback_handler import parse_callback_data
from onlycuts.app.integrations.telegram.command_parser import extract_ids_from_approval_message, parse_approval_command
from onlycuts.app.security.sanitization import sanitize_text

router = APIRouter(prefix="/telegram")


class CallbackEnvelope(BaseModel):
    id: str = Field(min_length=1)
    data: str = Field(min_length=3)
    actor_user_id: int = Field(gt=0)
    actor_chat_id: int = Field(gt=0)


class ReplyToMessage(BaseModel):
    text: str = Field(min_length=1)


class MessageEnvelope(BaseModel):
    message_id: int
    text: str = Field(min_length=1)
    actor_user_id: int = Field(gt=0)
    actor_chat_id: int = Field(gt=0)
    reply_to_message: ReplyToMessage | None = None


class TelegramCallbackRequest(BaseModel):
    callback_data: str | None = Field(default=None, min_length=3)
    actor_user_id: int | None = Field(default=None, gt=0)
    actor_chat_id: int | None = Field(default=None, gt=0)
    callback_id: str | None = Field(default=None, min_length=1)
    callback_query: CallbackEnvelope | None = None
    message: MessageEnvelope | None = None


class TelegramCallbackResponse(BaseModel):
    ok: bool
    accepted: bool
    action: str
    effect: str
    idempotent: bool


@router.post("/callback", response_model=TelegramCallbackResponse)
def telegram_callback(payload: TelegramCallbackRequest) -> TelegramCallbackResponse:
    """Handle inline callbacks and reply commands via ApprovalService."""
    try:
        with approval_service_scope() as (service, session):
            if payload.message is not None:
                if payload.message.reply_to_message is None:
                    raise HTTPException(status_code=400, detail="reply command must include reply_to_message")
                cmd = parse_approval_command(sanitize_text(payload.message.text))
                draft_id, content_item_id = extract_ids_from_approval_message(payload.message.reply_to_message.text)
                action = cmd.modifier if cmd.action == "regen" and cmd.modifier else cmd.action
                result = service.resolve_reply_command(
                    actor_user_id=payload.message.actor_user_id,
                    actor_chat_id=payload.message.actor_chat_id,
                    draft_id=draft_id,
                    content_item_id=content_item_id,
                    action=action,
                    source_id=f"reply:{payload.message.message_id}:{action}",
                    queue_note=cmd.queue_note,
                )
                session.commit()
                return TelegramCallbackResponse(
                    ok=True,
                    accepted=not result.idempotent_replay,
                    action=action,
                    effect=result.effect,
                    idempotent=result.idempotent_replay,
                )

            callback_data = payload.callback_data
            actor_user_id = payload.actor_user_id
            actor_chat_id = payload.actor_chat_id
            callback_id = payload.callback_id

            if payload.callback_query is not None:
                callback_data = payload.callback_query.data
                actor_user_id = payload.callback_query.actor_user_id
                actor_chat_id = payload.callback_query.actor_chat_id
                callback_id = payload.callback_query.id

            if not callback_data or actor_user_id is None or actor_chat_id is None:
                raise HTTPException(status_code=400, detail="callback_data, actor_user_id, and actor_chat_id are required")

            parsed = parse_callback_data(callback_data)
            result = service.resolve_action(
                actor_user_id=actor_user_id,
                actor_chat_id=actor_chat_id,
                draft_id=parsed.draft_id,
                content_item_id=parsed.content_item_id,
                action=parsed.action,
                source_type="callback",
                source_id=callback_id or f"derived:{actor_user_id}:{parsed.action}:{parsed.draft_id}",
            )
            session.commit()
            return TelegramCallbackResponse(
                ok=True,
                accepted=not result.idempotent_replay,
                action=parsed.action,
                effect=result.effect,
                idempotent=result.idempotent_replay,
            )
    except AuthorizationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except (InvariantViolation, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
