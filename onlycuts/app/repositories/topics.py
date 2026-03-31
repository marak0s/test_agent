from sqlalchemy import select
from sqlalchemy.orm import Session

from onlycuts.app.db.models import Topic


class TopicRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, channel_id: str, title: str, status: str) -> Topic:
        topic = Topic(channel_id=channel_id, title=title, status=status)
        self.session.add(topic)
        self.session.flush()
        return topic

    def list_new(self, channel_id: str) -> list[Topic]:
        return list(self.session.scalars(select(Topic).where(Topic.channel_id == channel_id, Topic.status == "new")))

    def get(self, topic_id: str) -> Topic | None:
        return self.session.scalar(select(Topic).where(Topic.id == topic_id))
