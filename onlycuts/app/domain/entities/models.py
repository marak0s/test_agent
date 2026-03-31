from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from onlycuts.app.domain.enums.statuses import (
    ApprovalStatus,
    ContentStatus,
    DraftReviewStatus,
    PublicationStatus,
    TopicStatus,
)
from onlycuts.app.domain.errors.exceptions import InvalidStateTransition, InvariantViolation


@dataclass(slots=True)
class ChannelEntity:
    id: UUID
    code: str
    name: str


@dataclass(slots=True)
class TopicEntity:
    id: UUID
    channel_id: UUID
    title: str
    status: TopicStatus = TopicStatus.NEW

    def mark_planned(self) -> None:
        if self.status not in {TopicStatus.NEW, TopicStatus.SHORTLISTED}:
            raise InvalidStateTransition("topic cannot be planned from current status")
        self.status = TopicStatus.PLANNED


@dataclass(slots=True)
class ContentItemEntity:
    id: UUID
    channel_id: UUID
    topic_id: UUID
    goal: str
    status: ContentStatus = ContentStatus.PLANNED
    current_draft_id: UUID | None = None

    def move_to_review(self, draft_id: UUID) -> None:
        if self.status not in {ContentStatus.PLANNED, ContentStatus.DRAFTING, ContentStatus.REVIEW}:
            raise InvalidStateTransition("cannot move content to review")
        self.status = ContentStatus.REVIEW
        self.current_draft_id = draft_id

    def approve(self) -> None:
        if self.status != ContentStatus.REVIEW:
            raise InvalidStateTransition("only review items may be approved")
        self.status = ContentStatus.APPROVED


@dataclass(slots=True)
class DraftEntity:
    id: UUID
    content_item_id: UUID
    channel_id: UUID
    body_text: str
    version: int
    review_status: DraftReviewStatus = DraftReviewStatus.PENDING_REVIEW


@dataclass(slots=True)
class ApprovalEntity:
    id: UUID
    draft_id: UUID
    actor_telegram_user_id: int
    action: str
    status: ApprovalStatus
    created_at: datetime


@dataclass(slots=True)
class PublicationEntity:
    id: UUID
    draft_id: UUID
    content_item_id: UUID
    channel_id: UUID
    snapshot_text: str
    status: PublicationStatus


def ensure_publishable(
    content_item: ContentItemEntity,
    draft: DraftEntity,
    approval: ApprovalEntity,
) -> None:
    if content_item.current_draft_id != draft.id:
        raise InvariantViolation("cannot publish non-current draft")
    if draft.review_status != DraftReviewStatus.PASSED:
        raise InvariantViolation("draft review must pass before publication")
    if approval.draft_id != draft.id or approval.status != ApprovalStatus.APPROVED:
        raise InvariantViolation("approval must be approved and reference exact draft")
    if draft.channel_id != content_item.channel_id:
        raise InvariantViolation("channel mismatch between draft and content item")


def new_id() -> UUID:
    return uuid4()