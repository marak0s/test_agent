from pydantic import BaseModel
from fastapi import APIRouter

router = APIRouter(prefix="/admin")


class RunJobRequest(BaseModel):
    job_name: str


class RunJobResponse(BaseModel):
    accepted: bool


@router.post("/run-job", response_model=RunJobResponse)
def run_job(_: RunJobRequest) -> RunJobResponse:
    # TODO wire to scheduler/dispatcher.
    return RunJobResponse(accepted=True)
