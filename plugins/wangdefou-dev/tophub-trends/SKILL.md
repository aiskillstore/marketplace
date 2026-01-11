---
name: tophub-trends
description: 获取并分析 TopHub 热榜数据，提供内容创作灵感。
---

# TopHub Trends Analysis Skill

这个 Skill 用于自动化获取 TopHub 热榜数据，并利用 Claude 分析当前最具传播潜力的热点话题，为内容创作者提供选题建议。

## 功能描述

1.  **Fetch Hot List**: 抓取 TopHub (https://tophub.today/hot) 的实时热榜数据。
2.  **Analyze Trends**: 使用 Claude 模型分析前 30 个热点，识别高流量潜力的話題。
3.  **Generate Report**: 生成包含选题建议的 Markdown 报告。

## 使用方法

这是一个基于 TypeScript 的脚本 Skill。

### 运行脚本

```bash
# 在项目根目录下运行
npx ts-node .claude/skills/tophub-trends/tophub.ts
```

### 输出结果

脚本运行后，会在 `defou-workflow-agent/outputs/trends/` 目录下生成两个文件：

1.  `tophub_hot_[timestamp].json`: 原始热榜数据。
2.  `tophub_analysis_[timestamp].md`: Claude 生成的分析报告。

## 依赖配置

确保 `defou-workflow-agent/.env` 文件中已配置以下环境变量：

-   `ANTHROPIC_API_KEY`: Anthropic API Key
-   `ANTHROPIC_BASE_URL`: (可选) API Base URL
-   `MOCK_MODE`: (可选) 设置为 `true` 可使用模拟数据进行测试
