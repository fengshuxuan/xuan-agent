# Xuan Agent

多用户 SaaS Agent 平台：支持用户注册登录、独立 workspace、会话管理、文件上传与鉴权下载、Python 沙箱执行、工具调用审计，并逐步扩展为可接入 MCP / 外部工具的通用工作助手。

## 项目目标

第一版目标不是做“万能 Agent”，而是先跑通一个 SaaS 化的稳定闭环：

```text
注册 / 登录
  → 创建会话
  → 上传文件
  → Agent 理解任务
  → 调用工具
  → 执行代码 / 操作文件
  → 返回结果和生成文件
```

## 当前分支

SaaS MVP 代码位于：

```text
saas-mvp-code
```

## 当前已实现

- 用户注册 / 登录
- JWT 鉴权
- 默认用户 workspace
- session 创建与消息记录
- 文件上传
- 文件鉴权下载
- tenant-scoped 文件工具
- Docker Python 沙箱工具
- 豆包 `doubao-seed-2.1-pro` 默认模型配置
- OpenAI-compatible Chat Completions Tool Calling runner
- 规则版 Agent Runtime fallback
- 工具调用记录
- usage 记录与基础月度配额
- Plan / Subscription 套餐表
- 新用户自动绑定 free 订阅
- PostgreSQL + Alembic migration 骨架
- Redis/RQ async chat job 骨架
- Next.js 最小登录 / 聊天 UI
- 前端用量展示面板
- GitHub Actions CI

## 推荐技术栈

- Frontend: Next.js / React / TypeScript
- Backend: FastAPI / Python
- Model: Doubao `doubao-seed-2.1-pro`
- Database: SQLite for local MVP，PostgreSQL for SaaS
- Migration: Alembic
- Agent Runtime: Doubao Tool Calling + SaaS-safe Tool Registry
- Sandbox: Docker 隔离 Python 执行环境
- Storage: 本地 workspace，后续可换 MinIO / S3
- Queue: Redis / RQ

## 目录结构

```text
xuan-agent/
  docs/                 项目阶段产物文档
  backend/              FastAPI 后端与 Agent Runtime
  frontend/             Next.js 前端骨架
  sandbox/              代码执行沙箱镜像
  docker-compose.yml    本地开发编排
  .env.example          环境变量示例
```

## 本地启动

复制环境变量：

```bash
cp .env.example .env
```

启用豆包模型时配置：

```env
LLM_PROVIDER=doubao
DOUBAO_API_KEY=你的火山方舟 API Key
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
DOUBAO_MODEL=doubao-seed-2.1-pro
```

先构建 Python 沙箱：

```bash
docker build -t xuan-agent-python-sandbox:latest ./sandbox
```

后端：

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --port 8000
```

前端：

```bash
cd frontend
npm install
npm run dev
```

访问：

```text
http://localhost:3000
```

## PostgreSQL / Redis

```bash
docker compose up postgres redis
```

使用 PostgreSQL 时：

```env
DATABASE_URL=postgresql+psycopg://xuan_agent:xuan_agent@localhost:5432/xuan_agent
REDIS_URL=redis://localhost:6379/0
```

执行迁移：

```bash
cd backend
alembic upgrade head
```

异步 Worker：

```bash
cd backend
rq worker xuan-agent --url redis://localhost:6379/0
```

## 测试示例

注册登录后，可以尝试：

```text
列出有哪些文件
```

```text
执行 ```python
print(1 + 1)
```
```

```text
生成文件
```

## 安全原则

- 所有 API 必须鉴权
- 所有数据绑定 user_id
- Agent 只能操作当前 session workspace
- 文件下载必须验证用户归属
- 默认禁止访问宿主机敏感目录
- 默认禁止危险 shell 命令
- Python 执行必须限制时间、内存、文件目录
- 用户上传文件内容只能作为数据，不能作为系统指令
- 模型只能选择工具，真正工具执行由后端 Tool Registry 完成

## 当前限制

- 默认前端仍调用同步 chat，async job 接口已准备好
- docker compose 出于安全考虑没有挂载 Docker socket，因此沙箱建议先用本机后端方式测试
- 暂未支持团队和真实支付
- 暂未支持 OAuth / 邮箱验证

## 后续规划

- 将前端 chat 切换为 async job polling
- 增加流式响应
- 增加套餐管理接口
- 增加支付接入
- 增加 MCP 工具接入层
- 增加多 Agent 分工
- 增加团队空间和订阅计费
