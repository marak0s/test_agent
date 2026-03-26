from datetime import datetime, timezone

from onlycuts.app.config.settings import settings
from onlycuts.app.domain.entities.models import ensure_publishable
from onlycuts.app.domain.enums.statuses import PublicationStatus, TopicStatus
from onlycuts.app.domain.errors.exceptions import InvariantViolation
from onlycuts.app.integrations.telegram.publisher import TelegramPublisher
from onlycuts.app.repositories.approvals import ApprovalRepository
from onlycuts.app.repositories.content_items import ContentItemRepository
from onlycuts.app.repositories.drafts import DraftRepository
from onlycuts.app.repositories.publications import PublicationRepository
from onlycuts.app.repositories.topics import TopicRepository


class PublishService:
    def __init__(
        self,
        content_items: ContentItemRepository,
        drafts: DraftRepository,
        approvals: ApprovalRepository,
        publications: PublicationRepository,
        topics: TopicRepository,
        publisher: TelegramPublisher,
    ):
        self.content_items = content_items
        self.drafts = drafts
        self.approvals = approvals
        self.publications = publications
        self.topics = topics
        self.publisher = publisher

    def queue(self, content_item_id: str, draft_id: str, note: str | None = None) -> str:
        item = self.content_items.get(content_item_id)
        draft = self.drafts.get(draft_id)
        approval = self.approvals.latest_for_draft(draft_id)
        if item is None or draft is None or approval is None:
            raise InvariantViolation("missing entities for queue")
        ensure_publishable(item, draft, approval)
        publication = self.publications.create(
            draft_id=draft_id,
            content_item_id=content_item_id,
            channel_id=str(item.channel_id),
            snapshot_text=draft.body_text,
            status=PublicationStatus.QUEUED.value,
            telegram_chat_id=settings.telegram_publish_chat_id,
            queued_at=datetime.now(tz=timezone.utc),
            failure_reason=note,
        )
        item.status = "queued"
        return str(publication.id)

    def publish_now(self, content_item_id: str, draft_id: str) -> str:
        item = self.content_items.get(content_item_id)
        draft = self.drafts.get(draft_id)
        approval = self.approvals.latest_for_draft(draft_id)
        if item is None or draft is None or approval is None:
            raise InvariantViolation("missing entities for publication")

        ensure_publishable(item, draft, approval)
        try:
            message_id = self.publisher.publish(settings.telegram_publish_chat_id, draft.body_text)
        except Exception as exc:  # pragma: no cover - defensive integration boundary
            publication = self.publications.create(
                draft_id=draft_id,
                content_item_id=content_item_id,
                channel_id=str(item.channel_id),
                snapshot_text=draft.body_text,
                status=PublicationStatus.FAILED.value,
                telegram_chat_id=settings.telegram_publish_chat_id,
                failure_reason=str(exc),
            )
            return str(publication.id)

        if message_id is None:
            publication = self.publications.create(
                draft_id=draft_id,
                content_item_id=content_item_id,
                channel_id=str(item.channel_id),
                snapshot_text=draft.body_text,
                status=PublicationStatus.FAILED.value,
                telegram_chat_id=settings.telegram_publish_chat_id,
                failure_reason="telegram returned no message id",
            )
            return str(publication.id)

        publication = self.publications.create(
            draft_id=draft_id,
            content_item_id=content_item_id,
            channel_id=str(item.channel_id),
            snapshot_text=draft.body_text,
            status=PublicationStatus.PUBLISHED.value,
            telegram_chat_id=settings.telegram_publish_chat_id,
            telegram_message_id=message_id,
            published_at=datetime.now(tz=timezone.utc),
        )
        item.status = "published"
        topic = self.topics.get(str(item.topic_id))
        if topic is not None:
            topic.status = TopicStatus.PUBLISHED.value
        return str(publication.id)
