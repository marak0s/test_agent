from types import SimpleNamespace

from onlycuts.app.integrations.telegram.approval_messages import build_approval_message
from onlycuts.app.services.approvals.approval_dispatch_service import ApprovalDispatchService


class StubBot:
    def __init__(self):
        self.calls = 0

    def send_message(self, chat_id: int, text: str, reply_markup: dict | None = None):
        self.calls += 1
        return SimpleNamespace(ok=True, message_id=123, error=None)


class StubArtifacts:
    def __init__(self):
        self.store = {}

    def create(self, kind: str, ref_id: str, payload: dict):
        self.store[(kind, ref_id)] = payload
        return SimpleNamespace(kind=kind, ref_id=ref_id, payload=payload)

    def exists(self, kind: str, ref_id: str) -> bool:
        return (kind, ref_id) in self.store

    def latest(self, kind: str, ref_id: str):
        payload = self.store.get((kind, ref_id))
        if payload is None:
            return None
        return SimpleNamespace(payload=payload)


class StubDraftRepo:
    def __init__(self, drafts):
        self._drafts = drafts

    def list_by_review_status(self, review_status: str):
        assert review_status == "passed"
        return self._drafts


class StubContentRepo:
    def __init__(self, item):
        self.item = item

    def get(self, _id: str):
        return self.item


class StubTopicRepo:
    def get(self, _id: str):
        return SimpleNamespace(title="Topic")


def test_approval_message_contains_stable_refs() -> None:
    msg = build_approval_message(
        topic_title="Topic",
        content_item_id="content-1234",
        draft_id="draft-5678",
        goal="Goal",
        body_text="Body",
        review_summary="Looks good",
    )
    assert "RefDraft: draft-5678" in msg
    assert "RefContent: content-1234" in msg


def test_dispatch_pending_is_idempotent_for_existing_artifact() -> None:
    draft = SimpleNamespace(id="draft-1", content_item_id="content-1", body_text="body")
    item = SimpleNamespace(id="content-1", topic_id="topic-1", current_draft_id="draft-1", status="review", goal="goal")
    artifacts = StubArtifacts()
    artifacts.create("approval_dispatch", "draft-1", {"ok": True})

    service = ApprovalDispatchService(
        bot=StubBot(),
        artifacts=artifacts,
        drafts=StubDraftRepo([draft]),
        content_items=StubContentRepo(item),
        topics=StubTopicRepo(),
    )

    sent = service.dispatch_pending_reviewed()
    assert sent == 0


def test_dispatch_pending_sends_once_for_reviewed_current_draft() -> None:
    draft = SimpleNamespace(id="draft-1", content_item_id="content-1", body_text="body")
    item = SimpleNamespace(id="content-1", topic_id="topic-1", current_draft_id="draft-1", status="review", goal="goal")
    bot = StubBot()
    artifacts = StubArtifacts()

    service = ApprovalDispatchService(
        bot=bot,
        artifacts=artifacts,
        drafts=StubDraftRepo([draft]),
        content_items=StubContentRepo(item),
        topics=StubTopicRepo(),
    )

    sent = service.dispatch_pending_reviewed()
    assert sent == 1
    assert bot.calls == 1
