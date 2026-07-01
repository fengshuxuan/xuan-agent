from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlmodel import Session, select

from app.models import UsageRecord
from app.services.plans import get_user_plan


def current_month_start() -> datetime:
    now = datetime.now(timezone.utc)
    return datetime(now.year, now.month, 1, tzinfo=timezone.utc)


def get_monthly_usage(db: Session, user_id: UUID, metric: str) -> float:
    stmt = select(func.coalesce(func.sum(UsageRecord.quantity), 0)).where(
        UsageRecord.user_id == user_id,
        UsageRecord.metric == metric,
        UsageRecord.created_at >= current_month_start(),
    )
    return float(db.exec(stmt).one())


def assert_message_quota(db: Session, user_id: UUID) -> None:
    plan = get_user_plan(db, user_id)
    used = get_monthly_usage(db, user_id, "message")
    if used >= plan.monthly_message_limit:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Monthly message quota exceeded. Upgrade plan or wait for next cycle.",
        )


def assert_code_execution_quota(db: Session, user_id: UUID) -> None:
    plan = get_user_plan(db, user_id)
    used = get_monthly_usage(db, user_id, "code_execution")
    if used >= plan.monthly_code_execution_limit:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Monthly code execution quota exceeded. Upgrade plan or wait for next cycle.",
        )


def get_upload_size_limit(db: Session, user_id: UUID) -> int:
    return get_user_plan(db, user_id).max_upload_file_bytes


def record_usage(
    db: Session,
    user_id: UUID,
    metric: str,
    quantity: float,
    metadata_json: str | None = None,
) -> None:
    db.add(
        UsageRecord(
            user_id=user_id,
            metric=metric,
            quantity=quantity,
            metadata_json=metadata_json,
        )
    )
