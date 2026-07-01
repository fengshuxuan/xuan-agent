# 08. SaaS 数据模型设计

## 设计原则

Xuan Agent 最终是多用户 SaaS，因此数据模型从一开始就按多租户设计。

核心原则：

- 所有用户数据必须绑定 `user_id`
- 团队数据预留 `organization_id`
- Agent 会话、文件、任务、工具调用都要可追踪
- 用量、配额、审计从第一版开始记录

## 核心实体关系

```text
users
  ├── organizations_members
  ├── workspaces
  │     ├── sessions
  │     │     ├── messages
  │     │     ├── tool_calls
  │     │     ├── files
  │     │     └── jobs
  │     └── usage_records
  └── subscriptions
```

## users

用户表。

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 用户 ID |
| email | varchar | 邮箱，唯一 |
| password_hash | varchar | 密码哈希 |
| display_name | varchar | 显示名称 |
| avatar_url | text | 头像 |
| status | varchar | active / disabled |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

## organizations

组织 / 团队表，P2 阶段启用。

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 组织 ID |
| name | varchar | 组织名称 |
| owner_user_id | uuid | 拥有者 |
| plan | varchar | free / pro / team / enterprise |
| created_at | timestamp | 创建时间 |

## organization_members

组织成员表。

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | ID |
| organization_id | uuid | 组织 ID |
| user_id | uuid | 用户 ID |
| role | varchar | owner / admin / member / viewer |
| created_at | timestamp | 加入时间 |

## workspaces

用户或组织的工作区。

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | workspace ID |
| user_id | uuid | 个人 workspace 所属用户 |
| organization_id | uuid nullable | 团队 workspace 所属组织 |
| name | varchar | 工作区名称 |
| storage_root | text | 存储根路径或对象存储前缀 |
| created_at | timestamp | 创建时间 |

## sessions

Agent 会话。

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | session ID |
| user_id | uuid | 用户 ID |
| workspace_id | uuid | 工作区 ID |
| title | varchar | 会话标题 |
| status | varchar | active / archived |
| metadata | jsonb | 扩展信息 |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

## messages

聊天消息表。

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | message ID |
| session_id | uuid | 会话 ID |
| user_id | uuid | 用户 ID |
| role | varchar | user / assistant / system / tool |
| content | text | 消息内容 |
| metadata | jsonb | token、模型、工具信息 |
| created_at | timestamp | 创建时间 |

## files

文件资产表。

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 文件 ID |
| user_id | uuid | 用户 ID |
| workspace_id | uuid | 工作区 ID |
| session_id | uuid nullable | 关联会话 |
| original_name | varchar | 原始文件名 |
| storage_key | text | 存储路径 / 对象 key |
| mime_type | varchar | MIME 类型 |
| size_bytes | bigint | 文件大小 |
| source | varchar | upload / generated |
| status | varchar | available / deleted |
| created_at | timestamp | 创建时间 |

## tool_calls

工具调用记录。

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | tool_call ID |
| user_id | uuid | 用户 ID |
| session_id | uuid | 会话 ID |
| job_id | uuid nullable | 任务 ID |
| tool_name | varchar | 工具名称 |
| input_json | jsonb | 输入参数摘要 |
| output_json | jsonb | 输出摘要 |
| status | varchar | success / failed / blocked |
| error_message | text | 错误信息 |
| started_at | timestamp | 开始时间 |
| finished_at | timestamp | 结束时间 |

## jobs

长任务表。

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | job ID |
| user_id | uuid | 用户 ID |
| session_id | uuid | 会话 ID |
| type | varchar | chat / code_execution / file_processing |
| status | varchar | queued / running / succeeded / failed / canceled |
| progress | integer | 0-100 |
| result_json | jsonb | 任务结果 |
| error_message | text | 错误信息 |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

## usage_records

用量记录表。

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | ID |
| user_id | uuid | 用户 ID |
| organization_id | uuid nullable | 组织 ID |
| metric | varchar | message / token / code_execution / storage |
| quantity | numeric | 数量 |
| metadata | jsonb | 模型、工具、文件等信息 |
| created_at | timestamp | 创建时间 |

## subscriptions

订阅表，P2 启用。

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | ID |
| user_id | uuid nullable | 个人订阅 |
| organization_id | uuid nullable | 团队订阅 |
| plan | varchar | free / pro / team / enterprise |
| status | varchar | active / past_due / canceled |
| provider | varchar | stripe / paddle / manual |
| provider_customer_id | varchar | 支付平台客户 ID |
| provider_subscription_id | varchar | 支付平台订阅 ID |
| current_period_start | timestamp | 当前周期开始 |
| current_period_end | timestamp | 当前周期结束 |

## audit_logs

审计日志。

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | ID |
| actor_user_id | uuid | 操作人 |
| organization_id | uuid nullable | 组织 ID |
| action | varchar | 操作类型 |
| resource_type | varchar | 资源类型 |
| resource_id | uuid nullable | 资源 ID |
| ip_address | varchar | IP |
| user_agent | text | User Agent |
| metadata | jsonb | 扩展信息 |
| created_at | timestamp | 创建时间 |

## MVP 数据库优先级

第一版必须先落地：

1. users
2. workspaces
3. sessions
4. messages
5. files
6. tool_calls
7. jobs
8. usage_records

后续再做：

1. organizations
2. organization_members
3. subscriptions
4. audit_logs 完整化

## 多租户查询规则

禁止写无租户过滤的查询。

错误示例：

```sql
SELECT * FROM files WHERE id = :file_id;
```

正确示例：

```sql
SELECT * FROM files
WHERE id = :file_id
  AND user_id = :current_user_id;
```

团队空间：

```sql
SELECT * FROM files
WHERE id = :file_id
  AND organization_id IN (:allowed_org_ids);
```

## 索引建议

```sql
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_messages_session_id ON messages(session_id);
CREATE INDEX idx_files_user_workspace ON files(user_id, workspace_id);
CREATE INDEX idx_tool_calls_session_id ON tool_calls(session_id);
CREATE INDEX idx_jobs_user_status ON jobs(user_id, status);
CREATE INDEX idx_usage_user_metric_created ON usage_records(user_id, metric, created_at);
```
