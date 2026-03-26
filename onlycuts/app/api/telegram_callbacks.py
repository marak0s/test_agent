from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from onlycuts.app.integrations.telegram.callback_handler import parse_callback_data

router = APIRouter(prefix="/telegram")


class CallbackRequest(BaseModel):
    callback_data: str


@router.post("/callback")
def telegram_callback(payload: CallbackRequest) -> dict:
    try:
        parsed = parse_callback_data(payload.callback_data)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="invalid callback payload") from exc
    return {"ok": True, "action": parsed.action}
