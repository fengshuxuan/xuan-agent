import subprocess
from pathlib import Path
from uuid import UUID

from app.core.config import get_settings
from app.services.workspace import WorkspaceGuard


class PythonSandboxResult(dict):
    stdout: str
    stderr: str
    exit_code: int


class PythonSandbox:
    def __init__(self, user_id: UUID, workspace_id: UUID, session_id: UUID):
        self.settings = get_settings()
        self.guard = WorkspaceGuard(user_id, workspace_id, session_id)
        self.guard.ensure_session_dirs()

    def execute(self, code: str) -> dict:
        script_path = self.guard.tmp_path("agent_script.py")
        script_path.write_text(code, encoding="utf-8")

        session_root = self.guard.session_root.resolve()
        cmd = [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "--memory",
            self.settings.sandbox_memory,
            "--cpus",
            self.settings.sandbox_cpus,
            "-v",
            f"{session_root}:/workspace",
            self.settings.sandbox_image,
            "python",
            "/workspace/tmp/agent_script.py",
        ]

        try:
            completed = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.settings.sandbox_timeout_seconds,
                check=False,
            )
            return {
                "stdout": completed.stdout[-20_000:],
                "stderr": completed.stderr[-20_000:],
                "exit_code": completed.returncode,
            }
        except subprocess.TimeoutExpired as exc:
            return {
                "stdout": exc.stdout or "",
                "stderr": "Execution timed out",
                "exit_code": 124,
            }
        except FileNotFoundError:
            return {
                "stdout": "",
                "stderr": "Docker is not available. Install Docker or configure a sandbox worker.",
                "exit_code": 127,
            }
