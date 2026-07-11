---
name: ticktick-cli
description: 使用 Python CLI 与 Dida365 Open API 交互以管理滴答清单任务/项目，适用于需要通过脚本或命令行调用滴答清单接口的场景（如项目/任务的查询、创建、更新、完成、删除）。
---

# ticktick-cli

通过本 skill 调用滴答清单 / TickTick Open API。默认中国区 Dida365；国际版只在登录时显式选择。

## 执行约定

先进入 skill 目录，再直接执行脚本：

```bash
cd skills/ticktick-cli
./scripts/ticktick_cli.py --json project list
```

- 不要用 `uv run python` 或 `python` 调用脚本；脚本自身带 uv shebang。
- 给 Agent 解析的输出一律加 `--json`，并且全局参数必须放在子命令前。
- 删除项目或任务前先确认用户意图；`delete` 会真实删除远端数据。
- 参数不确定时先查 `./scripts/ticktick_cli.py <command> --help`。

## 认证

默认假设本地 token 有效，直接执行用户请求的操作；不要在每次操作前先跑 `auth doctor`。

只有命令失败且报错指向认证、token、权限、区域或 API base URL 问题时，再诊断当前本地 token：

```bash
./scripts/ticktick_cli.py --json auth doctor
```

确实没有 token、token 失效或用户要求重新登录时再登录：

```bash
./scripts/ticktick_cli.py auth login
```

- 国际版登录用 `./scripts/ticktick_cli.py auth login --region ticktick`。
- 默认只输出授权链接，不自动打开浏览器；需要自动打开时加 `--open`。
- 登录会启动 localhost callback，默认等待 5 分钟；看到链接后应尽快完成授权。
- token 默认保存到 `~/.config/ticktick-cli/token.json`，可用 `TICKTICK_TOKEN_FILE` 覆盖。
- 后续命令只读本地 token 文件，并从 token 元数据推断区域和 API base URL。
- 远程 SSH 场景下，浏览器 callback 必须能访问运行 CLI 的机器；必要时在目标机器本地登录，或自行做端口转发。

## 日常操作

常用命令族：

- `auth login|doctor|logout`
- `project list|get|data|create|update|delete`
- `task get|create|update|complete|delete|move|completed|filter`
- `focus get|list|delete`
- `habit list|get|create|update|checkin|checkins`

常见入口：

```bash
./scripts/ticktick_cli.py --json project list
./scripts/ticktick_cli.py --json project data --project-id <project-id>
./scripts/ticktick_cli.py --json task get --project-id <project-id> --task-id <task-id>
./scripts/ticktick_cli.py --json task filter --project-id <project-id> --status 0
```

创建或更新 checklist 子任务：

- 简单标题：重复传 `--item`。
- 复杂字段：用 `--item-json` 传 JSON 数组，或传 `@path` 读取文件。
- 任务标签：创建/更新任务时重复传 `--tag`。
- 复杂 habit payload：用 `--payload-json` 传 JSON 对象，或传 `@path` 读取文件。

## 数据模型

- Project：任务容器，支持 list / kanban / timeline 等视图。
- Task：隶属于 Project，可包含时间、提醒、优先级、重复规则、标签与子任务。
- ChecklistItem：Task 下的子任务项。
- Column：看板列，仅在 kanban 场景常用。
- ProjectData：项目详情聚合，包含项目、未完成任务和列信息。
- Focus：专注/番茄钟记录。
- Habit：习惯与打卡记录。

## 参考

- [ticktick_cli.py](scripts/ticktick_cli.py)
- [滴答清单 OpenAPI](https://developer.dida365.com/docs/index.html#/openapi)
