from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from app.api.deps import get_current_user, get_owned_session
from app.db.session import get_db
from app.models import FileAsset, FileSource, User
from app.schemas.file import FileRead
from app.services.usage import get_upload_size_limit, record_usage
from app.services.workspace import WorkspaceGuard

router = APIRouter(tags=["files"])


def to_file_read(asset: FileAsset) -> FileRead:
    return FileRead(
        id=asset.id,
        original_name=asset.original_name,
        size_bytes=asset.size_bytes,
        mime_type=asset.mime_type,
        source=asset.source,
        download_url=f"/api/files/{asset.id}/download",
    )


@router.post("/sessions/{session_id}/files", response_model=FileRead)
def upload_file(
    session_id: UUID,
    uploaded_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileRead:
    max_file_bytes = get_upload_size_limit(db, current_user.id)
    session_obj = get_owned_session(session_id, db, current_user)
    guard = WorkspaceGuard(current_user.id, session_obj.workspace_id, session_obj.id)
    target_path = guard.upload_path(uploaded_file.filename or "uploaded-file")

    total_bytes = 0
    with target_path.open("wb") as buffer:
        while chunk := uploaded_file.file.read(1024 * 1024):
            total_bytes += len(chunk)
            if total_bytes > max_file_bytes:
                target_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Uploaded file exceeds the maximum allowed size for your plan.",
                )
            buffer.write(chunk)

    asset = FileAsset(
        user_id=current_user.id,
        workspace_id=session_obj.workspace_id,
        session_id=session_obj.id,
        original_name=uploaded_file.filename or target_path.name,
        storage_key=str(target_path),
        mime_type=uploaded_file.content_type,
        size_bytes=target_path.stat().st_size,
        source=FileSource.upload,
    )
    db.add(asset)
    record_usage(db, current_user.id, "uploaded_file_bytes", asset.size_bytes)
    db.commit()
    db.refresh(asset)
    return to_file_read(asset)


@router.get("/sessions/{session_id}/files", response_model=list[FileRead])
def list_session_files(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[FileRead]:
    get_owned_session(session_id, db, current_user)
    assets = db.exec(
        select(FileAsset).where(
            FileAsset.user_id == current_user.id,
            FileAsset.session_id == session_id,
            FileAsset.status == "available",
        )
    ).all()
    return [to_file_read(asset) for asset in assets]


@router.get("/files/{file_id}/download")
def download_file(
    file_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileResponse:
    asset = db.get(FileAsset, file_id)
    if not asset or asset.user_id != current_user.id or asset.status != "available":
        raise HTTPException(status_code=404, detail="File not found")

    path = asset.storage_key
    return FileResponse(path=path, filename=asset.original_name, media_type=asset.mime_type)
