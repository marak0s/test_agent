from onlycuts.app.integrations.scheduler.apscheduler_setup import build_scheduler


def test_scheduler_builds_blocking_scheduler() -> None:
    scheduler = build_scheduler()
    assert scheduler is not None
    assert scheduler.timezone is not None
