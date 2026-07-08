---
id: "2026-01-09-添加 TUI 管理工具用于管理 tmux sessions"
title: "添加 TUI 管理工具用于管理 tmux sessions（含双语界面）"
status: "completed"
created: "2026-01-09"
updated: "2026-01-09"
category: "feature"
related-issue: "docs/issues/20260109-添加 TUI 管理工具用于管理 tmux sessions.md"
---

# PR: 添加 TUI 管理工具用于管理 tmux sessions（含双语界面）

## 背景

当前 tmux skill 只提供 CLI 命令行工具，需要记住各种命令和参数。对于管理多个会话，需要反复执行 list、status、capture 等命令，操作效率较低。

## 变更内容

### 新增文件

1. **`tui.ts`** - 交互式 TUI 管理工具（双语界面）
   - 基于 `ink` 库构建，使用 React 组件化开发
   - 提供可视化的会话列表界面
   - 支持键盘导航和快捷键操作
   - 自动刷新会话状态（每 5 秒）
   - 支持创建、终止、捕获、监控会话
   - ✅ 双语界面，同时显示中文和英文

2. **`test-tui.ts`** - TUI 测试脚本
   - 创建测试会话
   - 提供双语使用说明

3. **`test-tui-core.ts`** - TUI 核心功能测试
   - 非交互式测试所有 TUI 功能
   - 验证会话同步、创建、捕获、状态检查、清理

4. **`demo-tui.ts`** - 完整演示脚本
   - 展示所有 TUI 功能
   - 创建多种类型的示例会话
   - 提供详细的双语使用说明

5. **`demo-bilingual.ts`** - 双语界面演示脚本
   - 专门展示双语界面特性
   - 演示双语标签和提示

6. **`examples/dev-workflow.ts`** - 开发工作流示例
   - 演示如何使用 TUI 管理开发环境

7. **`TUI.md`** - TUI 详细文档（双语）
   - 快速开始指南
   - 键盘快捷键说明
   - 界面说明和使用示例
   - 完整的双语文档

8. **`README.md`** - 项目总览文档（双语）
   - 功能特性介绍
   - 项目结构说明
   - 使用场景和示例
   - 更新为双语格式

9. **`BILINGUAL_REPORT.md`** - 双语化完成报告
   - 双语化实施详情
   - 更新文件列表
   - 界面示例
   - 测试验证结果

### 修改文件

1. **`SKILL.md`** - 更新文档
   - 添加 TUI 管理工具使用说明
   - 添加键盘快捷键说明
   - 添加使用示例

2. **`TUI.md`** - 新增 TUI 详细文档（双语）
   - 完整的双语使用指南
   - 界面说明和示例
   - 故障排除

3. **`README.md`** - 更新项目总览（双语）
   - 添加 TUI 模式说明
   - 更新为双语格式

### 依赖更新

- 添加 `ink@6.6.0` - React TUI 框架
- 添加 `react@19.2.3` - React 核心库
- 添加 `@types/react@19.2.7` - React 类型定义

## 功能特性

### TUI 界面

- **会话列表**：显示所有 tmux sessions（ID、名称、分类、状态、最后活动时间）
- **颜色编码**：
  - 状态颜色：running（绿色）、idle（黄色）、exited（红色）
  - 分类颜色：task（青色）、service（品红）、agent（蓝色）
- **自动刷新**：每 5 秒自动同步会话状态

### 键盘快捷键

- `↑/↓` - 导航会话列表
- `r` - 刷新会话列表
- `n` - 创建新会话（交互式输入名称、命令、分类）
- `c` - 捕获选中会话的输出
- `s` - 显示选中会话的详细状态
- `a` - 显示 attach 命令
- `k` - 终止选中会话（需要确认）
- `q/Esc` - 退出 TUI

### 创建会话流程

1. 按 `n` 进入创建模式
2. 输入会话名称，按 Enter 继续
3. 输入命令，按 Enter 继续
4. 输入分类（task/service/agent），按 Enter 创建
5. 自动返回会话列表

## 测试

### 功能测试

```bash
# 创建测试会话
bun ~/.pi/agent/skills/tmux/test-tui.ts

# 启动 TUI
bun ~/.pi/agent/skills/tmux/tui.ts

# 测试快捷键功能
# - 导航：↑/↓
# - 刷新：r
# - 创建：n
# - 捕获：c
# - 状态：s
# - Attach：a
# - 终止：k
# - 退出：q
```

### 验收标准

- ✅ TUI 界面正常显示
- ✅ 会话列表正确显示所有会话
- ✅ 键盘导航功能正常
- ✅ 创建会话功能正常
- ✅ 捕获输出功能正常
- ✅ 显示状态功能正常
- ✅ 显示 attach 命令功能正常
- ✅ 终止会话功能正常（含确认）
- ✅ 自动刷新功能正常
- ✅ 退出功能正常

## 回滚计划

如果出现问题，可以：

1. 删除新增文件：
   ```bash
   rm ~/.pi/agent/skills/tmux/tui.ts
   rm ~/.pi/agent/skills/tmux/test-tui.ts
   ```

2. 恢复文档：
   ```bash
   git checkout SKILL.md
   ```

3. 移除依赖：
   ```bash
   bun remove ink react @types/react
   ```

## 影响范围

- 新增功能，不影响现有 CLI 命令
- 仅添加新的 TUI 工具，向后兼容
- 不修改现有的 `lib.ts` 和 `types/index.ts`

## 相关资源

- [Issue](docs/issues/20260109-添加 TUI 管理工具用于管理 tmux sessions.md)
- [ink 官方文档](https://github.com/vadimdemedes/ink)

## Notes

- TUI 工具使用 `ink` 库，提供 React 组件化开发体验
- 复用现有的 `TmuxManager` 类进行会话管理
- 使用 `useStdin` 检查 TTY 支持，避免在非交互环境中报错
- 所有会话操作都通过 `TmuxManager` 类，确保数据一致性

---

## Status 更新日志

- **[2026-01-09 15:50]**: 状态变更 → completed，备注: 完成 TUI 工具开发和文档更新