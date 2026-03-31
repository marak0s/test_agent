from types import SimpleNamespace
from uuid import uuid4

from onlycuts.app.services.approvals.approval_service import ApprovalService


class StubApprovalRepo:
    def __init__(self):
        self.by_source = {}

    def find_by_source(self, source_type: str, source_id: str):
        return self.by_source.get((source_type, source_id))

    def create(self, **kwargs):
        approval = SimpleNamespace(**kwargs)
        self.by_source[(kwargs["source_type"], kwargs["source_id"])] = approval
        return approval


class StubDraftRepo:
    def __init__(self, draft):
        self._draft = draft

    def get(self, _draft_id):
        return self._draft

    def create(self, **kwargs):
        return SimpleNamespace(id=str(uuid4()), **kwargs)


class StubItemRepo:
    def __init__(self, item):
        self._item = item

    def get(self, _item_id):
        return self._item


class StubPublishService:
    def publish_now(self, content_item_id: str, draft_id: str) -> str:
        return f"pub-{content_item_id}-{draft_id}"

    def queue(self, content_item_id: str, draft_id: str, note: str | None = None) -> str:
        return f"queue-{content_item_id}-{draft_id}-{note or ''}"


def test_duplicate_source_is_idempotent(monkeypatch) -> None:
    monkeypatch.setattr("onlycuts.app.services.approvals.approval_service.settings.telegram_approver_user_id", 1)
    monkeypatch.setattr("onlycuts.app.services.approvals.approval_service.settings.telegram_approver_chat_id", 10)

    draft = SimpleNamespace(id="draft-1", content_item_id="item-1", channel_id="c1", body_text="body", review_status="passed")
    item = SimpleNamespace(id="item-1", current_draft_id="draft-1", channel_id="c1", status="review")

    svc = ApprovalService(
        approvals=StubApprovalRepo(),
        drafts=StubDraftRepo(draft),
        content_items=StubItemRepo(item),
        channels=SimpleNamespace(get=lambda _id: SimpleNamespace(approver_telegram_user_id=1, approver_telegram_chat_id=10)),
        publish_service=StubPublishService(),
    )
    first = svc.resolve_action(
        actor_user_id=1,
        actor_chat_id=10,
        draft_id="draft-1",
        content_item_id="item-1",
        action="post",
        source_type="callback",
        source_id="cb-1",
    )
    second = svc.resolve_action(
        actor_user_id=1,
        actor_chat_id=10,
        draft_id="draft-1",
        content_item_id="item-1",
        action="post",
        source_type="callback",
        source_id="cb-1",
    )

    assert first.idempotent_replay is False
    assert second.idempotent_replay is True
