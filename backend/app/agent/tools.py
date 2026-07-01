from uuid import UUID

from app.tools.file_tools import FileTools
from app.tools.python_sandbox import PythonSandbox


class ToolRegistry:
    def __init__(self, user_id: UUID, workspace_id: UUID, session_id: UUID):
        self.file_tools = FileTools(user_id, workspace_id, session_id)
        self.python_sandbox = PythonSandbox(user_id, workspace_id, session_id)

    def list_files(self) -> dict:
        return {"files": self.file_tools.list_files()}

    def read_text_file(self, path: str) -> dict:
        return {"path": path, "content": self.file_tools.read_text_file(path)}

    def write_text_file(self, path: str, content: str) -> dict:
        output_path = self.file_tools.write_text_file(path, content)
        return {"path": str(output_path), "name": output_path.name}

    def execute_python(self, code: str) -> dict:
        return self.python_sandbox.execute(code)
