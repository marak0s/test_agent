from pydantic import BaseModel, Field


class TelegramCallbackPayload(BaseModel):
    action: str = Field(min_length=2, max_length=32)
    draft_id: str = Field(min_length=8, max_length=64)
    content_item_id: str = Field(min_length=8, max_length=64)
