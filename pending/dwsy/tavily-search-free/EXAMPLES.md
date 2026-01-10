# Tavily Search Examples

本目录包含 Tavily Search 技能的使用示例。

## 示例 1: 基本搜索

```bash
python3 scripts/tavily_search.py --query "latest AI trends"
```

**预期输出**:
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
      "score": 0.95
    }
  ]
}
```

## 示例 2: 高级搜索

```bash
python3 scripts/tavily_search.py \
  --query "best practices for microservices architecture" \
  --search-depth advanced \
  --max-results 5
```

**说明**: 使用高级搜索模式，返回 5 个高质量结果。

## 示例 3: 技术对比搜索

```bash
python3 scripts/tavily_search.py --query "TypeScript vs JavaScript 2026"
```

**说明**: 搜索技术对比信息，获取最新观点。

## 示例 4: 编程问题搜索

```bash
python3 scripts/tavily_search.py --query "how to handle async errors in Python"
```

**说明**: 搜索编程相关的解决方案。

## 示例 5: 行业趋势搜索

```bash
python3 scripts/tavily_search.py \
  --query "cloud computing trends 2026" \
  --search-depth advanced \
  --max-results 8
```

**说明**: 深度搜索行业趋势信息。

## 示例 6: Python 集成示例

创建文件 `search_example.py`:

```python
import json
import sys
import os

# 添加脚本目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from tavily_search import tavily_search

# 执行搜索
query = "latest AI developments"
results = tavily_search(query, max_results=5, search_depth="basic")

# 打印结果
print(json.dumps(results, indent=2, ensure_ascii=False))

# 遍历结果
for result in results.get('results', []):
    print(f"\nTitle: {result.get('title')}")
    print(f"URL: {result.get('url')}")
    print(f"Content: {result.get('content', '')[:100]}...")
```

运行:
```bash
python3 search_example.py
```

## 示例 7: 批量搜索

创建文件 `batch_search.py`:

```python
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from tavily_search import tavily_search

queries = [
    "Python best practices 2026",
    "TypeScript tips and tricks",
    "React performance optimization",
    "Docker container security"
]

for query in queries:
    print(f"\n{'='*60}")
    print(f"Searching: {query}")
    print('='*60)
    
    results = tavily_search(query, max_results=3, search_depth="basic")
    
    for i, result in enumerate(results.get('results', []), 1):
        print(f"\n{i}. {result.get('title')}")
        print(f"   URL: {result.get('url')}")
        print(f"   Score: {result.get('score', 0):.2f}")
```

运行:
```bash
python3 batch_search.py
```

## 示例 8: 在 Pi Agent 中使用

```bash
# pi 会自动调用 tavily-search-free
pi "搜索最新的 AI 发展趋势"

# 或者明确指定
pi "使用 tavily 搜索 Python 异步编程最佳实践"
```

## 示例 9: 结果过滤和排序

创建文件 `filter_results.py`:

```python
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from tavily_search import tavily_search

query = "machine learning frameworks"
results = tavily_search(query, max_results=10, search_depth="advanced")

# 按分数排序
sorted_results = sorted(
    results.get('results', []),
    key=lambda x: x.get('score', 0),
    reverse=True
)

# 过滤高分结果
high_score_results = [r for r in sorted_results if r.get('score', 0) > 0.8]

print(f"Total results: {len(results.get('results', []))}")
print(f"High score results (>0.8): {len(high_score_results)}")

for i, result in enumerate(high_score_results[:5], 1):
    print(f"\n{i}. {result.get('title')} (Score: {result.get('score', 0):.2f})")
    print(f"   {result.get('content', '')[:150]}...")
```

运行:
```bash
python3 filter_results.py
```

## 示例 10: 保存结果到文件

创建文件 `save_results.py`:

```python
import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from tavily_search import tavily_search

query = "latest tech news"
results = tavily_search(query, max_results=10, search_depth="basic")

# 生成文件名
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"search_results_{timestamp}.json"

# 保存结果
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Results saved to: {filename}")
```

运行:
```bash
python3 save_results.py
```

## 常见使用场景

### 场景 1: 研究新技术
```bash
python3 scripts/tavily_search.py --query "Rust programming language advantages"
```

### 场景 2: 查找最佳实践
```bash
python3 scripts/tavily_search.py --query "REST API design best practices"
```

### 场景 3: 故障排查
```bash
python3 scripts/tavily_search.py --query "Docker container not starting permission denied"
```

### 场景 4: 行业分析
```bash
python3 scripts/tavily_search.py --query "fintech market trends 2026" --search-depth advanced
```

### 场景 5: 学习资源
```bash
python3 scripts/tavily_search.py --query "best Python tutorials for beginners"
```

## 性能对比

| 搜索模式 | 响应时间 | 结果质量 | 适用场景 |
|---------|---------|---------|---------|
| basic | ~1-2s | 良好 | 日常查询 |
| advanced | ~3-5s | 优秀 | 深度研究 |

## 注意事项

1. **API 限制**: 免费层级每月 1,000 次请求
2. **查询优化**: 使用具体关键词提高结果质量
3. **结果缓存**: 考虑缓存常用查询以节省 API 调用
4. **错误处理**: 在生产代码中添加适当的错误处理

## 更多示例

如需更多示例，请查看 [Tavily 官方文档](https://docs.tavily.com/)。