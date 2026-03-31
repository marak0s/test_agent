from sqlalchemy.orm import Session

from onlycuts.app.jobs.common import run_job


def topic_ingest_job(session: Session, fn):
    return run_job(session=session, name="topic_ingest", payload={}, fn=fn)
