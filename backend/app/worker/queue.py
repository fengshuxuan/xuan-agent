from redis import Redis
from rq import Queue

from app.core.config import get_settings


def get_redis() -> Redis:
    settings = get_settings()
    return Redis.from_url(settings.redis_url)


def get_default_queue() -> Queue:
    return Queue("xuan-agent", connection=get_redis())
