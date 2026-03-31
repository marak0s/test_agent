import argparse

from onlycuts.app.db.session import SessionLocal
from onlycuts.app.repositories.channels import ChannelRepository
from onlycuts.app.repositories.content_items import ContentItemRepository
from onlycuts.app.repositories.topics import TopicRepository
from onlycuts.app.services.topics.fanout_service import TopicFanoutService


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fan out one topic into multiple channels")
    parser.add_argument("--topic-id", required=True)
    parser.add_argument("--channel", action="append", required=True)
    args = parser.parse_args()

    with SessionLocal() as session:
        service = TopicFanoutService(
            topics=TopicRepository(session),
            channels=ChannelRepository(session),
            content_items=ContentItemRepository(session),
        )
        result = service.fan_out(topic_id=args.topic_id, channel_codes=args.channel)
        session.commit()
        print({"created": result.created, "skipped_existing": result.skipped_existing})
