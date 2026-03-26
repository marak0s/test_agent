from sqlalchemy import select
from sqlalchemy.orm import Session

from onlycuts.app.db.models import Approval


class ApprovalRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, draft_id: str, actor_telegram_user_id: int, action: str, status: str) -> Approval:
        approval = Approval(
            draft_id=draft_id,
            actor_telegram_user_id=actor_telegram_user_id,
            action=action,
            status=status,
        )
        self.session.add(approval)
        self.session.flush()
        return approval

    def latest_for_draft(self, draft_id: str) -> Approval | None:
        return self.session.scalar(select(Approval).where(Approval.draft_id == draft_id).order_by(Approval.created_at.desc()))
