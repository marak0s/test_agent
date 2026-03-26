from onlycuts.app.config.settings import settings
from onlycuts.app.domain.entities.models import ensure_publishable
from onlycuts.app.domain.enums.statuses import PublicationStatus
from onlycuts.app.domain.errors.exceptions import InvariantViolation
from onlycuts.app.integrations.telegram.publisher import TelegramPublisher
from onlycuts.app.repositories.approvals import ApprovalRepository
from onlycuts.app.repositories.content_items import ContentItemRepository
from onlycuts.app.repositories.drafts import DraftRepository
from onlycuts.app.repositories.publications import PublicationRepository


class PublishService:
    def __init__(
        self,
        content_items: ContentItemRepository,
        drafts: DraftRepository,
        approvals: ApprovalRepository,
        publications: PublicationRepository,
        publisher: TelegramPublisher,
    ):
        self.content_items = content_items
        self.drafts = drafts
        self.approvals = approvals
        self.publications = publications
        self.publisher = publisher

    def publish(self, content_item_id: str, draft_id: str) -> str:
        item = self.content_items.get(content_item_id)
        draft = self.drafts.get(draft_id)
        approval = self.approvals.latest_for_draft(draft_id)
        if item is None or draft is None or approval is None:
            raise InvariantViolation("missing entities for publication")
        ensure_publishable(item, draft, approval)
        message_id = self.publisher.publish(settings.telegram_publish_chat_id, draft.body_text)
        publication = self.publications.create(
            draft_id=draft_id,
            content_item_id=content_item_id,
            channel_id=str(item.channel_id),
            snapshot_text=draft.body_text,
            status=PublicationStatus.PUBLISHED.value if message_id else PublicationStatus.FAILED.value,
        )
        item.status = "published" if message_id else item.status
        return str(publication.id)
