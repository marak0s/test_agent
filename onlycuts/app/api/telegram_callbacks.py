from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from onlycuts.app.api.deps import approval_service_scope
from onlycuts.app.domain.errors.exceptions import AuthorizationError, InvariantViolation
from onlycuts.app.integrations.telegram.callback_handler import parse_callback_data

router = APIRouter(prefix="/telegram")


class CallbackEnvelope(BaseModel):
    """Optional Telegram-like envelope for callback updates."""

    id: str = Field(min_length=1)
    data: str = Field(min_length=3)
    actor_user_id: int = Field(gt=0)
    actor_chat_id: int = Field(gt=0)


class TelegramCallbackRequest(BaseModel):
    """Webhook payload for approval callbacks.

    Supports either a flat payload (`callback_data` + actor ids) or a nested
    envelope under `callback_query`.
    """

    callback_data: str | None = Field(default=None, min_length=3)
    actor_user_id: int | None = Field(default=None, gt=0)
    actor_chat_id: int | None = Field(default=None, gt=0)
    callback_id: str | None = Field(default=None, min_length=1)
    callback_query: CallbackEnvelope | None = None


class TelegramCallbackResponse(BaseModel):
    ok: bool
    accepted: bool
    action: str
    effect: str
    idempotent: bool


@router.post("/callback", response_model=TelegramCallbackResponse)
def telegram_callback(payload: TelegramCallbackRequest) -> TelegramCallbackResponse:
    """Validate callback payload and route action to ApprovalService."""
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

    try:
        parsed = parse_callback_data(callback_data)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="invalid callback payload") from exc

    try:
        with approval_service_scope() as (service, session):
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
