from datetime import datetime, timezone
from uuid import uuid4

import pytest

from onlycuts.app.domain.entities.models import ApprovalEntity, ContentItemEntity, DraftEntity, ensure_publishable
from onlycuts.app.domain.enums.statuses import ApprovalStatus, ContentStatus, DraftReviewStatus
from onlycuts.app.domain.errors.exceptions import AuthorizationError, InvariantViolation, InvalidStateTransition
from onlycuts.app.services.approvals.approval_service import ApprovalService


def test_content_item_approve_requires_review_status() -> None:
    item = ContentItemEntity(id=uuid4(), channel_id=uuid4(), topic_id=uuid4(), goal="x", status=ContentStatus.PLANNED)
    with pytest.raises(InvalidStateTransition):
        item.approve()


def test_publish_invariant_requires_approved_approval() -> None:
    channel_id = uuid4()
    draft = DraftEntity(id=uuid4(), content_item_id=uuid4(), channel_id=channel_id, body_text="x", version=1, review_status=DraftReviewStatus.PASSED)
    item = ContentItemEntity(id=uuid4(), channel_id=channel_id, topic_id=uuid4(), goal="x", status=ContentStatus.REVIEW, current_draft_id=draft.id)
    approval = ApprovalEntity(id=uuid4(), draft_id=draft.id, actor_telegram_user_id=1, action="reject", status=ApprovalStatus.REJECTED, created_at=datetime.now(timezone.utc))
    with pytest.raises(InvariantViolation):
        ensure_publishable(item, draft, approval)


def test_approval_authorization_enforced() -> None:
    class StubRepo:
        def create(self, **kwargs):
            return type("A", (), {"status": kwargs["status"]})

    svc = ApprovalService(approvals=StubRepo())
    with pytest.raises(AuthorizationError):
        svc.record_action(actor_user_id=999, draft_id="d1", action="post")
