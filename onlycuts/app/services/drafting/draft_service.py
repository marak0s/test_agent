from onlycuts.app.domain.enums.statuses import DraftReviewStatus
from onlycuts.app.llm.schemas.draft_output import DraftOutput
from onlycuts.app.repositories.artifacts import ArtifactRepository
from onlycuts.app.repositories.channels import ChannelRepository
from onlycuts.app.repositories.content_items import ContentItemRepository
from onlycuts.app.repositories.drafts import DraftRepository


class DraftGenerationService:
    def __init__(
        self,
        content_items: ContentItemRepository,
        drafts: DraftRepository,
        artifacts: ArtifactRepository,
        channels: ChannelRepository,
    ):
        self.content_items = content_items
        self.drafts = drafts
        self.artifacts = artifacts
        self.channels = channels

    def generate(self, content_item_id: str) -> str:
        item = self.content_items.get(content_item_id)
        if item is None:
            raise ValueError("content item not found")

        channel = self.channels.get(str(item.channel_id))
        language = channel.language if channel is not None else "en"
        output = DraftOutput(
            title="Working title",
            hook="Hard-earned lessons from shipping aiops",
            body_text=f"Language: {language}\nGoal: {item.goal}\n\nThree practical takeaways...",
            cta="Reply with your own lesson.",
            style_notes=f"concise; locale={channel.locale if channel is not None else 'en_US'}",
        )
        draft = self.drafts.create(
            content_item_id=str(item.id),
            channel_id=str(item.channel_id),
            body_text=output.body_text,
            review_status=DraftReviewStatus.PENDING_REVIEW.value,
        )
        item.current_draft_id = draft.id
        item.status = "review"
        self.artifacts.create(kind="draft_output", ref_id=str(draft.id), payload=output.model_dump())
        return str(draft.id)
