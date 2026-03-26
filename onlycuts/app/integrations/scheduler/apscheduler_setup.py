from apscheduler.schedulers.blocking import BlockingScheduler


def build_scheduler() -> BlockingScheduler:
    return BlockingScheduler(timezone="UTC")
