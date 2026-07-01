from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models import AgentSession, User, UserStatus, Workspace


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = decode_access_token(token)
        user_id = UUID(str(payload.get("sub")))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from exc

    user = db.get(User, user_id)
    if not user or user.status != UserStatus.active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_default_workspace(db: Session, user: User) -> Workspace:
    workspace = db.exec(select(Workspace).where(Workspace.user_id == user.id)).first()
    if not workspace:
        raise HTTPException(status_code=500, detail="Default workspace not initialized")
    return workspace


def get_owned_session(session_id: UUID, db: Session, user: User) -> AgentSession:
    session_obj = db.get(AgentSession, session_id)
    if not session_obj or session_obj.user_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_obj
