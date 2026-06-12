# zach-listing-health-checker

> **作者**：Zach ｜ 公众号「Zach的进化笔记」
>
> Learn in public！用真实消费者视角做 Listing 巡检和异常排查。

以真实消费者视角检查亚马逊 Listing 健康状态。

## 推荐安装方式：让 AI 帮你装

推荐在以下 IDE 中直接用自然语言安装：

- Claude Code
- Codex
- Cursor

把下面这句话直接发给你的 AI：

```text
帮我安装 `zach-listing-health-checker` 这个 skill，来源仓库是 `amazon-skills`。直接装到当前工作区，并把依赖一起检查好。
```

手动安装仍然保留，但只作为降级方案：
[../../docs/manual-install.md](../../docs/manual-install.md)

## 快速开始

```
/zach-listing-health-checker B0PUBLIC01 US YourBrand "wireless microphone, karaoke microphone"
```

## 是什么

一个纯网页抓取的 Listing 健康检查工具。不使用任何 API 或第三方数据工具，100% 模拟消费者打开亚马逊页面时能看到的内容。

## 它具体能帮你解决什么问题

这个 Skill 适合处理三类最常见但最浪费时间的场景：

1. **链接明明还在，销量却突然不对**
   它会从消费者真实可见的页面出发，检查价格、配送、Buy Box、购物车、优惠、页面可访问性这些会直接影响转化的环节。
2. **你怀疑 Listing 有问题，但不知道先查哪里**
   它会把健康检查拆成固定的检查清单，让 AI 先跑一轮完整巡检，再把异常点按优先级列出来。
3. **你想做周期巡检，而不是等出问题再救火**
   它很适合给核心 ASIN 做每周或每月例行健康检查，及时发现页面异常、差评变化和搜索可见性问题。

## 详细功能介绍

- **页面健康检查**
  检查商品页是否能正常打开，是否出现 404、狗狗页、异常跳转或页面结构缺失。
- **价格与成交条件检查**
  检查售价、优惠券、折扣、Buy Box 和 Add to Cart 状态，判断是否存在成交链路断点。
- **配送与 Prime 检查**
  检查 Prime、预计送达时间和配送信息，帮助判断是否是物流承诺影响了转化。
- **类目与 BSR 检查**
  拉取类目路径和排名，帮助你判断节点是否挂错、排名是否异常波动。
- **差评与搜索可见性检查**
  检查首页差评和目标关键词搜索结果里的曝光状态，用消费者路径验证“用户到底还能不能找到你”。

## 检查哪些内容

| # | 检查项 | 说明 |
|---|--------|------|
| 1 | 页面可访问性 | 非狗狗页面/404 |
| 2 | 价格与优惠 | 售价、折扣、优惠券 |
| 3 | 卖家信息 | Sold By 校验、Buy Box |
| 4 | 购物车状态 | Add to Cart 按钮 |
| 5 | 配送信息 | 配送时间、Prime |
| 6 | 类目与节点 | 大类 + 面包屑路径 |
| 7 | BSR 排名 | 各层级排名 |
| 8 | 差评监控 | 首页差评数量与内容 |
| 9 | 搜索可见性 | 关键词搜索结果中是否找到 |

## 使用场景

- **新品上架验收**：上架 24-48 小时后检查一切是否正常
- **日常巡检**：每周例行检查核心 ASIN
- **异常排查**：销量下降时排查链接问题

## 输出

Markdown 格式的健康检查报告，保存至：
```
outputs/listing-health-check/{品牌名}/{日期}_{ASIN}_健康检查报告.md
```

## 支持站点

US / UK / DE / FR / IT / ES / CA / JP / MX / AU

## 依赖

- Python 3 + beautifulsoup4（`pip install beautifulsoup4`）
- curl（系统自带）
- 脚本位于 `scripts/` 目录：`browser_utils.py`（通用抓取模块）、`fetch_amazon_page.py`（商品页）、`fetch_amazon_search.py`（搜索页）

## 详细文档

完整方法论见 [SKILL.md](./SKILL.md)

## 如果安装或运行出错，直接让 AI 帮你排查

把下面这段直接发给你的 AI，并把报错信息、截图或终端输出一起贴上：

```text
我已经安装了 `zach-listing-health-checker`，但现在遇到了问题。请你直接帮我排查并尽量修复：

1. 先判断是 skill 文件缺失、Python 依赖缺失、脚本路径错误、网络抓取失败，还是当前 IDE 没有正确加载
2. 自动检查当前工作区里和 `zach-listing-health-checker` 相关的文件、脚本和依赖
3. 如果可以自动修复，就直接修复
4. 修复后告诉我还需要重启 IDE、重新加载工作区，还是重新运行哪个命令
5. 最后给我一个最短的验证步骤，确认这个 skill 已经能用了
```

## 关于作者

关注「**Zach的进化笔记**」，获取 AI x 跨境电商的实战经验、工具和方法论：

<img src="../../assets/traffic/wechat-official-account.jpg" width="200" alt="公众号二维码" />

扫码加入交流群，一起交流 AI + 跨境电商的实战玩法：

<img src="../../assets/traffic/wechat-group.jpeg" width="200" alt="交流群二维码" />
