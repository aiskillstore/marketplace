# Tavily Search Free Skill

使用 Tavily Search API 进行高质量、实时的网络搜索，专为 LLMs 和 RAG（检索增强生成）管道优化。这是一个预配置的、性价比高的搜索工具。

## 特性

- 🔍 **实时搜索**: 获取最新的网络信息
- 🎯 **LLM 优化**: 结果格式专为大语言模型设计
- 💰 **成本效益**: 免费层级支持，适合个人项目
- 🚀 **简单易用**: 预配置 API，开箱即用
- 📊 **灵活配置**: 支持基本和高级搜索模式

## 快速开始

### 1. 安装依赖

```bash
cd ~/.pi/agent/skills/tavily-search-free
pip install tavily-python python-dotenv
```

### 2. 配置 API Key

在 `.env` 文件中配置 Tavily API Key：

```bash
TAVILY_API_KEY=your_api_key_here
```

> 💡 **提示**: 如需获取免费 API Key，请访问 [https://tavily.com/](https://tavily.com/)

### 3. 使用搜索

#### 方式 1: 通过 pi 自动调用（推荐）

`pi` 会自动调用此技能进行网络搜索，无需手动执行命令。

#### 方式 2: 手动执行

```bash
# 基本搜索
python3 scripts/tavily_search.py --query "latest AI trends"

# 深度搜索（更高质量但更慢）
python3 scripts/tavily_search.py --query "autonomous research agents" --search-depth advanced

# 限制结果数量
python3 scripts/tavily_search.py --query "Python best practices" --max-results 5
```

## 参数说明

| 参数 | 必填 | 默认值 | 说明 |
|-----|------|--------|------|
| `--query` | 是 | - | 搜索查询内容 |
| `--search-depth` | 否 | `basic` | 搜索深度：`basic` 或 `advanced` |
| `--max-results` | 否 | `10` | 最大返回结果数量（1-10） |

### 搜索深度

- **basic**: 快速搜索，适合一般查询
- **advanced**: 深度搜索，更高质量但响应时间更长

## 输出格式

脚本输出 JSON 格式，包含 `results` 数组：

```json
{
  "query": "latest AI trends",
  "search_depth": "basic",
  "max_results": 10,
  "results": [
    {
      "title": "Top AI Trends 2026",
      "url": "https://example.com/ai-trends",
      "content": "Summary of the content...",
      "score": 0.95,
      "raw_content": "Full content..."
    }
  ]
}
```

### 结果字段说明

- `title`: 页面标题
- `url`: 链接地址
- `content`: 内容摘要（适合 LLM 消费）
- `score`: 相关性评分（0-1）
- `raw_content`: 完整内容（可选）

## 使用示例

### 基本搜索

```bash
python3 scripts/tavily_search.py --query "TypeScript vs JavaScript"
```

### 高级搜索

```bash
python3 scripts/tavily_search.py \
  --query "best practices for microservices architecture" \
  --search-depth advanced \
  --max-results 5
```

### 在代码中使用

```python
import json
from tavily import TavilyClient

# 初始化客户端
client = TavilyClient(api_key="your_api_key")

# 执行搜索
response = client.search(query="latest AI news", max_results=5)

# 处理结果
for result in response["results"]:
    print(f"Title: {result['title']}")
    print(f"URL: {result['url']}")
    print(f"Content: {result['content']}\n")
```

## 与 Pi Agent 集成

此技能已集成到 Pi Agent 系统中，`pi` 会自动调用它进行网络搜索：

```bash
# pi 会自动使用 tavily-search-free 进行搜索
pi "搜索最新的 AI 发展趋势"
```

## 配置文件

### .env

```bash
# Tavily API Key
TAVILY_API_KEY=your_api_key_here
```

> ⚠️ **重要**: `.env` 文件已在 `.gitignore` 中，不会被提交到 Git。

## 常见问题

### Q: 如何获取免费的 Tavily API Key？

A: 访问 [https://tavily.com/](https://tavily.com/) 注册账号，免费层级每月提供 1,000 次搜索请求。

### Q: 搜索深度 basic 和 advanced 有什么区别？

A: `basic` 模式快速返回结果，适合一般查询；`advanced` 模式进行更深入的分析，质量更高但响应时间更长。

### Q: 如何在 Python 项目中导入使用？

A: 安装依赖后，直接导入 `tavily_search.py` 中的函数，或使用 Tavily SDK。

### Q: 搜索结果的数量有限制吗？

A: 免费层级每次最多返回 10 个结果，可通过 `--max-results` 参数调整。

## 性能优化

### 提高搜索速度
- 使用 `--search-depth basic`
- 减少 `--max-results` 数量
- 缓存常用查询结果

### 提高搜索质量
- 使用 `--search-depth advanced`
- 优化查询关键词
- 使用具体而非宽泛的查询

## 技术栈

- **Python**: 3.7+
- **tavily-python**: Tavily 官方 SDK
- **python-dotenv**: 环境变量管理

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎提交 Issue 和 Pull Request！

## 相关资源

- [Tavily 官网](https://tavily.com/)
- [Tavily 文档](https://docs.tavily.com/)
- [Tavily Python SDK](https://github.com/tavily/tavily-python)
- [Pi Agent Skills](https://github.com/Dwsy/pi-agent-skills)

## 作者

Created for Pi Agent System

---

**状态**: ✅ 生产就绪