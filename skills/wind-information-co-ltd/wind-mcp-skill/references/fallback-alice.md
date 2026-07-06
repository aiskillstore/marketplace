# wind-alice 最终兜底

> 何时读：按 SKILL.md「失败与回答」判定可切 wind-alice 后 | 权威于：wind-alice 兜底流程 | 不覆盖：触发条件（见 SKILL.md「失败与回答」与 `references/error-codes.json`）

本流程是所有 Wind MCP 路径的最终兜底。触发条件，以及哪些错误不构成触发条件
（Key、权限、额度、网络、后端不可用、JSON 转义、未知工具等须先修复根因，不走兜底），
统一见 SKILL.md「失败与回答」与 `references/error-codes.json` 各码的 agent_action；确认满足后再执行本流程。

## 触发前检查

1. 确认已经尝试可用的专项 Wind 路径。
2. 确认 `analytics_data` 兜底在当前问题上被允许且已失败，或当前问题明确不适合该兜底。
3. 确认失败摘要可说明数据覆盖、字段或口径问题。
4. 确认客户端环境是否能加载 `wind-alice`。仓库里存在 `skills/wind-alice`
   源码，不等于客户端已经安装。

## 已安装 wind-alice

用 AskUserQuestion 让用户决定是否切换，不得自动切换。

选项至少包含：

| 选项 | 含义 |
| --- | --- |
| 改用 wind-alice 继续 | 让 Alice Agent 用自然语言链路继续尝试 |
| 停止兜底 | 返回已尝试路径、错误码和后端原文摘要 |

用户同意后，将用户原始问题原封不动作为 wind-alice 的 prompt。默认不传
Alice 子 skill；只有用户明确点名 Alice 子 skill，例如“公司一页纸”“事实核验”
或“上市公司调研问题清单”时才传。

## 未安装 wind-alice

用 AskUserQuestion 告知用户需要先安装，给出继续安装或停止兜底的选择。
若用户选择安装，提供当前项目可用命令：

```bash
# GitHub
npx skills add Wind-Information-Co-Ltd/wind-skills --skill wind-alice -g -y

# Gitee 镜像（国内）
npx skills add https://gitee.com/wind_info/wind-skills.git --skill wind-alice -g -y
```

若用户只想安装到当前项目，去掉命令中的 `-g`。

## 用户拒绝

尊重选择，停止继续 fallback。简要返回：

- 已尝试的 Wind 路径
- 关键错误码
- 后端原文摘要或无结果摘要
