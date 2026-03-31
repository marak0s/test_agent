from onlycuts.app.llm.schemas.review_output import ReviewOutput
from onlycuts.app.repositories.artifacts import ArtifactRepository
from onlycuts.app.repositories.drafts import DraftRepository
from onlycuts.app.security.policy_checks import run_policy_checks


class DraftReviewService:
    def __init__(self, drafts: DraftRepository, artifacts: ArtifactRepository):
        self.drafts = drafts
        self.artifacts = artifacts

    def review(self, draft_id: str) -> bool:
        draft = self.drafts.get(draft_id)
        if draft is None:
            raise ValueError("draft not found")
        policy = run_policy_checks(draft.body_text)
        output = ReviewOutput(
            result="pass" if policy["ok"] else "fail",
            style_ok=True,
            novelty_ok=True,
            factual_risk="low",
            claim_risk="low",
            publish_ready=policy["ok"],
            review_notes="Automated baseline review",
        )
        draft.review_status = "passed" if output.publish_ready else "failed"
        self.artifacts.create(kind="review_output", ref_id=str(draft.id), payload=output.model_dump())
        return output.publish_ready
