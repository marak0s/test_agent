from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from onlycuts.app.db.session import SessionLocal
from onlycuts.app.jobs.approval_dispatch import approval_dispatch_job

router = APIRouter(prefix="/admin")


class RunJobRequest(BaseModel):
    job_name: str


class RunJobResponse(BaseModel):
    accepted: bool
    output: dict | None = None


@router.post("/run-job", response_model=RunJobResponse)
def run_job(request: RunJobRequest) -> RunJobResponse:
    if request.job_name != "approval_dispatch":
        raise HTTPException(status_code=400, detail="unsupported job_name")

    with SessionLocal() as session:
        output = approval_dispatch_job(session)
        return RunJobResponse(accepted=True, output=output)
