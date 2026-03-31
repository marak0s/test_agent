from types import SimpleNamespace
from uuid import uuid4

from onlycuts.app.services.publishing.publish_service import PublishService


class StubRepo:
    def __init__(self, values=None):
        self.values = values or {}
        self.records = []

    def get(self, key):
        return self.values.get(key)

    def latest_for_draft(self, draft_id):
        return self.values.get(draft_id)

    def create(self, **kwargs):
        rec = SimpleNamespace(id=str(uuid4()), **kwargs)
        self.records.append(rec)
        return rec


class StubPublisher:
    def __init__(self, message_id=42):
        self.message_id = message_id

    def publish(self, _chat_id, _text):
        return self.message_id


def test_publish_success_updates_status() -> None:
    item = SimpleNamespace(id="item-1", topic_id="topic-1", channel_id="c1", current_draft_id="draft-1", status="review")
    draft = SimpleNamespace(id="draft-1", content_item_id="item-1", channel_id="c1", body_text="hello", review_status="passed")
    approval = SimpleNamespace(draft_id="draft-1", status="approved")
    topic = SimpleNamespace(id="topic-1", status="planned")
    channel = SimpleNamespace(id="c1", publish_telegram_chat_id=555)

    service = PublishService(
        content_items=StubRepo({"item-1": item}),
        drafts=StubRepo({"draft-1": draft}),
        approvals=StubRepo({"draft-1": approval}),
        publications=StubRepo(),
        topics=StubRepo({"topic-1": topic}),
        channels=StubRepo({"c1": channel}),
        publisher=StubPublisher(message_id=77),
    )

    publication_id = service.publish_now("item-1", "draft-1")
    assert publication_id
    assert item.status == "published"
    assert topic.status == "published"


def test_publish_failure_records_reason() -> None:
    item = SimpleNamespace(id="item-1", topic_id="topic-1", channel_id="c1", current_draft_id="draft-1", status="review")
    draft = SimpleNamespace(id="draft-1", content_item_id="item-1", channel_id="c1", body_text="hello", review_status="passed")
    approval = SimpleNamespace(draft_id="draft-1", status="approved")

    service = PublishService(
        content_items=StubRepo({"item-1": item}),
        drafts=StubRepo({"draft-1": draft}),
        approvals=StubRepo({"draft-1": approval}),
        publications=StubRepo(),
        topics=StubRepo(),
        channels=StubRepo({"c1": SimpleNamespace(id="c1", publish_telegram_chat_id=555)}),
        publisher=StubPublisher(message_id=None),
    )

    service.publish_now("item-1", "draft-1")
    assert service.publications.records[-1].status == "failed"
