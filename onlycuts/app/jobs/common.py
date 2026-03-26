from collections.abc import Callable

from sqlalchemy.orm import Session

from onlycuts.app.domain.enums.statuses import JobStatus
from onlycuts.app.repositories.jobs import JobRepository


def run_job(session: Session, name: str, payload: dict, fn: Callable[[], dict]) -> dict:
    repo = JobRepository(session)
    job = repo.create(job_name=name, status=JobStatus.RUNNING.value, payload=payload)
    try:
        output = fn()
        job.status = JobStatus.SUCCESS.value
        session.commit()
        return output
    except Exception:
        job.status = JobStatus.FAILED.value
        session.commit()
        raise
