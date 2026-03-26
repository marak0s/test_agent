from sqlalchemy.orm import Session

from onlycuts.app.jobs.common import run_job


def draft_generation_job(session: Session, fn):
    return run_job(session=session, name="draft_generation", payload={}, fn=fn)
