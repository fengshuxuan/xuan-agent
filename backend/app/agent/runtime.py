from dataclasses import dataclass, field
from typing import Any, Callable
from uuid import UUID

from sqlmodel import Session

from app.agent.tools import ToolRegistry
from app.core.config import get_settings
from app.llm.openai_responses import OpenAIResponsesToolRunner
from app.models import AgentSession, FileAsset, FileSource, Message, MessageRole, ToolCall, UsageRecord, utc_now


@dataclass
class RuntimeResult:
    reply: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    files: list[FileAsset] = field(default_factory=list)


class AgentRuntime:
    """SaaS-safe Agent runtime.

    If OPENAI_API_KEY is configured, the runtime uses model tool calling.
    Otherwise it falls back to a small rule-based router so local development
    works without external API credentials.
    """

    def __init__(self, db: Session, user_id: UUID, session_obj: AgentSession):
        self.db = db
        self.user_id = user_id
        self.session = session_obj
        self.settings = get_settings()
        self.tools = ToolRegistry(user_id, session_obj.workspace_id, session_obj.id)

    def run(self, message: str) -> RuntimeResult:
        self.db.add(
            Message(
                session_id=self.session.id,
                user_id=self.user_id,
                role=MessageRole.user,
                content=message,
            )
        )

        if self._should_use_llm():
            result = self._run_with_llm(message)
        else:
            result = self._run_with_rules(message)

        self.db.add(
            Message(
                session_id=self.session.id,
                user_id=self.user_id,
                role=MessageRole.assistant,
                content=result.reply,
            )
        )
        self.db.add(UsageRecord(user_id=self.user_id, metric="message", quantity=1))
        self.db.commit()

        for asset in result.files:
            self.db.refresh(asset)
        return result

    def _should_use_llm(self) -> bool:
        return bool(
            self.settings.llm_tool_calling_enabled
            and self.settings.llm_provider == "openai"
            and self.settings.openai_api_key
        )

    def _run_with_llm(self, message: str) -> RuntimeResult:
        tool_calls: list[ToolCall] = []
        generated_files: list[FileAsset] = []

        runner = OpenAIResponsesToolRunner()
        llm_result = runner.run(
            user_message=message,
            tools=self.tools.definitions(),
            context=self._session_context(),
            call_tool=lambda name, args: self._call_named_tool(
                name=name,
                arguments=args,
                tool_calls=tool_calls,
                generated_files=generated_files,
            ),
        )

        return RuntimeResult(
            reply=llm_result.reply,
            tool_calls=tool_calls,
            files=generated_files,
        )

    def _run_with_rules(self, message: str) -> RuntimeResult:
        lower = message.lower()
        tool_calls: list[ToolCall] = []
        generated_files: list[FileAsset] = []

        if "列出" in message or "有哪些文件" in message or "list files" in lower:
            result = self._call_named_tool("list_files", {}, tool_calls, generated_files)
            reply = "当前会话文件：\n" + "\n".join(result.get("files", []))
            if not result.get("files"):
                reply = "当前会话还没有文件。"

        elif "执行" in message or "运行" in message or "python" in lower:
            code = self._extract_code(message)
            result = self._call_named_tool(
                "execute_python",
                {"code": code},
                tool_calls,
                generated_files,
            )
            reply = (
                "Python 执行完成。\n\n"
                f"exit_code: {result.get('exit_code')}\n\n"
                f"stdout:\n{result.get('stdout') or '(empty)'}\n\n"
                f"stderr:\n{result.get('stderr') or '(empty)'}"
            )

        elif "写入" in message or "生成文件" in message or "write file" in lower:
            result = self._call_named_tool(
                "write_text_file",
                {
                    "path": "agent-output.md",
                    "content": "# Agent Output\n\n" + message,
                },
                tool_calls,
                generated_files,
            )
            reply = f"已生成文件：{result.get('name', 'agent-output.md')}"

        else:
            reply = (
                "我已经收到你的消息。当前未配置 OPENAI_API_KEY，因此使用规则版 MVP。"
                " 配置 OPENAI_API_KEY 后，我会启用真实 LLM Tool Calling。"
            )

        return RuntimeResult(reply=reply, tool_calls=tool_calls, files=generated_files)

    def _call_named_tool(
        self,
        name: str,
        arguments: dict[str, Any],
        tool_calls: list[ToolCall],
        generated_files: list[FileAsset],
    ) -> dict[str, Any]:
        result, call = self._audit_tool_call(
            name=name,
            arguments=arguments,
            fn=lambda: self.tools.execute(name, arguments),
        )
        tool_calls.append(call)

        if name == "write_text_file" and "path" in result:
            asset = FileAsset(
                user_id=self.user_id,
                workspace_id=self.session.workspace_id,
                session_id=self.session.id,
                original_name=result.get("name") or "agent-output.md",
                storage_key=result["path"],
                source=FileSource.generated,
            )
            self.db.add(asset)
            generated_files.append(asset)

        if name == "execute_python":
            self.db.add(UsageRecord(user_id=self.user_id, metric="code_execution", quantity=1))

        return result

    def _audit_tool_call(
        self,
        name: str,
        arguments: dict[str, Any],
        fn: Callable[[], dict[str, Any]],
    ) -> tuple[dict[str, Any], ToolCall]:
        call = ToolCall(
            user_id=self.user_id,
            session_id=self.session.id,
            tool_name=name,
            input_summary=str(arguments)[:1000],
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

    def _session_context(self) -> str:
        return (
            f"user_id={self.user_id}; "
            f"workspace_id={self.session.workspace_id}; "
            f"session_id={self.session.id}"
        )

    def _extract_code(self, message: str) -> str:
        if "```" in message:
            parts = message.split("```")
            if len(parts) >= 3:
                code = parts[1]
                if code.startswith("python"):
                    code = code[len("python") :]
                return code.strip()
        return message
