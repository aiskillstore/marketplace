---
name: gpt-series-reasoning-style
version: 1.5.6
description: 交付验收与多智能体协作纪律（防假完成）。Use when 涉及数字验算、代码交付、多Agent协作、需要防假完成的任务；or when user says "做完了帮我查/看看对不对/验收"、派发子任务或多个AI分工。约束交付是否真实，不单独设定创意质量满意标准（见 DISCIPLINE 完成档位 C1/C2）。小改/一句话问答不加载。
license: MIT
compatibility: "Works with any model or client supporting the Agent Skills SKILL.md convention (Claude Code, Codex, Cursor, etc.)."
metadata:
  author: JadeYingWah
---

# 强制门禁

本文件不含交付纪律。**纪律全文在 `DISCIPLINE.md`**——它只能在**你即将动手做事或回答用户的前一刻**被读取。

**「前一刻」= 下列动作里最早发生的那个之前**：①创建/修改交付物相关文件（含脚手架）；②输出施工级方案并要用户确认；③跑构建/测试等产线命令；④以「做完了」口径声称交付。

创意/视觉类：在上述动作之前，允许一轮**不读** DISCIPLINE 的方向构想；**任务里有你不认识的专名/概念时，仍须先问用户或搜索**（此时不读 DISCIPLINE，但要完成确认）。

- 在前一刻之前，**禁止读取** `DISCIPLINE.md`，禁止凭记忆引用它的任何内容，禁止提前预览任何流程；禁止读取 `plan-rules.md` / `review-rules.md` / `multi-agent.md`。
- 到了前一刻，读取 `DISCIPLINE.md`，然后**严格按其中内容执行任务**。
