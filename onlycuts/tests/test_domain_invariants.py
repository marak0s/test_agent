from types import SimpleNamespace
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


def test_approval_authorization_enforced(monkeypatch) -> None:
    monkeypatch.setattr("onlycuts.app.services.approvals.approval_service.settings.telegram_approver_user_id", 1)
    monkeypatch.setattr("onlycuts.app.services.approvals.approval_service.settings.telegram_approver_chat_id", 10)

    class StubRepo:
        def find_by_source(self, source_type: str, source_id: str):
            return None

        def create(self, **kwargs):
            return type("A", (), {"status": kwargs["status"]})

    class StubDraftRepo:
        def get(self, _draft_id):
            return type("D", (), {"id": "d1", "content_item_id": "c1", "review_status": "passed", "body_text": "x", "channel_id": "ch"})

        def create(self, **kwargs):
            return type("D2", (), {"id": "d2", **kwargs})

    class StubItemRepo:
        def get(self, _content_id):
            return type("C", (), {"id": "c1", "current_draft_id": "d1", "channel_id": "ch", "status": "review"})

    class StubPublish:
        def publish_now(self, content_item_id: str, draft_id: str):
            return "pub"

        def queue(self, content_item_id: str, draft_id: str, note: str | None = None):
            return "queue"

    svc = ApprovalService(approvals=StubRepo(), drafts=StubDraftRepo(), content_items=StubItemRepo(), channels=SimpleNamespace(get=lambda _id: SimpleNamespace(approver_telegram_user_id=1, approver_telegram_chat_id=10)), publish_service=StubPublish())
    with pytest.raises(AuthorizationError):
        svc.resolve_action(
            actor_user_id=999,
            actor_chat_id=10,
            draft_id="d1",
            content_item_id="c1",
            action="post",
            source_type="callback",
            source_id="id-1",
        )
