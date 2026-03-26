import argparse

from onlycuts.app.db.session import SessionLocal
from onlycuts.app.services.topics.ingest_service import TopicIngestService
from onlycuts.app.repositories.channels import ChannelRepository
from onlycuts.app.repositories.topics import TopicRepository


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", required=True)
    parser.add_argument("--topic", action="append", required=True)
    args = parser.parse_args()

    with SessionLocal() as session:
        svc = TopicIngestService(ChannelRepository(session), TopicRepository(session))
        count = svc.ingest(channel_code=args.channel, titles=args.topic)
        session.commit()
        print(f"ingested {count} topics")
