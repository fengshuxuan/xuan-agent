import json
from dataclasses import dataclass, field
from typing import Any, Callable

from openai import OpenAI


@dataclass
class ChatToolCallEvent:
    tool_name: str
    arguments: dict[str, Any]
    result: dict[str, Any]


@dataclass
class ChatToolRunResult:
    reply: str
    tool_events: list[ChatToolCallEvent] = field(default_factory=list)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class OpenAICompatibleChatToolRunner:
    """Tool-calling runner for OpenAI-compatible Chat Completions APIs.

    This is used for Doubao / Volcano Ark style OpenAI-compatible endpoints.
    The model chooses tool calls; the application executes tenant-scoped tools.
    """

    def __init__(self, api_key: str, base_url: str, model: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def run(
        self,
        user_message: str,
        tools: list[dict[str, Any]],
        call_tool: Callable[[str, dict[str, Any]], dict[str, Any]],
        system_prompt: str,
        max_tool_rounds: int = 3,
    ) -> ChatToolRunResult:
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]
        chat_tools = [self._to_chat_completion_tool(tool) for tool in tools]
        tool_events: list[ChatToolCallEvent] = []
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0

        for _ in range(max_tool_rounds):
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=chat_tools,
                tool_choice="auto",
            )
            if completion.usage:
                prompt_tokens += completion.usage.prompt_tokens or 0
                completion_tokens += completion.usage.completion_tokens or 0
                total_tokens += completion.usage.total_tokens or 0

            message = completion.choices[0].message
            messages.append(message.model_dump(exclude_none=True))

            if not message.tool_calls:
                return ChatToolRunResult(
                    reply=message.content or "已完成。",
                    tool_events=tool_events,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                )

            for tool_call in message.tool_calls:
                function = tool_call.function
                try:
                    arguments = json.loads(function.arguments or "{}")
                except json.JSONDecodeError:
                    arguments = {}

                result = call_tool(function.name, arguments)
                tool_events.append(
                    ChatToolCallEvent(
                        tool_name=function.name,
                        arguments=arguments,
                        result=result,
                    )
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result, ensure_ascii=False),
                    }
                )

        return ChatToolRunResult(
            reply="工具调用轮次已达到上限，请缩小任务范围后重试。",
            tool_events=tool_events,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )

    def _to_chat_completion_tool(self, tool: dict[str, Any]) -> dict[str, Any]:
        """Convert Responses-style function tool schema to Chat Completions schema."""
        return {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "parameters": tool.get(
                    "parameters",
                    {"type": "object", "properties": {}, "additionalProperties": False},
                ),
            },
        }
