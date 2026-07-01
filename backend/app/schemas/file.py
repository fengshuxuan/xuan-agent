from uuid import UUID

from pydantic import BaseModel


class FileRead(BaseModel):
    id: UUID
    original_name: str
    size_bytes: int
    mime_type: str | None = None
    source: str
    download_url: str
