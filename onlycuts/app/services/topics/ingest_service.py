from onlycuts.app.domain.enums.statuses import TopicStatus
from onlycuts.app.repositories.channels import ChannelRepository
from onlycuts.app.repositories.topics import TopicRepository
from onlycuts.app.security.sanitization import sanitize_text


class TopicIngestService:
    def __init__(self, channels: ChannelRepository, topics: TopicRepository):
        self.channels = channels
        self.topics = topics

    def ingest(self, channel_code: str, titles: list[str]) -> int:
        channel = self.channels.get_by_code(channel_code) or self.channels.create(code=channel_code, name=channel_code)
        count = 0
        for title in titles:
            clean = sanitize_text(title)
            if clean:
                self.topics.create(channel_id=channel.id, title=clean, status=TopicStatus.NEW.value)
                count += 1
        return count
