# 阶段 2：表达变更

[English](show-changes.md)

准备计划的前提是用户提出的任务和[阶段 1](map-project.zh.md) 建立的可用地图。实施还须按 [SKILL.zh.md](../SKILL.zh.md) 取得用户对已展示方案的确认。
阅读[契约](contract.zh.md)、`schemas/activity.schema.json` 和事件示例。
使用准确的项目、地图、版本和模块 ID；生成事件前解决过时覆盖，不替换成虚构地图，也不从文字猜 ID。

## 记录操作

编辑前，按 [development.zh.md](development.zh.md) 选择相关任务规范。在 `planned` 的原因中说明预期可观察行为和验证方法；已执行结果使用现有 `checks`，适用的已记录约束使用 `constraintReviews`，不增加事件字段。

1. 编辑前：追加 `planned`，包含完整 `scope`、当前 `targets`、相对项目的 `files` 和基于模块的简短原因。渲染并交付计划，询问确认并等待。最初的编码请求不代表批准未展示方案；复用用户对同一方案已有的确认，遵循明确的单次任务豁免。
2. 确认后，每组编辑前：追加 `editing`，填写具体路径，目标只包含当前编辑模块。
3. 检查前：追加 `verifying`；测试或测试数据路径不自动算作修改文件。
4. 任务结束：追加 `completed`、`failed` 或 `cancelled`，适用时在 `checks` 中记录实际命令、退出码和观察结果。

每行 JSONL 都携带完整范围和目标。编辑新增模块前，用新的 `planned` 解释范围扩大，更新预览并确认变化范围。有归属文件的编辑应将所有匹配所有者列为目标；无归属文件同时列入 `files` 与 `unmappedFiles`。不能为通过校验编造归属，误导性规则应回到阶段 1 修正。

每个会话只允许一个活动任务，序号从 1 连续递增。终态后使用新任务 ID，不重开旧任务。项目与地图版本固定，新版本使用新会话/文件。这些是 Agent 声明：检查执行前保持待定，事件发出或任务结束不代表成功。

## 渲染与交付

```sh
node <skill-root>/scripts/render.mjs <map.json> <activity.html> <activity.jsonl>
```

渲染器校验完整事件流后才替换输出。成功后交付，遵循阶段 1 的预览检查。

- 真实活动默认最新记录，模拟默认首条计划。历史和可折叠文件/检查描述所选步骤，不是累计 Git 差异。
- 架构、更改、对照共享位置；对照联动选择、缩放和滚动，窄屏上下排列。
- 范围保留轮廓，非目标弱化；编辑前高亮计划目标，验证目标单独标识，终态移除目标光晕。未执行检查即未验证。
- `--simulation` 仅用于 `examples/harness.activity.jsonl` 等虚构记录，不得称为实际观测。
- 每种活动语言都提供事件 `translations[locale].reason` 和检查 `translations[locale].summary`，缺失时回退原文。
- 更新需重新生成并刷新。尚无上传、自动刷新、实时拦截或 Git 验证；未来显示回执只确认渲染，不代表批准或正确性。
