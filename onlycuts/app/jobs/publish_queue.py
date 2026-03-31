from sqlalchemy.orm import Session

from onlycuts.app.jobs.common import run_job


def publish_queue_job(session: Session, fn):
    return run_job(session=session, name="publish_queue", payload={}, fn=fn)
