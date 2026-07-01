# 05. 任务拆分

## 阶段 1：项目初始化

- [x] 初始化 README
- [x] 建立 docs 文档目录
- [x] 输出需求分析
- [x] 输出 MVP 范围
- [x] 输出产品流程
- [x] 输出技术架构
- [x] 建立后端骨架
- [x] 建立前端骨架
- [x] 建立沙箱骨架

## 阶段 2：后端基础

- [x] FastAPI 入口
- [x] 配置模块
- [x] Chat API 请求响应模型
- [x] Agent Runtime 初版
- [x] 工具注册器初版
- [x] 文件工具初版
- [x] Python 沙箱工具初版
- [ ] 接入真实 LLM API
- [ ] 增加流式输出
- [ ] 增加持久化会话

## 阶段 3：前端基础

- [x] Next.js 项目骨架
- [x] 聊天页面初版
- [x] API 调用示例
- [ ] 文件上传组件
- [ ] 工具调用状态展示
- [ ] 生成文件下载区
- [ ] SSE / WebSocket 流式消息

## 阶段 4：工具系统

- [x] list_files
- [x] read_text_file
- [x] write_text_file
- [x] execute_python 接口骨架
- [ ] CSV 预览工具
- [ ] Excel 读取工具
- [ ] 图表生成工具
- [ ] 文件下载 URL 工具
- [ ] 工具调用日志持久化

## 阶段 5：安全加固

- [x] workspace 路径校验设计
- [x] Docker 沙箱设计
- [x] 禁止默认网络设计
- [x] 执行超时设计
- [ ] 单元测试覆盖路径逃逸
- [ ] Docker 资源限制验证
- [ ] 文件大小限制
- [ ] 高风险工具确认机制

## 阶段 6：测试与部署

- [x] 测试计划文档
- [x] docker-compose 初版
- [ ] 后端单元测试
- [ ] 集成测试
- [ ] GitHub Actions CI
- [ ] 部署文档

## 第一版优先级

建议按以下顺序继续开发：

1. 接入真实模型 API
2. 完成文件上传接口
3. 完成前端上传组件
4. 让 Agent 自动调用 list/read/write/execute 工具
5. 增加 CSV / Excel 处理
6. 增加下载文件展示
7. 增加测试与 CI
