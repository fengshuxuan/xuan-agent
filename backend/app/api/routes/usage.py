from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.db.session import get_db
from app.models import User
from app.schemas.usage import UsageItem, UsageResponse
from app.services.usage import get_monthly_usage

router = APIRouter(prefix="/usage", tags=["usage"])


@router.get("/me", response_model=UsageResponse)
def get_my_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UsageResponse:
    settings = get_settings()
    return UsageResponse(
        items=[
            UsageItem(
                metric="message",
                used=get_monthly_usage(db, current_user.id, "message"),
                limit=settings.free_monthly_messages,
            ),
            UsageItem(
                metric="code_execution",
                used=get_monthly_usage(db, current_user.id, "code_execution"),
                limit=settings.free_monthly_code_executions,
            ),
            UsageItem(
                metric="uploaded_file_bytes",
                used=get_monthly_usage(db, current_user.id, "uploaded_file_bytes"),
                limit=None,
            ),
            UsageItem(
                metric="generated_file_bytes",
                used=get_monthly_usage(db, current_user.id, "generated_file_bytes"),
                limit=None,
            ),
        ]
    )
