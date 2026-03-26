from onlycuts.app.integrations.scheduler.apscheduler_setup import build_scheduler


if __name__ == "__main__":
    scheduler = build_scheduler()
    scheduler.start()
    print("scheduler started")
