# 09. SaaS 开发路线图

## 总体路线

Xuan Agent 应按“先闭环、再多用户、再商业化”的路线推进。

```text
Phase 0：产品设计
Phase 1：单用户 MVP
Phase 2：多用户账号系统
Phase 3：SaaS 基础设施
Phase 4：Agent 能力增强
Phase 5：团队版与计费
Phase 6：生产级运营
```

## Phase 0：产品设计

目标：明确产品、架构、风险边界。

交付物：

- 需求分析
- MVP 范围
- 产品流程
- 技术架构
- 安全方案
- SaaS 架构
- 数据模型

状态：已完成初版。

## Phase 1：单用户 MVP

目标：跑通 Agent 核心闭环。

功能：

- FastAPI 后端
- Next.js 前端
- Chat API
- 文件上传
- Workspace 文件管理
- Python 沙箱执行
- 文件生成与下载
- 工具调用日志

验收标准：

- 用户能发消息
- 用户能上传 CSV / TXT
- Agent 能读取文件
- Agent 能执行 Python
- Agent 能生成输出文件

## Phase 2：多用户账号系统

目标：支持真实用户注册和登录。

功能：

- 用户注册
- 用户登录
- JWT 鉴权
- 密码哈希
- current_user 中间件
- 每个用户独立 workspace
- sessions/messages/files 绑定 user_id

验收标准：

- A 用户看不到 B 用户文件
- A 用户不能访问 B 用户 session
- 所有 API 必须鉴权
- 文件下载必须鉴权

## Phase 3：SaaS 基础设施

目标：具备对外服务的基础能力。

功能：

- PostgreSQL 持久化
- Redis 队列
- Worker 执行任务
- 对象存储 MinIO / S3
- 用量统计 usage_records
- 限流 rate limit
- 审计日志 audit_logs
- 错误监控

验收标准：

- 长任务不阻塞 API
- 用户用量可统计
- 系统错误可追踪
- 文件可持久保存

## Phase 4：Agent 能力增强

目标：让 Agent 从“工具调用 Demo”变成实用助手。

功能：

- 接入真实 LLM Tool Calling
- Planner / Executor
- 文件解析增强
- CSV / Excel 分析
- 图表生成
- 文档总结
- 代码调试
- 工具调用可视化
- 失败重试

验收标准：

- 能稳定分析 Excel / CSV
- 能解释并修复 Python 错误
- 能生成图表和报告
- 工具失败后能给出清晰原因

## Phase 5：团队版与计费

目标：具备商业化能力。

功能：

- 订阅套餐
- 免费版 / Pro / Team
- 配额控制
- 支付平台接入
- organization
- organization_members
- 团队 workspace
- 成员角色权限
- 管理账单页面

验收标准：

- 免费用户有额度限制
- Pro 用户有更高额度
- 团队可以邀请成员
- 管理员可以查看团队用量

## Phase 6：生产级运营

目标：长期稳定运营。

功能：

- 管理后台
- 风控规则
- 文件安全扫描
- 成本看板
- 用户行为分析
- 模型调用成本统计
- 灰度发布
- 备份与恢复
- SLA 监控

验收标准：

- 能定位用户问题
- 能控制模型和沙箱成本
- 能发现滥用行为
- 能稳定扩容

## 技术债控制原则

从第一版开始避免以下设计：

- 不要把文件路径只按 session_id 存，必须包含 user_id
- 不要让前端传来的 user_id 直接生效，必须从 token 解析
- 不要无鉴权下载文件
- 不要把代码执行放在 API 进程里
- 不要把工具调用结果只放内存
- 不要绕过 Tool Registry 直接执行工具

## 当前最优开发顺序

接下来建议按这个顺序写代码：

1. Backend FastAPI 骨架
2. Auth 数据模型和 current_user 中间件
3. WorkspaceService，路径中包含 user_id
4. Session / Message 表结构
5. File API，上传和下载都鉴权
6. Agent Runtime，支持工具调用
7. Python Sandbox，绑定 user workspace
8. Usage 记录
9. 前端登录页和聊天页
10. Worker 队列

## 一句话原则

这个项目要按 SaaS 架构从第一行代码开始写，哪怕第一版只给一个人用。
