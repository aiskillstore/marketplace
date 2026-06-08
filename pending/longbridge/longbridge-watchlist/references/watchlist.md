# longbridge-watchlist-admin

⚠️ **Mutating skill**: changes the user's watchlist state on Longbridge. No money is involved, but the change is persistent.

## Two-step protocol (mandatory)

Every mutation must run as **two distinct turns**:

1. **Preview** — describe exactly what you are about to do (group name, symbols added / removed, whether the group will be deleted with members purged), in the user's language. **Do not run the CLI yet.**
2. **Wait for explicit confirmation** containing "确认 / yes / 是的 / confirm". If the user replies anything ambiguous, ask again — do **not** assume consent.
3. **Execute** — only after step 2, run the actual `longbridge watchlist <subcommand> ...` command.

> The Longbridge CLI's `delete` subcommand prints its own confirmation prompt — let it run; do not pipe `yes` or pass any flag that bypasses it. For `create` / `update`, this skill's preview-then-confirm protocol is the SKILL-layer gate.

## Routing to the read skill

If the user gives a group **name** (not an id), first call `longbridge watchlist --format json` (handled by `longbridge-watchlist`) to look up `group_id`, then run mutations here.

| User says             | Skill                                     |
| --------------------- | ----------------------------------------- |
| 看 / list / show      | `longbridge-watchlist` (read)             |
| 加 / 删 / 创建 / 改名 | `longbridge-watchlist-admin` (this skill) |

For ambiguous prompts (_"整理我的自选"_) — **ask** what specific action the user wants.

## CLI subcommands

`longbridge watchlist` carries three write subcommands. **Always run `longbridge watchlist <subcommand> --help` first if you are not 100% sure of the current flag spelling, defaults, or argument order** — this protects against version drift.

| Action                      | CLI invocation (typical shape — verify with `--help` before use)            |
| --------------------------- | --------------------------------------------------------------------------- |
| Create a new group          | `longbridge watchlist create "<name>" --format json`                        |
| Add symbols to a group      | `longbridge watchlist update <group_id> --add <SYMBOL>... --format json`    |
| Remove symbols from a group | `longbridge watchlist update <group_id> --remove <SYMBOL>... --format json` |
| Rename a group              | `longbridge watchlist update <group_id> --name "<new>" --format json`       |
| Delete a group              | `longbridge watchlist delete <group_id> --format json`                      |

> The `delete` subcommand has a built-in confirmation prompt (per `longbridge watchlist --help`). Let it run interactively in your environment.

## Preview templates (LLM)

> 即将{动作}:{plan 摘要}。是否确认执行?
>
> About to {action}: {plan summary}. Confirm?
>
> 即將{動作}:{plan 摘要}。是否確認執行?

Examples:

- _"即将创建自选股分组「科技股」。是否确认执行?"_
- _"About to add NVDA.US, AAPL.US to group 12345. Confirm?"_
- _"即將刪除分組 12345。是否確認?"_

## Output

`longbridge watchlist <subcommand> --format json` returns the resulting group object (or an updated list). On success, surface a short confirmation in the user's language and remind them to verify the change in the Longbridge app if needed.

## Error handling

| Situation                                        | LLM response                                                                                                                                                                                                                          |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Shell `command not found: longbridge`            | Tell the user to install [longbridge-terminal](https://github.com/longportapp/longbridge-terminal); MCP fallback can apply (see below) but **only after user confirmation** — never use MCP to bypass the preview / confirm protocol. |
| stderr contains `not logged in` / `unauthorized` | Tell the user to run `longbridge auth login` (this account requires trade scope; re-auth and tick "Trade").                                                                                                                           |
| Bad `group_id`                                   | Re-run the read skill (`longbridge-watchlist`) and re-check the id.                                                                                                                                                                   |
| Other stderr                                     | Surface verbatim. **Do not silently retry** — if a mutating call failed, ask the user before any second attempt.                                                                                                                      |

## OAuth scope

Mutating operations require the **trade scope**. Without it, both CLI and MCP fail with `unauthorized` / `not in authorized scope`. Tell the user to `longbridge auth logout && longbridge auth login` and tick "Trade" in the browser.
