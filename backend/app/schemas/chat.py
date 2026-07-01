from uuid import UUID

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class ToolCallRead(BaseModel):
    tool_name: str
    status: str
    input_summary: str | None = None
    output_summary: str | None = None
    error_message: str | None = None


class FileResult(BaseModel):
    file_id: UUID
    name: str
    download_url: str


class ChatResponse(BaseModel):
    session_id: UUID
    reply: str
    tool_calls: list[ToolCallRead] = []
    files: list[FileResult] = []
