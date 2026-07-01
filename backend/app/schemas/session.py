from uuid import UUID

from pydantic import BaseModel


class SessionCreate(BaseModel):
    title: str | None = None


class SessionRead(BaseModel):
    id: UUID
    title: str
    workspace_id: UUID
    status: str


class MessageCreate(BaseModel):
    content: str


class MessageRead(BaseModel):
    id: UUID
    role: str
    content: str
