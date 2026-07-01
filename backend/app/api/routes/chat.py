from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.agent.runtime import AgentRuntime
from app.api.deps import get_current_user, get_owned_session
from app.core.config import get_settings
from app.db.session import get_db
from app.models import Job, User
from app.schemas.chat import ChatRequest, ChatResponse, FileResult, ToolCallRead
from app.schemas.job import AsyncChatResponse, JobRead
from app.worker.queue import get_default_queue
from app.worker.tasks import run_chat_job

router = APIRouter(prefix="/sessions", tags=["chat"])


def to_job_read(job: Job) -> JobRead:
    return JobRead(
        id=job.id,
        session_id=job.session_id,
        type=job.type,
        status=job.status,
        progress=job.progress,
        result_json=job.result_json,
        error_message=job.error_message,
    )


@router.post("/{session_id}/chat", response_model=ChatResponse)
def chat(
    session_id: UUID,
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    session_obj = get_owned_session(session_id, db, current_user)
    runtime = AgentRuntime(db=db, user_id=current_user.id, session_obj=session_obj)
    result = runtime.run(payload.message)

    return ChatResponse(
        session_id=session_obj.id,
        reply=result.reply,
        tool_calls=[
            ToolCallRead(
                tool_name=call.tool_name,
                status=call.status,
                input_summary=call.input_summary,
                output_summary=call.output_summary,
                error_message=call.error_message,
            )
            for call in result.tool_calls
        ],
        files=[
            FileResult(
                file_id=file.id,
                name=file.original_name,
                download_url=f"/api/files/{file.id}/download",
            )
            for file in result.files
        ],
    )


@router.post("/{session_id}/chat/async", response_model=AsyncChatResponse)
def chat_async(
    session_id: UUID,
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AsyncChatResponse:
    settings = get_settings()
    if not settings.worker_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Worker mode is disabled. Set WORKER_ENABLED=true to use async chat.",
        )

    session_obj = get_owned_session(session_id, db, current_user)
    job = Job(user_id=current_user.id, session_id=session_obj.id, type="chat")
    db.add(job)
    db.commit()
    db.refresh(job)

    queue = get_default_queue()
    queue.enqueue(
        run_chat_job,
        str(job.id),
        str(current_user.id),
        str(session_obj.id),
        payload.message,
        job_timeout=600,
    )

    return AsyncChatResponse(job=to_job_read(job))
