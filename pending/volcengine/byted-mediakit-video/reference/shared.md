# MediaKit 共享规则

本技能指导你如何通过 mediakit-cli 操作媒体资源，以及调用过程中的通用规则和注意事项。

## 前置检查

### 依赖安装

首次使用前，确认 CLI 已安装：

```bash
# 安装
npm install -g @volcengine/mediakit-cli

# 验证
mediakit-cli --version
```

### 鉴权信息检查

优先级：环境变量 > 配置文件（文件路径 `~/.mediakit/config.json`）

#### 字段说明

- 环境变量/配置文件：`MEDIAKIT_API_KEY`、`MEDIAKIT_ENDPOINT`、`MEDIAKIT_SURFACE`、`MEDIAKIT_RUNTIME`

| 变量 | 必填 | 说明 |
|------|------|------|
| `MEDIAKIT_API_KEY` | 云端模式必填 | API 认证 Token |
| `MEDIAKIT_ENDPOINT` | 否 | API 访问点 |
| `MEDIAKIT_SURFACE` | 否 | 请求来源 Header `x-surface`；默认 `cli`，Skill 建议 `skill`，Plugin 建议 `plugin`，最终上报 `cli/skill` 或 `cli/plugin` |
| `MEDIAKIT_RUNTIME` | 否 | 请求来源 Header `x-runtime`；按宿主设置为 `claude`、`arkclaw` 等，未配置时回退环境探测或 `unknown` |

任一必填项缺失时，终止执行并输出所有缺失项的列表及修复建议。

云端调用会自动携带 `x-surface` / `x-runtime`。Header 优先级为：环境变量 > `~/.mediakit/config.json` > 默认值/环境探测。当本 Skill/Plugin 通过 `mediakit-cli` 调用云端能力时，运行环境应注入 `MEDIAKIT_SURFACE=skill|plugin` 与 `MEDIAKIT_RUNTIME=<宿主>`；CLI 会保留原始产物前缀并上报 `x-surface=cli/skill|cli/plugin`。若未显式配置，CLI 默认按 `x-surface=cli`，`x-runtime` 依次回退 `IDENTITY_NAME` / `OPENCLAW_SERVICE_MARKER` 环境探测，最后为 `unknown`。

### 来源上报约束

- Skill 调用 `mediakit-cli` 时，必须显式设置 `MEDIAKIT_SURFACE=skill`，不能依赖用户已有环境变量。
- Plugin 调用 `mediakit-cli` 时，必须显式设置 `MEDIAKIT_SURFACE=plugin`，不能复用 Skill 的取值。
- 宿主环境标识建议同时显式设置 `MEDIAKIT_RUNTIME=<宿主>`；若未设置，CLI 会回退为环境探测值或 `unknown`。

```bash
MEDIAKIT_SURFACE=skill MEDIAKIT_RUNTIME=<runtime> mediakit-cli editing add-image-to-video

MEDIAKIT_SURFACE=plugin MEDIAKIT_RUNTIME=<runtime> mediakit-cli editing add-image-to-video
```

## CLI 使用方式

### 初始化配置

首次使用建议先运行初始化向导：

```bash
mediakit-cli init
```

Agent 非交互初始化可显式写入请求来源与运行时配置：

```bash
mediakit-cli init --mode cloud-first --api-key <key> --runtime <runtime> --surface cli --yes
mediakit-cli init --mode local-first --api-key <key> --endpoint <url> --output-path ~/mediakit-output --runtime <runtime> --surface cli --credential-store config --yes
```

初始化后常用命令如下：

```bash
# 查看当前配置
mediakit-cli config show

# 切换默认模式到本地优先
mediakit-cli config set mode local-first

# 切换默认模式到云端优先
mediakit-cli config set mode cloud-first

# 刷新环境检查并查看依赖状态
mediakit-cli doctor
```

### 命令结构

MediaKit CLI 统一使用 `domain + tool` 的调用方式：

```bash
mediakit-cli {domain} {tool} [flags]
```

常见帮助命令：

```bash
# 查看所有 domain
mediakit-cli --domains

# 查看某个分组下的工具列表
mediakit-cli {domain} --help

# 查看具体工具的参数
mediakit-cli {domain} {tool} --help

# 动态发现工具能力与返回结构
mediakit-cli {domain} {tool} --schema
mediakit-cli --local {domain} {tool} --schema
```

当前产物覆盖的 domain 包括：`editing`, `video`。

### Schema 发现

每个 capability 命令都支持 `--schema`，用于 Agent 动态读取工具能力，不要求传必填业务参数。

返回结构包含：

- `name`：工具名，使用 snake_case，如 `add_image_to_video`
- `description`：工具描述，自动包含 `Mode` 与 `Async` 信息
- `input_schema`：输入参数 JSON Schema
- `output_schema`：当前执行模式下的返回结构

输出区分规则：

- 默认按全局 `mode` 配置解析返回面
- `--local ... --schema` 输出本地模式返回面，本地模式直接返回最终结果字段
- 云端异步工具输出 `task_id` / `request_id`，并在 `final_result` 中描述 `query-task` 完成态结果
- `query-task` 是 cloud only，schema 描述任务状态与完成态结果

示例：

```bash
mediakit-cli editing trim-video --schema
mediakit-cli --local editing trim-video --schema
```

### 单次调用模式覆盖

除 `config set mode` 设置默认模式外，还支持仅对当前命令生效的临时覆盖：

```bash
mediakit-cli --local editing add-image-to-video

mediakit-cli --cloud editing add-image-to-video
```

补充规则：

- `--local` / `--cloud` 只影响当前命令，不修改全局 `config.mode`
- `--local` 与 `--cloud` 互斥，不能同时传入

## 异步任务

提交异步媒体处理任务成功后会返回 `task_id` 字段。通过 `shared query-task` 命令查询结果。

```bash
mediakit-cli shared query-task --task-id <task_id>
```

## local / cloud 约束

- `query-task` 是 **cloud only** 工具
- local 模式下不支持 query-task
- 当前本轮能力以云端执行为主；如需显式声明，请优先使用 `--cloud`

### Cloud 模式媒体输入补充

- 当命令以 `--cloud` 或 `cloud-first` 策略执行时，媒体输入参数（如 `video_url`、`audio_url`、`image_url`、`subtitle_url`、`sub_image_url` 及对应数组/对象子字段）可传入 `http://` / `https://` URL、`mediakit://...` file_id 或本地文件路径
- `http://` / `https://` URL 与 `mediakit://...` file_id 会原样提交；本地文件路径会由 CLI 先上传为 `mediakit://...` file_id，再提交给云端工具
- 各工具 reference 中的参数说明来自 APIHub/OpenAPI 原始字段描述；若其中写有公网 URL 或 HTTP/HTTPS URL，表示云端 API 最终接收的资源形态，不限制 CLI cloud 模式的本地路径预处理能力

### Local 模式补充

- 本地输出目录优先级：`--output-path` > `MEDIAKIT_OUTPUT_PATH` > config `output_path` > `~/.mediakit/temp`
- 当 `--output-path` 指向具体媒体文件名时，直接作为最终输出文件；否则按输入文件名生成 `{原文件名}_{工具名}.{ext}`，重复时追加 6 位随机数
- 无法从输入 URL 或路径提取文件名时，退回 `{工具名}-{UnixNano}.{ext}`
- local 模式依赖 `ffmpeg` / `ffprobe`，缺失时错误中会给出 `install_guide`
- local 模式媒体处理输出必须贴合接口 response schema，禁止输出内部执行元数据

### 错误响应

- CLI cloud 模式直接透传 API 返回的原始 error 对象，不提取 `message`
- CLI local 模式返回结构化错误：`{"error":{"type":"...","code":"...","message":"..."}}`
- MCP error_response 直接透传原始 error 内容，dict 原样作为 `error` 字段值

## 幂等参数维护

| 参数 | 作用 | 维护建议 |
|------|------|----------|
| `client_token` | 主动控制幂等 | 请求重试时复用同一值；强制重新执行时传新的唯一值 |
| `callback_args` | 透传回调参数 | 建议与 `client_token` 一起维护，便于回调对账与重试追踪 |

补充规则：

- `client_token` 长度不超过 64 个字符
- `callback_args` 可用于回调透传与对账追踪

## 轮询策略

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `poll-interval-seconds` | 轮询间隔 | 10s |
| `max-poll-attempts` | 轮询次数，0 代表不查询 | 0 |
| `poll-complete` | 阻塞至终态 | - |
