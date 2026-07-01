from sqlmodel import Session, select

from app.models import Plan

DEFAULT_PLANS = [
    {
        "code": "free",
        "name": "Free",
        "monthly_message_limit": 100,
        "monthly_code_execution_limit": 20,
        "storage_bytes_limit": 500 * 1024 * 1024,
        "max_upload_file_bytes": 10 * 1024 * 1024,
        "price_cents": 0,
        "currency": "USD",
    },
    {
        "code": "pro",
        "name": "Pro",
        "monthly_message_limit": 3000,
        "monthly_code_execution_limit": 500,
        "storage_bytes_limit": 10 * 1024 * 1024 * 1024,
        "max_upload_file_bytes": 100 * 1024 * 1024,
        "price_cents": 1900,
        "currency": "USD",
    },
]


def seed_default_plans(db: Session) -> None:
    for payload in DEFAULT_PLANS:
        existing = db.exec(select(Plan).where(Plan.code == payload["code"])).first()
        if existing:
            continue
        db.add(Plan(**payload))
    db.commit()
