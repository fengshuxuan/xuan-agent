"use client";

import { useState } from "react";
import { ChatResponse, downloadFile, sendChat, uploadFile } from "../lib/api";

type ChatMessage = {
  role: "user" | "assistant" | "system";
  content: string;
};

export function Chat({
  token,
  sessionId,
  onActivity,
}: {
  token: string;
  sessionId: string;
  onActivity?: () => void;
}) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "system",
      content: "已进入 SaaS MVP 会话。可以试试：列出有哪些文件、执行 Python 代码、生成文件。",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [lastResponse, setLastResponse] = useState<ChatResponse | null>(null);

  async function onSend() {
    if (!input.trim()) return;
    const message = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: message }]);
    setLoading(true);
    try {
      const response = await sendChat(token, sessionId, message);
      setLastResponse(response);
      setMessages((prev) => [...prev, { role: "assistant", content: response.reply }]);
      onActivity?.();
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: error instanceof Error ? error.message : "请求失败" },
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function onUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setLoading(true);
    try {
      const asset = await uploadFile(token, sessionId, file);
      setMessages((prev) => [
        ...prev,
        { role: "system", content: `已上传文件：${asset.original_name}` },
      ]);
      onActivity?.();
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: error instanceof Error ? error.message : "上传失败" },
      ]);
    } finally {
      setLoading(false);
      event.target.value = "";
    }
  }

  return (
    <section className="chat-shell">
      <div className="messages">
        {messages.map((message, index) => (
          <div className={`message ${message.role}`} key={`${message.role}-${index}`}>
            <strong>{message.role}</strong>
            <p>{message.content}</p>
          </div>
        ))}
      </div>

      {lastResponse?.tool_calls?.length ? (
        <div className="panel">
          <h3>工具调用</h3>
          {lastResponse.tool_calls.map((tool, index) => (
            <div key={`${tool.tool_name}-${index}`} className="tool-call">
              <b>{tool.tool_name}</b> · {tool.status}
              {tool.error_message ? <p>{tool.error_message}</p> : null}
            </div>
          ))}
        </div>
      ) : null}

      {lastResponse?.files?.length ? (
        <div className="panel">
          <h3>生成文件</h3>
          {lastResponse.files.map((file) => (
            <button
              className="secondary"
              key={file.file_id}
              onClick={() => downloadFile(token, file.download_url, file.name)}
            >
              下载 {file.name}
            </button>
          ))}
        </div>
      ) : null}

      <div className="composer">
        <input type="file" onChange={onUpload} disabled={loading} />
        <textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="输入消息，例如：执行 ```python\nprint(1+1)\n```"
        />
        <button onClick={onSend} disabled={loading}>
          {loading ? "处理中..." : "发送"}
        </button>
      </div>
    </section>
  );
}
