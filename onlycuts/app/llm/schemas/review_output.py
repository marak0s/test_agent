from pydantic import BaseModel


class ReviewOutput(BaseModel):
    result: str
    style_ok: bool
    novelty_ok: bool
    factual_risk: str
    claim_risk: str
    publish_ready: bool
    review_notes: str
