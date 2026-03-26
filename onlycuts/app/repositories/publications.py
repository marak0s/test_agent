from sqlalchemy.orm import Session

from onlycuts.app.db.models import Publication


class PublicationRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, draft_id: str, content_item_id: str, channel_id: str, snapshot_text: str, status: str) -> Publication:
        publication = Publication(
            draft_id=draft_id,
            content_item_id=content_item_id,
            channel_id=channel_id,
            snapshot_text=snapshot_text,
            status=status,
        )
        self.session.add(publication)
        self.session.flush()
        return publication
