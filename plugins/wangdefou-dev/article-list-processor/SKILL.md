---
name: article-list-processor
description: 读取包含文章列表的 Markdown 文件，自动抓取原文内容并生成爆款文案。
---

# Article List Processor Skill

这个 Skill 专门用于处理“文章列表”。你只需要提供一个包含多个文章标题和链接的 Markdown 文件，它就会自动遍历列表，逐个抓取网页内容，并应用 Defou x Stanley 工作流进行重写。

## 功能描述

1.  **Parse List**: 读取 `defou-workflow-agent/local_inputs/` 下的 Markdown 文件，解析出所有的 `[标题](链接)`。
2.  **Fetch Content**: 使用爬虫技术（Readability）自动抓取目标链接的正文内容。
3.  **Generate**: 使用 Defou x Stanley 风格重写每一篇文章。
4.  **Save**: 将每篇文章的重写结果单独保存为文件。

## 使用场景

当你收集了一堆高质量的文章链接（比如从 Newsletter、Twitter 或 RSS 收集的），想要批量把它们转化为自己的爆款内容时，使用此 Skill。

## 使用方法

### 1. 准备清单文件

在 `defou-workflow-agent/local_inputs/` 下创建一个文件（例如 `reading_list.md`），内容格式如下：

```markdown
# 我的今日阅读清单

1. [为什么年轻人不爱存钱了？](https://example.com/article1)
2. [如何通过 AI 提高效率](https://example.com/article2)
- [DeepSeek 深度解析](https://example.com/article3)
```

### 2. 启动全自动监听

```bash
npm run skill:list
```

终端将显示 `👀 Watching directory: ...`，此时程序进入后台监听状态。

### 3. 投放任务

将你的清单文件（如 `links.md`）直接拖入 `defou-workflow-agent/local_inputs/` 文件夹。

### 4. 自动执行

系统将自动触发以下流程：
1.  **检测**: 发现新文件 `links.md`。
2.  **抓取 & 生成**: 遍历链接，抓取正文，生成 Defou/Stanley 风格初稿。
3.  **验证 (Verify)**: 初稿生成完毕后，**自动**启动 `skill:verify` 进行爆款要素验证和优化。
4.  **归档**: 原文件被移入 `archive/`。

你只需要去 `outputs/viral-verified-posts/` 收取最终成品即可。
