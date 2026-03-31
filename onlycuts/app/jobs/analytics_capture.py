from sqlalchemy.orm import Session

from onlycuts.app.jobs.common import run_job


def analytics_capture_job(session: Session, fn):
    return run_job(session=session, name="analytics_capture", payload={}, fn=fn)
