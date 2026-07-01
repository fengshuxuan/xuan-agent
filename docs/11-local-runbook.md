# 11. SaaS MVP 本地运行手册

## 当前分支

本阶段代码位于：

```text
saas-mvp-code
```

## 先构建 Python 沙箱

```bash
docker build -t xuan-agent-python-sandbox:latest ./sandbox
```

## 后端启动

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

## 测试流程

1. 打开前端
2. 用 demo@example.com / password123 注册
3. 系统自动创建 session
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
- 工具调用记录
- message / usage 记录

## 当前限制

- Agent Runtime 还是规则路由，不是真正 LLM Tool Calling
- 数据库默认 SQLite，生产应换 PostgreSQL
- docker-compose 中后端容器调用宿主机 Docker 还需要进一步处理 host path 映射
- 暂未支持异步 job worker
- 暂未支持团队和计费

## 下一步

1. 接入真实 LLM Tool Calling
2. 增加 PostgreSQL + Alembic migration
3. 增加 Redis worker
4. 增加用量配额限制
5. 增加 OAuth / 邮箱验证
