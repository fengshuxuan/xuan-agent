# 12. Doubao Seed 2.1 Pro 接入说明

## 模型选择

项目默认模型改为：

```text
doubao-seed-2-1-pro-260628
```

默认 provider：

```text
doubao
```

## 环境变量

```env
LLM_PROVIDER=doubao
LLM_TOOL_CALLING_ENABLED=true
LLM_MAX_TOOL_ROUNDS=3
DOUBAO_API_KEY=你的火山方舟 API Key
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
DOUBAO_MODEL=doubao-seed-2-1-pro-260628
```

## 接入方式

当前实现使用 OpenAI-compatible Chat Completions 风格调用。

文件：

```text
backend/app/llm/openai_compatible_chat.py
```

核心逻辑：

```text
用户消息
  ↓
Doubao 模型判断是否需要工具
  ↓
模型返回 tool_calls
  ↓
后端 ToolRegistry 执行 tenant-scoped 工具
  ↓
工具结果以 role=tool 回传模型
  ↓
模型生成最终回答
```

## 安全边界

模型不能直接访问文件系统或执行代码。

模型只能选择：

```text
list_files
read_text_file
write_text_file
execute_python
```

真正执行由后端完成：

```text
backend/app/agent/tools.py
backend/app/tools/file_tools.py
backend/app/tools/python_sandbox.py
```

所有工具都绑定：

```text
user_id
workspace_id
session_id
```

## Fallback

如果没有配置 `DOUBAO_API_KEY`，系统会自动使用规则版 fallback。

规则版支持：

- 列出文件
- 执行 Python
- 生成文件

这样本地开发不依赖模型 API。

## 后续增强

1. 根据火山方舟实际 tool calling 返回格式做兼容测试
2. 增加流式输出
3. 增加模型调用 token usage 记录
4. 增加模型错误重试
5. 增加 provider abstraction，支持 qwen / deepseek / openai 等 provider
