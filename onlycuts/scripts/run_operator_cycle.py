import argparse

from onlycuts.app.config.settings import settings
from onlycuts.app.db.session import SessionLocal
from onlycuts.app.jobs.operator_cycle import operator_cycle_job


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run planner->draft->review->dispatch operator cycle")
    parser.add_argument("--channel", default=settings.default_channel_code)
    args = parser.parse_args()

    with SessionLocal() as session:
        output = operator_cycle_job(session, channel_code=args.channel)
        print(output)
