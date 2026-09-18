---
name: weekly-report
description: 根据执行文档和/或 README 版本记录生成工作周报（供用户向同事做正式汇报）。用户说「周报」时使用。
---

# 周报

首行：**`[weekly]`**。日常入口：[agent-entry-route.md](../references/agent-entry-route.md)；争议/recovery：[CORE.md](../CORE.md)

定稿规则必须先 Read：[weekly-report.md](../templates/weekly-report.md)。

## 触发

用户说「周报」时启用；不参与 Express/Direct/Standard/Full 路由。本岗一次性产出，不切换流水线模式、不写会话开关。用户借「周报」顺带提代码/README 改动需求时，不在本岗处理——须另起一条先 `[PM]` 判车道（硬门禁 #7）。

## 模型路由 + 子窗

本岗**不要求子窗**：用户单独说「周报」时在当前窗直接做即可。细则 → [model-routing.md](../references/model-routing.md) §周报例外。

## Checklist

1. Read [weekly-report.md](../templates/weekly-report.md)
2. 文档路径与日期区间至少一项；都缺则向用户索取
3. 默认只输出正文，不改执行文档/README/代码
4. 标题固定 `# 工作周报`；章节名不得改、不得换成别的骨架
5. 用户要求保存到文件时才写入；默认 `.ai-gates/Doc/Weekly/`

## 正文骨架（固定）

```markdown
# 工作周报

**周期：YYYY年M月D日—M月D日**

## 本周工作

## 下周工作
```

章节层级与取材/黑话翻译/自检/示例 → 模板。详细字段 → [retrospective-metrics.md](../references/retrospective-metrics.md)
