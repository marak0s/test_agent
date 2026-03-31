from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from onlycuts.app.config.settings import settings
from onlycuts.app.db.session import SessionLocal
from onlycuts.app.jobs.approval_dispatch import approval_dispatch_job
from onlycuts.app.jobs.operator_cycle import operator_cycle_job

router = APIRouter(prefix="/admin")


class RunJobRequest(BaseModel):
    job_name: str
    channel_code: str | None = None


class RunJobResponse(BaseModel):
    accepted: bool
    output: dict | None = None


@router.post("/run-job", response_model=RunJobResponse)
def run_job(request: RunJobRequest) -> RunJobResponse:
    with SessionLocal() as session:
        if request.job_name == "approval_dispatch":
            output = approval_dispatch_job(session, channel_code=request.channel_code)
            return RunJobResponse(accepted=True, output=output)

        if request.job_name == "operator_cycle":
            channel_code = request.channel_code or settings.default_channel_code
            output = operator_cycle_job(session, channel_code=channel_code)
            return RunJobResponse(accepted=True, output=output)

    raise HTTPException(status_code=400, detail="unsupported job_name")
