from pathlib import Path
from uuid import UUID

from app.services.workspace import WorkspaceGuard


class FileTools:
    def __init__(self, user_id: UUID, workspace_id: UUID, session_id: UUID):
        self.guard = WorkspaceGuard(user_id, workspace_id, session_id)
        self.guard.ensure_session_dirs()

    def list_files(self) -> list[str]:
        root = self.guard.session_root
        files: list[str] = []
        for path in root.rglob("*"):
            if path.is_file():
                files.append(str(path.relative_to(root)))
        return sorted(files)

    def read_text_file(self, path: str, max_chars: int = 20_000) -> str:
        resolved = self.guard.resolve(path)
        if not resolved.exists() or not resolved.is_file():
            raise FileNotFoundError(f"File not found: {path}")
        return resolved.read_text(encoding="utf-8", errors="replace")[:max_chars]

    def write_text_file(self, path: str, content: str) -> Path:
        # MVP only writes to outputs/ to avoid overwriting uploads accidentally.
        safe_name = Path(path).name
        resolved = self.guard.output_path(safe_name)
        resolved.write_text(content, encoding="utf-8")
        return resolved
