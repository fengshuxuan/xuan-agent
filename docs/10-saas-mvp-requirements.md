# 10. SaaS MVP 需求补充

## 为什么要补充 SaaS MVP

如果最终目标是多用户 SaaS，就不能先做一个完全单用户本地工具，然后后期再硬改。第一版可以功能简单，但底层必须支持：

- 用户身份
- 数据隔离
- 文件隔离
- 会话归属
- 用量记录
- 权限控制

## SaaS MVP 必须包含

### 1. 用户系统

最小功能：

- 注册
- 登录
- 当前用户信息 `/api/me`
- 退出登录，前端清 token 即可

第一版可以不做：

- 找回密码
- 邮箱验证
- OAuth
- 企业 SSO

### 2. 鉴权系统

最小功能：

- JWT Access Token
- 后端依赖 `get_current_user`
- 所有业务接口必须鉴权
- 禁止前端传 user_id 决定数据归属

### 3. 用户 Workspace

每个用户默认有一个 workspace。

路径设计：

```text
workspace/users/{user_id}/workspaces/{workspace_id}/sessions/{session_id}/
```

### 4. 会话隔离

每个 session 必须绑定：

```text
session_id
user_id
workspace_id
```

用户只能读取自己的 session。

### 5. 文件隔离

每个文件记录必须绑定：

```text
file_id
user_id
workspace_id
session_id
storage_key
```

下载文件时不能只通过路径下载，必须先验证文件归属。

### 6. 工具调用审计

每次工具执行记录：

```text
user_id
session_id
tool_name
input_summary
output_summary
status
error
started_at
finished_at
```

### 7. 用量统计

第一版至少记录：

- message_count
- code_execution_count
- uploaded_file_bytes
- generated_file_bytes

后续再记录 token。

## SaaS MVP API

### Auth

```text
POST /api/auth/register
POST /api/auth/login
GET  /api/me
```

### Sessions

```text
POST /api/sessions
GET  /api/sessions
GET  /api/sessions/{session_id}
POST /api/sessions/{session_id}/messages
```

### Files

```text
POST /api/sessions/{session_id}/files
GET  /api/sessions/{session_id}/files
GET  /api/files/{file_id}/download
```

### Agent

```text
POST /api/sessions/{session_id}/chat
GET  /api/jobs/{job_id}
```

### Usage

```text
GET /api/usage/me
```

## 第一版限制

为了尽快上线，SaaS MVP 可以先限制：

- 每个用户只允许 1 个默认 workspace
- 不支持团队
- 不支持支付
- 不支持自定义模型 key
- 不支持公共分享链接
- 不支持浏览器自动化
- 不支持发送邮件等外部副作用工具

## 验收标准

SaaS MVP 必须通过这些测试：

1. 用户 A 注册并上传文件
2. 用户 B 注册后看不到用户 A 的文件
3. 用户 B 不能访问用户 A 的 session URL
4. 用户 A 的 Python 沙箱只能访问用户 A 当前 session 目录
5. 用户 A 下载文件必须经过鉴权
6. 每次 chat 都能记录 message 和 usage
7. 每次工具调用都能记录 tool_call

## 结论

第一版不一定要商业化，但必须多用户化。

正确路线是：

```text
SaaS 多租户底座
  +
单用户级 Agent 能力
  +
后续再扩展团队、计费、MCP、插件市场
```
