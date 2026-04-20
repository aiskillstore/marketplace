# liepin-cli Reference

## Install Context
- 目标用户本机需已安装 `liepin-cli` 并在 PATH 中可用。
- 若未安装，请参考 [liepin-tech-2026/liepin-cil](https://github.com/liepin-tech-2026/liepin-cil) 的 README 完成安装（`pip install -e` 或 `uv sync`）。
- Auth、帮助、命令表、payload 格式与示例均见该仓库 README。

## Core Commands
```bash
liepin-cli setup
liepin-cli auth setup
liepin-cli auth status
liepin-cli auth open
liepin-cli auth clear

liepin-cli resume get --output json
liepin-cli job search --job-name "Java开发" --address "北京" --page 0 --output json
liepin-cli job apply --job-id 123456 --job-kind 2 --output json
```

## User-Facing Help Rule
- 首次帮助只展示面向业务的命令与参数。
- 除非用户明确要求完整帮助，否则不提隐藏/内部 flag。
- `job apply` 首次帮助聚焦 `--job-id` 和 `--job-kind`。
- `resume --help` 首次帮助只说明用途和子命令概览。

### Auth Commands

| Command | Description |
|------|------|
| `liepin-cli auth setup` | 交互式授权，与 `liepin-cli setup` 等价 |
| `liepin-cli auth status` | 查看已保存 token（脱敏） |
| `liepin-cli auth clear` | 清除本地已保存的 token |
| `liepin-cli auth open` | 打开猎聘授权页，便于刷新 token |

### Resume Commands

| Command | Description | Common args | Supports `--input` |
|------|------|------|------|
| `liepin-cli resume get` | 获取当前简历 | 无 | 否 |
| `liepin-cli resume update-base-info` | 更新基础资料 | `--real-name`、`--sex`、`--birthday`、`--city-code`、`--start-job`、`--start-job-month` | 是 |
| `liepin-cli resume update-self-assess` | 更新自我评价 | `--self-assess` | 是 |
| `liepin-cli resume add-edu-exp` | 新增教育经历 | `--school`、`--major`、`--start`、`--end`、`--degree` | 是 |
| `liepin-cli resume update-edu-exp` | 更新教育经历 | `--edu-id`，以及学校/专业/起止时间/学历等字段 | 是 |
| `liepin-cli resume add-work-exp` | 新增工作经历 | `--comp-name`、`--rw-title`、`--work-start`、`--work-end`、`--salary` | 是 |
| `liepin-cli resume update-work-exp` | 更新工作经历 | `--work-id`，以及公司/职位/时间/薪资等字段 | 是 |
| `liepin-cli resume add-project-exp` | 新增项目经历 | `--name`、`--start`、`--end`、`--position` | 是 |
| `liepin-cli resume update-project-exp` | 更新项目经历 | `--id`，以及项目名称/时间/角色等字段 | 是 |
| `liepin-cli resume add-job-want` | 新增求职期望 | `--jobtitle`、`--dq`、`--want-salary-low`、`--want-salary-high` | 是 |
| `liepin-cli resume update-job-want` | 更新求职期望 | `--id`，以及职位/地点/薪资等字段 | 是 |

### Job Commands

| Command | Description | Common args | Supports `--input` |
|------|------|------|------|
| `liepin-cli job search` | 搜索职位 | `--job-name`、`--address`、`--salary-floor`、`--page` | 是 |
| `liepin-cli job apply` | 投递职位 | `--job-id`、`--job-kind`（两者都必填） | 是 |

## Auth Recovery
- 缺少 token：运行 `liepin-cli setup` 或 `liepin-cli auth setup`
- token 未授权：先运行 `liepin-cli auth open`，再执行 `liepin-cli auth setup`
- Token 优先级：`--token` > `LIEPIN_USER_TOKEN` > 本地配置文件（`~/.config/liepin-cli/config.json`）

## `jobKind` Rule
- `job apply --job-kind` 必须使用搜索返回的类型编码，如 `1` 或 `2`
- 先搜索，再复用返回的类型值，不要猜测

## `--input` Rule
- 多数 add/update 命令支持 `--input <json-file>`
- 合并顺序：先读文件，再用显式 CLI 参数覆盖，最后去除空值并校验
- README 示例 payload 路径仅为说明，不随仓库一起提供

## Output Mode Rule
- Chat 需要机器可读输出时，优先用 `--output json`
- `pretty` 对空响应显示 `成功。`，`json` 输出 `null`

## Exit Codes
- `0`：成功
- `1`：远端/API 失败（HTTP 或网络错误）
- `2`：本地输入或配置错误（缺少 token、JSON 非法、字段不合法等）
