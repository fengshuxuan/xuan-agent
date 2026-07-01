from typing import Any
from uuid import UUID

from app.tools.file_tools import FileTools
from app.tools.python_sandbox import PythonSandbox


class ToolRegistry:
    def __init__(self, user_id: UUID, workspace_id: UUID, session_id: UUID):
        self.file_tools = FileTools(user_id, workspace_id, session_id)
        self.python_sandbox = PythonSandbox(user_id, workspace_id, session_id)

    def definitions(self) -> list[dict[str, Any]]:
        """Tool definitions formatted for the OpenAI Responses API."""
        return [
            {
                "type": "function",
                "name": "list_files",
                "description": "List files available in the current authenticated session workspace.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                },
            },
            {
                "type": "function",
                "name": "read_text_file",
                "description": "Read a UTF-8 compatible text file from the current session workspace.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path inside the session workspace, such as uploads/data.csv.",
                        }
                    },
                    "required": ["path"],
                    "additionalProperties": False,
                },
            },
            {
                "type": "function",
                "name": "write_text_file",
                "description": "Write a new text file into the session outputs folder.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Output filename. The file will be written under outputs/.",
                        },
                        "content": {
                            "type": "string",
                            "description": "Text content to write.",
                        },
                    },
                    "required": ["path", "content"],
                    "additionalProperties": False,
                },
            },
            {
                "type": "function",
                "name": "execute_python",
                "description": (
                    "Execute Python code in the current session Docker sandbox. "
                    "Use this for data analysis, file processing, and safe calculations."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Python code to execute. Use /workspace as the session root.",
                        }
                    },
                    "required": ["code"],
                    "additionalProperties": False,
                },
            },
        ]

    def execute(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name == "list_files":
            return self.list_files()
        if name == "read_text_file":
            return self.read_text_file(path=str(arguments["path"]))
        if name == "write_text_file":
            return self.write_text_file(
                path=str(arguments["path"]),
                content=str(arguments["content"]),
            )
        if name == "execute_python":
            return self.execute_python(code=str(arguments["code"]))
        raise ValueError(f"Unknown tool: {name}")

    def list_files(self) -> dict[str, Any]:
        return {"files": self.file_tools.list_files()}

    def read_text_file(self, path: str) -> dict[str, Any]:
        return {"path": path, "content": self.file_tools.read_text_file(path)}

    def write_text_file(self, path: str, content: str) -> dict[str, Any]:
        output_path = self.file_tools.write_text_file(path, content)
        return {"path": str(output_path), "name": output_path.name}

    def execute_python(self, code: str) -> dict[str, Any]:
        return self.python_sandbox.execute(code)
