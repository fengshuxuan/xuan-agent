from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.api.deps import get_current_user, get_default_workspace, get_owned_session
from app.db.session import get_db
from app.models import AgentSession, Message, MessageRole, User
from app.schemas.session import MessageCreate, MessageRead, SessionCreate, SessionRead

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionRead)
def create_session(
    payload: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SessionRead:
    workspace = get_default_workspace(db, current_user)
    session_obj = AgentSession(
        user_id=current_user.id,
        workspace_id=workspace.id,
        title=payload.title or "New Chat",
    )
    db.add(session_obj)
    db.commit()
    db.refresh(session_obj)
    return SessionRead(
        id=session_obj.id,
        title=session_obj.title,
        workspace_id=session_obj.workspace_id,
        status=session_obj.status,
    )


@router.get("", response_model=list[SessionRead])
def list_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SessionRead]:
    sessions = db.exec(
        select(AgentSession).where(AgentSession.user_id == current_user.id)
    ).all()
    return [
        SessionRead(
            id=s.id,
            title=s.title,
            workspace_id=s.workspace_id,
            status=s.status,
        )
        for s in sessions
    ]


@router.get("/{session_id}", response_model=SessionRead)
def get_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SessionRead:
    session_obj = get_owned_session(session_id, db, current_user)
    return SessionRead(
        id=session_obj.id,
        title=session_obj.title,
        workspace_id=session_obj.workspace_id,
        status=session_obj.status,
    )


@router.post("/{session_id}/messages", response_model=MessageRead)
def create_message(
    session_id: UUID,
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageRead:
    get_owned_session(session_id, db, current_user)
    message = Message(
        session_id=session_id,
        user_id=current_user.id,
        role=MessageRole.user,
        content=payload.content,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return MessageRead(id=message.id, role=message.role, content=message.content)


@router.get("/{session_id}/messages", response_model=list[MessageRead])
def list_messages(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MessageRead]:
    get_owned_session(session_id, db, current_user)
    messages = db.exec(
        select(Message)
        .where(Message.session_id == session_id, Message.user_id == current_user.id)
        .order_by(Message.created_at)
    ).all()
    return [MessageRead(id=m.id, role=m.role, content=m.content) for m in messages]
