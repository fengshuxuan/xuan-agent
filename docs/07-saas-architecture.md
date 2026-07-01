# 07. 多用户 SaaS 架构设计

## 目标变化

Xuan Agent 的最终形态不是单机个人助手，而是一个多用户 SaaS 服务：

```text
多用户注册 / 登录
  → 每个用户拥有独立 workspace
  → 每个用户拥有独立会话、文件、任务、用量
  → Agent 在安全沙箱中执行工具
  → 支持套餐、配额、审计、团队空间
```

因此架构必须从第一版开始保留 SaaS 扩展能力。

## SaaS 核心能力

| 模块 | 说明 | MVP 是否需要 |
|---|---|---|
| 用户账号 | 注册、登录、用户资料 | P0 |
| 认证鉴权 | JWT / Session / OAuth | P0 |
| 多租户隔离 | 用户 / 组织数据隔离 | P0 |
| Workspace 隔离 | 每个用户 / session 独立文件空间 | P0 |
| 会话管理 | 每个用户拥有多个 Agent 会话 | P0 |
| 文件资产 | 用户上传文件、生成文件 | P0 |
| 工具审计 | 记录工具调用、执行结果 | P1 |
| 用量统计 | token、代码执行、文件存储 | P1 |
| 套餐配额 | 免费版 / Pro / Team | P1 |
| 支付计费 | Stripe / Paddle / 国内支付 | P2 |
| 团队空间 | organization / members / roles | P2 |
| 管理后台 | 用户、订单、日志、风控 | P2 |

## 多租户模型

建议采用：

```text
User
  ↓
Organization，可选
  ↓
Workspace
  ↓
Session
  ↓
Messages / Files / Tool Calls / Jobs
```

第一版可以先只做 User + Workspace，后续再升级 Team / Organization。

### 单用户模式

```text
user_id
  └── workspace_id
        ├── sessions
        ├── files
        ├── jobs
        └── usage
```

### 团队模式

```text
organization_id
  ├── members
  ├── roles
  ├── workspaces
  ├── billing_account
  └── audit_logs
```

## 数据隔离原则

所有业务表都必须带上：

```text
user_id
organization_id，可选
workspace_id，可选
```

所有查询必须通过当前登录用户过滤：

```sql
WHERE user_id = current_user.id
```

团队空间则通过成员关系过滤：

```sql
WHERE organization_id IN current_user.organizations
```

## 文件隔离原则

生产环境不建议把用户文件直接存在项目目录。

推荐路径：

```text
object-storage/
  users/{user_id}/workspaces/{workspace_id}/sessions/{session_id}/uploads/
  users/{user_id}/workspaces/{workspace_id}/sessions/{session_id}/outputs/
```

本地开发可以映射为：

```text
workspace/users/{user_id}/workspaces/{workspace_id}/sessions/{session_id}/
```

Agent 和沙箱只能访问当前 session 目录。

## SaaS 后端架构

```text
Frontend
  ↓
API Gateway / FastAPI
  ├── Auth Middleware
  ├── Rate Limit Middleware
  ├── Tenant Resolver
  └── Request Validation
  ↓
Application Services
  ├── User Service
  ├── Session Service
  ├── File Service
  ├── Agent Service
  ├── Tool Service
  ├── Usage Service
  └── Billing Service
  ↓
Infrastructure
  ├── PostgreSQL
  ├── Redis
  ├── Object Storage
  ├── Docker / Firecracker Sandbox
  ├── LLM Provider
  └── Observability
```

## 认证方案

MVP 推荐：

- 邮箱密码登录
- JWT access token
- refresh token
- bcrypt / argon2 密码哈希

后续扩展：

- GitHub OAuth
- Google OAuth
- 企业 SSO
- Magic Link

## 鉴权模型

基础角色：

| 角色 | 权限 |
|---|---|
| owner | 管理组织、账单、成员、全部资源 |
| admin | 管理成员、workspace、资源 |
| member | 使用 Agent、上传文件、创建任务 |
| viewer | 只读查看 |

第一版单用户可以先不暴露角色，但后端数据模型要预留。

## 配额与限流

每个用户需要限制：

- 每日消息数
- 每月 token 数
- 每日代码执行次数
- 单次代码执行时长
- 单个文件大小
- 总存储空间
- 并发任务数量

示例套餐：

| 套餐 | 消息 | 代码执行 | 存储 | 文件大小 |
|---|---:|---:|---:|---:|
| Free | 100 / 月 | 20 / 月 | 500 MB | 10 MB |
| Pro | 3000 / 月 | 500 / 月 | 10 GB | 100 MB |
| Team | 组织共享 | 组织共享 | 100 GB | 500 MB |

## 任务队列

代码执行、文件处理、大型分析任务不应该阻塞 HTTP 请求。

推荐：

```text
API 接收请求
  ↓
创建 job
  ↓
放入 Redis Queue / Celery
  ↓
Worker 调用 Agent / Sandbox
  ↓
更新 job 状态
  ↓
前端轮询或 SSE 接收结果
```

## 审计日志

SaaS 必须记录关键行为：

- 登录 / 登出
- 文件上传 / 下载 / 删除
- 工具调用
- Python 执行
- API Key 创建 / 删除
- 套餐变更
- 管理员操作

审计日志字段：

```text
id
actor_user_id
organization_id
action
resource_type
resource_id
ip_address
user_agent
metadata
created_at
```

## 生产安全要求

- HTTPS 强制
- 密码哈希存储
- JWT 过期与刷新
- CSRF / CORS 配置
- API rate limit
- 文件类型校验
- 病毒扫描，可后续接入
- 沙箱网络默认关闭
- 所有租户查询必须带权限过滤
- 敏感配置只放环境变量 / Secret Manager

## 推荐部署形态

### MVP 部署

```text
Vercel / Netlify 前端
  +
云服务器 Docker Compose
  +
PostgreSQL
  +
本地文件 / MinIO
```

### 正式 SaaS 部署

```text
Frontend CDN
  +
API Service，多副本
  +
Worker Service，多副本
  +
PostgreSQL RDS
  +
Redis
  +
S3 / OSS / R2
  +
Sandbox Worker Pool
  +
Monitoring / Logging
```

## 开发策略

为了不重构，第一版代码就要按 SaaS 方式设计：

1. 所有 API 都要有 `current_user`
2. 所有数据表都要有 `user_id`
3. workspace 路径必须包含 `user_id`
4. 文件下载必须鉴权
5. 工具调用必须记录 user_id / session_id
6. Agent Runtime 不直接相信前端传来的路径
7. 所有长任务都预留 job_id
