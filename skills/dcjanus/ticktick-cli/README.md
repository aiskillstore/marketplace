# ticktick-cli 记录

## 背景
- 目标：通过 Python CLI（供 Codex 调用）管理滴答清单账号。
- 技术栈：uv script + Typer + Pydantic + httpx。
- API 文档：[滴答清单 OpenAPI](https://developer.dida365.com/docs/index.html#/openapi)（更新较少，需自行验证）。
- CLI 入口：[ticktick_cli.py](scripts/ticktick_cli.py)。

## 认证现状
- CLI 已可正常调用（依赖可用的 OAuth Token）。
- 仍需：在开发者平台注册 OAuth app，并部署服务端逻辑获取 OAuth Token（Worker 路径见下）。

## CLI 进度
- 已支持项目/任务的增删改查与完成。
- 已支持更新 Checklist 子任务，推荐使用 JSON 方式：`--item-json`（可传 JSON 字符串或 `@path` 文件）。
- 典型场景：按剧集/章节拆分追踪，每集一个子任务并写入 `startDate`。

## OAuth Worker 运行所需信息
- `TICKTICK_CLIENT_ID`：在 [Dida365 Developer Center](https://developer.dida365.com/manage) 创建 OAuth 应用后获得。
- `TICKTICK_CLIENT_SECRET`：同上，用于 server-to-server 交换 token。

## 计划
- 已使用 Cloudflare Worker 部署 OAuth 服务端逻辑，并跑通流程。
- 部署脚本：[ticktick-oauth-worker.js](skills/ticktick-cli/assets/ticktick-oauth-worker.js)。
- 后续：优化 [SKILL.md](SKILL.md)，补充更多 CLI 可用性用例。
- 规划中：在 CLI 内部实现搜索、jq 风格筛选与裁剪输出，方便 Codex 调用时精确获取目标字段。
