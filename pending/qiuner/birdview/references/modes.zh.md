# 项目触发模式

[English](modes.md)

Birdview 默认按需调用，默认 `on-demand`。用户选择技能、明确要求 Birdview 或架构/约束/更改图时才运行。普通编码、小修复和功能规划不触发；仅讨论方案不授权编辑。

## 调用入口

Codex 使用 `/skills` 选择 Birdview，或输入 `$birdview`；Claude Code 使用 `/birdview`。其他宿主使用各自的技能选择器或明确请求，不保证支持同样的斜杠命令。调用作用于当前任务。仅讨论 Birdview 不会启动建图。

## 配置与迁移

```sh
node <skill-root>/scripts/birdview.mjs setup --project <project-root>
node <skill-root>/scripts/birdview.mjs mode auto --project <project-root>
node <skill-root>/scripts/birdview.mjs mode on-demand --project <project-root>
node <skill-root>/scripts/birdview.mjs mode off --project <project-root>
node <skill-root>/scripts/birdview.mjs mode --project <project-root>
node <skill-root>/scripts/birdview.mjs uninstall --project <project-root>
```

`setup` 为新项目默认选择 `on-demand`，保留已有 `auto`、`on-demand` 或 `off`。使用 `mode auto` 主动开启每次改代码（含小改动）及明确分析涉及模块的规划前自动介入；使用 `mode on-demand` 恢复按需调用。查询只读。更新技能不会重写其他项目，请在新任务中验证所选模式。

基础约束与画图触发独立。`setup`、`mode auto` 和 `mode on-demand` 从 [foundation.txt](foundation.txt) 安装基础约束，要求聚焦源码、依据证据、适度验证和查看协作记录，不要求读取技能或生成地图。`off` 停用基础约束和画图，当前任务明确调用除外。`uninstall` 仅移除项目管理段，保留文件、其他规则、技能与地图；保留技能时恢复默认按需行为。

## 存储与边界

使用已安装技能的绝对路径和目标项目根目录。省略 `--project` 时只使用当前目录，不搜索父目录。`--agent codex`（默认）和 `--agent deepseek` 使用 `AGENTS.md`；`--agent claude-code` 使用 `CLAUDE.md`。写入和查询使用相同宿主参数，不跨文件同步。源码仓库可选执行 `npm link` 后使用 `birdview mode`；Node 命令不需要 link。

只修改 `<!-- birdview:mode:start -->` 与 `<!-- birdview:mode:end -->` 间的管理段，保留周围字节。重复配置不产生变化；损坏或重复标记、非普通文件导致拒绝写入。管理段为英文机器指令。

这些配置依赖宿主加载，不是文件写入拦截。不要覆盖其他位置的冲突指令；报告已知冲突。已有会话可能保留旧指令，CLI 测试只证明配置行为；新任务仍需检查真实技能选择和产物。
