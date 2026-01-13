# Crawl4AI Skill

> 强大的网页爬取和数据提取技能，支持 JavaScript 渲染、结构化数据提取和多 URL 批量处理。

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

基于 [crawl4ai-skill](https://github.com/brettdavies/crawl4ai-skill) 代码做基础实现。

## 特性

- **智能爬取** - 自动处理 JavaScript 渲染页面
- **结构化提取** - 支持 CSS 选择器和 LLM 两种提取模式
- **Markdown 生成** - 自动将网页内容转换为格式化的 Markdown
- **批量处理** - 高效处理多个 URL
- **会话管理** - 支持登录认证和状态保持
- **反爬虫对策** - 内置反检测和代理支持
- **Google 搜索** - 专用搜索结果提取脚本

## 安装

```bash
# 安装 crawl4ai
pip install crawl4ai

# 安装 Playwright 浏览器
crawl4ai-setup

# 验证安装
crawl4ai-doctor
```

## 快速开始

### CLI 模式（推荐）

```bash
# 基础爬取，输出 Markdown
crwl https://example.com

# JSON 格式输出
crwl https://example.com -o json

# 绕过缓存，详细输出
crwl https://example.com -o json -v --bypass-cache
```

### Python SDK

```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://example.com")
        print(result.markdown[:500])

asyncio.run(main())
```

## 使用示例

### Google 搜索爬取

```bash
# 搜索并提取前 20 个结果
python scripts/google_search.py "搜索关键词" 20

# 示例
python scripts/google_search.py "2026年Go语言展望" 20
```

**输出格式：**
```json
{
  "query": "搜索关键词",
  "total_results": 20,
  "results": [
    {
      "title": "结果标题",
      "link": "https://example.com",
      "description": "结果描述",
      "site_name": "网站名称"
    }
  ]
}
```

### 数据提取

#### 1. CSS 选择器提取（最快，无需 LLM）

```bash
# 生成提取 schema
python scripts/extraction_pipeline.py --generate-schema https://shop.com "提取所有商品信息"

# 使用 schema 进行提取
crwl https://shop.com -e extract_css.yml -s schema.json -o json
```

**Schema 格式：**
```json
{
  "name": "products",
  "baseSelector": ".product-card",
  "fields": [
    {"name": "title", "selector": "h2", "type": "text"},
    {"name": "price", "selector": ".price", "type": "text"},
    {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"}
  ]
}
```

#### 2. LLM 智能提取

```yaml
# extract_llm.yml
type: "llm"
provider: "openai/gpt-4o-mini"
instruction: "提取商品名称和价格"
api_token: "your-api-token"
```

```bash
crwl https://shop.com -e extract_llm.yml -o json
```

### Markdown 生成与过滤

```bash
# 基础 Markdown
crwl https://docs.example.com -o markdown > docs.md

# 过滤后的 Markdown（移除噪音）
crwl https://docs.example.com -o markdown-fit

# 使用 BM25 内容过滤
crwl https://docs.example.com -f filter_bm25.yml -o markdown-fit
```

**过滤器配置：**
```yaml
# filter_bm25.yml
type: "bm25"
query: "机器学习教程"
threshold: 1.0
```

### 动态内容处理

```bash
# 等待特定元素加载
crwl https://example.com -c "wait_for=css:.ajax-content,page_timeout=60000"

# 扫描整个页面
crwl https://example.com -c "scan_full_page=true,delay_before_return_html=2.0"
```

### 批量处理

```python
# Python SDK 并发处理
urls = [
    "https://site1.com",
    "https://site2.com",
    "https://site3.com"
]
results = await crawler.arun_many(urls, config=config)
```

### 登录认证

```yaml
# login_crawler.yml
session_id: "user_session"
js_code: |
  document.querySelector('#username').value = 'user';
  document.querySelector('#password').value = 'pass';
  document.querySelector('#submit').click();
wait_for: "css:.dashboard"
```

```bash
# 先登录
crwl https://site.com/login -C login_crawler.yml

# 访问受保护内容
crwl https://site.com/protected -c "session_id=user_session"
```

## 目录结构

```
crawl4ai/
├── README.md                   # 本文件
├── SKILL.md                    # 技能详细文档
├── scripts/                    # 实用脚本
│   ├── google_search.py       # Google 搜索爬虫
│   ├── extraction_pipeline.py # 数据提取管道
│   ├── basic_crawler.py       # 基础爬虫
│   └── batch_crawler.py       # 批量爬虫
├── references/                 # 参考文档
│   ├── cli-guide.md           # CLI 完整指南
│   ├── sdk-guide.md           # SDK 快速参考
│   └── complete-sdk-reference.md # 完整 API 文档
└── tests/                      # 测试文件
    ├── README.md
    ├── run_all_tests.py
    ├── test_basic_crawling.py
    ├── test_data_extraction.py
    ├── test_markdown_generation.py
    └── test_advanced_patterns.py
```

## 提供的脚本

| 脚本 | 功能 |
|------|------|
| `google_search.py` | Google 搜索结果爬取，JSON 输出 |
| `extraction_pipeline.py` | 三种提取策略：CSS/LLM/手动 |
| `basic_crawler.py` | 基础网页爬取，带截图功能 |
| `batch_crawler.py` | 批量 URL 处理 |

## 配置说明

### BrowserConfig（浏览器配置）

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `headless` | 无头模式 | `true` |
| `viewport_width` | 视口宽度 | `1920` |
| `viewport_height` | 视口高度 | `1080` |
| `user_agent` | 用户代理 | 随机 |
| `proxy_config` | 代理配置 | `null` |

### CrawlerRunConfig（爬虫配置）

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `page_timeout` | 页面超时(ms) | `30000` |
| `wait_for` | 等待条件 | `null` |
| `cache_mode` | 缓存模式 | `enabled` |
| `js_code` | 执行的 JS | `null` |
| `css_selector` | CSS 选择器 | `null` |

## 最佳实践

1. **优先使用 CLI** - 快速任务用 CLI，自动化用 SDK
2. **使用 Schema 提取** - 比 LLM 快 10-100 倍，零成本
3. **开发时启用缓存** - 只在需要时使用 `--bypass-cache`
4. **合理设置超时** - 普通站点 30s，JS 重度站点 60s+
5. **使用内容过滤** - 获取更干净的 Markdown 输出
6. **遵守速率限制** - 请求之间添加延迟

## 常见问题

### JavaScript 内容未加载

```bash
crwl https://example.com -c "wait_for=css:.dynamic-content,page_timeout=60000"
```

### 被反爬虫检测

```yaml
# browser.yml
headless: false
user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
user_agent_mode: "random"
```

### 提取内容为空

```bash
# 调试模式查看完整输出
crwl https://example.com -o all -v

# 尝试不同的等待策略
crwl https://example.com -c "wait_for=js:document.querySelector('.content')!==null"
```

## 文档

- [CLI 完整指南](references/cli-guide.md) - 命令行接口详解
- [SDK 快速参考](references/sdk-guide.md) - Python SDK 速查
- [完整 API 文档](references/complete-sdk-reference.md) - 5900+ 行完整参考

## 许可证

MIT License

## 相关链接

- [Crawl4AI 官方仓库](https://github.com/unclecode/crawl4ai)
- [Playwright 文档](https://playwright.dev/python/)
- [BeautifulSoup 文档](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
