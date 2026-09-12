# Completion Claims — CI guard fixture（安全层行为回归夹具）

> 用途：给 CI 一个**最小、确定、无副作用**的声明清单，用来断言 `claim-check.py`
> 的两层拦截真的在生效——而不是只验证 CLI 能 `--help`。
>
> 为什么需要它：解释器默认拒层历史上被绕过三次（`python3.13` / 引号包裹路径 /
> wrapper 前缀），每次都是"代码看起来还在、CLI 还能跑"，但拦截没触发。
> 本夹具把「应当被拦」与「应当放行」各写一条，任一层静默失效（fail-open）CI 立刻红。
>
> 期望结果（CI 逐步断言）：
> - `git --version` —— 放行并实跑，exit=0（证明白名单外的普通命令仍可用，不是全拦）
> - `python -c …` —— 被**解释器间接执行默认拒**拦下（输出含 `interpreter-indirect`）
> - `` `python -c …` `` —— **反引号包裹形态**（markdown 行内代码）同样被拦下；batch 48 实测该形态曾整体绕过
>   解释器层（首词带上反引号后不在家族集合里，15/15 执行、saw 0 blocked），修复后必须仍然 BLOCKED
> - `rm -rf …` —— 被**破坏性命令黑名单**拦下（输出含 `dangerous pattern`）
> 被拦命令**不会被执行**；工具整体退出码 1，且 trust note 计数应为 **saw 3 blocked**。

## Files

- VERSION

## Commands

- git --version   # expect exit 0
- python -c "print(1)"   # expect exit 0
- `python -c "print(1)"`   # expect exit 0 (backtick-wrapped form — batch 48)
- rm -rf /tmp/claim-check-guard-never-created
