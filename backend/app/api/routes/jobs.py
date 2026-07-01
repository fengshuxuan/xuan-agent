from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Job, User
from app.schemas.job import JobRead

router = APIRouter(prefix="/jobs", tags=["jobs"])


def to_job_read(job: Job) -> JobRead:
    return JobRead(
        id=job.id,
        session_id=job.session_id,
        type=job.type,
        status=job.status,
        progress=job.progress,
        result_json=job.result_json,
        error_message=job.error_message,
    )


@router.get("/{job_id}", response_model=JobRead)
def get_job(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobRead:
    job = db.get(Job, job_id)
    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found")
    return to_job_read(job)
