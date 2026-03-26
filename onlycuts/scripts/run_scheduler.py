import logging
import signal

from onlycuts.app.integrations.scheduler.apscheduler_setup import build_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("onlycuts.scheduler")


def _heartbeat() -> None:
    logger.info("scheduler heartbeat")


if __name__ == "__main__":
    scheduler = build_scheduler()
    scheduler.add_job(_heartbeat, "interval", seconds=60, id="heartbeat", replace_existing=True)

    def _handle_signal(signum, _frame) -> None:
        logger.info("received signal %s; shutting down scheduler", signum)
        if scheduler.running:
            scheduler.shutdown(wait=False)

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    logger.info("scheduler started (blocking mode)")
    for job in scheduler.get_jobs():
        logger.info("registered job id=%s trigger=%s", job.id, job.trigger)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        _handle_signal(signal.SIGINT, None)
