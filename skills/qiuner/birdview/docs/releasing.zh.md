# 发布检查清单

[English](releasing.md)

1. 审阅 diff 并确定发布版本。保持 `package.json`、`package-lock.json` 根包条目、README 版本徽章和发布说明一致。
2. 运行 `npm ci`、`npm run typecheck`、`npm run check:build`、`npm test`、`npm run validate:examples` 和 `node scripts/check-docs.mjs`。更新文档确认记录前先审阅双语内容。
3. 运行 `npm run build:demo` 并检查生成文件的 diff。打开两种语言的演示，在桌面和移动端检查架构、更改、对照、指引和详情是否保持一屏。使用 `npx playwright install chromium` 安装 Chromium，再运行 `npm run test:browser`（查看器、指引、约束、视口及网站），记录跳过的检查。
4. 分发时包含 `LICENSE` 和 `THIRD_PARTY_NOTICES`。检查截图、示例和附件不含私有数据；单独分发生成的 HTML 时保留其中的第三方许可证声明。
5. 编写发布说明，包含改动、安装、验证和已知限制。Birdview 展示 Agent 声明的活动，不独立观测编辑，也不强制执行改前流程。
6. 获得明确授权后，提交已审阅的改动、创建版本标签并发布 GitHub Release。创建标签前，对已提交的发布候选运行 `npm run check:install`。检查标签和下载内容。准备 GitHub 发版不代表开启 npm 发布，包仍保持 `private`。

GitHub 提供双语问题反馈和功能建议表单。默认 PR 模板为英文，可按需使用中文配套模板。这些平台模板不是可执行的 Skill 指令。
