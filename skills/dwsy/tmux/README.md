# tmux Skill

远程控制 tmux 会话，用于交互式 CLI、后台任务和服务管理。
Remote control tmux sessions for interactive CLIs, background tasks, and service management.

## 功能特性/Features

- 🚀 **CLI 模式/Mode**: 完整的命令行界面用于会话管理/Full command-line interface for session management
- 🖥️ **TUI 模式/Mode**: 交互式终端用户界面用于可视化会话管理/Interactive terminal user interface for visual session management
- 🔧 **TypeScript API**: 编程控制用于自动化/Programmatic control for automation
- 🔄 **自动清理/Auto-cleanup**: 24 小时无活动后自动清理会话/Automatic session cleanup after 24 hours of inactivity
- 💾 **会话持久化/Session Persistence**: 跨 Agent 重启的状态跟踪/State tracking across Agent restarts
- 🔒 **私有套接字/Private Socket**: 隔离套接字避免与个人 tmux 冲突/Isolated socket to avoid conflicts with personal tmux

## 快速开始/Quick Start

### CLI 模式/Mode

```bash
# 创建会话/Create session
bun ~/.pi/agent/skills/tmux/lib.ts create my-task "echo 'Hello'" task

# 列出会话/List sessions
bun ~/.pi/agent/skills/tmux/lib.ts list

# 捕获输出/Capture output
bun ~/.pi/agent/skills/tmux/lib.ts capture pi-task-my-task-20250107-123456
```

### TUI 模式/Mode

```bash
# 启动交互式 TUI/Launch interactive TUI
bun ~/.pi/agent/skills/tmux/tui.ts

# 或先创建测试会话/Or create test sessions first
bun ~/.pi/agent/skills/tmux/test-tui.ts
bun ~/.pi/agent/skills/tmux/tui.ts
```

## Project Structure

```
tmux/
├── lib.ts              # Core TmuxManager class and CLI
├── tui.ts              # Interactive TUI application
├── types/
│   └── index.ts        # TypeScript type definitions
├── scripts/
│   ├── find-sessions.sh    # Helper script to find sessions
│   └── wait-for-text.sh    # Helper script to wait for text output
├── examples/
│   ├── long-task.ts        # Example: Long-running task
│   ├── python-repl.ts      # Example: Python REPL
│   ├── start-service.ts    # Example: Service management
│   └── dev-workflow.ts     # Example: Development workflow
├── test-tui.ts         # Create test sessions for TUI
├── test-tui-core.ts    # Test TUI core functionality
├── SKILL.md            # Main documentation
├── TUI.md              # TUI documentation
├── package.json        # Dependencies
└── tsconfig.json       # TypeScript configuration
```

## Documentation

- **[SKILL.md](SKILL.md)** - Complete skill documentation
- **[TUI.md](TUI.md)** - TUI usage guide
- **[docs/issues/](docs/issues/)** - Issue tracking
- **[docs/pr/](docs/pr/)** - Pull request tracking

## Use Cases

### Development Workflow

```bash
# Start multiple services
bun ~/.pi/agent/skills/tmux/lib.ts create dev-server "npm run dev" service
bun ~/.pi/agent/skills/tmux/lib.ts create build-watch "npm run build:watch" task
bun ~/.pi/agent/skills/tmux/lib.ts create test-runner "npm run test:watch" task

# Use TUI to manage them
bun ~/.pi/agent/skills/tmux/tui.ts
```

### Background Tasks

```bash
# Start long-running task
bun ~/.pi/agent/skills/tmux/lib.ts create training "python train.py" task

# Check progress later
bun ~/.pi/agent/skills/tmux/lib.ts list
bun ~/.pi/agent/skills/tmux/lib.ts capture pi-task-training-20250107-123456
```

### Interactive Tools

```bash
# Python REPL
bun ~/.pi/agent/skills/tmux/lib.ts create python "PYTHON_BASIC_REPL=1 python3 -q" task

# Send commands
bun ~/.pi/agent/skills/tmux/lib.ts send pi-task-python-20250107-123456 "print('Hello')"
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `create <name> <command> [category]` | Create a new session |
| `list [filter]` | List all sessions |
| `status <id>` | Show session status |
| `send <id> <keys>` | Send keys to session |
| `capture <id> [lines]` | Capture pane output |
| `kill <id>` | Kill a session |
| `cleanup [hours]` | Cleanup old sessions |
| `attach <id>` | Print attach command |
| `sync` | Sync session status |

## TUI Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `↑/↓` | Navigate sessions |
| `r` | Refresh list |
| `n` | New session |
| `c` | Capture output |
| `s` | Show status |
| `a` | Show attach command |
| `k` | Kill session |
| `q/Esc` | Quit |

## Session Categories

- **task**: Temporary sub-tasks (compilation, testing)
- **service**: Long-running services (dev servers, databases)
- **agent**: Agent-specific tasks (training, data processing)

## Session Status

- **running**: Process is active with recent output
- **idle**: Process exists but no recent output
- **exited**: Process has terminated

## Socket Convention

- **Socket Directory**: `${TMPDIR:-/tmp}/pi-tmux-sockets`
- **Default Socket**: `/tmp/pi-tmux-sockets/pi.sock`
- **Environment Variable**: `PI_TMUX_SOCKET_DIR` (optional override)

## Requirements

- tmux (Linux/macOS)
- Bun runtime
- Bash (for helper scripts)

## License

MIT