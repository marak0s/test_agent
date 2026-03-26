from sqlalchemy.orm import Session

from onlycuts.app.jobs.common import run_job


def approval_dispatch_job(session: Session, fn):
    return run_job(session=session, name="approval_dispatch", payload={}, fn=fn)
