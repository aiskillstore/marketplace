---
name: master-orchestrator
description: 全自动总指挥：串联热点抓取、内容生成与爆款验证的全流程技能。
---

# Master Orchestrator (全自动总指挥)

这个 Skill 是 Defou Workflow Agent 的“大脑”和“指挥中心”。它将原本独立的技能模块串联成一条完整的自动化生产流水线，实现从“全网热点”到“高质量成品”的零人工干预作业。

## 功能描述

它按顺序自动调度以下两个核心引擎：

1.  **内容生成引擎 (Content Generation Engine)**
    *   **对应技能**: `tophub-defou-stanley-combo`
    *   **动作**: 
        *   抓取 TopHub 全网热榜。
        *   智能筛选 Top 10 最具爆款潜力的话题。
        *   基于 Defou x Stanley 风格生成初稿。
    *   **产出**: `outputs/defou-stanley-posts/` 下的初稿文件。

2.  **质量验证引擎 (Quality Verification Engine)**
    *   **对应技能**: `viral-verification`
    *   **动作**:
        *   自动读取上一步生成的初稿。
        *   模拟“增长黑客”进行 6 维爆款要素打分。
        *   生成最终优化建议和终稿。
    *   **产出**: `outputs/viral-verified-posts/` 下的最终成品。

## 使用方法

### 运行脚本

```bash
# 在项目根目录下运行
npm run skill:master
```

或者直接使用 `ts-node`：

```bash
npx ts-node src/master.ts
```

### 输出结果

你只需要关注最终的产出目录：

`defou-workflow-agent/outputs/viral-verified-posts/`

这里存放了经过双重 AI 智慧加持的最终文章，可以直接用于发布。

## 依赖配置

无需额外配置，它复用项目的全局 `.env` 配置。
