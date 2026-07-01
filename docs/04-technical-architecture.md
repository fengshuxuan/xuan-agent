# 04. 技术架构设计

## 总体架构

```text
Frontend Next.js
  ↓ HTTP / SSE
Backend FastAPI
  ↓
Agent Runtime
  ├── Session Manager
  ├── Tool Router
  ├── Tool Registry
  ├── Agent Loop
  └── Result Formatter
  ↓
Tools
  ├── File Tools
  ├── Python Sandbox Tool
  ├── Data Tools
  └── Future MCP Tools
  ↓
Workspace + Docker Sandbox
```

## 后端模块

```text
backend/app/
  main.py                 FastAPI 入口
  core/config.py          配置读取
  schemas/chat.py         请求响应模型
  agent/runtime.py        Agent 执行循环
  agent/tools.py          工具注册与路由
  tools/file_tools.py     文件工具
  tools/python_sandbox.py Python 沙箱工具
```

## Agent Runtime 设计

MVP 阶段采用轻量 Agent Loop：

1. 接收用户消息
2. 根据规则和模型意图判断是否需要工具
3. 调用工具
4. 将工具结果交给 Agent 汇总
5. 返回最终回复

后续可以升级为：

- Planner / Executor 分离
- Tool Calling JSON Schema
- 多 Agent Handoff
- Human-in-the-loop 审批
- Tracing 与 Evaluation

## 工具系统设计

每个工具包含：

```json
{
  "name": "read_text_file",
  "description": "读取当前 session workspace 内的文本文件",
  "risk_level": "low",
  "requires_confirmation": false,
  "parameters": {
    "path": "string"
  }
}
```

工具风险分级：

| 等级 | 说明 | 示例 |
|---|---|---|
| low | 只读 | list_files, read_file |
| medium | 写新文件 | write_file |
| high | 覆盖 / 删除 / 外部副作用 | delete_file, send_email |

MVP 暂不启用高风险工具。

## Workspace 设计

```text
workspace/
  sessions/
    {session_id}/
      uploads/
      outputs/
      tmp/
```

规则：

- 所有文件路径必须 resolve 到当前 session 根目录下
- 不允许 `../` 跳出 workspace
- 不允许读取 `.env`、SSH key、系统目录
- 输出文件默认放到 `outputs/`

## Python 沙箱设计

MVP 使用 Docker CLI 调用沙箱镜像：

```text
主进程
  ↓ docker run --rm
sandbox container
  ↓
/workspace 挂载为只读或受控读写目录
```

限制项：

- `--network none`
- `--memory 512m`
- `--cpus 1`
- `timeout 10s`
- 只挂载当前 session workspace

## API 设计

### POST /api/chat

请求：

```json
{
  "session_id": "optional-session-id",
  "message": "帮我分析这个文件"
}
```

响应：

```json
{
  "session_id": "session-id",
  "reply": "分析完成...",
  "tool_calls": [],
  "files": []
}
```

### POST /api/files/upload

上传文件到 session workspace。

### GET /api/files/{session_id}

列出当前 session 文件。

## 后续架构扩展

- 数据库：PostgreSQL 保存 session、message、tool_call、file_asset
- 队列：Redis + RQ / Celery 处理长任务
- 对象存储：MinIO / S3 保存文件
- 向量库：pgvector / Qdrant 做 RAG
- MCP：将工具层扩展为 MCP Client
