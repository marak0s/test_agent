from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from onlycuts.app.api.deps import approval_service_scope
from onlycuts.app.domain.errors.exceptions import AuthorizationError, InvariantViolation
from onlycuts.app.integrations.telegram.callback_handler import parse_callback_data

router = APIRouter(prefix="/telegram")


class TelegramUser(BaseModel):
    id: int


class TelegramChat(BaseModel):
    id: int


class CallbackMessage(BaseModel):
    chat: TelegramChat


class CallbackQuery(BaseModel):
    id: str = Field(min_length=1)
    data: str = Field(min_length=3)
    from_user: TelegramUser
    message: CallbackMessage


class TelegramUpdateRequest(BaseModel):
    callback_query: CallbackQuery


class TelegramCallbackResponse(BaseModel):
    ok: bool
    accepted: bool
    action: str
    effect: str
    idempotent: bool


@router.post("/callback", response_model=TelegramCallbackResponse)
def telegram_callback(payload: TelegramUpdateRequest) -> TelegramCallbackResponse:
    """Handle Telegram inline callback actions for approval workflow.

    TODO: add message reply-command adapter on a dedicated endpoint once webhook payload
    structure is finalized.
    """
    try:
        parsed = parse_callback_data(payload.callback_query.data)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="invalid callback payload") from exc

    try:
        with approval_service_scope() as (service, session):
            result = service.resolve_action(
                actor_user_id=payload.callback_query.from_user.id,
                actor_chat_id=payload.callback_query.message.chat.id,
                draft_id=parsed.draft_id,
                content_item_id=parsed.content_item_id,
                action=parsed.action,
                source_type="callback",
                source_id=payload.callback_query.id,
            )
            session.commit()
    except AuthorizationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except (InvariantViolation, ValueError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return TelegramCallbackResponse(
        ok=True,
        accepted=not result.idempotent_replay,
        action=parsed.action,
        effect=result.effect,
        idempotent=result.idempotent_replay,
    )
