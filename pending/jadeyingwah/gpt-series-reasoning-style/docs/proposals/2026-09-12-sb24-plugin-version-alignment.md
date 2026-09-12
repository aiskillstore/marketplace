# 提案：插件清单版本一致性守卫（暂定 SB24）/ Proposal: plugin-manifest version-alignment guard

- 日期 / Date: 2026-09-12
- 状态 / Status: **Proposed（待总指挥裁决；未实施）**
- 触发 / Trigger: 1.2.0 之后新增 Claude Code 插件打包（`.claude-plugin/plugin.json`、`.claude-plugin/marketplace.json`）
- 关联 / Related: SB1（version consistency）、SB21（prose 计数）、CI（`.github/workflows/selfcheck.yml`）、`references/self-test.md`

## 背景 / Background

1.2.0 之前，版本真值只有 `VERSION` 一个机器可读源，SB1 负责把它与 SKILL.md / README / self-test / site 四个**文本表面**对齐。

Claude Code 插件打包引入后，版本号新增两处**机器可读**落点：

- `.claude-plugin/plugin.json` 的 `version`
- `.claude-plugin/marketplace.json` 的 `version` 与 `plugins[0].version`

Claude Code 的更新判定依赖清单里的版本字符串：设了 `version` 就只在该字符串变化时向用户推送更新。三处一旦漂移（例如发版时只改了 `VERSION` 忘了改清单），会出现「仓库已新版、插件市场仍显示/钉住旧版」的真实分发故障，且无任何报错。

当前 SB1 不读取 `.claude-plugin/`，覆盖不到这两个新表面。

## 提议 / Proposal

让静态自检对三处版本做一致性断言：`VERSION` == `plugin.json.version` == `marketplace.json.plugins[0].version`（顶层 `marketplace.json.version` 是清单自身版本，一并纳入或明确豁免）。

## 准入门槛（为何本次不直接实施）/ Bar

项目对新增 SB 项有准入要求：必须先用一次**人为漂移的 RED 实证**证明守卫真的会红（能抓到真实缺陷），且新增守卫会把 SB 计数 22 → 23，牵动 SB21 的 prose 计数、CI 步数口径、`references/self-test.md` 等多个表面，成本不为零。本次只完成打包，没有发版漂移的真实案件，不满足「先有 RED 实证」的准入，故不落地。

本次的临时缓解：发布时用一次性脚本本地断言三处一致（22 项结构检查全部 PASS，脚本未入库），selfcheck 仍为 22/22、指纹不变。

## 裁决选项 / Options

- **A. 新增 SB24**：补一次 RED 实证（临时把 `plugin.json.version` 改成失配值，确认新守卫判失败；改回后转绿），再正式实施，并同步 SB21 / CI / self-test 的全部计数表面。
- **B. 暂不立项**：保持 22 项，发版流程里人工核对三处版本，接受漏改风险。
- **C.（推荐）并入现有 SB1**：不增加 SB 计数，把 SB1「version consistency」的监控表面从四个文本表面扩展到包含两份插件清单。改动面最小、不触发 SB21/CI 计数变更，语义上也本就属于「版本一致性」。同样要求先做一次 RED 实证。

## 建议 / Recommendation

倾向 **C**：这是既有守卫职责的自然延伸，而非一类新缺陷；新增独立编号会高估其独立性。无论选哪个，落地前都应先制造一次失配确认守卫能红，避免出现「从不失败的检查」（项目反例 F6 / 鉴别力原则）。
