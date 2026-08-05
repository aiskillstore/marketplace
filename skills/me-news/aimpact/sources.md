# ME News Sources Configuration

## Active Sources

### MetaEra AI 快讯
- URL: https://agent.me.news/skill/flash/list?page=1&size=20&category=ai
- Type: API
- Scope: AI 分类快讯
- Priority: Primary

### Aimpact AI 新闻
- URL: https://agent.me.news/skill/aimpact/articles?page=1&size=20&category=ai
- Type: API
- Scope: AI 新闻列表
- Priority: Primary

### Aimpact OpenClaw 新闻
- URL: https://agent.me.news/skill/aimpact/articles?page=1&size=20&category=openclaw
- Type: API
- Scope: OpenClaw 新闻列表
- Priority: Primary

### Aimpact 行业大事件
- URL: https://agent.me.news/skill/aimpact/events
- Type: API
- Scope: AI 行业大事件
- Priority: Primary

## Source Strategy
- 当前仅使用 ME News 自有信源
- 执行前必须读取本文件，按已启用信源采集
- 后续新增信源按同一格式追加到 `Active Sources`
