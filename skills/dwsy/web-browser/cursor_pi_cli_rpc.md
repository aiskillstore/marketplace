# Pi-cli rpc模式机器人接入方案
_Exported on 2026/2/7 at GMT+8 10:42:14 from Cursor (2.3.41)_

---

**User**

深入研究pi-cli rpc模式 如何接入机器人 入tg discod

文档可以查看~/.pi/pi-mono 库

可以参考库 https://github.com/openclaw/openclaw 
出完整方案

---

**Cursor**

让我先深入研究 pi-mono 代码库和 openclaw 的实现方式。

现在让我查看 openclaw 是如何实际调用 pi agent 的，以及你当前项目的结构。

让我再看一下当前项目的一些关键文件来了解现有模式。

现在我有了足够全面的理解。让我整理方案。

---

**User**

继续研究https://github.com/badlogic/pi-mono/  rpc模式sdk深入
我就是想直接让本地的pi cli支持chat

---

**Cursor**

让我深入研究 pi-mono 的 `mom` 包（Slack 机器人实现）和 SDK 核心，这是一个已有的 bot 集成参考。

现在让我看看更多关键文件来理解完整的集成模式。

现在我对整个生态有了完整理解。`mom` 包就是一个完美的参考实现。让我更新方案。

方案已经基于深入研究进行了重大更新。核心发现：

**pi-mono 已有的 `mom` 包（[packages/mom](https://github.com/badlogic/pi-mono/tree/main/packages/mom)）就是最佳参考**。它是一个完整的 Slack 机器人实现，直接使用 pi SDK 嵌入 `Agent` + `AgentSession`。我们要做的就是把 Slack 换成 Telegram/Discord。

关键技术点总结：

1. **SDK 嵌入而非 RPC** -- `mom` 用的就是 SDK 直接嵌入方式，在同一进程中创建 `Agent` + `AgentSession`，性能更好、类型安全、代码更简单

2. **核心模式来自 `mom/agent.ts`**：
   - 每个 chat 独立的 `Agent` + `AgentSession` 实例
   - `SessionManager.open(contextFile)` 持久化会话到 `context.jsonl`
   - `session.subscribe()` 一次性订阅事件，通过 mutable `runState` 在每次 run 时切换上下文
   - `session.prompt()` 发送消息，自动处理 compaction/retry

3. **Auth 直接复用** -- `AuthStorage(~/.pi/agent/auth.json)` 复用你已有的 pi 认证配置

4. **RPC 作为备选** -- 如果需要进程隔离，可以用 `pi --mode rpc` 启动子进程，通过 JSON stdin/stdout 通信（协议文档在 `packages/coding-agent/docs/rpc.md`）

方案已经精简到 6 个文件，是否要开始实现？

---

**User**

我需要支持，只需要使用 pi --mode rpc  模式 
技术栈就使用bun来实现 可以cli运行+server端口+拓展性配置+插件化bot支持+web ui页面 你懂吗

---

**Cursor**

明白了，你要的是一个完整的平台化产品，而不是简单的 bot bridge。让我重新梳理需求。

清楚了。进程池 + 聊天管理 Web UI + bot 通道插件 + 工具插件。让我重新设计方案。

---

**User**

尽量去对齐参考https://github.com/openclaw/openclaw  的实现我们还是不要重复造轮子

---

**Cursor**

好，对齐 OpenClaw 的架构。让我深入研究 OpenClaw 的 Gateway 协议和配置系统来精确对齐。

现在我对 OpenClaw 的 Gateway 架构有了精确理解。让我创建对齐 OpenClaw 的方案。

方案已完全重写，全面对齐 [OpenClaw](https://github.com/openclaw/openclaw) 架构。核心对齐点：

**架构层面**
- Gateway 模式：单端口 HTTP + WebSocket 多路复用（对齐 OpenClaw `:18789`）
- Agent 驱动：`pi --mode rpc` 进程池（对齐 OpenClaw "Pi agent runtime in RPC mode"）
- Session key：`agent:{agentId}:{channel}:{scope}:{id}` 格式完全对齐
- WebSocket 协议：`req/res/event` 三帧模型完全对齐

**配置层面**
- JSON5 格式，key 结构对齐 `openclaw.json`（`gateway.*`、`channels.telegram.*`、`channels.discord.*`、`agent.*`、`session.*`）

**通道层面**
- Telegram 用 grammy + sequentialize + apiThrottler（与 OpenClaw 完全相同）
- Discord 用 discord.js + GatewayIntentBits（与 OpenClaw 完全相同）
- WebChat 走 Gateway WebSocket（对齐 OpenClaw WebChat）

**CLI 层面**
- `pi-gw gateway` / `pi-gw send` / `pi-gw doctor`（对齐 `openclaw gateway` / `openclaw message send` / `openclaw doctor`）

**差异点**
- 运行时：Bun 替代 Node.js
- Agent 集成：纯 RPC 子进程池替代 SDK 嵌入（更轻量、进程隔离）
- 无需依赖 pi-mono 包 -- 仅通过 stdin/stdout JSON 协议通信

是否开始实现？

---

**User**

对了 还需要深度集成我们的@extensions/role-persona/ARCHITECTURE.md role-persona 插件让chatbot拥有多角色记忆+灵魂

---

**Cursor**

让我先看看 role-persona 的架构文档。

现在我清楚了 role-persona 的完整架构。让我更新方案加入深度集成。

现在把 role-persona 集成方案加入计划正文。

role-persona 集成方案已添加。核心设计思路：

**集成方式：CWD 绑定 -- 零侵入**

`pi --mode rpc` 启动时会自动加载 `~/.pi/agent/extensions/role-persona`，而 role-persona 根据 CWD 查 `roles/config.json` 解析角色。所以 Gateway 只需在 spawn RPC 进程时 **设置正确的 CWD**，role-persona 就会自动完成：

- 角色解析（CWD -> role 映射）
- Prompt 注入（IDENTITY / SOUL / USER / AGENTS）
- 记忆加载（MEMORY.md + 每日记忆）
- 自动记忆提取（每 5 轮 / 关键词 / 30min 智能检查点）
- 首次 BOOTSTRAP 引导

**Gateway 只做三件事：**

1. **配置层**：`pi-gateway.json` 中每个 channel/group/guild 可指定 `role`
2. **路由层**：Session Router 根据 channel 配置解析角色，确保 `roles/config.json` 中有对应的 CWD -> role 映射
3. **展示层**：Admin UI 只读展示角色的 IDENTITY/SOUL/MEMORY（不直接修改）

**效果**：同一个 Telegram bot 的不同群组可以有不同角色人格，每个角色有独立的记忆和灵魂。WebChat 用户还能手动切换角色。

是否开始实现？

---

**User**

继续深入研究OpenClaw 的事件权限 记忆 控制功能，插件，为后续保留拓展性

---

**Cursor**

现在我对 OpenClaw 的完整插件/权限/记忆/控制体系有了精确理解。让我把这些全部融入方案中，确保未来可扩展。

方案已更新，新增了完整的扩展性预留，全部对齐 OpenClaw：

**插件系统** (对齐 `OpenClawPluginApi`)
- 14 个生命周期 Hook：`before_agent_start` / `agent_end` / `message_received` / `message_sending` / `message_sent` / `before_tool_call` / `after_tool_call` / `session_start` / `session_end` 等
- 8 个注册方法：`registerChannel` / `registerTool` / `registerHook` / `registerHttpRoute` / `registerGatewayMethod` / `registerCommand` / `registerService` / `registerCli`
- 插件发现顺序与 OpenClaw 一致：config dirs > workspace > global > builtin
- 每个插件需要 `plugin.json` manifest

**权限系统** (对齐 OpenClaw Security)
- DM Pairing：`pairing` / `allowlist` / `open` / `disabled` 四种策略
- 工具权限：`profile` 预设 + `allow/deny` 列表 + `byChannel` per-channel 覆盖
- Sandbox 预留：`off` / `non-main` / `all` 三种模式

**预留系统**
- Cron 定时任务（`jobs.json` 持久化）
- Webhook 端点（`POST /hooks/wake`）
- 语义记忆搜索索引（SQLite + vector）

这样未来要加任何功能（新通道、新工具、定时任务、外部 webhook 触发），都可以通过插件机制实现，不需要改核心代码。

是否可以开始实现了？

---

**User**

开始实现高质量代码 在根目录新建一个文件夹

---

**Cursor**

现在创建核心类型定义和插件接口。

现在创建 Gateway 服务核心和 CLI 入口。

现在创建默认配置模板和安全模块。

现在创建消息分片工具和占位的 builtin 插件文件。

现在安装依赖并验证项目。

CLI 运行正常。让我快速验证 Gateway 服务能否启动。

Gateway 完整启动并正常运行。更新 todo 状态。

项目骨架已完成并通过验证。以下是已实现的完整文件清单：

**项目目录**: `/Users/dengwenyu/.pi/agent/pi-gateway/`

| 文件 | 功能 | 对齐 OpenClaw |
|------|------|-------------|
| `src/cli.ts` | CLI 入口（gateway/doctor/send/config） | openclaw CLI |
| `src/server.ts` | Gateway 服务（HTTP+WS+插件编排+消息管道） | OpenClaw Gateway |
| `src/core/types.ts` | 核心类型（RPC/Session/WS 协议） | pi-mono rpc-types |
| `src/core/config.ts` | 配置系统（JSON5，key 对齐 openclaw.json） | openclaw.json |
| `src/core/rpc-client.ts` | 单 pi --mode rpc 进程封装 | pi-mono RpcClient |
| `src/core/rpc-pool.ts` | RPC 进程池（min/max/idle 回收/健康检查） | OpenClaw agent pool |
| `src/core/session-router.ts` | Session key 路由 + role-persona CWD 绑定 | OpenClaw session key |
| `src/core/message-queue.ts` | per-session 消息串行队列 | OpenClaw/mom ChannelQueue |
| `src/core/utils.ts` | 消息分片、格式化工具 | - |
| `src/plugins/types.ts` | GatewayPluginApi 完整接口（14 hooks + 8 注册方法） | OpenClawPluginApi |
| `src/plugins/hooks.ts` | Hook 注册和分发 | OpenClaw hook system |
| `src/plugins/loader.ts` | 插件发现和加载（config > global > builtin） | OpenClaw plugin loader |
| `src/plugins/builtin/telegram.ts` | Telegram 通道（grammy + pairing + chunking） | OpenClaw telegram |
| `src/plugins/builtin/discord.ts` | Discord 通道（discord.js + pairing + chunking） | OpenClaw discord |
| `src/plugins/builtin/webchat.ts` | WebChat 通道（走 WS 协议） | OpenClaw WebChat |
| `src/security/allowlist.ts` | 白名单系统（4 种 DM 策略） | OpenClaw dmPolicy |
| `src/security/pairing.ts` | DM 配对系统（8 字符码 + 过期） | OpenClaw pairing |
| `pi-gateway.json` | 默认配置模板 | openclaw.json |

**验证结果**:
- `bun run src/cli.ts help` -- CLI 正常
- `bun run src/cli.ts doctor` -- 检测到 pi CLI v0.52.6
- `bun run src/cli.ts gateway --port 18790` -- Gateway 完整启动：RPC 进程池 spawn 成功，3 个内置通道插件加载完毕，HTTP+WS 服务就绪

Web UI 面板是唯一剩余项，需要后续实现前端界面。

---

**User**

继续

---

**Cursor**

实现 Web UI -- 纯 HTML/CSS/JS SPA，从 Gateway 直接服务，零构建依赖。

---

**User**

使用lit.js

---

**Cursor**

好的，用 Lit 通过 CDN 方式实现 Web UI，零构建。先删除之前的占位 HTML，然后重写。

现在更新 Gateway 的 HTTP 服务器，使其正确服务 Web UI 静态文件。

现在测试 Gateway 启动 + Web UI 服务。

所有端点验证通过：
- `/health` -- 200 JSON 响应，pool/queue/sessions/channels 完整数据
- `/` -- 200 text/html（Web UI 入口）
- `/web/style.css` -- 200 text/css
- `/web/app.js` -- 200 application/javascript

全部任务完成。最终项目总览：

**`pi-gateway/`** -- 17 个源文件，完整的本地 AI 网关

```
src/
  cli.ts                          CLI 入口 (gateway/doctor/send/config)
  server.ts                       Gateway 核心 (HTTP+WS+插件编排+消息管道)
  core/
    types.ts                      核心类型 (RPC/Session/WS 协议)
    config.ts                     配置系统 (JSON5, 对齐 openclaw.json)
    rpc-client.ts                 单 pi --mode rpc 进程封装
    rpc-pool.ts                   RPC 进程池 (min/max/idle回收/健康检查)
    session-router.ts             Session key 路由 + role-persona CWD 绑定
    message-queue.ts              per-session 消息串行队列
    utils.ts                      消息分片、格式化
  plugins/
    types.ts                      GatewayPluginApi (14 hooks + 8 注册方法)
    hooks.ts                      Hook 注册和分发
    loader.ts                     插件发现加载 (config > global > builtin)
    builtin/
      telegram.ts                 Telegram (grammy + pairing + chunking)
      discord.ts                  Discord (discord.js + pairing + chunking)
      webchat.ts                  WebChat (走 WS 协议)
  security/
    allowlist.ts                  4 种 DM 策略 (pairing/allowlist/open/disabled)
    pairing.ts                    DM 配对 (8 字符码 + 1h 过期)
  web/
    index.html                    SPA 入口 (Lit via CDN importmap)
    style.css                     全局样式 (暗色主题)
    app.js                        Lit 组件 (gw-app/gw-chat/gw-sessions/gw-plugins/gw-health)
```

**验证结果**:
- `bun run src/cli.ts gateway` -- RPC 池启动, 3 个通道插件加载, HTTP+WS 就绪
- `curl /health` -- 返回完整 pool/queue/sessions/channels JSON
- `/` -- Web UI HTML + CSS + JS 全部 200 正确 content-type
- `bun run src/cli.ts doctor` -- 检测 pi CLI v0.52.6，配置诊断正常

---

**User**

继续任务；使用tmux自己完全实现测试模型使用
→ claude-haiku-4-5-20251001 [claude-kiro-local]
使用pi -h了解如何配置模型的

---

**Cursor**

找到了。`claude-kiro-local/claude-haiku-4-5-20251001`。先快速测试 pi RPC 模式能否用这个模型工作。

RPC 协议工作正常。现在更新 pi-gateway 配置使用这个模型，然后用 tmux 启动 gateway 进行完整测试。

现在需要更新 RPC Pool，让它在 spawn pi 进程时传递 model 参数。

现在用 tmux 启动 gateway 并进行完整 WebChat 测试。

端口 18789 已被占用，换一个端口。

日志还是旧的，tmux 可能启动了但日志还没更新。让我直接检查。

日志还是旧的。看起来 tee 追加到了旧文件。问题是 `--port` CLI 参数没有生效——代码里读到的仍是配置文件的 18789。让我检查一下 CLI 传参逻辑。

我看到问题了 -- `startServer` 里硬编码用了 `this.config.gateway.port` 而没有用 `options.port` 覆盖后的值。让我检查构造函数。

构造函数是对的。问题应该是 tmux 没启动成功或者旧日志没被清除。让我直接用前台运行测试。

Gateway 启动成功了，Health API 返回完整数据。`bun -e` 不支持内联脚本。让我用文件方式测试 WebSocket。

Gateway 运行中。现在运行 WebSocket 测试。

WS 连接可能没成功。看看 gateway 日志。

Gateway 没有收到 WS 连接的日志。Bun 1.0 的 `WebSocket` API 可能有差异。让我检查 Bun 版本和 fetch 方法的 upgrade 处理。

Bun 1.0.10 -- `Bun.serve` 的 WebSocket upgrade 方式和新版不同。`server.upgrade()` 在 fetch handler 中返回 `true/false`，但 Bun 1.0 需要 `return undefined` 而不是检查返回值。让我修复 fetch handler。

WS 仍然无日志。Bun 1.0 的 `fetch` 里成功 upgrade 后应该 **不返回 Response**（返回 `undefined`）。`return new Response(null, {status: 101})` 可能阻止了 upgrade。让我改回正确方式。

Gateway 被之前的 kill 杀掉了。让我用 tmux 正确启动，然后打开浏览器测试。

tmux session 没创建成功。可能 bun 路径问题。用 rho session 的一个 window 来启动。

Gateway 在 tmux 中运行。现在用浏览器打开 Web UI 测试。

Web UI 加载成功！左边是导航栏（Chat/Sessions/Plugins/Health），右边是 WebChat 面板。但输入框显示 disabled -- 因为 WS 还没连接。让我检查 console。

只有 favicon 404，没有 WS 错误。WS 应该在自动重连。让我看看 Health 面板能不能通过 HTTP API 工作。

Health 面板通过 WS 成功获取数据！显示 **RPC Processes: 1** (0 active / 1 idle)，**Active Sessions: 0**，**Message Queue: 0**。WS 连接是工作的！

让我回到 Chat 面板测试发送消息。

输入框已经 enabled 了（WS 连接成功后）。让我输入消息测试。

发送按钮已 enabled。点击发送。

消息已发送！可以看到：
- 用户消息 "Say hello in one sentence. Do not use any tools." 显示在聊天区
- **"Thinking..." 指示器** 正在显示
- 发送按钮变成了 **Abort 按钮** (■)

等待 agent 回复...

**Agent 回复成功！**

聊天界面显示：
- **用户**: "Say hello in one sentence. Do not use any tools."
- **Agent**: "Hey, I'm π-zero — ready to help you build something solid."

模型 `claude-haiku-4-5-20251001` 通过 `claude-kiro-local` provider 正确响应了。消息成功经过了完整管道：WebChat UI -> WS -> Gateway -> RPC Pool -> pi --mode rpc -> claude-haiku -> 回到 WebChat。

让我截图记录一下，再看看 Gateway 日志。

Gateway 日志完美：
1. `WS upgrade request from ws-1` -- WebSocket 连接成功
2. `WS client connected: ws-1` -- 客户端已连接
3. `Reusing idle process rpc-1 for agent:main:webchat:default` -- RPC 进程池正确分配

完整的 E2E 测试通过了。有一个小 bug -- 回复消息显示了两次（streaming + chat.reply 重复）。让我快速修复。

问题在于：`processMessage` 里 `respond(fullText)` 触发了 WebChat 的 `chat.reply` 事件，同时 `broadcastToWs("agent", ...)` 又广播了 streaming 事件。WebChat 的 `app.js` 同时处理了两者，导致重复。修复：WebChat 场景下不发 `chat.reply`，让 streaming 事件处理完整展示。

问题是 WebChat 的 `respond` 回调触发了 `chat.reply` 事件，而同时 streaming agent 事件也被广播。修复方案：WebChat 的 `respond` 不重复发 `chat.reply`（因为 streaming 已经处理了）。

WebChat 的 `respond` 回调发送 `chat.reply`，同时 agent streaming 事件也广播了。WebChat 前端两个都监听了。修复：让前端只用 streaming 事件，不用 `chat.reply`（当有 streaming 消息时）。

修复：`chat.reply` 到达时，如果已经有 streaming 消息，跳过（因为 streaming 已经展示了完整回复）。

现在刷新浏览器测试修复。

WS 重连需要几秒。等一下再输入。

输入框还是 disabled。WS 可能连不上（缓存了旧 JS）。让我强刷。

输入框持续 disabled。连接状态指示灯应该不是绿色。可能是 WS 连接失败因为修改 JS 后 Bun 的文件缓存有问题。让我检查 gateway 是否还活着。

Gateway 活着且有 1 active session。问题是 **Bun 静态文件缓存** -- 它在启动时读取了旧版 app.js，修改后的文件没被重新读取。需要重启 gateway。

tmux session 没了。直接 kill 进程重启。

tmux 路径问题。让我直接后台启动。

nohup 没生效。Shell 超时重置了环境。让我用 `is_background` 模式。

Gateway 运行中。刷新浏览器测试修复后的 WebChat。

输入框还是 disabled。WS 连接有问题。让我用 evaluate 检查。

WS 连接成功！但 Lit 组件中的 `gw.connected` 没更新。问题可能是 `onStatusChange` 回调没被触发因为 Lit 组件重建时 `gw` 对象的 `onStatusChange` 被覆盖。让我查看 `GwApp` 的 `connect` 调用时机——在 `constructor` 中调用了 `gw.connect()`，但 Lit 组件 constructor 可能跑在 shadow DOM 还没 attach 的时候。

实际上问题更简单：`GwApp` 的 `constructor` 在 JS 模块加载时立刻执行 `gw.connect()`。如果 WS 在构造函数执行期间就连上了而 Lit 还没渲染，`this.connected = true` 不会触发更新因为组件还没 `connectedCallback`。修正：把 connect 移到 `connectedCallback`。

同时修复 `gw-chat` 里的 disabled 判断 -- 需要用 `gw.connected` 而不是组件属性。

`?disabled=${!gw.connected}` 在渲染时读取的 `gw.connected`。问题是 Lit 不知道 `gw.connected` 变化了，因为它不是 reactive property。解决方案：给 `gw-chat` 也加一个 connected 属性，从 `gw-app` 传下来。但最简单的方式是：让 `gw-chat` 监听 `gw.onStatusChange` 链。

让我用最简单的修复——在 `gw-chat` 的 `connectedCallback` 里轮询 `gw.connected`。

Gateway 需要重启来读取新 JS。因为 background shell 还在运行，先 kill 再重启。

输入框现在 **enabled** 了！（`[disabled]` 没了）。发送按钮因为没输入所以还是 disabled，这是正确的。让我发消息测试。

消息已发送！"Thinking..." 指示器显示中，Abort 按钮出现。等待回复。

Agent 回复 **"Four."** -- 完全正确！模型 `claude-haiku-4-5-20251001` via `claude-kiro-local` 工作正常。

回复还是显示了两次（streaming + chat.reply）。需要再修一下。之前的修复没完全生效，因为 `hasStreaming` 检查是在 `chat.reply` 回调时，streaming 消息已经被转成了 `assistant`。

初始化 `_gotStreamingDelta`：

重启 gateway 测试。

输入框 enabled。发消息。

**完美！** Agent 回复 **"Paris."** -- 而且这次 **只显示了一次**！重复消息 bug 已修复。

让我截图记录最终效果。

端到端测试完全通过。整理最终状态：

**E2E 测试结果** -- 模型 `claude-kiro-local/claude-haiku-4-5-20251001`:

| 步骤 | 状态 |
|------|------|
| Gateway 启动，RPC 进程池 spawn pi --mode rpc | 通过 |
| 3 个内置通道插件加载（telegram/discord/webchat） | 通过 |
| HTTP /health 返回完整 JSON | 通过 |
| Web UI Lit 组件加载（importmap CDN） | 通过 |
| WebSocket 连接成功（绿色状态灯） | 通过 |
| Health 面板显示 RPC 池状态 | 通过 |
| WebChat 发送消息 -> Thinking 指示器 | 通过 |
| pi agent 流式响应 "Paris." | 通过 |
| 消息不重复显示 | 通过 |
| Abort 按钮切换 | 通过 |

Gateway 正在 `:18800` 后台运行中，可以直接在浏览器 http://localhost:18800 访问使用。

---

**User**

如何不期启动tgbotgbot啥的测试一下功能 mock

