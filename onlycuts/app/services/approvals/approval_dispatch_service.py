from onlycuts.app.config.settings import settings
from onlycuts.app.integrations.telegram.approval_messages import build_approval_message, inline_keyboard
from onlycuts.app.integrations.telegram.bot_client import TelegramBotClient
from onlycuts.app.repositories.artifacts import ArtifactRepository
from onlycuts.app.repositories.channels import ChannelRepository
from onlycuts.app.repositories.content_items import ContentItemRepository
from onlycuts.app.repositories.drafts import DraftRepository
from onlycuts.app.repositories.topics import TopicRepository


class ApprovalDispatchService:
    def __init__(
        self,
        bot: TelegramBotClient,
        artifacts: ArtifactRepository,
        drafts: DraftRepository,
        content_items: ContentItemRepository,
        topics: TopicRepository,
        channels: ChannelRepository,
    ):
        self.bot = bot
        self.artifacts = artifacts
        self.drafts = drafts
        self.content_items = content_items
        self.topics = topics
        self.channels = channels

    def _approver_chat_id_for_channel(self, channel_id: str) -> int:
        channel = self.channels.get(channel_id)
        if channel is not None and channel.approver_telegram_chat_id is not None:
            return int(channel.approver_telegram_chat_id)
        return settings.telegram_approver_chat_id

    def dispatch(
        self,
        channel_id: str,
        topic_title: str,
        content_item_id: str,
        draft_id: str,
        goal: str,
        body_text: str,
        review_summary: str | None = None,
    ) -> bool:
        approver_chat_id = self._approver_chat_id_for_channel(channel_id)
        msg = build_approval_message(topic_title, content_item_id, draft_id, goal, body_text, review_summary)
        result = self.bot.send_message(
            chat_id=approver_chat_id,
            text=msg,
            reply_markup=inline_keyboard(draft_id, content_item_id),
        )
        self.artifacts.create(
            kind="approval_dispatch",
            ref_id=draft_id,
            payload={
                "chat_id": approver_chat_id,
                "message_id": result.message_id,
                "ok": result.ok,
                "error": result.error,
            },
        )
        return result.ok

    def dispatch_pending_reviewed(self, channel_code: str | None = None) -> int:
        """Send approval messages for reviewed drafts not yet dispatched."""
        sent = 0
        reviewed_drafts = self.drafts.list_by_review_status("passed")
        for draft in reviewed_drafts:
            draft_id = str(draft.id)
            if self.artifacts.exists(kind="approval_dispatch", ref_id=draft_id):
                continue

            item = self.content_items.get(str(draft.content_item_id))
            if item is None or str(item.current_draft_id) != draft_id or item.status != "review":
                continue

            channel = self.channels.get(str(item.channel_id))
            if channel_code and (channel is None or channel.code != channel_code):
                continue

            topic = self.topics.get(str(item.topic_id))
            review_artifact = self.artifacts.latest(kind="review_output", ref_id=draft_id)
            review_summary = None
            if review_artifact is not None:
                review_summary = review_artifact.payload.get("review_notes")

            ok = self.dispatch(
                channel_id=str(item.channel_id),
                topic_title=topic.title if topic is not None else "Unknown topic",
                content_item_id=str(item.id),
                draft_id=draft_id,
                goal=item.goal,
                body_text=draft.body_text,
                review_summary=review_summary,
            )
            if ok:
                sent += 1

        return sent
