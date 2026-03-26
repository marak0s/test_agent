from sqlalchemy.orm import Session

from onlycuts.app.jobs.common import run_job


def topic_planner_job(session: Session, fn):
    return run_job(session=session, name="topic_planner", payload={}, fn=fn)
