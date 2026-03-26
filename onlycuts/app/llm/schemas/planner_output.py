from pydantic import BaseModel


class PlannerOutput(BaseModel):
    recommended_rubric: str
    angle: str
    fit_score: float
    novelty_score: float
    business_value_score: float
    concise_brief: str
