---
id: "2026-01-09-添加 TUI 管理工具用于管理 tmux sessions"
title: "添加 TUI 管理工具用于管理 tmux sessions"
status: "completed"
created: "2026-01-09"
updated: "2026-01-09"
category: "feature"
tags: ["tui", "tmux", "session-management"]
related-pr: "docs/pr/20260109-添加 TUI 管理工具用于管理 tmux sessions.md"
---

# Issue: 添加 TUI 管理工具用于管理 tmux sessions

## Goal

为 tmux skill 添加一个交互式 TUI (Terminal User Interface) 管理工具，提供可视化的会话管理界面，支持实时监控、操作和清理 tmux sessions。

## 背景/问题

当前 tmux skill 只提供 CLI 命令行工具，需要记住各种命令和参数。对于管理多个会话，需要反复执行 list、status、capture 等命令，操作效率较低。

TUI 工具可以提供：
- 可视化的会话列表
- 实时状态监控
- 快捷键操作
- 直观的操作界面

## 验收标准 (Acceptance Criteria)

- [x] WHEN 用户执行 `bun tui.ts`，系统 SHALL 显示交互式 TUI 界面
- [x] WHERE TUI 界面 SHALL 显示所有 tmux sessions 的列表（ID、名称、分类、状态、最后活动时间）
- [x] IF 用户按 `r` 键，THEN 系统 SHALL 刷新会话列表
- [x] IF 用户按 `k` 键并选择会话，THEN 系统 SHALL 终止该会话
- [x] IF 用户按 `c` 键并选择会话，THEN 系统 SHALL 捕获并显示该会话的输出
- [x] IF 用户按 `a` 键并选择会话，THEN 系统 SHALL 显示 attach 命令
- [x] IF 用户按 `s` 键并选择会话，THEN 系统 SHALL 显示详细状态信息
- [x] IF 用户按 `n` 键，THEN 系统 SHALL 提示输入名称和命令创建新会话
- [x] IF 用户按 `q` 或 `Esc` 键，THEN 系统 SHALL 退出 TUI
- [x] WHERE TUI 界面 SHALL 支持键盘导航（上下箭头选择、Enter 确认）
- [x] WHERE TUI 界面 SHALL 每 5 秒自动刷新会话状态

## 实施阶段

### Phase 1: 技术选型和设计
- [x] 分析需求和依赖
- [x] 选择 TUI 库（使用 `ink`）
- [x] 设计界面布局和交互逻辑

### Phase 2: 核心功能实现
- [x] 实现会话列表显示
- [x] 实现键盘事件处理
- [x] 实现会话操作（kill、capture、attach、status）
- [x] 实现新会话创建
- [x] 实现自动刷新机制

### Phase 3: 用户体验优化
- [x] 添加颜色主题
- [x] 添加快捷键提示
- [x] 优化布局和间距
- [x] 添加确认对话框（删除操作）

### Phase 4: 验证
- [x] 功能测试
- [x] 边界情况测试
- [x] 更新文档

## 关键决策

| 决策 | 理由 |
|------|------|
| 使用 `ink` 库 | 基于 React，易于维护，社区活跃，TypeScript 支持好 |
| 自动刷新间隔 5 秒 | 平衡实时性和性能，避免频繁请求 |
| 键盘优先操作 | 符合终端用户习惯，操作效率高 |

## 遇到的错误

| 日期 | 错误 | 解决方案 |
|------|------|---------|
| | | |

## 相关资源

- [ ] 相关文档: `SKILL.md`, `TUI.md`
- [ ] 相关 Issue: `docs/issues/20260109-添加 TUI 管理工具用于管理 tmux sessions.md`
- [ ] 参考资料: [ink 官方文档](https://github.com/vadimdemedes/ink)

## Notes

- 使用 `ink` 库构建 TUI，因为它提供 React 组件化开发体验
- 复用现有的 `TmuxManager` 类进行会话管理
- 需要处理异步操作和状态更新
- 考虑添加过滤功能（按分类、状态过滤）
- ✅ 已实现双语界面，同时显示中文和英文
- ✅ 所有用户可见文本均已双语化
- ✅ 文档已更新为双语格式

---

## Status 更新日志

- **[2026-01-09 10:30]**: 状态变更 → in-progress，备注: 开始实施 Phase 1
- **[2026-01-09 15:50]**: 状态变更 → completed，备注: 完成 TUI 工具开发和文档更新