import signal
import threading

from onlycuts.app.integrations.scheduler.apscheduler_setup import build_scheduler


def _tick() -> None:
    print("scheduler tick")


if __name__ == "__main__":
    scheduler = build_scheduler()
    scheduler.add_job(_tick, "interval", seconds=60, id="heartbeat", replace_existing=True)

    stop_event = threading.Event()

    def _handle_signal(signum, _frame):
        print(f"received signal {signum}; shutting down scheduler")
        scheduler.shutdown(wait=False)
        stop_event.set()

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    print("scheduler started")
    scheduler.start()
