# AIMPACT Crypto Sources Configuration

## Active Sources

### MetaEra AI 快讯
- URL: https://agent.me.news/skill/flash/list?page=1&size=20
- Type: API
- Scope: 全量快讯（需筛选 Crypto 相关新闻）
- Priority: Primary

### Aimpact Crypto 新闻
- URL: https://agent.me.news/skill/aimpact/articles?page=1&size=20&category=crypto
- Type: API
- Scope: Crypto 新闻列表
- Priority: Primary

## Source Strategy
- 优先读取 MetaEra 全量快讯，并从返回结果中筛选 Crypto 相关新闻
- 同步使用 AIMPACT Crypto 新闻作为主信源补充
- 执行前必须读取本文件，按已启用信源采集
- 后续新增信源按同一格式追加到 `Active Sources`
