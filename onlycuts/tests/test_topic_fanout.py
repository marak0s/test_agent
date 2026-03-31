from types import SimpleNamespace

from onlycuts.app.services.topics.fanout_service import TopicFanoutService


class StubTopics:
    def get(self, topic_id: str):
        return SimpleNamespace(id=topic_id)


class StubChannels:
    def __init__(self):
        self.channels = {
            "only_ai_ops_ru": SimpleNamespace(id="ch-ru", code="only_ai_ops_ru", language="ru", is_active=True),
            "only_ai_ops_en": SimpleNamespace(id="ch-en", code="only_ai_ops_en", language="en", is_active=True),
        }

    def get_by_code(self, code: str):
        return self.channels.get(code)


class StubContentItems:
    def __init__(self):
        self.entries = {}

    def get_or_create(self, channel_id: str, topic_id: str, goal: str, status: str):
        key = (topic_id, channel_id)
        if key in self.entries:
            return self.entries[key], False
        item = SimpleNamespace(topic_id=topic_id, channel_id=channel_id, goal=goal, status=status)
        self.entries[key] = item
        return item, True


def test_topic_fanout_creates_ru_and_en_items() -> None:
    content = StubContentItems()
    service = TopicFanoutService(topics=StubTopics(), channels=StubChannels(), content_items=content)

    summary = service.fan_out(topic_id="topic-1", channel_codes=["only_ai_ops_ru", "only_ai_ops_en"])

    assert summary.created == 2
    assert summary.skipped_existing == 0


def test_topic_fanout_skips_duplicates() -> None:
    content = StubContentItems()
    service = TopicFanoutService(topics=StubTopics(), channels=StubChannels(), content_items=content)

    service.fan_out(topic_id="topic-1", channel_codes=["only_ai_ops_ru", "only_ai_ops_en"])
    summary = service.fan_out(topic_id="topic-1", channel_codes=["only_ai_ops_ru", "only_ai_ops_en"])

    assert summary.created == 0
    assert summary.skipped_existing == 2
