# 安全说明

本文件面向技能平台审核与最终用户，说明 `zentao-task-planner` 如何处理凭据与网络请求。

## 凭据来源与去向

- 唯一凭据来源：进程环境变量 `ZENTAO_BASE_URL` / `ZENTAO_ACCOUNT` / `ZENTAO_PASSWORD`，或用户通过 `--env-file` 显式指定的本地 `.env` 文件；环境变量优先于 `.env`。
- 技能包内不含任何真实凭据，只附带 `.env.example` 模板；`.env` 与 `__pycache__/` 在打包时会被排除。
- 凭据唯一用途：以 POST 表单体方式调用用户自己禅道站点的 `user-login.json` 接口完成登录。凭据不会出现在 URL、查询参数、日志或错误信息中（`ZentaoConfig.__repr__` 对密码做了遮蔽）。
- 脚本不会写入、复制或上传 `.env`，凭据始终留在用户本机。

## 网络边界

- `ZentaoClient` 的所有 HTTP 请求统一经过 `_url()` 构造地址，强制限制在 `ZENTAO_BASE_URL` 前缀之下；代码中不存在任何第三方域名、远程下载执行、遥测或数据上报。
- 所有请求统一设置 30 秒超时；HTTPS 站点走标准证书校验（未关闭 `verify`）。
- 请求使用真实的 User-Agent（`zentao-task-planner-skill/1.0`），不伪装浏览器。

## 写操作保护

- 创建任务、按日期完成任务、关闭任务、修复工时日期等写操作默认 dry-run 预览，必须显式传 `--execute` 才会提交。
- SKILL.md 要求所有有副作用的操作先向用户展示预览结果并获得确认。

## 依赖

运行时依赖均为常用开源库：`requests`、`beautifulsoup4`、`python-dotenv`、`chinese-calendar`。技能包内只有 Python 源码和 Markdown 文档，不含二进制或编译产物。

## 漏洞反馈

请通过仓库 Issue 反馈安全问题。
