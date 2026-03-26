from sqlalchemy import select
from sqlalchemy.orm import Session

from onlycuts.app.db.models import Channel


class ChannelRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_code(self, code: str) -> Channel | None:
        return self.session.scalar(select(Channel).where(Channel.code == code))

    def create(self, code: str, name: str) -> Channel:
        channel = Channel(code=code, name=name)
        self.session.add(channel)
        self.session.flush()
        return channel
