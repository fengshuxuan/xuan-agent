from uuid import UUID

from pydantic import BaseModel


class JobRead(BaseModel):
    id: UUID
    session_id: UUID
    type: str
    status: str
    progress: int
    result_json: str | None = None
    error_message: str | None = None


class AsyncChatResponse(BaseModel):
    job: JobRead
