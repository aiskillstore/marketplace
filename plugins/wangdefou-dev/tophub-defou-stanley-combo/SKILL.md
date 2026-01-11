---
name: tophub-defou-stanley-combo
description: 自动获取 TopHub 热榜，精选选题，并使用 Defou x Stanley 风格生成爆款内容。
---

# TopHub x Stanley Workflow Combo

这个 Skill 结合了 `tophub-trends` 的热点获取能力和 `defou-stanley-workflow` 的深度内容创作能力，实现从“热点发现”到“爆款内容生成”的全自动化流程。

## 功能描述

1.  **Fetch Trends**: 获取 TopHub 实时热榜数据。
2.  **Select Topics**: 智能筛选最具爆款潜力的 **10** 个选题。
3.  **Generate Content**: 批量为这 10 个选题应用 Defou x Stanley 工作流，生成包含“极致爆款版”、“深度认知版”和“得否Stanley融合版”的三合一内容。
4.  **Save Output**: 输出 Markdown 格式的最终稿件。

## 使用方法

### 运行脚本

```bash
# 在项目根目录下运行
npx ts-node .claude/skills/tophub-defou-stanley-combo/index.ts
```

### 输出结果

脚本运行后，会在 `defou-workflow-agent/outputs/defou-stanley-posts/` 目录下生成文件：

1.  `post_[timestamp]_[topic].md`: 最终生成的内容稿件。
