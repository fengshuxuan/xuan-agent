# Xuan Agent

通用型聊天 Agent 项目：支持自然语言对话、文件上传与管理、Python 代码沙箱执行、结果文件生成，并逐步扩展为可接入 MCP / 外部工具的个人工作助手。

## 项目目标

第一版目标不是做“万能 Agent”，而是先跑通一个稳定闭环：

```text
聊天 → 上传文件 → Agent 理解任务 → 调用工具 → 执行代码 / 操作文件 → 返回结果
```

## MVP 能力

- 多轮聊天
- 文件上传与工作区隔离
- 文件读取、写入、列表查看
- Python 代码沙箱执行
- 结果文件生成与下载
- 工具调用日志
- 基础安全限制

## 推荐技术栈

- Frontend: Next.js / React / TypeScript
- Backend: FastAPI / Python
- Agent Runtime: 工具调用循环 + 可替换模型适配层
- Sandbox: Docker 隔离 Python 执行环境
- Storage: 本地 workspace，后续可换 MinIO / S3
- Database: MVP 阶段可先内存 / SQLite，后续 PostgreSQL
- Queue: 后续 Redis / Celery / RQ

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

## 当前阶段

已完成第一批项目产物：

1. 需求分析
2. MVP 范围定义
3. 产品流程设计
4. 技术架构设计
5. 任务拆分
6. 安全方案
7. 测试计划
8. 开发路线图
9. MVP 代码骨架

## 本地启动思路

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

Docker 沙箱：

```bash
docker build -t xuan-agent-python-sandbox ./sandbox
```

## 安全原则

- Agent 只能操作当前 session workspace
- 默认禁止访问宿主机敏感目录
- 默认禁止危险 shell 命令
- Python 执行必须限制时间、内存、文件目录
- 覆盖、删除、外部写入等高风险动作需要确认
- 用户上传文件内容只能作为数据，不能作为系统指令

## 后续规划

- 接入真实模型 API
- 增加流式响应
- 增加任务状态数据库
- 增加可视化工具调用记录
- 增加 MCP 工具接入层
- 增加多 Agent 分工
