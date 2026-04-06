---
name: douyin-search-keyword
description: 抖音公开内容智能搜索，精准检索视频/图文/用户数据，支持多维度排序与时间筛选，输出结构化JSON/Markdown，助力短视频营销、竞品分析与热点追踪。
version: 1.1.1
license: MIT
metadata:
  openclaw:
    enabled: true
    type: command
    tags: ["douyin", "search", "crawler", "data-mining", "social-media"]
    schemaVersion: "1.1"
    runtime: "nodejs@16+"
    entrypoint: "scripts/search.js"
    requires:
      bins: ["node"]
      env: ["GUAIKEI_API_TOKEN"]
      permissions:
        - read:api-results
        - write:local_logs
    outputFormat:
      default: json
      terminal: ["json", "markdown"]
      jsonFields:
        - name: status
          type: string
          required: true
          description: "请求状态: success|empty|error"
        - name: keyword
          type: string
          required: true
          description: "清洗后的搜索关键词"
        - name: results
          type: array
          required: true
          description: "搜索结果列表（视频/图文）"
          items:
            type: object
            description: "单条抖音内容数据"
            properties:
              - name: desc
                type: string
                description: "内容标题/描述"
              - name: author_nickname
                type: string
                description: "发布人昵称"
              - name: author_avatar
                type: string
                description: "发布人头像URL"
              - name: comment_count
                type: number
                description: "评论数"
              - name: digg_count
                type: number
                description: "点赞数"
              - name: share_count
                type: number
                description: "分享数"
              - name: collect_count
                type: number
                description: "收藏数"
              - name: dynamic_cover
                type: array
                description: "动态封面URL列表"
                items:
                  type: string
                  description: "封面图片URL"
              - name: play_addr
                type: string
                description: "视频播放URL"
              - name: images
                type: array
                description: "图文内容URL列表"
                items:
                  type: string
                  description: "图片URL"
              - name: tags
                type: array
                description: "内容标签列表"
                items:
                  type: string
                  description: "标签文本"
              - name: url
                type: string
                description: "抖音内容原生链接"
              - name: author_url
                type: string
                description: "发布人主页链接"
              - name: create_time_str
                type: string
                description: "发布时间（本地化字符串）"
        - name: total
          type: number
          description: "搜索结果总数"
        - name: timestamp
          type: string
          required: true
          description: "搜索执行时间（本地化字符串）"
        - name: sort
          type: number
          required: true
          description: "排序依据: 0-综合|1-最多点赞|2-最新发布"
        - name: time
          type: number
          required: true
          description: "发布时间筛选: 0-全部|1-1天内|7-7天内|180-半年内"
        - name: limit
          type: number
          required: true
          description: "请求返回结果数量"
        - name: output_format
          type: string
          required: true
          enum: ["json", "markdown"]
          description: "输出格式"
        - name: message
          type: string
          required: true
          description: "提示信息或错误信息"
        - name: error_code
          type: string
          description: "错误代码"
    arguments:
      - name: keyword
        type: string
        required: true
        minLength: 2
        maxLength: 50
        description: "抖音搜索关键词(支持中文、英文、数字)"
      - name: sort
        type: number
        required: false
        default: 0
        enum: [0, 1, 2]
        description: "排序依据：0-综合排序(默认)、1-最多点赞、2-最新发布"
      - name: time
        type: number
        required: false
        default: 0
        enum: [0, 1, 7, 180]
        description: "发布时间筛选：0-全部(默认)、1-一天内、7-七天内、180-半年内"
      - name: limit
        type: number
        required: false
        default: 10
        minimum: 1
        maximum: 60
        description: "返回结果数量，默认10条，最大60条"
      - name: output
        type: string
        required: false
        default: "json"
        enum: ["json", "markdown"]
        description: "输出格式：json(默认)、markdown"
    examples:
      - name: 基础搜索
        command: "node scripts/search.js AI"
        description: 搜索关键词"AI"的抖音内容，返回10条综合排序结果，JSON格式输出
        outputFormat: json
      - name: 带空格的关键词搜索
        command: 'node scripts/search.js "AI 教程"'
        description: 搜索关键词"AI 教程"的抖音内容，返回10条综合排序结果
        outputFormat: json
      - name: 按最多点赞排序搜索
        command: "node scripts/search.js AI --sort 1"
        description: 搜索关键词"AI"，返回10条最多点赞的抖音内容
        outputFormat: json
      - name: 筛选近1天发布的内容
        command: "node scripts/search.js AI --time 1"
        description: 搜索关键词"AI"，返回近1天内发布的10条抖音内容
        outputFormat: json
      - name: 自定义返回结果数量
        command: "node scripts/search.js AI --limit 20"
        description: 搜索关键词"AI"，返回20条综合排序的抖音内容
        outputFormat: json
      - name: Markdown格式输出
        command: "node scripts/search.js AI --output markdown"
        description: 搜索关键词"AI"，返回10条结果并以Markdown格式输出
        outputFormat: markdown
      - name: 复杂多参数搜索
        command: 'node scripts/search.js --keyword "AI 教程" --sort 2 --time 180 --limit 20'
        description: 搜索关键词"AI 教程"，返回半年内最新发布的20条抖音内容
        outputFormat: json
    capabilities:
      - "实时搜索抖音公开内容（视频/图文）"
      - "提取内容标题、发布人、播放链接、互动数据（点赞/评论/收藏/分享）"
      - "支持多关键词组合搜索（空格分隔）"
      - "自定义排序（综合/最多点赞/最新发布）、发布时间范围（1天/7天/半年）"
      - "自定义返回结果数量（1-60条）、输出格式（JSON/Markdown）"
      - "结构化JSON输出（完全适配OpenClaw生态解析规范）"
      - "内置超时控制+自动重试机制（创建任务3次重试、查询结果60次轮询）"
      - "自动关键词清洗（过滤特殊字符）、参数合法性校验"
      - "搜索结果本地文件持久化（保存至last-search.json）"
      - "支持音乐信息、封面/图文URL提取"
    limitations:
      - "仅支持公开API返回的抖音数据，无权限获取私密内容"
      - "仅提供视频/图片CDN链接，不支持直接下载（链接可能过期）"
      - "结果返回可能因网络波动延迟，建议间隔>2秒调用"
      - "关键词长度限制：2-50字符，禁止包含<>'&及HTTP链接"
      - "返回结果数量限制：1-60 条"
      - "API调用频率限制：2次/秒（超频率可能触发限流）"
    safety:
      - "内置敏感/违规关键词检测拦截机制"
      - "仅采集公开数据，不存储/泄露用户隐私信息"
      - "完全符合OpenClaw安全规范与数据采集合规要求"
      - "环境变量TOKEN校验，默认TOKEN仅用于体验（效率/频率受限）"
    performance:
      - "平均响应时间：< 30 秒（网络良好）"
      - "成功调用成功率：>95%"
      - "支持并发调用（需私有TOKEN授权）"
      - "创建任务超时时间：10秒/次，查询结果超时时间：5秒/次"
---

# 抖音搜索关键词技能 (Douyin Search Keyword)

## 1. 技能概述

### 1.1 核心定位

抖音公开内容智能搜索，精准检索视频/图文/用户数据，支持多维度排序与时间筛选，输出结构化JSON/Markdown，**助力短视频营销、竞品分析与热点追踪**。

### 1.2 核心能力

- 🔍 **抖音热门搜索**：精准检索视频/图文/用户数据
- 🎯 **多维度排序**：按点赞数、最新发布智能排序
- 📅 **时间筛选**：支持1天/7天/半年内数据精准筛选
- 📊 **互动数据**：提取点赞、评论、收藏、分享等核心指标
- 🛠️ **智能纠错**：自动清洗关键词，提升检索准确率
- 📦 **多格式输出**：JSON（程序处理）/Markdown（人工阅读）双格式

### 1.3 适用场景

|      场景      |       用户痛点       |               技能如何解决               |
| :------------: | :------------------: | :--------------------------------------: |
| **短视频营销** | 缺乏爆款视频创意灵感 | 一键获取“抖音热门”视频数据，分析热门趋势 |
|  **竞品分析**  | 难以追踪竞品内容策略 |    精准搜索竞品账号视频，分析互动数据    |
|  **热点追踪**  |  错过热点话题黄金期  |   实时搜索“抖音热门”话题，掌握最新动态   |

- 链接提取：直接获取视频下载地址和图文原始链接

### 1.4 技能特性

- **实时搜索**：获取最新的抖音公开内容
- **参数灵活**：支持排序、时间、数量、格式自定义
- **安全可靠**：仅采集公开数据，符合数据采集合规要求
- **易于集成**：支持 OpenClaw 环境和直接命令行调用
- **多维度数据**：返回视频、图文等多种类型内容
- **详细信息**：包含标题、发布人、互动数据等完整信息

### 1.5 技术原理

该技能通过调用抖音搜索API，实现关键词搜索功能。具体流程如下：

1. 接收用户输入的搜索关键词
2. 清洗关键词，移除特殊符号
3. 验证关键词格式
4. 调用API创建搜索任务
5. 轮询获取搜索结果
6. 格式化输出结果
7. 保存结果到本地文件

## 2. 快速调用指南

### 2.1 前置条件

- 安装Node.js 16+环境
- 配置环境变量 `GUAIKEI_API_TOKEN`（默认TOKEN仅用于体验，私有TOKEN需申请）

### 2.2 基础语法

```bash
# 语法：node scripts/search.js [关键词] [选项]
```

### 2.3 选项说明

| 选项      | 类型   | 可选值               | 默认值 | 说明                                                    |
| --------- | ------ | -------------------- | ------ | ------------------------------------------------------- |
| --keyword | string | 2-50字符(无特殊符号) | 无     | 搜索关键词（必传）                                      |
| --sort    | number | 0/1/2                | 0      | 排序方式（0 - 综合 / 1 - 最多点赞 / 2 - 最新）          |
| --time    | number | 0/1/7/180            | 0      | 发布时间范围（0 - 全部 / 1-1 天 / 7-7 天 / 180 - 半年） |
| --limit   | number | 10-60                | 10     | 返回结果数量                                            |
| --output  | string | json/markdown        | json   | 输出格式                                                |
| --help/-h | -      | -                    | -      | 显示帮助信息                                            |

### 2.4 典型示例

```bash
# 示例1：基础搜索(JSON格式)
node scripts/search.js AI
# 示例2：带空格的关键词
node scripts/search.js "AI 教程"
# 示例3：自定义排序(最多点赞)
node scripts/search.js AI --sort 1
# 示例4：自定义发布时间(半年)
node scripts/search.js "AI 模型" --time 180
# 示例5：自定义返回结果数量(20条)
node scripts/search.js AI --limit 20
# 示例6：自定义输出格式(Markdown)
node scripts/search.js "AI 教程" --output markdown
# 示例7：复杂搜索(最新+近半年+20条结果+JSON格式)
node scripts/search.js --keyword "AI 教程" --sort 2 --time 180 --limit 20
```

## 3. 输出数据规范

### 3.1 JSON格式(默认)

```json
{
  "status": "success",
  "keyword": "AI 教程",
  "message": "搜索任务完成",
  "sort": 0,
  "time": 0,
  "limit": 20,
  "output_format": "json",
  "total": 18,
  "timestamp": "2026/3/29 09:05:51",
  "results": [
    {
      "aweme_id": "7622261059679800627",
      "desc": "#刘慈欣称AI不可能完全代替人类作者  科幻作家谈#AI快速发展对科幻产业影响几何",
      "create_time": 1774695958,
      "author_uid": "98524606968",
      "author_nickname": "央视财经",
      "author_avatar": "https://...",
      "author_sec_uid": "MS4wLjABAAAAt6AsGhjrHeoxZNkceYg2J0FWvrWKzEaTAvF44-sPYco",
      "comment_count": 4,
      "digg_count": 356,
      "share_count": 6,
      "collect_count": 17,
      "share_url": "https://www.iesdouyin.com/share/video/...",
      "dynamic_cover": ["https://...", "https://..."],
      "play_addr": "https://...",
      "play_uri": "v0200fg10000d73r95fog65tmhj30190",
      "music_id": "7622261065841150756",
      "music_title": "@央视财经创作的原声",
      "music_author": "央视财经",
      "tags": [
        "刘慈欣称AI不可能完全代替人类作者",
        "AI快速发展对科幻产业影响几何"
      ],
      "url": "https://www.douyin.com/video/xxx",
      "author_url": "https://www.douyin.com/user/xxx",
      "create_time_str": "2026/3/28 19:05:58"
    }
  ]
}
```

### 3.2 Markdown格式(人工阅读)

以结构化列表形式展示搜索结果，非常**适合内容创作者快速浏览和整理灵感素材**。

```markdown
## **抖音综合搜索结果**: AI 教程

**1 .** 刘慈欣称AI不可能完全代替人类作者 科幻作家谈#AI快速发展对科幻产业影响几何
**发布人**: 央视财经
**发布时间**: 2026/3/28 19:05:58
**链接**: https://www.douyin.com/video/xxx
**封面**: https://...
**视频**: https://...
**点赞**: 364 **评论**: 4 **收藏**: 18 **分享**: 7

---

**共 20 条结果**
```

## 4. 注意事项

## 4.1 合规要求

- 仅用于抖音公开数据采集，禁止爬取私密 / 违规内容
- 符合 OpenClaw 安全规范与数据采集合规要求

### 4.2 风控提示

- 默认 TOKEN 有调用频率限制，生产环境建议使用私有 TOKEN
- CDN 链接（视频 / 图片）为临时链接，建议及时下载留存
- 关键词包含违规内容时，技能会直接拦截并提示
