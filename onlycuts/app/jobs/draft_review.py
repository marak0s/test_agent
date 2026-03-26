from sqlalchemy.orm import Session

from onlycuts.app.jobs.common import run_job


def draft_review_job(session: Session, fn):
    return run_job(session=session, name="draft_review", payload={}, fn=fn)
