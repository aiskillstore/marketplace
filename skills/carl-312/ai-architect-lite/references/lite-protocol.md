# Lite Protocol 快速卡片
> 目的：保留 AI Architecture 初衷（外部记忆 + manifest 调度），以一页指南快速落地；语言默认简体中文。

## .ai_context 最小必需
- 必备：`03_ACTIVE_TASK.md`；`01/02` 可选。
- 03 模板：
```markdown
# Active Task Context
## Current Mission
- Title: <任务标题>
- State: Drafting | Executing | Verifying | Blocked
- Owner: AI | Human
- Notes: <可选说明>

## Development Log (Append Only)
### [YYYY-MM-DD HH:MM] Action: <动作>
- Changes: <文件/命令>
- Outcome: <结果>
- Next: <下一步>
```

## 调度 / Manifest
- Slash 优先，其次 Intent（如有），再普通对话。
- 未配置 `cognitive_skills` 时保持纯命令；未命中命令则按 Current Mission 回复。
- 长文档放 `references/` 按需加载；避免把规范塞进主对话。

## 日志写入
- 推荐命令：`python skills/memory-sync/entrypoint.py --note "..." --action "..." --changes "..." --outcome "..." --next "..."`
- 若脚本不可用，手动按模板追加 `Development Log`。

## 安全与范围
- 执行前说明目的与影响，不写密钥。
- 作用域限定 `PROJECT_ROOT`，避免跨项目修改。
