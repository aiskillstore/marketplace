# Optional Hooks / 可选 Hook（默认不装）

> **定位与边界**：行为层 skill 的最大死穴是"模型想不起调用"。本 hook 用**一行**会话启动提醒
> 缓解遗忘率——它是 opt-in 的，默认不装，且刻意只输出一行：本 skill 的原则是显式按名调用、
> 不做常驻上下文包装，琐碎任务直接执行（轻通道）。一行提醒是对"遗忘"的对冲，不是对
> "显式调用"原则的放弃。不装 hook，skill 功能完全不受影响。
>
> **Positioning**: the classic failure mode of a behavior-layer skill is "the model forgets to
> invoke it". This hook injects EXACTLY ONE reminder line at session start — opt-in by default,
> and deliberately one line: the skill's own principle is explicit invocation, no resident
> context stuffing, trivial tasks proceed directly. The hook hedges forgetting; it does not
> replace explicit invocation. The skill works fully without it.

## 安装 / Install (Claude Code)

1. 安装本 skill（如未装）：`./scripts/install.sh agents`（或对应平台脚本）。
2. 编辑宿主配置 `~/.claude/settings.json`，加入：

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$HOME/.agents/skills/gpt-series-reasoning-style/hooks/session-reminder.sh\""
          }
        ]
      }
    ]
  }
}
```

> matcher 含 `compact`：长会话压缩后提醒会被吞掉，`compact` 让它重注入（详见下方"matcher 变体"）。

3. 重启会话，会话开头应出现一行 `[skill-reminder] …`。

Windows（PowerShell 宿主）用等效命令：

```text
powershell -NoProfile -Command "Write-Output '[skill-reminder] 多阶段/含糊/高影响任务？考虑按名调用 gpt-series-reasoning-style（实现前门禁 + 证据验收）。琐碎任务直接做。 | Multi-stage/ambiguous task? Consider invoking gpt-series-reasoning-style by name (gate + evidence acceptance). Trivial tasks: just proceed.'"
```

> 该命令的输出与 `hooks/session-reminder.sh` **逐字一致**（同为中英双语一行）；历史上这里是一段更短的中文，
> 同一提醒在两个平台上说法不同，属于不该有的分叉——提醒内容以 `session-reminder.sh` 为唯一权威。

## 进阶 / Advanced：按提示词触发（更省 token）

若宿主支持 `UserPromptSubmit` + matcher，可只在提示词包含"实现/开发/做一个/重构"等词时注入。
默认不建议：每条提示都注入同样违反"最小常驻面"原则。

## 进阶 / Advanced：matcher 变体（compact 后重注入）

Claude Code 的 `SessionStart` 支持 matcher：`startup`（会话启动）、`clear`（清空后）、
`compact`（**上下文压缩后**）。长会话必然触发 compact，而压缩会把启动提醒一并吞掉——
建议 matcher 写成 `"startup|clear|compact"`，让压缩后也重注入这一行（与 superpowers
hooks.json 的实践一致）：

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$HOME/.agents/skills/gpt-series-reasoning-style/hooks/session-reminder.sh\""
          }
        ]
      }
    ]
  }
}
```

## 卸载 / Remove

删除 settings.json 中对应 hook 条目即可；脚本文件可留可删。

## 自检 / Verify

```bash
bash hooks/session-reminder.sh   # 应只输出一行
```
