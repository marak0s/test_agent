from sqlalchemy import func, select
from sqlalchemy.orm import Session

from onlycuts.app.db.models import Draft


class DraftRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, content_item_id: str, channel_id: str, body_text: str, review_status: str) -> Draft:
        max_version = self.session.scalar(select(func.max(Draft.version)).where(Draft.content_item_id == content_item_id)) or 0
        draft = Draft(
            content_item_id=content_item_id,
            channel_id=channel_id,
            body_text=body_text,
            version=max_version + 1,
            review_status=review_status,
        )
        self.session.add(draft)
        self.session.flush()
        return draft

    def get(self, draft_id: str) -> Draft | None:
        return self.session.scalar(select(Draft).where(Draft.id == draft_id))

    def list_for_content_item(self, content_item_id: str) -> list[Draft]:
        return list(self.session.scalars(select(Draft).where(Draft.content_item_id == content_item_id).order_by(Draft.version.asc())))


    def list_by_review_status(self, review_status: str) -> list[Draft]:
        return list(self.session.scalars(select(Draft).where(Draft.review_status == review_status)))
