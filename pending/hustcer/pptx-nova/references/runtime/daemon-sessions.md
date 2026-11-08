# Agent Sessions —— daemon、stdio JSON-RPC 与 MCP

> 一次 `xdoc pptx apply` 要做完整四件事：起进程 → 读 PPTX zip → 解 OOXML 模型 →
> 应用 patch + 序列化输出。多步 Agent 工作流（典型："inspect 看现状 → apply 改
> 标题 → inspect 验证 → apply 改颜色 → ..."）反复重复前三步是浪费。daemon 把
> 模型留在内存里，让后续调用按 session 复用。
>
> 当前 runtime 的 daemon 默认自动拉起（auto-spawn）：不再需要手动 `xdoc daemon start`，
> 任何带 `--daemon` 的 `pptx apply|inspect` 调用在检测到 daemon 未运行时会
> 自动 fork 一个 detached daemon 进程并等其就绪。下面所有命令直接加 `--daemon`
> 就行。

## §0 先选 transport

CLI、daemon、JSON-RPC 和 MCP 是同一 PPTX 业务能力的不同 adapter，不应各自复制
patch 语义或验证规则：

| 场景                                           | 推荐边界        | 原因                                                   |
| ---------------------------------------------- | --------------- | ------------------------------------------------------ |
| 单命令、CI phase、普通 skill runner            | 一次性 CLI      | 进程/文件边界清楚，失败隔离最好                        |
| shell 驱动的多轮 inspect/apply                 | CLI `--daemon`  | 保留现有命令形态并复用 deck session                    |
| Agent host 已持有长生命周期子进程              | `xdoc json-rpc` | stdio NDJSON，免端口/state-file 协调，直接复用 session |
| MCP client（Claude Code / Cursor / Inspector） | `xdoc mcp`      | 标准 MCP over stdio，客户端已有 tool 发现与调用机制    |

不要仅凭 `json-rpc` 命令存在就实现 host。先在连接中调用 `xdoc.capabilities`，
或从 `xdoc schema` / `cli/runtime/probe.mjs` 的 `capabilities.agentTransports.jsonRpc`
读取完整 `xdoc-json-rpc-contract/v1`；协议版本未知时保留原始内容并 fail closed。
daemon 也遵循同一原则：从
`capabilities.agentTransports.daemon.contract` 读取当前 runtime 的完整公开契约，
不要只看兼容索引里的 `defaults` / `environment` / `subcommands`。
MCP host 必须先确认 `capabilities.agentTransports.mcp.status == "disclosed"`，再读取
`capabilities.agentTransports.mcp.contract` 的完整协议版本、方法、结果编码与安全边界；
未知 `schemaVersion` 时保留原始合同并 fail closed，不要只凭 `mcp` 命令存在就启用。

## §1 起手最短路径

```bash
# 直接用 — daemon 未运行时会自动拉起；启动耗时取决于环境
xdoc pptx inspect deck.pptx --daemon --json > inspect.json

# 状态查询 / 显式关闭（status / stop 不会触发 auto-spawn）
xdoc daemon status --json
xdoc daemon stop
```

如果你仍然偏好显式拉起（CI 里用 `trap` 清理、或想一次写好日志路径），手动
`xdoc daemon start` 仍然可用：

```bash
xdoc daemon start &           # 前台进程，& 放后台
nohup xdoc daemon start >/tmp/xdoc-daemon.log 2>&1 &
```

但**绝大多数 Agent 场景下不需要显式 start** —— auto-spawn 已经接管。

## §2 客户端用法

任意 `pptx apply` 或 `pptx inspect` 调用加 `--daemon`（auto-spawn + 优雅回退）
或 `--daemon-strict`（auto-spawn 失败时硬错而不是 fallback）：

```bash
# 默认模式：auto-spawn + 失败 fallback 到一次性
xdoc pptx inspect deck.pptx --daemon --json > inspect.json

# 严格模式：CI / 脚本里防止"误用一次性、看不出来"；auto-spawn 失败也直接 DaemonUnavailable
xdoc pptx apply -p patch.json -i deck.pptx -o deck.pptx --daemon-strict --overwrite
```

⚠️ **`--daemon` 只对 `pptx apply` / `pptx inspect` 生效**。`pptx new` / `pptx select`
会在解析阶段报 `xdoc pptx --daemon is only valid with apply or inspect`；
`pptx preview` / `slide-copy` / `extract-style` / `import-template` / `refurbish-skin` /
`morph-check` 报 `does not accept --daemon/--daemon-strict`。其余 action
（`chrome-detect` / `chrome-remove` / `chrome-apply` / `remap-theme` / `template-fill` /
`check-brand` / `catalog` / `recipe` / `replay|audit|rollback` / i18n 系列等）当前
会静默忽略该 flag 并按一次性进程执行，不要指望它们复用 session。

session 按 filesystem identity 键化，而不是只比较 path 字符串。现存文件优先使用
device/inode（Windows 为 volume/file-index）身份；可证明指向同一对象的 symlink、
hard link，以及主机文件系统规则下等价的大小写/分隔符 alias 会共享同一份内存
Presentation。无法取得对象身份时使用解析后的 lexical identity；只有在目标目录已
证明大小写不敏感时才折叠大小写。

同一 session 的 `inspect` / `apply` 按进入顺序 FIFO 串行，不同 filesystem-identity
session 可以并发执行：

- `inspect` 可复用同 revision、精确输入字节及路径绑定的报告；冷 inspect 仍要构建完整模型，
  大报告还受缓存预算与传输开销影响，不能承诺每次几乎零成本。
- `apply` 使用 session 保留的原始读取字节或最近一次交付字节创建候选，失败时不污染
  live session；成功后同时更新 Presentation 和交付字节，避免重新序列化改变输入身份。
  dry-run 不交付候选。当前 runtime 会检查磁盘字节，外部原地改写（即使 inode 不变）
  也会使旧模型/报告失效并重新加载；不要把 live session 当作永远冻结的文件快照。
  保留不可变输入文件与 SHA-256 作为任务证据。

同一 deck 的多轮 inspect/apply 优先复用一个 daemon；冷 inspect 并发受工作锁约束，
不要靠并行重复读取同一大文件提速。缓存命中可绕过冷工作锁，基线审计只复用精确
输入，候选仍完整检查。协作式执行让状态查询保持响应，不改变 FIFO、失败原子性或
已开始 mutation 的取消保护；不把本机性能测量当作跨机器延迟保证。
长文本交互可在当前 `pptx.apply` 合同披露后选用 `--detail summary`，
但需要完整前后值的门禁继续使用默认 `full`；见 `schema-discovery.md#apply-report-detail`。
派生 inspect/baseline 缓存随所属 session 淘汰、替换或部分发布失效一起释放；成功提交也使
旧 inspect 报告失效。无输入的新建 apply 不占用输入 baseline 缓存。保留磁盘证据与普通
重开路径，不将缓存生命周期或命中情况当成正确性门禁，也不为清缓存重放 mutation。

CLI、JSON-RPC 和 MCP 的 patch 都拒绝重复 key，包括转义后名称相同的 key。
保留完整原请求、原始 PPTX 字节和相对资产解析上下文；默认值补齐及资源物化后的
执行内容不能代替原提交内容。重试应复用同一次读取的资产快照，不能因同名文件已
被替换而悄悄改用新内容。

## §3 关键环境变量

| 变量                           | 默认                             | 含义                                                              |
| ------------------------------ | -------------------------------- | ----------------------------------------------------------------- |
| `XDOC_DAEMON_AUTO_SPAWN`       | `1`                              | `0` / `false` 关闭 auto-spawn；CI/sandbox 隔离用                  |
| `XDOC_DAEMON_SPAWN_TIMEOUT_MS` | `5000`                           | auto-spawn 后等 daemon 就绪的最长时间（毫秒）                     |
| `XDOC_DAEMON_LOG`              | `$TMPDIR/xdoc-daemon.log`        | auto-spawn 出来的 daemon stdout/stderr 合并日志路径               |
| `XDOC_DAEMON_PORT`             | `0`（随机端口）                  | data endpoint 端口；host 固定为 IPv4 loopback `127.0.0.1`         |
| `XDOC_DAEMON_STATE`            | `$TMPDIR/xdoc-daemon-state.json` | 状态文件路径（含 data/control port + token）；lock 自动加 `.lock` |
| `XDOC_DAEMON_IDLE_MS`          | `300000`（5 分钟）               | 单个 session 空闲多久后淘汰                                       |
| `XDOC_DAEMON_MAX_SESSIONS`     | `64`                             | 同时常驻的 session 上限（LRU 淘汰）                               |
| `XDOC_DAEMON_MAX_CONNECTIONS`  | `64`                             | data plane active connection 上限；control endpoint 不计入        |

跨平台 temp 目录探测顺序：`TMPDIR` → `TEMP` → `TMP` → `LOCALAPPDATA`（Windows）。

> ⚠️ token 用 `BCryptGenRandom`（Windows）/`arc4random_buf`（Apple/BSD）/
> `getrandom`（Linux）/`/dev/urandom`（fallback）生成，不是时间戳，不会被预测。
> state 文件写入用 `.tmp.<random>` + atomic rename，删除用 `.removed.<random>` +
> delete，避免 TOCTOU，所以可以放心放在 `$TMPDIR`。
>
> auto-spawn 的并发安全靠 `<state>.lock` 文件 + `CreateMode::CreateNew`（=
> `O_CREAT|O_EXCL`）选出单一赢家；lock 内容 `{pid, deadlineMs, startedAtMs}`，
> stale 判定 = deadline 已过 OR 文件中 pid 不再存活（`kill(pid,0)` 探测）。

## §4 并发、端点与生命周期契约

daemon state 同时发布 `port`（data plane）和 `controlPort`（control plane）：

- data plane 承载 `ping` / discovery / schema / `pptx.inspect` / `pptx.apply`。
  每个 TCP connection 只承载一个 newline-delimited JSON request；active connection
  受 `maxConnections` 限制，饱和时后续连接留在 kernel listen backlog，不进入无界
  application queue。data frame 上限为 67,174,400 bytes。
- control plane 独立、顺序处理 `status` / `shutdown`，不占 data admission，因此 data
  plane 满载时仍能查询状态或关闭。control frame 上限为 65,536 bytes，读取超时
  1,000 ms，避免 partial client 长时间占住生命周期操作。

session registry 只短暂持锁。进入 session FIFO 的请求持有 active lease；leased
session 不会被 idle/LRU pruning 淘汰。PPTX 与 sidecar publication 也先预留身份，
避免并发输出路径互相覆盖或把别的 session 的缓存静默当成当前结果。

`xdoc daemon status --json` 当前返回 `xdoc-daemon-status/v2`，除两个端点和连接上限外，
还暴露：

- `activeConnections`：尚未完成 handler 的已接收 data connection
- `activeMutations`：已取得 session FIFO、进入 protected mutation 的 apply 数
- `mutationStartedCount` / `mutationCompletedCount`：daemon 启动后的累计 mutation
  进入/释放计数

累计计数不是 per-mutation id。只有在没有无关 apply 的受控 probe 中，跨 snapshot
比较计数差值，才能证明先前 active mutation 仍在途；普通并发环境不要靠它识别“同
一个 mutation”。

shutdown 先关闭两个 listener，对尚未 dispatch 的业务请求返回 `shutting_down`，再
排空所有已 accepted handler；已经进入 mutation 的请求不会被抢占。同 revision 旧
daemon 仍在 drain 时，新 auto-spawn/readiness 会保持 `shutting_down` 并 fail closed，
应等待排空后重试，不要手删 state 文件或并行拉起替代进程。

## §5 与 dry-run / sidecar 的关系

daemon 不改变 patch 语义，只改变执行链路：

- `--dry-run --json` 在 daemon 模式下同样工作，且更快（共用 in-memory model）
- 写盘时 sidecar 文件 `<out>.xdoc.json` 照常生成，后续 `rollback --from-sidecar`
  不依赖 daemon
- `apply` 失败时 live session 不变，可以接着 inspect 看当前状态；这不保证所有磁盘输出
  未变。晚期 sidecar 失败与 one-shot 一样披露 `primaryOutputPublished:true`、
  `outputUntouched:false`、已发布的 `output` 和失败的 `blockedOutput`（未知时可为 null）。
  主 PPTX 与 sidecar 不是联合原子事务；先读报告和磁盘，不自动重放 mutation 或补 `--overwrite`。
- sidecar 不得与输入或主 PPTX 指向同一文件；已有 sidecar 需要覆盖授权。
  同样适用 `../common-workflow.md` 的输出安全和 `troubleshooting.md` 的部分发布恢复流程。
- **agent schema 渲染缓存**：daemon 启动时会预热一次 `xdoc schema` 的 JSON
  渲染（多 KB / 多结构），后续每次 schema 取用从 in-memory 缓存深拷贝返回。
  Agent 反复拉 `--mode index` / `--mode ops --ops <name>` / 切 `--minimal` 都不会再付重新构建
  schema 的成本

## §6 典型 Agent 多步工作流

### 6.1 inspect-driven 修改（典型 Agent loop）

```bash
# 注意：不再需要 daemon start！第一次 --daemon 调用自动拉起
xdoc pptx inspect deck.pptx --daemon --json > inspect.json

# Agent 根据 inspect 生成 patch1.json（改主标题文字）
xdoc pptx apply -p patch1.json -i deck.pptx -o deck.pptx --daemon --overwrite --dry-run --json > dry1.json
xdoc pptx apply -p patch1.json -i deck.pptx -o deck.pptx --daemon --overwrite

# 第二轮：验证 + 下一步（命中已在内存中的 session，秒回）
xdoc pptx inspect deck.pptx --daemon --json > inspect-after.json
# ... 多轮修改 ...

# 可选：完事后关 daemon；不关也行，5 分钟 idle 后 session 自动淘汰
xdoc daemon stop
```

### 6.2 批量场景：同一模板上反复 apply / inspect

```bash
# 注意：template-fill 上 --daemon 不生效（被忽略）。批量数据驱动场景仍是一次性进程
for data in data/*.json; do
  out="dist/$(basename $data .json).pptx"
  xdoc pptx template-fill $data --template template.pptx -o $out --overwrite
done

# 但如果你的批量是"反复改同一个 deck"，daemon 收益巨大：
for patch in patches/*.json; do
  xdoc pptx apply -p $patch -i deck.pptx -o deck.pptx --daemon --overwrite
done
```

### 6.3 CI / 自动化测试

CI 里用 `--daemon-strict`，保证测试确实走 daemon transport 而不是一次性 fallback；
需要证明 session reuse 时，再结合 status/sessionCount 或受控时序证据。用 `trap`
清理后台 daemon：

```bash
trap 'xdoc daemon stop >/dev/null 2>&1' EXIT
# 第一个 --daemon-strict 调用会触发 auto-spawn，失败直接报错
xdoc pptx inspect deck.pptx --daemon-strict --json >/dev/null
# ... 跑测试 ...
```

### 6.4 sandbox / 不允许 fork 的环境

某些容器 / sandbox 禁止子进程；这种环境关闭 auto-spawn 强制走一次性：

```bash
export XDOC_DAEMON_AUTO_SPAWN=0
# 此后 --daemon 在 daemon 不在时直接 fallback（不再尝试 fork）
# --daemon-strict 在 daemon 不在时直接 DaemonUnavailable
```

## §7 不要做的事

- **不要把正确性建立在 idle session 永不淘汰上** — active lease 期间不会被淘汰，
  但空闲 session 仍受 5 分钟 timeout 和 64-session LRU 上限约束。需要严格任务隔离
  或独立证据时，为任务使用不同 `XDOC_DAEMON_STATE`，或退回一次性 CLI
- **不要把生命周期累计计数当作 mutation id** — 它们只适合无无关 apply 的受控
  overlap probe；普通并发状态只能说明 aggregate lifecycle
- **不要假设 session 长时间常驻** — `XDOC_DAEMON_IDLE_MS` 默认 5 分钟，Agent 工作流
  之间有长时间停顿时模型已经被释放，下一次调用会重新加载（行为正确，但失去
  加速）
- **不要在 daemon 模式下手动覆写 `<out>.xdoc.json`** — sidecar 由 apply 路径自己
  写；手动改会让 rollback 失败
- **不要给 `apply` / `inspect` 以外的 action 加 `--daemon`** —
  `new` / `select` / `preview` / `slide-copy` / `extract-style` / `import-template` /
  `refurbish-skin` / `morph-check` 在解析阶段会拒绝，其它 action 只会静默忽略
- **Windows 上 daemon 仍在 MVP** — macOS/Linux 已稳定，Windows 路径走 `TEMP` /
  `TMP` / `LOCALAPPDATA` fallback，但 CI 覆盖还不全。生产 CI 用 Windows 时建议
  先用一次性模式跑通，再切 daemon

## §8 stdio JSON-RPC host contract

启动 `xdoc json-rpc` 后，stdin/stdout 都是逐行 UTF-8 JSON-RPC 2.0；每 frame 最大
8 MiB，stdout 只能出现 protocol frame，日志和进程诊断只读 stderr。无 initialize
握手，EOF 会在当前同步请求返回后干净退出。当前 server 串行执行并提供 backpressure，
不要在 host 侧假设并行 mutation。

最小会话：

```text
{"jsonrpc":"2.0","id":1,"method":"xdoc.ping","params":{}}
{"jsonrpc":"2.0","id":2,"method":"xdoc.capabilities","params":{}}
{"jsonrpc":"2.0","id":3,"method":"xdoc.schema","params":{"mode":"index"}}
{"jsonrpc":"2.0","id":4,"method":"pptx.inspect","params":{"inputPath":"/abs/deck.pptx"}}
{"jsonrpc":"2.0","id":5,"method":"xdoc.shutdown","params":{}}
```

公开方法以返回契约的 `methods` 为准。若本次 runtime 披露 `schemaDiscovery`，
按其中的 method/params 在同一连接获取完整 schema，以 `valuePointer` 指向的
值作为 JSON Pointer fragment 引用的解析根；不需要另起 CLI 进程。
`xdoc.schema` 复用渐进披露，默认 `mode=index`，需要操作细节时请求 `mode=ops`。
调用前以该 method 的 `paramsSchema` 校验参数；完整 patch、报告与 intent 契约
通过 apply 的相应 `*SchemaRef` 解析。旧 runtime 未披露时不要猜测可用入口。

`pptx.apply` 的 `patch` 是对象；非 dry-run 时必须给
`outputPath`。mutation 与 shutdown 必须带 request id，发送成 notification 会被
忽略且不修改 deck。普通 notification 永远没有 response。

当本次契约披露 `intentSchemaRef` 时，apply 可接收一个可选 `intent` JSON 对象。
按解析后的现有 Feature Intent schema 构造完整对象：Feature/output 必须匹配实际
动作（apply 无输入为 create、有输入为 modify，输出为 pptx）。该字段不接收路径或
JSON 字符串，也不能改用内部 `intentJson` 或独立的授权布尔参数。未提供 intent
时沿用默认求解；dry-run 仍校验显式 intent，成功不代表真实写入已获得授权。

返回 value 包在 `xdoc-json-rpc-result/v1`（`method` / `exitCode` / `value` /
`artifacts`）中；二进制不会进入 stdout，产物通过 artifact ref 报告。传
`progressToken` 可收到 `$/progress` 的 begin/end notification，但没有百分比保证。
`$/cancelRequest` 只会取消队列中尚未 dispatch 的同 id 请求，不能中断当前同步方法。
batch 也按顺序执行，并在 progress notification 之后返回一个 response array。

需要验证返回值时，通过同一连接的 `xdoc.schema`、`mode=full` 解析
`resultEnvelope.schemaRef`、方法的 `reportSchemaRef` 与 `errorDataSchemaRef`；
分别检查协议 envelope 和内部业务 report，不能只验证外层就认定操作成功。
`-32602` 参数错误的 `data.details.field` 是相对公开参数的 JSON Pointer：
apply 的字段从 `/patch` 或 `/intent` 开始，MCP 则从 `/arguments/patch` 或
`/arguments/intent` 开始；保留原始指针，不自行补 `/params`。

这是 Agent transport，不是替代 skill 的验证阶段。普通 runner 仍应保持 dry-run、
apply、post-apply inspect 与证据 gate 的因果顺序；host 只替换调用 adapter。

## §9 MCP client（`xdoc mcp`）

如果宿主本身就是 MCP client（Claude Code、Cursor、MCP Inspector），不需要自己写
JSON-RPC adapter：`xdoc mcp` 直接提供标准 MCP over stdio。配置形状固定，没有选项：

```json
{ "mcpServers": { "xdoc": { "command": "xdoc", "args": ["mcp"] } } }
```

启动前用本次运行生成的 capability snapshot 确认 MCP 已公开，并按完整
`capabilities.agentTransports.mcp.contract` 配置 client。成熟 MCP SDK 会处理协议
协商；自定义 host 必须遵守合同中的 `protocolVersions`、`methods`、`framing`、
`resultEncoding` 和 `security`：现代 era 无 initialize 且每请求携带其要求的 `_meta`；
2025 era 先 `initialize` 再发 `notifications/initialized`，初始化完成前仅允许 `ping`；
一条连接只能进入一个 era，2024 revision 不受支持。不要把这些规则从版本号猜出来。

只使用当前 `contract.tools[]` 公开的 tool。已批准的 runtime 当前公开以下三个，细粒度
操作仍在 `pptx_apply.patch.ops[]` 里：

| tool           | 用途                                                                |
| -------------- | ------------------------------------------------------------------- |
| `xdoc_schema`  | 渐进获取 patch operation schema（等价 `xdoc schema` 的 disclosure） |
| `pptx_inspect` | 只读结构化 report（`pptx-inspect/v1`）                              |
| `pptx_apply`   | 创建/编辑 deck，支持 `dryRun` 与 `overwrite`                        |

用它时有五条必须记住：

- `xdoc_schema` 默认 `mode=index`。`mode=full` 包含完整合同，体积随 runtime 变化；
  只在确实需要时请求，通常优先用 `mode=ops` + `ops:[...]` 获取目标操作。
- **传绝对路径**。相对路径是相对 `xdoc` 子进程的工作目录，不是 client 的。
- `isError: true` 是**业务失败**，不是 JSON-RPC transport error。完整
  `xdoc-mcp-tool-result/v1` envelope 的位置由 `contract.resultEncoding` 决定：支持的 era
  放在 `structuredContent`，`2025-03-26` 则放在 `content` 的紧凑 JSON 中；从 envelope
  的 `value` 读取完整 xdoc report。只有实际存在的 `remediation` 才进入修复分派；
  核对 kind、完整 shape、自己保有的请求/文档摘要与冻结的资源上下文后重新校验和授权。
  `remediationUnavailable` 保留诊断，不允许跳过匹配；流程见 `troubleshooting.md`。
- 产物通过 artifact ref 返回（`path` / `state`）；deck 字节永不进协议通道。
  `dryRun` 的 artifact 是 `planned`，文件并不存在。
- `overwrite` 默认 false，已存在的输出会得到 `output_exists`。annotations 只是 hint，
  真正的防护是服务端检查。

若 `tools/list` 的 `pptx_apply.inputSchema` 披露可选 `intent`，按该 schema 传完整
JSON 对象，遵守 §8 的 Feature/output 绑定；不传文件路径、JSON 字符串、`intentJson`
或三个独立布尔便捷字段。对象由 runtime 的既有 intent 校验器和授权求解器处理，
不能声明 host 实测事实。CLI 仍只在单 action schema/help 披露时接收授权选项，
`--intent` 与三个便捷开关互斥；CLI dry-run 同样校验意图，但不发布产品。

与 §8 同理：这是 transport，不替代 skill 的验证阶段。dry-run → apply →
post-apply inspect → 证据 gate 的因果顺序不变。

## §10 故障排查

| 现象                                       | 排查                                                                                                               |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| `--daemon` 看着没加速（每次还是慢）        | `xdoc daemon status --json` 看 `status: running` 与 `sessionCount`；session 是否被复用                             |
| auto-spawn 超时 `daemon spawn timeout`     | 磁盘慢或父目录权限问题？看 `$TMPDIR/xdoc-daemon.log`；调大 `XDOC_DAEMON_SPAWN_TIMEOUT_MS`                          |
| `--daemon-strict` 报 "no daemon reachable" | auto-spawn 被关了？检查 `XDOC_DAEMON_AUTO_SPAWN`；或子进程 fork 被沙箱拒绝                                         |
| inspect 返回旧数据                         | 上次 apply 没成功导致 session 没更新；`xdoc daemon stop` + 再 inspect 触发重载                                     |
| `status: stale` / revision 不匹配          | 用 `xdoc daemon stop` 让 runtime 安全退役旧 state/daemon，再由下一次 `--daemon` 自动拉起；不要手删 state 文件      |
| `shutting_down`                            | 同 revision daemon 正在 drain；等待 accepted handler 排空后重试。不要手删 state，也不要并行 auto-spawn replacement |
| data plane 饱和或 ping 排队                | 看 status v2 的 `activeConnections` / `maxConnections`；`status` / `stop` 应仍经独立 `controlPort` 可达            |
| mutation overlap 证据不稳定                | 先排除无关 apply；累计 started/completed 不是 mutation id，只在受控 probe 中结合 `activeMutations` 判断            |
| token 不匹配 / 权限拒绝                    | 先保留 `status --json` 与日志证据，再执行 `xdoc daemon stop`；若仍失败，切一次性 CLI 并报告，不要手删 state 文件   |
| lock 文件残留（`<state>.lock`）            | auto-spawn 进程崩了；下次 `--daemon` 会自动判 stale（deadline 过 OR pid 死）并重抢                                 |
| 内存占用涨                                 | 检查 session 数（`status --json`）；把 `XDOC_DAEMON_MAX_SESSIONS` 调小，或主动 `daemon stop`                       |
| daemon stdout/stderr 看不到                | auto-spawn 出来的 daemon 输出在 `XDOC_DAEMON_LOG`（默认 `$TMPDIR/xdoc-daemon.log`）                                |
