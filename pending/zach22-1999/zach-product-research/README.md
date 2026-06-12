# zach-product-research

> **作者**：Zach ｜ 公众号「Zach的进化笔记」
>
> Learn in public！用 Sorftime 做结构化选品分析，输出市场调研结论和可复核数据。

基于 **Sorftime MCP** 的选品分析 Skill，帮助发现高潜力市场机会、验证竞争格局、测算投入产出。

## 推荐安装方式：让 AI 帮你装

推荐在以下 IDE 中直接用自然语言安装：

- Claude Code
- Codex
- Cursor

把下面这句话直接发给你的 AI：

```text
帮我安装 `zach-product-research` 这个 skill，来源仓库是 `amazon-skills`。直接装到当前工作区，并把依赖一起检查好。
```

手动安装仍然保留，但只作为降级方案：
[../../docs/manual-install.md](../../docs/manual-install.md)

## 它能做什么

这个 Skill 不只是“查几个数据”，而是把一轮完整的市场调研拆成了可以复用的流程。

1. **先找市场**
   它会从类目、关键词、潜力产品三个入口开始，先判断你给的产品词到底有没有独立市场，还是混在别的需求池里。
2. **再看竞争格局**
   它会拉 Top100、看品牌集中度、价格带、评论门槛、新品渗透情况，帮你判断这个市场是拥挤、垄断，还是还有结构性机会。
3. **再做结构化拆解**
   它会把 Top100 产品按属性维度打标，再做交叉分析，找出高需求低供给、供给稀薄或明显空白的组合。
4. **再看消费者真实痛点**
   它会结合差评、关键词和竞品信息，判断用户到底在抱怨什么，哪些点只是“看起来合理”，哪些点是真需求。
5. **最后给出 Go / No-Go**
   最终不是只给你一堆表格，而是会输出进入壁垒评估、机会优先级、产品矩阵建议和明确的 Go / No-Go 结论。

## 你最终会拿到什么

- 一份可读的 Markdown 市场调研报告
- 一份适合快速浏览和分享的 HTML 精简报告
- 一份可交叉核查数据的 Excel 多 Sheet 文件
- 一份可视化 Dashboard 看板
- 一组原始和中间 JSON 工件，方便你继续二次分析

## 前置条件

- **Sorftime MCP 已配置并启用**

## 使用方法

直接对 AI 说：

```text
帮我用 Sorftime 分析一下美国站蓝牙耳机的选品机会。
```

或者使用 skill 命令：

```text
/zach-product-research laptop backpack US
```

## 主要 Sorftime MCP 工具

- `search_categories_broadly`
- `category_search_from_product_name`
- `category_report`
- `potential_product`
- `keyword_search_results`
- `keyword_detail`
- `product_detail`
- `product_reviews`
- `ali1688_similar_product`

## 输出

- 市场调研报告 Markdown
- 精简 HTML 报告
- 多 Sheet Excel 数据文件
- 原始和中间 JSON 数据

## 生成与校验脚本

Skill 自带渲染与校验脚本：

```bash
python skills/zach-product-research/scripts/render_deliverables.py all --input payload.json
```

Windows 用户如遇编码或路径问题，可参考：
[scripts/WINDOWS_USAGE.md](./scripts/WINDOWS_USAGE.md)

## 如果安装或运行出错，直接让 AI 帮你排查

把下面这段直接发给你的 AI，并把报错信息、截图或终端输出一起贴上：

```text
我已经安装了 `zach-product-research`，但现在遇到了问题。请你直接帮我排查并尽量修复：

1. 先判断是 skill 文件缺失、依赖缺失、Sorftime MCP 未连接、路径错误，还是当前 IDE 没有正确加载
2. 自动检查当前工作区里和 `zach-product-research` 相关的文件、配置、脚本和依赖
3. 如果可以自动修复，就直接修复
4. 修复后告诉我还需要重启 IDE、重新加载工作区，还是重新运行哪个命令
5. 最后给我一个最短的验证步骤，确认这个 skill 已经能用了
```

## 关于作者

关注「**Zach的进化笔记**」，获取 AI x 跨境电商的实战经验、工具和方法论：

<img src="../../assets/traffic/wechat-official-account.jpg" width="200" alt="公众号二维码" />

扫码加入交流群，一起交流 AI + 跨境电商的实战玩法：

<img src="../../assets/traffic/wechat-group.jpeg" width="200" alt="交流群二维码" />
