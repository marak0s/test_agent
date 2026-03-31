from dataclasses import dataclass

from onlycuts.app.domain.enums.statuses import ContentStatus
from onlycuts.app.repositories.channels import ChannelRepository
from onlycuts.app.repositories.content_items import ContentItemRepository
from onlycuts.app.repositories.topics import TopicRepository


@dataclass
class FanoutSummary:
    created: int
    skipped_existing: int


class TopicFanoutService:
    """Creates channel-specific content items for a single source topic."""

    def __init__(self, topics: TopicRepository, channels: ChannelRepository, content_items: ContentItemRepository):
        self.topics = topics
        self.channels = channels
        self.content_items = content_items

    def fan_out(self, topic_id: str, channel_codes: list[str]) -> FanoutSummary:
        topic = self.topics.get(topic_id)
        if topic is None:
            raise ValueError("topic not found")

        created = 0
        skipped = 0
        for code in channel_codes:
            channel = self.channels.get_by_code(code)
            if channel is None or not channel.is_active:
                continue
            goal = f"{code} {channel.language} angle"
            _, was_created = self.content_items.get_or_create(
                channel_id=str(channel.id),
                topic_id=str(topic.id),
                goal=goal,
                status=ContentStatus.PLANNED.value,
            )
            if was_created:
                created += 1
            else:
                skipped += 1

        return FanoutSummary(created=created, skipped_existing=skipped)
