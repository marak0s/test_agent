import signal

from onlycuts.app.integrations.scheduler.apscheduler_setup import build_scheduler


def _heartbeat() -> None:
    print("[onlycuts] scheduler heartbeat")


if __name__ == "__main__":
    scheduler = build_scheduler()
    scheduler.add_job(_heartbeat, "interval", seconds=60, id="heartbeat", replace_existing=True)

    def _handle_signal(signum, _frame) -> None:
        print(f"[onlycuts] received signal {signum}; shutting down")
        if scheduler.running:
            scheduler.shutdown(wait=False)

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    print("[onlycuts] scheduler started; registered jobs:")
    for job in scheduler.get_jobs():
        print(f" - {job.id}: {job.trigger}")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        _handle_signal(signal.SIGINT, None)
