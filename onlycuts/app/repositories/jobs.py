from sqlalchemy.orm import Session

from onlycuts.app.db.models import JobRun


class JobRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, job_name: str, status: str, payload: dict) -> JobRun:
        job = JobRun(job_name=job_name, status=status, payload=payload)
        self.session.add(job)
        self.session.flush()
        return job
