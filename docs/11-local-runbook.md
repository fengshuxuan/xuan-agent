# 11. SaaS MVP 本地运行手册

## 当前分支

本阶段代码位于：

```text
saas-mvp-code
```

## 环境变量

复制环境变量模板：

```bash
cp .env.example .env
```

如果要启用豆包模型工具调用，需要配置：

```env
LLM_PROVIDER=doubao
DOUBAO_API_KEY=你的火山方舟 API Key
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
DOUBAO_MODEL=doubao-seed-2.1-pro
```

如果不配置 `DOUBAO_API_KEY`，后端会自动使用规则版 fallback，方便本地开发。

## 先构建 Python 沙箱

```bash
docker build -t xuan-agent-python-sandbox:latest ./sandbox
```

## 后端启动，SQLite 简单模式

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --port 8000
```

健康检查：

```bash
curl http://localhost:8000/health
```

## PostgreSQL + Redis 模式

启动依赖：

```bash
docker compose up postgres redis
```

设置：

```env
DATABASE_URL=postgresql+psycopg://xuan_agent:xuan_agent@localhost:5432/xuan_agent
REDIS_URL=redis://localhost:6379/0
```

执行迁移：

```bash
cd backend
alembic upgrade head
```

再启动后端：

```bash
uvicorn app.main:app --reload --port 8000
```

## 前端启动

```bash
cd frontend
npm install
npm run dev
```

访问：

```text
http://localhost:3000
```

前端已包含：

- 登录 / 注册
- Chat UI
- 文件上传
- 工具调用展示
- 生成文件下载
- 用量面板

## Worker 启动

同步接口：

```text
POST /api/sessions/{session_id}/chat
```

异步接口：

```text
POST /api/sessions/{session_id}/chat/async
GET  /api/jobs/{job_id}
```

启用异步模式：

```env
WORKER_ENABLED=true
```

启动 worker：

```bash
cd backend
rq worker xuan-agent --url redis://localhost:6379/0
```

## 测试流程

1. 打开前端
2. 用 demo@example.com / password123 注册
3. 系统自动创建 session 和 free subscription
4. 上传一个 txt / csv 文件
5. 输入：`列出有哪些文件`
6. 输入：

```text
执行 ```python
print(1 + 1)
```
```

7. 输入：`生成文件`
8. 点击生成文件下载按钮
9. 观察右侧用量面板变化

## 当前 MVP 已支持

- 用户注册
- 用户登录
- JWT 鉴权
- 默认 workspace
- session 创建
- 文件上传
- 鉴权下载
- tenant-scoped 文件工具
- Docker Python 沙箱执行
- 豆包 `doubao-seed-2.1-pro` 工具调用配置
- OpenAI-compatible Chat Completions runner
- 规则版 fallback
- 工具调用记录
- message / usage 记录
- llm token usage 记录
- monthly message / code execution quota
- Plan / Subscription 套餐表
- free / pro 默认套餐 seed
- PostgreSQL + Alembic migration 骨架
- Redis/RQ async chat worker 骨架
- GitHub Actions CI

## 当前限制

- 默认前端仍然使用同步 chat；async job API 已准备好
- docker compose 出于安全考虑没有挂载 Docker socket，因此沙箱建议先用本机后端方式测试
- 暂未支持团队和真实支付
- 暂未支持 OAuth / 邮箱验证

## 下一步

1. 前端切换 async job polling
2. 增加套餐管理 API
3. 增加支付接入
4. 增加 MCP 工具接入层
5. 增加 organization/team 空间
