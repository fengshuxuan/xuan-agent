from dataclasses import dataclass, field
from uuid import UUID

from sqlmodel import Session

from app.agent.tools import ToolRegistry
from app.models import AgentSession, FileAsset, FileSource, Message, MessageRole, ToolCall, UsageRecord, utc_now


@dataclass
class RuntimeResult:
    reply: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    files: list[FileAsset] = field(default_factory=list)


class AgentRuntime:
    """MVP rule-based runtime.

    This is intentionally simple. The next stage should replace the heuristic
    routing with real LLM tool calling while preserving tenant-scoped tools,
    usage records, and audit logs.
    """

    def __init__(self, db: Session, user_id: UUID, session_obj: AgentSession):
        self.db = db
        self.user_id = user_id
        self.session = session_obj
        self.tools = ToolRegistry(user_id, session_obj.workspace_id, session_obj.id)

    def run(self, message: str) -> RuntimeResult:
        user_message = Message(
            session_id=self.session.id,
            user_id=self.user_id,
            role=MessageRole.user,
            content=message,
        )
        self.db.add(user_message)

        lower = message.lower()
        tool_calls: list[ToolCall] = []
        generated_files: list[FileAsset] = []

        if "列出" in message or "有哪些文件" in message or "list files" in lower:
            result, call = self._call_tool("list_files", lambda: self.tools.list_files())
            tool_calls.append(call)
            reply = "当前会话文件：\n" + "\n".join(result.get("files", []))
            if not result.get("files"):
                reply = "当前会话还没有文件。"

        elif "执行" in message or "运行" in message or "python" in lower:
            code = self._extract_code(message)
            result, call = self._call_tool("execute_python", lambda: self.tools.execute_python(code))
            tool_calls.append(call)
            reply = (
                "Python 执行完成。\n\n"
                f"exit_code: {result.get('exit_code')}\n\n"
                f"stdout:\n{result.get('stdout') or '(empty)'}\n\n"
                f"stderr:\n{result.get('stderr') or '(empty)'}"
            )

        elif "写入" in message or "生成文件" in message or "write file" in lower:
            result, call = self._call_tool(
                "write_text_file",
                lambda: self.tools.write_text_file(
                    "agent-output.md",
                    "# Agent Output\n\n" + message,
                ),
            )
            tool_calls.append(call)
            asset = FileAsset(
                user_id=self.user_id,
                workspace_id=self.session.workspace_id,
                session_id=self.session.id,
                original_name=result["name"],
                storage_key=result["path"],
                source=FileSource.generated,
            )
            self.db.add(asset)
            generated_files.append(asset)
            reply = f"已生成文件：{result['name']}"

        else:
            reply = (
                "我已经收到你的消息。当前 MVP 已支持：列出文件、执行 Python、生成文本文件。"
                " 后续会接入真实 LLM 工具调用，让我能自动判断和完成更多任务。"
            )

        assistant_message = Message(
            session_id=self.session.id,
            user_id=self.user_id,
            role=MessageRole.assistant,
            content=reply,
        )
        self.db.add(assistant_message)
        self.db.add(UsageRecord(user_id=self.user_id, metric="message", quantity=1))
        self.db.commit()

        for asset in generated_files:
            self.db.refresh(asset)
        return RuntimeResult(reply=reply, tool_calls=tool_calls, files=generated_files)

    def _call_tool(self, name: str, fn):
        call = ToolCall(
            user_id=self.user_id,
            session_id=self.session.id,
            tool_name=name,
            input_summary=name,
            status="running",
        )
        self.db.add(call)
        self.db.commit()
        self.db.refresh(call)

        try:
            result = fn()
            call.status = "success"
            call.output_summary = str(result)[:1000]
        except Exception as exc:  # noqa: BLE001 - audit and surface tool failures
            result = {"error": str(exc)}
            call.status = "failed"
            call.error_message = str(exc)
        finally:
            call.finished_at = utc_now()
            self.db.add(call)
            self.db.commit()
            self.db.refresh(call)
        return result, call

    def _extract_code(self, message: str) -> str:
        if "```" in message:
            parts = message.split("```")
            if len(parts) >= 3:
                code = parts[1]
                if code.startswith("python"):
                    code = code[len("python") :]
                return code.strip()
        return message
