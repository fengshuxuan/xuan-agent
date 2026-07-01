# 13. 异步任务与套餐配额说明

## 异步 Chat Job

当前同步接口仍可使用：

```text
POST /api/sessions/{session_id}/chat
```

新增异步接口：

```text
POST /api/sessions/{session_id}/chat/async
GET  /api/jobs/{job_id}
```

启用条件：

```env
WORKER_ENABLED=true
REDIS_URL=redis://localhost:6379/0
```

启动 worker：

```bash
cd backend
rq worker xuan-agent --url redis://localhost:6379/0
```

流程：

```text
前端发起 chat/async
  → 后端创建 jobs 记录
  → 投递 Redis/RQ
  → worker 执行 AgentRuntime
  → 更新 job.status / progress / result_json
  → 前端轮询 /api/jobs/{job_id}
```

## 套餐模型

新增表：

```text
plans
subscriptions
```

默认套餐：

| Plan | 消息/月 | 代码执行/月 | 存储 | 单文件 |
|---|---:|---:|---:|---:|
| free | 100 | 20 | 500 MB | 10 MB |
| pro | 3000 | 500 | 10 GB | 100 MB |

注册时会自动为用户创建 free subscription。

## 配额读取方式

配额不再只从 `.env` 读取，而是：

```text
user_id
  → active subscription
  → plan_code
  → plans 表
  → limit
```

使用位置：

- chat message quota
- code execution quota
- upload file size limit
- usage panel 展示

## 用量指标

当前 usage_records 支持：

```text
message
code_execution
uploaded_file_bytes
generated_file_bytes
llm_prompt_tokens
llm_completion_tokens
llm_total_tokens
```

## 下一步

1. 前端将同步 chat 切换为 async job 模式
2. 增加 job polling UI
3. 增加套餐管理接口
4. 接入 Stripe / Paddle / 国内支付
5. 增加团队 organization 共享配额
