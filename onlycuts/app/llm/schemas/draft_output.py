from pydantic import BaseModel


class DraftOutput(BaseModel):
    title: str
    hook: str
    body_text: str
    cta: str
    style_notes: str
