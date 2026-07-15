# 软件工程师 Agent 综合参考

> 本文档记录了 `software-architect`（software-architecture/ 分类）与 `software-engineering/` 分类下 16 个工程师 Agent 的完整关系图谱。
> 共计 17 个 Agent（1 架构师 + 16 工程师）。
> 对应 PDF 综合报告：`/Users/zhanglin/软件工程师Agent综合汇报.pdf`
>
> **注意**：搜索软件工程师 Agent 时必须同时检查 `software-architecture/` 和 `software-engineering/` 两个分类，架构师常被遗漏。

## 16 个工程师 Agent 清单

| # | Agent名称 | 中文名 | 创建时间 | 所属层级 |
|---|-----------|--------|----------|----------|
| 1 | ops-engineer | 运维工程师 | 2026-07-15 11:04 | 基础设施与运维层 |
| 2 | backend-developer | 后端开发工程师 | 2026-07-15 11:10 | 后端服务层 |
| 3 | data-engineer | 数据工程师 | 2026-07-15 12:36 | 数据层 |
| 4 | security-engineer | 安全工程师 | 2026-07-15 12:47 | 风控安全层 |
| 5 | frontend-developer | 前端开发工程师 | 2026-07-15 14:09 | 前端展示层 |
| 6 | mobile-engineer | 移动端工程师 | 2026-07-15 14:09 | 移动端层 |
| 7 | devops-sre-engineer | DevOps/SRE工程师 | 2026-07-15 15:25 | 基础设施与运维层 |
| 8 | search-engineer | 搜索工程师 | 2026-07-15 15:26 | 搜索与检索层 |
| 9 | web-scraper | 爬虫/数据采集工程师 | 2026-07-15 15:26 | 数据采集层 |
| 10 | bi-analyst | BI/数据分析工程师 | 2026-07-15 15:29 | 数据分析层 |
| 11 | risk-control-engineer | 风控工程师 | 2026-07-15 15:31 | 风控安全层 |
| 12 | payment-engineer | 支付工程师 | 2026-07-15 15:32 | 支付交易层 |
| 13 | test-engineer | 测试工程师 | 2026-07-15 15:39 | 质量保障层 |
| 14 | ai-multimodal-engineer | AI/多模态工程师 | 2026-07-15 15:40 | AI/ML层 |
| 15 | perf-fullstack-engineer | 性能测试/全栈工程师 | 2026-07-15 15:40 | 质量保障层 |
| 16 | algorithm-engineer | 算法工程师 | 2026-07-15 15:41 | AI/ML层 |

## 2. 分层架构关系

顶层设计层（跨层）：software-architect（架构设计、C4图、ADR、技术选型）
   │
前端展示层：frontend-developer, mobile-engineer
   │
后端服务层：backend-developer, payment-engineer, search-engineer
   │
AI/ML层：ai-multimodal-engineer, algorithm-engineer
   │
数据层：data-engineer, bi-analyst
   │
数据采集层：web-scraper
   │
风控安全层：risk-control-engineer, security-engineer
   │
质量保障层：test-engineer, perf-fullstack-engineer
   │
支付交易层：payment-engineer
   │
搜索与检索层：search-engineer
   │
基础设施与运维层：devops-sre-engineer, ops-engineer

## 3. 协作模式速查

| 模式 | 协作链路 | 适用场景 |
|------|----------|----------|
| 架构驱动 | software-architect > 全层Agent执行 | 新系统设计、技术栈选型 |
| Pipeline | web-scraper > data-engineer > bi-analyst > frontend-developer | 数据采集到展示 |
| DevOps | backend/frontend-developer > test-engineer > devops-sre-engineer > ops-engineer | 代码到上线 |
| Security Chain | security-engineer > devops-sre-engineer > risk-control-engineer | 全链路安全 |
| Data-Driven | web-scraper > data-engineer > bi-analyst > backend/frontend-developer | 数据驱动决策 |
| MLOps | data-engineer > algorithm/ai-engineer > test-engineer > devops-sre-engineer | AI模型全生命周期 |
| Payment Security | payment-engineer > risk-control-engineer > security-engineer > devops-sre-engineer | 支付安全 |
| Search + AI | search-engineer + ai-engineer > backend-developer > frontend-developer | 智能搜索 |
| Perf Optimization | perf-fullstack-engineer + test-engineer > backend/frontend-developer > devops-sre-engineer | 性能优化 |
