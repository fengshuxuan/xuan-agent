from pydantic import BaseModel


class UsageItem(BaseModel):
    metric: str
    used: float
    limit: float | None = None


class UsageResponse(BaseModel):
    items: list[UsageItem]
