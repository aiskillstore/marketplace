# 贡献指南

[English](CONTRIBUTING.md)

## 开发与拉取请求

使用 Node.js 18 或更高版本。在 GitHub Fork 仓库，在自己的 Fork 中使用专注当前改动的分支，向上游默认分支提交 PR。较大的功能先通过 Issue 讨论问题。问题反馈应包含可复现步骤和脱敏输入。

```sh
npm ci
npm run typecheck
npm run check:build
npm test
npm run validate:examples
node scripts/check-docs.mjs
```

修改查看器或渲染器时运行 `npm run build:demo` 并审阅已跟踪演示文件的 diff。验证中英文、桌面和移动端及受影响的交互。运行 `npx playwright install chromium` 和 `npm run test:browser` 进行真实浏览器检查，详见[发布检查清单](docs/releasing.zh.md)。行为改动应补充回归覆盖，在 PR 模板中说明实际运行的检查和剩余限制。不要包含私有源码数据或凭据。

CI 在 Windows 和 Linux 上使用 Node.js 18、24 检查，校验文档和示例，验证已跟踪演示与渲染器输出一致，并审计干净源码归档安装。Linux Node.js 24 任务运行 Chromium 查看器与网站测试。贡献内容按仓库的 [MIT 许可证](LICENSE) 分发；保留[第三方声明](THIRD_PARTY_NOTICES)。

## TypeScript 迁移

结构契约由 `src/contracts/models.mts` 中的 TypeBox 定义维护，同时推导 TypeScript 类型。`npm run build` 生成运行时模块并重新生成 `schemas/*.schema.json`，不要直接修改交换文件。Ajv 仍负责运行时校验，跨记录检查由 `src/validate.mts` 维护并生成 `scripts/validate.mjs`。迁移专用冻结基线已在验收后删除。契约测试对照当前运行时校验器与导出 Schema，包括变异输入及输入不变性检查。`npm run typecheck` 也检查类型收窄及非法类型案例，`check:build` 校验生成 Schema。阶段状态与剩余工作见[迁移施工文档](docs/typescript-migration.zh.md)。

项目模式 CLI 和 HTML 渲染器由 `src/birdview.mts` 和 `src/render.mts` 维护；修改后执行 `npm run build`。严格 TypeScript 编译为兼容 Node.js 18 的 ESM，输出原有的 `scripts/*.mjs` 命令路径。生成文件随源码一起分发，技能用户无需编译。CI 检查类型，并将临时干净构建与分发的 JavaScript 对比。不要直接修改生成文件。渲染器的临时声明已删除；外部架构 JSON 仍需运行时校验。浏览器入口也已迁入 TypeScript。

仓库检查工具也由 `src/check-docs.mts` 和 `src/check-build.mts` 维护；使用 `npm run build` 重新生成分发脚本。`npm test` 严格检查所有 TypeScript 测试，将单元测试打包到被忽略的 `.test-build/`。测试导入实际分发模块，保留 CLI 入口判断及安装行为。`npm run test:browser` 运行编译后的浏览器测试。已提交的构建检查器可以验证干净检出，无需先覆盖它要检查的产物。

浏览器实现由 `src/viewer/main.mts` 维护，显式导入 `routing.mts` 和 `i18n.mts`。入口负责 DOM 语言更新、活动、约束及指引状态，不再依赖跨脚本隐式全局变量或 JavaScript 文本插入。`tsconfig.viewer.json` 在不含 Node 全局类型的环境下检查。固定版本 esbuild 生成自包含 `assets/viewer.js` 和供测试的纯 ESM 模块，`check:build` 校验全部产物。路由和翻译测试覆盖当前行为，不再保留旧实现。修改此边界时保留 CSS、文案和交互行为并验证截图。

## 提交规则

- 未经用户明确要求，不执行 `git add`、`git commit`、`git push`、创建分支或改写历史。
- 提交标题使用 `type(scope): 中文说明 / English summary` 格式的 Conventional Commits。
- 每个提交只包含一组逻辑一致的变更；不同性质的改动必须分别暂存和提交。
- 不提交本地状态或临时构建产物；遵循各目录的 `.gitignore`。从 `src/` 生成到 `scripts/` 的分发 JavaScript、浏览器产物 `assets/viewer.js`，以及 `schemas/` 中生成的交换 Schema 是明确例外，须随其 TypeScript 源码变更一起提交。不要提交 `.test-build/`。
- 提交前检查 staged diff，排除无关文件、生成物、调试输出和未说明的格式化。

## 文档维护

- 同目录下英文 `name.md` 与中文 `name.zh.md` 配对，首个标题下互链。优先引用同语言文档，避免正文混用语言。
- 两版含义一致，包含示例、约束和限制；标识、命令、数据路径和枚举不翻译。同步编辑、审阅，不用摘要替代译文。
- 用户指令优先。有差异时按实现与授权需求核对并修正两版，任何语言都不覆盖另一版。
- 仅 `SKILL.md` 保留可执行 frontmatter（`name`、`description`）；`SKILL.zh.md` 是阅读版，不重复注册。
- 根目录、`references/`、`docs/`、`examples/` 新增自有 Markdown 必须配对；新自有目录加入检查范围，依赖和生成输出除外。

## 检查与记录

```sh
node scripts/check-docs.mjs
```

检查配对、语言互链、本地 Markdown 链接和自确认后的变化。`docs/i18n.json` 保存将 CRLF 规范化为 LF 后的 SHA-256；哈希不能判断译文准确性。

核对两版后才更新记录，并与成对文件一起提交：

```sh
node scripts/check-docs.mjs --update
```

不要仅为消除报错刷新哈希。

网站与主题启动逻辑由 `src/site/main.mts` 和 `src/viewer/theme.mts` 维护。生成的分发产物为 `docs/site.js` 和 `assets/theme.js`，随源码一起提交。渲染器在样式之前内嵌主题启动逻辑，保持首次绘制前的主题选择。`build` 和 `check:build` 均覆盖这两份产物。

`build-artifacts.json` 列出全部分发 JS 模块与交换 Schema。`check:build` 拒绝缺失、过期、未登记及废弃产物。`npm run check:install` 使用 Git 和 tar 审计已提交的 `HEAD` 归档，在临时目录安装依赖，构建前执行 doctor 和三个 Agent 的 setup/uninstall，再检查产物可复现性。请先提交；该检查有意排除未提交工作，也不使用当前检出的 node_modules。
