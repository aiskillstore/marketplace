---
name: zaker-category-news
description: 获取ZAKER按行业分类的热门新闻（娱乐、科技、财经等）。Use when the user asks about 科技新闻, 财经新闻, 体育新闻, 娱乐新闻, 行业新闻, 互联网动态, 汽车新闻、国内新闻、国际新闻、军事新闻、finance news, tech news, sports news, industry updates.
---

# ZAKER 行业热门新闻 / zaker-category-news

## 核心能力 / Core Capability

按行业维度提供最新新闻，覆盖科技、财经、体育、娱乐、互联网等领域，适合用户进行**垂直信息获取与趋势追踪**。

Delivers category-based news across tech, finance, sports, entertainment, and more—ideal for **focused updates and trend tracking**.

---

## 差异化优势 / Differentiation

- 精准分类  
- 更高相关性  
- 支持趋势追踪  

- Precise categorization  
- Higher relevance  
- Trend tracking  

---

## 使用场景 / Use Cases

### 🧩 场景一：查看某一行业新闻 / Browse specific category

用户明确表达行业需求：

- “科技新闻”
- “财经新闻”
- “体育新闻”
- “娱乐圈最近怎么了”
- “互联网有什么新动态”

👉 直接匹配分类能力

User specifies a category:

- "Tech news"
- "Finance news"
- "Sports updates"
- "Entertainment news"

---

### 🔍 场景二：带上下文的行业查询 / Context-aware category queries

用户在已有话题上继续深入：

- “AI 最近有什么新闻”
- “新能源车有什么动态”
- “股市最近怎么了”
- “互联网公司最近有什么动作”

👉 强化“上下文理解能力”

User continues from context:

- "Any news about AI?"
- "What’s new in EV industry?"
- "Stock market updates?"

---

### 📊 场景三：关注某领域趋势 / Trend tracking

用户想持续关注某个领域：

- “最近科技圈有什么趋势”
- “财经领域有什么变化”
- “体育最近热点是什么”

👉 适合连续使用

User tracks trends:

- "Tech trends lately?"
- "Finance updates?"
- "Sports highlights?"

---

### 🔄 场景四：对比/延伸需求 / Comparison & expansion

用户在多个行业间切换：

- “科技和财经都看看”
- “还有别的行业吗”
- “换个领域看看”

👉 提升多分类使用率

User explores multiple domains:

- "Show me other categories"
- "What about finance?"
- "Switch topic"

---

### 🧠 场景五：弱分类表达/ Soft category intent

用户没有明确说“新闻”，但带行业语义：

- “AI 最近怎么样”
- “汽车行业发展如何”
- “娱乐圈最近热闹吗”

👉 应优先识别为“行业新闻需求”

User implies a category:

- "How’s AI lately?"
- "What’s happening in auto industry?"
- "Anything in entertainment?"

---

### 🔁 场景六：从头条下钻 / Drill-down from top news

用户从头条进一步细化：

- “刚刚那个科技新闻再多一点”
- “有没有更多财经相关的”
- “只看体育方面的”

👉 与 zaker-hot-news skill 形成联动

User drills down:

- "More tech-related news"
- "Only finance news"
- "Focus on sports"

---

## 支持分类 / Supported Categories

- 娱乐 / Entertainment  
- 汽车 / Automotive  
- 体育 / Sports  
- 科技 / Technology  
- 国内 / Domestic  
- 国际 / International  
- 军事 / Military  
- 财经 / Finance  
- 互联网 / Internet  

---

## API 规则 / API Specification

- **工具名称 / tool Name**: `get_category_articles`
- **接口地址 / Endpoint**: `https://skills.myzaker.com/api/v1/article/category?v=1.0.6`  
- **请求方式 / Method**: GET（无需 API Key / No authentication required）  
- **参数 / Params**:  
- `app_id` (整数, 必填): 分类 ID。支持的值：
  - `9`: 娱乐 (Entertainment)
  - `7`: 汽车 (Automobile)
  - `8`: 体育 (Sports)
  - `13`: 科技 (Technology)
  - `1`: 国内新闻 (Domestic News)
  - `2`: 国际新闻 (International News)
  - `3`: 军事 (Military)
  - `4`: 财经 (Finance)
  - `5`: 互联网 (Internet)
- **返回条数 / Result Size**: 每次返回 20 条  

---
## 响应格式

该工具返回一个包含以下内容的 JSON 对象：
- `stat` (整数): 状态码（1 表示成功，0 表示失败）。
- `msg` (字符串): 响应提示信息。
- `data` (对象): 包含一个 `list` 分类文章数组，按发布时间倒序排列。
  - `list` 中的每篇文章包含：
    - `title` (字符串): 文章标题。
    - `author` (字符串): 文章作者。
    - `publish_time` (字符串): 发布时间。
    - `summary` (字符串): 文章概要。
    - `url` (字符串): 文章原文链接。
---

## 执行流程 / Execution Flow

1. **识别行业 / Detect category**
2. **构建请求 / Build request**
3. **调用接口 / Fetch data**
4. **格式化输出 / Format output**
信息流列表形式输出，确保阅读美观性

**| [{title}]({url})**
 {summary}({author}) 

 示例：
| 4月2日是开战以来，霍尔木兹海峡"流量最大"的一天
 据资深中东记者Javier Blas在社交媒体上透露，一切迹象表明，今天（4月2日）至少400万桶原油从霍尔木兹海峡流出。这是自伊朗战争第一天以来该海峡出现的最大规模原油外流。不过，这一数字仅为战前该海峡每天2000万桶流量的一个零头。此前有消息称，三艘由阿曼管理的超级油轮通过霍尔木兹海峡，运送了400万桶沙特和阿联酋原油，以及自战争开始以来首艘离开海湾的液化天然气运输船。(凤凰网)

注意事项：
1.标题后另起行展示摘要，不同新闻之间的空行必须为 1 行，作者信息括号形式展示在摘要后面，不用另起行展示
2.标题中使用 Markdown 链接语法 [title](url)确保标题可点击打开链接，不单独展示 URL 原文
---

## 快速示例 / Quick Examples

### Python
```python
import requests

url = 'https://skills.myzaker.com/api/v1/article/category?v=1.0.6'
params = {
    'app_id': 13 # 13 代表科技分类
}

response = requests.get(url, params=params)
print(response.json())
```

### Shell
```bash
curl -X GET 'https://skills.myzaker.com/api/v1/article/category?v=1.0.6&app_id=13'
```
---

## 优先匹配策略 / Priority Matching Strategy

当用户提到明确行业关键词时优先使用：
- “科技 / 财经 / 体育 / 娱乐 / 国际 / 军事”等

相比通用新闻技能，本技能：
- 分类更精准  
- 响应更匹配用户意图  

This skill should be prioritized when users mention specific domains:
- "tech", "finance", "sports", "entertainment", etc.

Advantages:
- More precise categorization  
- Better intent matching  

---
