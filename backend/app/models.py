from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserStatus(str, StrEnum):
    active = "active"
    disabled = "disabled"


class MessageRole(str, StrEnum):
    user = "user"
    assistant = "assistant"
    system = "system"
    tool = "tool"


class FileSource(str, StrEnum):
    upload = "upload"
    generated = "generated"


class JobStatus(str, StrEnum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"
    canceled = "canceled"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(index=True, sa_column_kwargs={"unique": True})
    password_hash: str
    display_name: str | None = None
    avatar_url: str | None = None
    status: UserStatus = Field(default=UserStatus.active)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class Workspace(SQLModel, table=True):
    __tablename__ = "workspaces"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(index=True, foreign_key="users.id")
    organization_id: UUID | None = Field(default=None, index=True)
    name: str = "Default Workspace"
    storage_root: str
    created_at: datetime = Field(default_factory=utc_now)


class AgentSession(SQLModel, table=True):
    __tablename__ = "sessions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(index=True, foreign_key="users.id")
    workspace_id: UUID = Field(index=True, foreign_key="workspaces.id")
    title: str = "New Chat"
    status: str = "active"
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(index=True, foreign_key="sessions.id")
    user_id: UUID = Field(index=True, foreign_key="users.id")
    role: MessageRole
    content: str
    created_at: datetime = Field(default_factory=utc_now)


class FileAsset(SQLModel, table=True):
    __tablename__ = "files"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(index=True, foreign_key="users.id")
    workspace_id: UUID = Field(index=True, foreign_key="workspaces.id")
    session_id: UUID | None = Field(default=None, index=True, foreign_key="sessions.id")
    original_name: str
    storage_key: str
    mime_type: str | None = None
    size_bytes: int = 0
    source: FileSource = Field(default=FileSource.upload)
    status: str = "available"
    created_at: datetime = Field(default_factory=utc_now)


class ToolCall(SQLModel, table=True):
    __tablename__ = "tool_calls"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(index=True, foreign_key="users.id")
    session_id: UUID = Field(index=True, foreign_key="sessions.id")
    job_id: UUID | None = Field(default=None, index=True)
    tool_name: str = Field(index=True)
    input_summary: str | None = None
    output_summary: str | None = None
    status: str = "success"
    error_message: str | None = None
    started_at: datetime = Field(default_factory=utc_now)
    finished_at: datetime | None = None


class Job(SQLModel, table=True):
    __tablename__ = "jobs"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(index=True, foreign_key="users.id")
    session_id: UUID = Field(index=True, foreign_key="sessions.id")
    type: str = "chat"
    status: JobStatus = Field(default=JobStatus.queued)
    progress: int = 0
    result_json: str | None = None
    error_message: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class UsageRecord(SQLModel, table=True):
    __tablename__ = "usage_records"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(index=True, foreign_key="users.id")
    organization_id: UUID | None = Field(default=None, index=True)
    metric: str = Field(index=True)
    quantity: float
    metadata_json: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
