from contextlib import contextmanager

from onlycuts.app.db.session import SessionLocal
from onlycuts.app.integrations.telegram.bot_client import TelegramBotClient
from onlycuts.app.integrations.telegram.publisher import TelegramPublisher
from onlycuts.app.repositories.approvals import ApprovalRepository
from onlycuts.app.repositories.content_items import ContentItemRepository
from onlycuts.app.repositories.drafts import DraftRepository
from onlycuts.app.repositories.publications import PublicationRepository
from onlycuts.app.repositories.topics import TopicRepository
from onlycuts.app.services.approvals.approval_service import ApprovalService
from onlycuts.app.services.publishing.publish_service import PublishService


@contextmanager
def approval_service_scope():
    with SessionLocal() as session:
        publish_service = PublishService(
            content_items=ContentItemRepository(session),
            drafts=DraftRepository(session),
            approvals=ApprovalRepository(session),
            publications=PublicationRepository(session),
            topics=TopicRepository(session),
            publisher=TelegramPublisher(TelegramBotClient()),
        )
        service = ApprovalService(
            approvals=ApprovalRepository(session),
            drafts=DraftRepository(session),
            content_items=ContentItemRepository(session),
            publish_service=publish_service,
        )
        yield service, session
