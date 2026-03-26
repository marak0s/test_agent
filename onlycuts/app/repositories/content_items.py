from sqlalchemy import select
from sqlalchemy.orm import Session

from onlycuts.app.db.models import ContentItem


class ContentItemRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, channel_id: str, topic_id: str, goal: str, status: str) -> ContentItem:
        item = ContentItem(channel_id=channel_id, topic_id=topic_id, goal=goal, status=status)
        self.session.add(item)
        self.session.flush()
        return item

    def get(self, content_item_id: str) -> ContentItem | None:
        return self.session.scalar(select(ContentItem).where(ContentItem.id == content_item_id))
