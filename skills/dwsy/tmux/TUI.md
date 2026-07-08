# Tmux TUI 管理工具/Manager

交互式终端用户界面（TUI）用于管理 tmux sessions。

## 快速开始/Quick Start

```bash
# 启动 TUI/Launch TUI
bun ~/.pi/agent/skills/tmux/tui.ts

# 或者先创建测试会话/Or create test sessions first
bun ~/.pi/agent/skills/tmux/test-tui.ts
bun ~/.pi/agent/skills/tmux/tui.ts
```

## 键盘快捷键/Keyboard Shortcuts

| 快捷键/Shortcut | 功能/Function |
|-----------------|---------------|
| `↑/↓` | 导航会话列表/Navigate sessions |
| `r` | 刷新会话列表/Refresh sessions |
| `n` | 创建新会话/Create new session |
| `c` | 捕获选中会话的输出/Capture output |
| `s` | 显示选中会话的详细状态/Show status |
| `a` | 显示 attach 命令/Show attach command |
| `k` | 终止选中会话（需要确认）/Kill session (confirm) |
| `q` / `Esc` | 退出 TUI/Exit TUI |

## 创建会话流程/Create Session Flow

1. 按 `n` 进入创建模式/Press `n` to enter create mode
2. 输入会话名称，按 Enter 继续/Enter name, press Enter to continue
3. 输入命令，按 Enter 继续/Enter command, press Enter to continue
4. 输入分类（task/service/agent），按 Enter 创建/Enter category, press Enter to create
5. 自动返回会话列表/Auto-return to session list

## 界面说明/UI Description

### 会话列表/Session List

```
Tmux 会话管理器/Session Manager                   自动刷新/Auto-refresh: 5秒/s

会话ID/Session ID               名称/Name  分类/Category 状态/Status  最后活动/Last Activity
───────────────────────────────────────────────────────────────────────────────────
pi-task-compile-20260109-123456 compile   任务/Task   运行中/Running  0m ago
pi-service-dev-server-20260109-123456 dev-server 服务/Service 运行中/Running  5m ago
```

### 颜色编码/Color Coding

- **状态颜色/Status Colors**：
  - 🟢 `运行中/Running` - 会话正在运行/Session is running
  - 🟡 `空闲/Idle` - 会话空闲/Session is idle
  - 🔴 `已退出/Exited` - 会话已退出/Session has exited

- **分类颜色/Category Colors**：
  - 🔵 `任务/Task` - 临时任务/Temporary tasks
  - 🟣 `服务/Service` - 长期服务/Long-running services
  - 🟦 `代理/Agent` - Agent 任务/Agent-specific tasks

### 创建会话界面/Create Session Interface

```
创建新会话/Create New Session

名称/Name: my-task
命令/Command: echo "Hello World"
分类/Category: task (任务/服务/代理/Task/Service/Agent)

按 Enter 继续/Press Enter to continue，按 Esc 取消/Press Esc to cancel

> my-task█
```

### 捕获输出界面/Capture Output Interface

```
捕获输出/Capture Output

pi-task-compile-20260109-123456

Building...
Compiling main.c...
Linking...
Build successful!

按 Esc 返回/Press Esc to return
```

### 状态详情界面/Status Detail Interface

```
会话状态/Session Status

ID/会话ID: pi-task-compile-20260109-123456
名称/Name: compile
分类/Category: task
状态/Status: running
创建时间/Created: 2026-01-09T12:34:56Z
最后活动/Last Activity: 2026-01-09T12:35:00Z
命令/Command: make all

按 Esc 返回/Press Esc to return
```

### 连接命令界面/Attach Command Interface

```
连接命令/Attach Command

pi-task-compile-20260109-123456

要连接到此会话，请运行/To attach to this session, run:

  tmux -S /tmp/pi-tmux-sockets/pi.sock attach -t pi-task-compile-20260109-123456

断开连接/Detach with: Ctrl+b d

按 Esc 返回/Press Esc to return
```

### 确认删除界面/Confirm Kill Interface

```
确认终止/Confirm Kill

确定要终止以下会话吗？/Are you sure you want to kill session:
  pi-task-compile-20260109-123456

[Y]是/Yes  [N]否/No
```

## 使用示例/Usage Examples

### 管理开发服务器/Manage Development Server

```bash
# 启动 TUI/Launch TUI
bun ~/.pi/agent/skills/tmux/tui.ts

# 按 'n' 创建新会话/Press 'n' to create new session
# 名称/Name: dev-server
# 命令/Command: npm run dev
# 分类/Category: service

# 按 'c' 捕获输出查看日志/Press 'c' to capture output and view logs
# 按 'a' 获取 attach 命令进行交互式操作/Press 'a' to get attach command for interactive access
# 按 'k' 停止服务器/Press 'k' to stop server
```

### 监控编译任务/Monitor Compilation Task

```bash
# 启动 TUI/Launch TUI
bun ~/.pi/agent/skills/tmux/tui.ts

# 按 'n' 创建编译任务/Press 'n' to create compilation task
# 名称/Name: compile
# 命令/Command: make all
# 分类/Category: task

# 按 'c' 捕获输出查看编译进度/Press 'c' to capture output and view compilation progress
# 按 'r' 刷新状态/Press 'r' to refresh status
# 编译完成后按 'k' 清理会话/Press 'k' to cleanup after compilation
```

### 批量管理会话/Bulk Manage Sessions

```bash
# 启动 TUI/Launch TUI
bun ~/.pi/agent/skills/tmux/tui.ts

# 使用 ↑/↓ 导航会话列表/Use ↑/↓ to navigate session list
# 按 's' 查看每个会话的详细状态/Press 's' to view detailed status of each session
# 按 'k' 清理不需要的会话/Press 'k' to cleanup unwanted sessions
# 按 'r' 刷新确保状态同步/Press 'r' to refresh and ensure status sync
```

## 技术细节/Technical Details

### 依赖/Dependencies

- `ink@6.6.0` - React TUI 框架/Framework
- `react@19.2.3` - React 核心库/Core library
- `@types/react@19.2.7` - React 类型定义/Type definitions

### 自动刷新/Auto-refresh

TUI 每 5 秒自动刷新会话状态，确保显示最新的会话信息。你也可以按 `r` 手动刷新。
TUI auto-refreshes session status every 5 seconds to ensure latest information. You can also press `r` to manually refresh.

### 数据同步/Data Synchronization

TUI 通过 `TmuxManager` 类与 tmux 通信，确保数据一致性。所有操作都会同步到会话存储文件。
TUI communicates with tmux via `TmuxManager` class, ensuring data consistency. All operations are synchronized to the session storage file.

## 故障排除/Troubleshooting

### TUI 无法启动/TUI Cannot Launch

确保在交互式终端中运行 TUI：
Ensure TUI is running in an interactive terminal:

```bash
# ✅ 正确/Correct: 在终端中运行/Run in terminal
bun ~/.pi/agent/skills/tmux/tui.ts

# ❌ 错误/Error: 通过管道或重定向运行/Run through pipe or redirection
echo "" | bun ~/.pi/agent/skills/tmux/tui.ts
```

### 会话列表为空/Session List Empty

1. 按下 `r` 刷新会话列表/Press `r` to refresh session list
2. 检查 tmux 是否正常运行/Check if tmux is running: `tmux -V`
3. 检查 socket 路径/Check socket path: `ls -la /tmp/pi-tmux-sockets/`

### 键盘无响应/Keyboard Not Responding

1. 确保在交互式终端中运行/Ensure running in interactive terminal
2. 尝试按 `q` 或 `Esc` 退出/Try pressing `q` or `Esc` to exit
3. 重新启动 TUI/Restart TUI

## 相关文档/Related Documentation

- [tmux Skill 文档/Documentation](SKILL.md)
- [lib.ts API 文档/API Documentation](lib.ts)
- [types/index.ts](types/index.ts)