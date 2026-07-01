from uuid import UUID

from sqlmodel import Session, select

from app.models import Plan, Subscription, SubscriptionStatus

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


def get_active_subscription(db: Session, user_id: UUID) -> Subscription | None:
    return db.exec(
        select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.status == SubscriptionStatus.active,
        )
    ).first()


def get_user_plan(db: Session, user_id: UUID) -> Plan:
    subscription = get_active_subscription(db, user_id)
    plan_code = subscription.plan_code if subscription else "free"
    plan = db.exec(select(Plan).where(Plan.code == plan_code, Plan.is_active == True)).first()  # noqa: E712
    if plan:
        return plan

    fallback = db.exec(select(Plan).where(Plan.code == "free")).first()
    if fallback:
        return fallback

    # Last-resort object for tests before seed_default_plans has run.
    return Plan(**DEFAULT_PLANS[0])
