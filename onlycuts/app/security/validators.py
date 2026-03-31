from pydantic import BaseModel, Field, field_validator

from onlycuts.app.integrations.telegram.approval_messages import ACTIONS


class TelegramCallbackPayload(BaseModel):
    action: str = Field(min_length=2, max_length=32)
    draft_id: str = Field(min_length=8, max_length=64)
    content_item_id: str = Field(min_length=8, max_length=64)

    @field_validator("action")
    @classmethod
    def validate_action(cls, value: str) -> str:
        if value not in ACTIONS:
            raise ValueError("unsupported action")
        return value
