# AIMPACT Prediction Market Sources Configuration

## Active Sources

### MetaEra Prediction 快讯 API
- URL: https://agent.me.news/skill/flash/list?page=1&size=20&category=prediction
- Type: API
- Scope: 预测市场分类快讯
- Priority: Primary
- Rate Limit: 按 ME News API 限制

### ME News Poly Events API
- URL: https://agent.me.news/skill/poly/events?page=1&size=20&active_only=true
- Type: API
- Scope: ME News 聚合的预测市场事件（仅活跃事件）
- Priority: Primary
- Rate Limit: 按 ME News API 限制

## Source Strategy
- 优先使用 MetaEra Prediction 快讯 API 获取最新预测市场快讯
- 同步使用 ME News Poly Events API 获取活跃事件详情并补充结构化数据
- 执行前必须读取本文件，按已启用信源采集
- 后续新增平台（如 Manifold、Metaculus）按同一格式追加到 `Active Sources`
- 注意 API Rate Limit，避免过度调用
