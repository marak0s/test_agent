from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from onlycuts.app.db.models import Publication


class PublicationRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        draft_id: str,
        content_item_id: str,
        channel_id: str,
        snapshot_text: str,
        status: str,
        telegram_chat_id: int | None = None,
        telegram_message_id: int | None = None,
        failure_reason: str | None = None,
        queued_at: datetime | None = None,
        published_at: datetime | None = None,
    ) -> Publication:
        publication = Publication(
            draft_id=draft_id,
            content_item_id=content_item_id,
            channel_id=channel_id,
            snapshot_text=snapshot_text,
            status=status,
            telegram_chat_id=telegram_chat_id,
            telegram_message_id=telegram_message_id,
            failure_reason=failure_reason,
            queued_at=queued_at,
            published_at=published_at,
        )
        self.session.add(publication)
        self.session.flush()
        return publication

    def latest_for_draft(self, draft_id: str) -> Publication | None:
        return self.session.scalar(select(Publication).where(Publication.draft_id == draft_id).order_by(Publication.created_at.desc()))
