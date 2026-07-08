# Git Commit Guidelines

## Purpose

`cc-act` 在执行 `create-pr` / `update-pr` 时，必须让 Git 历史成为可 review、可 bisect、可 revert、可交接的工程记录，而不是一句含糊的摘要。

提交记录要同时满足 5 个目标：

1. `git log --oneline` 能看懂变更类型和范围。
2. `git show` 能解释问题、取舍、验证和风险。
3. 每个 commit 边界足够小，后续可以独立 review、cherry-pick 或 revert。
4. PR body、handoff 和 commit history 讲同一套事实。
5. 后续维护者不需要聊天记录，也能知道为什么这么改。

## Research Baseline

本规范吸收当前公开实践，但落成 `cc-devflow` 自己的提交合同：

- Git 官方 `git commit` 文档建议首行少于 50 字符，空一行后写更完整描述；Git 会把首个空行前内容当成 title。
- Git 官方 `SubmittingPatches` 强调提交说明和代码同样重要，要解释 future maintainer 需要知道的 `why`，并使用祈使句。
- Conventional Commits 1.0.0 给出机器可读标题、body、footer 结构，`feat` / `fix` / `BREAKING CHANGE` 可驱动 changelog 和 semver。
- Git trailer 规范支持结构化 footer，例如 `Reviewed-by`、`Signed-off-by`、`Refs`。
- GitHub/GitLab 支持在 commit message 或 PR/MR 描述里用 closing keywords 关联和关闭 issue。
- 近期提交信息研究提示：只有 Conventional Commit 标题还不够，很多提交仍然信息量不足；所以本规范要求正文模板，而不是只要求 `type(scope): subject`。

## Commit Record Contract

默认使用 Conventional Commits 标题，但非平凡提交必须带正文。

`type(scope)` 保持 ASCII 和机器可读；`subject`、正文标题、正文内容默认使用项目 `Output language`。中文项目输出中文 commit 文本，不能照抄英文模板。

```text
<type>(<scope>): <中文 subject>

问题:
- <哪里坏了、缺了、风险在哪里、读者为什么要关心>

变更:
- <持久实现、模板、脚本、产物或契约变化>
- <关键边界、数据形状、工作流决策>

原因:
- <为什么当前方案是正确取舍>
- <为什么没有选择更窄、更宽或其它替代方案>

验证:
- <命令、产物、review gate，或明确 not-run 原因>

风险:
- <影响范围、迁移问题、回滚路径，或“低：仅文档/模板”>

关联:
- <REQ/FIX/RM/issue/PR/spec/review artifact，适用时填写>

<footer trailers when applicable>
```

正文不是复述 diff。正文解释 diff 看不出来的上下文：为什么改、边界在哪里、怎么证明、哪里可能坏。

## When Body Is Required

只允许非常小的机械变更使用单行 commit。满足任一条件时必须写 body：

1. 修改超过 1 个文件。
2. 改变用户可见行为、公共 API、CLI、schema、prompt、skill contract、验证脚本或发布流程。
3. 修 bug、回归、flaky、性能、安全、权限、数据一致性或 trust boundary。
4. 引入或改变测试策略、mock 边界、fixture、golden artifact。
5. 触碰 roadmap / task.md / PR brief / handoff 等 durable artifact。
6. 有兼容性、迁移、回滚或 follow-up 风险。

单行 commit 仅适合：

- typo / spelling
- 纯格式化且无行为变化
- 单文件注释澄清
- 生成物版本号同步，且 changelog 或 PR body 已解释原因

## Commit Message Format

```text
<type>(<scope>): <subject>

<body>

<footer>
```

规则：

1. `type` 必须表达变更性质。
2. `scope` 必须是 repo 里真实模块、skill、capability、script、doc area 或 package 名；不要写 `misc` / `stuff`。
3. `subject` 使用项目输出语言；中文项目写中文短句，`type(scope)` 仍保持 Conventional Commits ASCII 前缀。
4. `subject` 目标 50 字符以内；超过时先缩 scope 或拆 commit。
5. `body` 使用上面的中文结构化标题；非平凡提交不要只写一段泛泛说明。
6. `footer` 使用 Git trailer 风格：`Token: value`，每个 trailer 独立一行。
7. 如果当前仓库已有更严格规范，以仓库规范为准；但不能低于本文件的信息量要求。

## Allowed Types

- `feat`: 新功能或新增可观察能力
- `fix`: 修复缺陷、回归或错误行为
- `docs`: 文档、指南、示例文字
- `style`: 纯格式调整，不改行为
- `refactor`: 重构，不改外部行为
- `perf`: 性能优化
- `test`: 测试、fixture、golden artifact、验证 seam
- `build`: 构建系统、打包、发布配置
- `ci`: CI / workflow / automation
- `chore`: 依赖、脚本、仓库维护、生成物同步
- `revert`: 回滚既有 commit

## Body Templates By Type

### `feat`

```text
问题:
- <谁以前无法完成什么>

变更:
- <新增能力>
- <公共接口、产物、命令或用户可见流程>

原因:
- <为什么这个范围是当前正确切片>
- <哪些内容明确不在本次范围内>

验证:
- <命令或人工证明>

风险:
- <兼容性、发布、迁移、回滚>

关联:
- <REQ/RM/spec/issue>
```

### `fix`

```text
问题:
- <报告的现象和影响>

根因:
- <first bad state 或被破坏的契约>

变更:
- <最小修复>
- <为什么这不是只补症状>

验证:
- <可用时写 failing-before / passing-after 证据>
- <回归命令>

风险:
- <影响范围和回滚路径>

关联:
- <FIX/issue/root-cause/verification evidence>
```

### `refactor`

```text
问题:
- <坏味道、耦合、重复或维护风险>

不变量:
- <必须保持不变的行为>

变更:
- <移动、重命名、抽取或收敛的结构>

原因:
- <为什么这会简化系统>
- <为什么兼容性被保留或为何要改变>

验证:
- <测试、类型检查、diff check>

风险:
- <触碰的调用方和回滚路径>
```

### `test`

```text
问题:
- <以前没有覆盖的行为或回归>

变更:
- <新增的测试 seam、fixture 或断言>

原因:
- <为什么这个 seam 能触达真实触发链>
- <为什么更浅的覆盖会制造假安全>

验证:
- <测试命令和预期信号>

风险:
- <flaky 风险、fixture 维护成本、运行耗时>
```

### `docs`

```text
问题:
- <读者困惑、契约过期、缺 runbook 或文档漂移>

变更:
- <更新的章节或示例>

原因:
- <使用的真相源>
- <未来读者不再需要追问什么>

验证:
- <链接检查、示例检查、渲染检查，或 not-run 原因>

风险:
- <低，或文档继续漂移的风险>
```

### `build` / `ci` / `chore`

```text
问题:
- <工具链、依赖、发布或自动化缺口>

变更:
- <配置、脚本、package、lockfile、生成物>

原因:
- <为什么现在需要这个工具链变更>

验证:
- <真实工具入口或最接近的 smoke>

风险:
- <环境、版本、发布、回滚>
```

### `revert`

```text
问题:
- <为什么被回滚的 commit 不安全或错误>

变更:
- 回滚 <sha> (<subject>)。

原因:
- <为什么现在回滚优于向前修复>

验证:
- <回滚后的命令或证据>

风险:
- <丢失的行为、follow-up、回滚本次回滚的路径>
```

## Commit Boundary Rules

生成 commit 前必须先写 commit plan，并运行
`../../do-not-repeat-yourself/SKILL.md`。不要先 `git add .` 再想
message。

Commit plan 模板：

```text
Commit 1:
- 类型/scope:
- 文件:
- 分组原因:
- 验证:
- DRY record:
- Commit 文本草稿:

Commit 2:
- 类型/scope:
- 文件:
- 分组原因:
- 验证:
- Commit 文本草稿:
```

拆分规则：

1. 功能、测试、文档、配置属于不同类型时，拆成多个 commit。
2. 多个模块彼此独立时，按模块拆分 commit。
3. 数据模型、服务层、API、UI 横跨多层时，优先按层拆分，除非某层单独无法通过验证。
4. 修 bug 与补防御性 guard / follow-up 不是同一件事，能拆就拆。
5. 生成物和源文件一起提交，必须在 body 里说明生成关系和验证命令。
6. 一个 commit 如果预期触碰超过 8 个文件，先问自己是否混了多个语义；不能拆时在 body 的 `Risk` 里说明原因。
7. 每个 commit 尽量独立可验证。不能独立跑全量测试时，至少给出最贴近该 commit 的验证。

DRY gate:

1. 先按 `../../do-not-repeat-yourself/SKILL.md` 检查 staged 或待 stage 的
   commit bucket。
2. 如果当前 diff 新增 helper、adapter、validator、parser、script、skill、
   prompt rule、schema 或跨模块 doc rule，必须记录已有 wheel、复用结果
   或无法复用的原因。
3. 发现当前 diff 里有可由已有 wheel 覆盖的新机制时，默认删除新机制并
   改用已有 wheel。
4. 历史重复只报告，不扩大本 commit 重构，除非它阻断当前正确性。

推荐拆分顺序：

1. 数据 / schema / contract
2. 核心实现
3. 测试
4. 文档 / examples
5. 构建 / 发布 / 生成物

## History Rules

1. 推送前优先同步 base branch，并尽量用 `git pull --rebase` 或 `git rebase <base>` 保持线性历史。
2. 已有打开 PR / MR 时，更新现有 PR / MR，不重复创建第二个。
3. rebase 之后如果必须强推，只允许 `git push --force-with-lease`，不要裸 `--force`。
4. 不改写公共分支历史。
5. 不把 WIP、AI 过程笔记、debug probe、临时日志留在最终历史里；必要时 squash/fixup 到语义 commit。
6. 使用 `fixup!` / `squash!` 时，最终 ship 前要 autosquash 成干净历史，除非团队明确接受。

## Footer Trailers

Footer 用于机器和长期审计，不用于塞正文。

常用 trailers：

- `BREAKING CHANGE: <what breaks and migration path>`
- `Closes: #123`
- `Refs: #123`
- `Reviewed-by: <name>`
- `Co-authored-by: <name> <email>`
- `Signed-off-by: <name> <email>`，仅在项目要求 DCO / signoff 时使用
- `Change-Id: <id>`，仅在 Gerrit 或项目要求时使用

GitHub/GitLab 自动关闭 issue 时，每个 issue 都要带 closing keyword，例如：

```text
Closes: #10
Resolves: #123
Fixes: owner/repo#100
```

只想关联不想关闭时，用 `Refs:`，不要用 closing keyword。

## Bad Messages

禁止这些标题：

- `fix bug`
- `update files`
- `misc changes`
- `wip`
- `improve stuff`
- `final changes`
- `address feedback`
- `cleanup`
- `changes from review`

可以改成：

```text
fix(auth): 拒绝过期 refresh token

问题:
- 后台续期流程会接受已经过期的 refresh token。

根因:
- 续期路径信任缓存的过期标记，而不是 token payload 里的真实过期时间。

变更:
- 发放替换 token 前先解析 payload 过期时间。
- 缓存只保留为优化手段，不再作为信任边界。

验证:
- npm test -- auth-token-refresh.test.ts

风险:
- 低：只影响 auth 续期路径；回滚会恢复旧缓存检查。

关联:
- FIX-042
```

## CC-Act Enforcement

`cc-act` 在 `create-pr` / `update-pr` 模式下至少要检查：

1. 是否先列出 commit plan，再 staging。
2. DRY record 是否来自 `../../do-not-repeat-yourself/SKILL.md`，并覆盖新增机制和 staged diff。
3. staged files 是否只属于当前 commit bucket。
4. commit title 是否符合 Conventional Commits 或仓库更严格规范。
5. 非平凡 commit 是否有 `问题`、`变更`、`原因`、`验证`、`风险`。
6. `fix` commit 是否写了 `根因`，且不是只描述 symptom。
7. `验证` 是否是实际命令 / artifact / explicit skip reason，而不是 “tested locally”。
8. footer 是否使用 trailer 风格，issue closing keyword 是否符合目标平台语义。
9. push、PR body、handoff 是否与最终 commit history 表达同一套事实。

如果无法满足这些条件，停在 `local-handoff` 或 reroute，不要制造粗糙历史。
