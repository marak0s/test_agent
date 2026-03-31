from sqlalchemy import select
from sqlalchemy.orm import Session

from onlycuts.app.config.settings import settings
from onlycuts.app.db.models import Channel


class ChannelRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_code(self, code: str) -> Channel | None:
        return self.session.scalar(select(Channel).where(Channel.code == code))

    def get(self, channel_id: str) -> Channel | None:
        return self.session.scalar(select(Channel).where(Channel.id == channel_id))

    def create(
        self,
        code: str,
        name: str,
        language: str = "en",
        locale: str = "en_US",
        approver_telegram_user_id: int | None = None,
        approver_telegram_chat_id: int | None = None,
        publish_telegram_chat_id: int | None = None,
        is_active: bool = True,
    ) -> Channel:
        channel = Channel(
            code=code,
            name=name,
            language=language,
            locale=locale,
            approver_telegram_user_id=approver_telegram_user_id if approver_telegram_user_id is not None else settings.telegram_approver_user_id,
            approver_telegram_chat_id=approver_telegram_chat_id if approver_telegram_chat_id is not None else settings.telegram_approver_chat_id,
            publish_telegram_chat_id=publish_telegram_chat_id if publish_telegram_chat_id is not None else settings.telegram_publish_chat_id,
            is_active=is_active,
        )
        self.session.add(channel)
        self.session.flush()
        return channel
