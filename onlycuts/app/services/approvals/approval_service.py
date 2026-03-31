from dataclasses import dataclass

from onlycuts.app.config.settings import settings
from onlycuts.app.domain.enums.statuses import ApprovalStatus
from onlycuts.app.domain.errors.exceptions import AuthorizationError, InvariantViolation
from onlycuts.app.repositories.approvals import ApprovalRepository
from onlycuts.app.repositories.content_items import ContentItemRepository
from onlycuts.app.repositories.drafts import DraftRepository
from onlycuts.app.services.publishing.publish_service import PublishService


ACTION_TO_STATUS = {
    "post": ApprovalStatus.APPROVED.value,
    "queue": ApprovalStatus.APPROVED.value,
    "reject": ApprovalStatus.REJECTED.value,
    "regen": ApprovalStatus.REWRITE_REQUESTED.value,
    "shorter": ApprovalStatus.REWRITE_REQUESTED.value,
    "stronger": ApprovalStatus.REWRITE_REQUESTED.value,
    "help": ApprovalStatus.PENDING.value,
}


@dataclass
class ApprovalResolution:
    status: str
    effect: str
    publication_id: str | None = None
    draft_id: str | None = None
    idempotent_replay: bool = False


class ApprovalService:
    def __init__(
        self,
        approvals: ApprovalRepository,
        drafts: DraftRepository,
        content_items: ContentItemRepository,
        publish_service: PublishService,
    ):
        self.approvals = approvals
        self.drafts = drafts
        self.content_items = content_items
        self.publish_service = publish_service

    def resolve_reply_command(
        self,
        actor_user_id: int,
        actor_chat_id: int,
        draft_id: str,
        content_item_id: str,
        action: str,
        source_id: str,
        queue_note: str | None = None,
    ) -> ApprovalResolution:
        """Reply command adapter that reuses core action resolution path."""
        return self.resolve_action(
            actor_user_id=actor_user_id,
            actor_chat_id=actor_chat_id,
            draft_id=draft_id,
            content_item_id=content_item_id,
            action=action,
            source_type="reply_command",
            source_id=source_id,
            queue_note=queue_note,
        )

    def resolve_action(
        self,
        actor_user_id: int,
        actor_chat_id: int,
        draft_id: str,
        content_item_id: str,
        action: str,
        source_type: str,
        source_id: str,
        queue_note: str | None = None,
    ) -> ApprovalResolution:
        self._assert_actor(actor_user_id=actor_user_id, actor_chat_id=actor_chat_id)
        existing = self.approvals.find_by_source(source_type=source_type, source_id=source_id)
        if existing is not None:
            return ApprovalResolution(status=existing.status, effect="noop_duplicate", idempotent_replay=True)

        item = self.content_items.get(content_item_id)
        draft = self.drafts.get(draft_id)
        if item is None or draft is None:
            raise InvariantViolation("approval target not found")
        if str(draft.content_item_id) != str(item.id):
            raise InvariantViolation("draft/content relation mismatch")

        status = ACTION_TO_STATUS.get(action)
        if status is None:
            raise ValueError("unsupported action")

        approval = self.approvals.create(
            draft_id=draft_id,
            actor_telegram_user_id=actor_user_id,
            action=action,
            status=status,
            source_type=source_type,
            source_id=source_id,
        )

        if action == "post":
            publication_id = self.publish_service.publish_now(content_item_id=content_item_id, draft_id=draft_id)
            return ApprovalResolution(status=approval.status, effect="published", publication_id=publication_id)
        if action == "queue":
            publication_id = self.publish_service.queue(content_item_id=content_item_id, draft_id=draft_id, note=queue_note)
            return ApprovalResolution(status=approval.status, effect="queued", publication_id=publication_id)
        if action in {"regen", "shorter", "stronger"}:
            new_draft = self._rewrite_draft(action=action, draft_id=draft_id, content_item_id=content_item_id)
            return ApprovalResolution(status=approval.status, effect="rewritten", draft_id=str(new_draft.id))
        if action == "reject":
            draft.review_status = "failed"
            item.status = "rejected"
            return ApprovalResolution(status=approval.status, effect="rejected")
        return ApprovalResolution(status=approval.status, effect="help")

    def _assert_actor(self, actor_user_id: int, actor_chat_id: int) -> None:
        if actor_user_id != settings.telegram_approver_user_id:
            raise AuthorizationError("only configured approver may take actions")
        if actor_chat_id != settings.telegram_approver_chat_id:
            raise AuthorizationError("actions must come from configured approver chat")

    def _rewrite_draft(self, action: str, draft_id: str, content_item_id: str):
        draft = self.drafts.get(draft_id)
        item = self.content_items.get(content_item_id)
        if draft is None or item is None:
            raise InvariantViolation("draft/content item missing")
        if str(item.current_draft_id) != str(draft.id):
            raise InvariantViolation("only current draft can be rewritten")

        draft.review_status = "superseded"
        if action == "regen":
            new_text = draft.body_text + "\n\n[Regenerated for another pass]"
        elif action == "shorter":
            new_text = draft.body_text[: max(60, len(draft.body_text) // 2)]
        else:
            new_text = "Stronger hook: " + draft.body_text

        new_draft = self.drafts.create(
            content_item_id=str(item.id),
            channel_id=str(item.channel_id),
            body_text=new_text,
            review_status="pending_review",
        )
        item.current_draft_id = new_draft.id
        item.status = "drafting"
        return new_draft
