# Use My Browser

**_[English](./README.md)_**

`use-my-browser` 是一个浏览器自动化策略 skill，适用于需要操作用户当前的浏览器会话、检查页面、承接 DevTools 上下文、调试动态应用、操作已登录网站以及从渲染后的页面中提取媒体内容的智能体；它还会教会智能体何时真正需要浏览器，以及何时应将任务路由到公共网页工具、实时 Chrome 会话、原始抓取或干净的浏览器上下文。

> [!IMPORTANT]
> 当任务本身涉及浏览器自动化，但智能体仍需要判断应使用公共网页工具、实时 Chrome 会话、原始抓取还是干净浏览器上下文时，该 skill 尤其有用。

## 为什么需要该 skill

网页任务常常看起来像是“直接打开浏览器就行”，但在实际中，它们会分化成非常不同的自动化工作：有些需要用户已经登录的 Chrome 会话，有些需要对实时 DOM 或网络请求进行 DevTools 检查，有些在干净的浏览器上下文中会更安全，还有些其实根本不需要浏览器自动化。该 skill 的存在，是为了帮助智能体更有判断地处理这类浏览器驱动任务：在有帮助时延续用户当前的浏览器状态，在猜测之前先从页面提取证据，并在尽量不打扰用户会话的前提下选择合适的层级。

## 能力

该 skill 可以帮助智能体完成以下事情：

| 能力                 | 含义                                                                                                                                            |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| 智能工具路由         | 智能体可以根据任务在公共网页搜索、处理后的读取、原始抓取、基于 shell 的抓取和实时浏览器工具之间做出选择，而不是将所有事情都强行塞进同一条路径。 |
| 实时 Chrome 控制     | 当登录状态、cookies、当前应用上下文或已选中的 DevTools 目标很重要时，智能体可以接入用户当前的 Chrome 会话。                                     |
| 基于 DevTools 的交互 | 智能体可以在动态页面上使用 DOM 读取、点击、表单填写、上传、控制台检查、网络检查、性能工具以及必要时的截图来进行检查和操作。                     |
| DevTools 交接        | 如果用户已经在 Elements 中选中了某个元素，或在 Network 中选中了某个请求，智能体就可以直接沿用那个上下文，而不是从头复现问题。                   |
| 证据优先检查         | 智能体会优先使用快照、DOM 读取、控制台输出、网络请求和直接提取，再考虑截图或重复性的 UI 交互。                                                  |
| 媒体提取             | 智能体可以直接从页面提取图片或视频 URL，检查媒体状态，并且只在确实需要像素级证据时才使用渲染后的截图。                                          |
| 并行研究             | 对于彼此独立的目标，智能体可以批量处理公共网页工作，更高效地组织多个站点之间的比较，同时避免对依赖同一可变页面状态的任务并行操作。              |
| 隔离浏览器回退       | 当任务需要干净的浏览器上下文，或者实时 Chrome 会话不可用时，智能体可以切换到独立的自动化浏览器，而不是强行通过用户当前的浏览器会话来完成一切。  |
| 站点记忆             | 该 skill 支持保存经过验证的站点级备注，例如 URL 模式、平台特征、提取策略和已知陷阱，以便在之后的会话中复用。                                    |
| 安全升级             | 智能体可以从最便宜、最可能成功的路径开始，只在必要时逐步升级，并避免在任务并不真正需要时打扰用户的实时浏览器会话。                              |

## 示例用法

按意图分组时，这些例子最容易理解：

**已登录浏览器操作**

- `将该视频发到 bilibili 上，最后一次点击留给我`
- `检查该已登录的仪表盘，不要让我再登录一次`

**网站检查与 UX 审查**

- `访问页面 https://xi-xu.me，看看它的 UX 设计怎么样`
- `比较这些公开来源，给出引用，并且只有在静态路径失败时才使用浏览器`

**社交网站与动态站点研究**

- `去抖音搜索 Xi Xu 的账号，看看他最近发了什么`
- `从该懒加载页面里提取真实的图片或视频源地址`

**DevTools 交接**

- `我已经在 DevTools 里选中了失败的请求。解释一下它为什么返回 403`
- `我已经在 Elements 里点中了坏掉的元素。找出布局为什么不对`

**并行比较工作**

- `同时研究这 5 个项目的网站，并给我一份对比总结`
- `比较这三个产品页面，告诉我它们的引导流程有什么不同`

## 安装

使用 `skills` CLI 安装该 skill：

```bash
bunx skills add xixu-me/skills -s use-my-browser
```

如果没有 Bun，可以使用 `npx`：

```bash
npx skills add xixu-me/skills -s use-my-browser
```

## 前置条件

当智能体可以通过 Chrome DevTools MCP 复用你当前的 Chrome 会话时，该 skill 的效果最好。若要进行实时浏览器自动化，请先设置 Chrome 远程调试，然后配置 MCP 服务器，使其能自动连接到正在运行的浏览器。

> [!IMPORTANT]
> 开始前请先确保 Chrome 已经在运行。否则智能体可能无法连接到当前的浏览器会话，并可能回退到一个独立的隔离浏览器会话。

在 Chrome (>=144) 中，访问 `chrome://inspect/#remote-debugging` 以启用远程调试。

![展示如何在 Chrome 中启用远程调试的截图](https://developer.chrome.com/static/blog/chrome-devtools-mcp-debug-your-browser-session/image/chrome-remote-debugging.png)

要让 Chrome DevTools MCP 服务器连接到正在运行的 Chrome 实例，请在 MCP 服务器配置中使用 `--autoConnect` 命令行参数。

你可以使用 Bun 或 npm 来运行它：

```bash
bunx chrome-devtools-mcp@latest --autoConnect --no-usage-statistics
```

```bash
npx chrome-devtools-mcp@latest --autoConnect --no-usage-statistics
```

许多智能体运行时会使用如下所示的 JSON 风格 MCP 配置：

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "bunx",
      "args": [
        "chrome-devtools-mcp@latest",
        "--autoConnect",
        "--no-usage-statistics"
      ]
    }
  }
}
```

对于 Codex，MCP 配置可以是这样：

```toml
[mcp_servers.chrome-devtools]
command = "bunx"
args = ["chrome-devtools-mcp@latest", "--autoConnect", "--no-usage-statistics"]
```

## 策略模型

该 skill 不只是一些浏览器技巧的集合。它教授的是一种浏览策略。

### 1. 在选工具前先定义成功

智能体从目标开始，而不是从工具开始。它会先判断任务是更偏重引用、交互、调试，还是依赖用户当前的浏览器状态。

### 2. 从能够成功的最低成本层开始

默认的路由模型是：

1. 公共网页搜索与页面读取
2. 处理后的内容读取
3. 用于获取源 HTML、请求头或直接资源的原始抓取
4. 实时 Chrome DevTools 会话
5. 干净的浏览器自动化

这是一个升级模型，而不是死板的阶梯。如果任务显然依赖当前已登录的浏览器状态，智能体就应该直接从实时会话开始。

### 3. 将每个结果都当作证据

每一步都应该更新计划。搜索结果、快照、请求、控制台日志和截图都是证据，而不是形式。该 skill 鼓励智能体停止重复失败策略，并在当前层级已不再提供信息时切换到其他层级。

### 4. 保护用户的浏览器会话

在使用实时浏览器时：

- 只有当当前页面状态确实是任务重点时才复用当前页面
- 否则，打开或使用一个专门的工作标签页
- 避免关闭、重新加载或劫持用户可能仍然关心的标签页
- 优先进行结构化提取，而不是侵入式交互

### 5. 优先使用一手来源，而不是二手总结

搜索用于发现。验证则应来自一手来源、官方文档、直接页面、原始响应，以及在需要时取得的实时浏览器会话证据。

## 该 skill 如何实现这些

该 skill 被拆分为一个主策略文件和一小组聚焦的参考文件：

- [`SKILL.md`](./SKILL.md)：主决策模型、安全规则、升级逻辑和示例
- [`references/tool-matrix.md`](./references/tool-matrix.md)：在公共网页、原始抓取、实时浏览器工具和干净浏览器上下文之间进行选择的路由规则
- [`references/session-playbook.md`](./references/session-playbook.md)：会话卫生、登录处理、DOM 优先提取和实时会话回退模式
- [`references/browser-recipes.md`](./references/browser-recipes.md)：具体的浏览器操作和工具映射
- [`references/site-patterns/README.md`](./references/site-patterns/README.md)：如何保存经过验证的站点特定备注，而不将猜测变成策略

这些文件共同构成了该 skill 的“调度策略”层：

- 先尝试什么
- 何时升级
- 何时切换模式
- 如何让彼此独立的研究任务保持分离
- 如何避免不必要的浏览器侵入

## 何时使用

在以下情况下使用该 skill：

- 用户想做网页研究、页面检查或浏览器交互，并且工具选择很重要
- 任务依赖当前浏览器会话、cookies 或登录状态
- 用户已经打开了相关页面、DevTools 元素或网络请求
- 目标站点是动态站点，或者强依赖反爬机制，导致静态抓取不可靠
- 任务需要 DOM、控制台、网络、性能或渲染状态等证据
- 你需要一种有意识的方法来比较多个网站或公开来源

## 何时不要使用

在以下情况下不要使用该 skill：

- 任务完全是本地的，与网页无关
- 普通的公共网页读取已经足够，不需要做浏览器层面的决策
- 用户明确表示不希望触碰他们的实时浏览器会话
- 工作完全属于隔离自动化，并且不会从实时会话路由模型中受益

## 它的不同之处

大多数面向浏览器的 skill 关注的是如何驱动浏览器，而该 skill 关注的是何时、为什么，以及应该在哪一层去做这件事。

这让它更适合那些需要判断力而不只是点击能力的智能体。

## 参考资料

- [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp)
- [Let your Coding Agent debug your browser session with Chrome DevTools MCP](https://developer.chrome.com/blog/chrome-devtools-mcp-debug-your-browser-session)

## 灵感

- [Web Access](https://github.com/eze-is/web-access)
