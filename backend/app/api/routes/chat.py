from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.agent.runtime import AgentRuntime
from app.api.deps import get_current_user, get_owned_session
from app.db.session import get_db
from app.models import User
from app.schemas.chat import ChatRequest, ChatResponse, FileResult, ToolCallRead

router = APIRouter(prefix="/sessions", tags=["chat"])


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
