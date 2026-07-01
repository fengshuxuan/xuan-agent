from pathlib import Path
from uuid import UUID

from app.core.config import get_settings


class WorkspaceGuard:
    """Build and validate tenant-scoped paths.

    All resolved paths must stay under:
    workspace/users/{user_id}/workspaces/{workspace_id}/sessions/{session_id}
    """

    def __init__(self, user_id: UUID, workspace_id: UUID, session_id: UUID | None = None):
        self.settings = get_settings()
        self.user_id = user_id
        self.workspace_id = workspace_id
        self.session_id = session_id

    @property
    def user_root(self) -> Path:
        return self.settings.workspace_root / "users" / str(self.user_id)

    @property
    def workspace_root(self) -> Path:
        return self.user_root / "workspaces" / str(self.workspace_id)

    @property
    def session_root(self) -> Path:
        if not self.session_id:
            return self.workspace_root
        return self.workspace_root / "sessions" / str(self.session_id)

    def ensure_session_dirs(self) -> None:
        for folder in ["uploads", "outputs", "tmp"]:
            (self.session_root / folder).mkdir(parents=True, exist_ok=True)

    def resolve(self, relative_path: str) -> Path:
        if Path(relative_path).is_absolute():
            raise ValueError("Absolute paths are not allowed")

        candidate = (self.session_root / relative_path).resolve()
        root = self.session_root.resolve()
        if root not in candidate.parents and candidate != root:
            raise ValueError("Path escapes the workspace")

        blocked_names = {".env", ".ssh", "id_rsa", "id_ed25519"}
        if any(part in blocked_names for part in candidate.parts):
            raise ValueError("Sensitive paths are not allowed")
        return candidate

    def upload_path(self, filename: str) -> Path:
        self.ensure_session_dirs()
        safe_name = Path(filename).name
        return self.resolve(f"uploads/{safe_name}")

    def output_path(self, filename: str) -> Path:
        self.ensure_session_dirs()
        safe_name = Path(filename).name
        return self.resolve(f"outputs/{safe_name}")

    def tmp_path(self, filename: str) -> Path:
        self.ensure_session_dirs()
        safe_name = Path(filename).name
        return self.resolve(f"tmp/{safe_name}")
