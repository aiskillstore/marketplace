# zach-feature-demand-validator

> **作者**：Zach ｜ 公众号「Zach的进化笔记」
>
> Learn in public！用真实用户证据验证一个功能点是不是值得做。

功能需求真伪验证器。

这个 Skill 不解决“我要不要做这个品类”，而是解决另一个更常见的问题：

**这个微创新功能，到底是不是用户真的在意。**

对亚马逊卖家来说，大多数产品开发都不是颠覆式创新，而是在现有市场供给上做微创新。问题也往往出在这里：功能看起来合理，不代表需求真实存在。

这个 Skill 用三维数据交叉验证：

| 维度 | 数据源 | 作用 |
|------|--------|------|
| Review 信号 | Sorftime `product_reviews` 或本地 `review_source_pack` | 看用户评论里有没有直接提到、抱怨缺失、或者对现有实现不满意 |
| 关键词信号 | Sorftime `keyword_detail` / `keyword_trend` / `keyword_extends` | 看用户有没有主动搜索这个功能 |
| 社区信号 | WebSearch（Reddit + Quora） | 看用户在购买前有没有讨论这个功能 |

## 它具体能帮你解决什么问题

这个 Skill 解决的不是“大盘值不值得做”，而是更具体的一层：

1. **某个功能是不是用户真正在意**
   比如 self-cleaning、steam、foldable、anti-drip 这种功能，看起来都有道理，但不一定有人愿意为它买单。
2. **用户是真的在抱怨这个缺失，还是只是你主观觉得应该有**
   它会把评论、关键词和社区讨论放在一起看，避免只凭感觉做产品决策。
3. **这个功能是加分项，还是能影响转化的核心卖点**
   最终你拿到的不是一句“我觉得值得做”，而是证据链完整的判断。

## 详细功能介绍

- **评论证据验证**
  从评论里找用户是否直接提到这个功能、抱怨缺失、吐槽现有实现，判断需求是真存在还是伪命题。
- **关键词证据验证**
  看用户是否会主动搜索这个功能点，避免做一个“用户不会搜、不会买、不会感知”的伪创新。
- **社区讨论验证**
  看用户在 Reddit、Quora 这类社区里，是否在购买前就会反复提这个问题。
- **降级证据链支持**
  即使你没有 Sorftime，也能先用本地 review 证据包跑通第一层验证。
- **结构化交付**
  最后会输出 Markdown 结论、标准 CSV 和可回查证据，让你后续继续做产品立项或内部讨论。

## 推荐安装方式：让 AI 帮你装

推荐在以下 IDE 中直接用自然语言安装：

- Claude Code
- Codex
- Cursor

把下面这句话直接发给你的 AI：

```text
帮我安装 `zach-feature-demand-validator` 这个 skill，来源仓库是 `amazon-skills`。直接装到当前工作区，并把依赖一起检查好。
```

手动安装仍然保留，但只作为降级方案：
[../../docs/manual-install.md](../../docs/manual-install.md)

## 两种使用模式

### 1. Sorftime 完整版

适合已经配置 Sorftime MCP 的环境。

- Review 维度：Sorftime
- 关键词维度：Sorftime
- 社区维度：WebSearch

### 2. 无 Sorftime 降级版

适合暂时没有 Sorftime MCP，但手里已经有 Amazon 评论证据的人。

- Review 维度：`review_source_pack`
- 关键词维度：明确写“未验证 / 待补充”
- 社区维度：WebSearch

这不是完整版，但至少能把“评论里到底有没有人在乎这个功能”这条证据链先跑通。

## 快速使用

### 业务输入

```text
帮我验证一下 air fryer 加 steam 功能在美国站是不是真需求
帮我验证一下 B0XXXX 的 self-cleaning 功能在 US 站值不值得做
```

### Review fallback 输入

```text
review_source_pack/
├── source_manifest.json
└── raw/
    ├── reviews.csv
    ├── reviews.txt
    └── reviews.html
```

详细格式见 [`references/review_fallback_pack.md`](./references/review_fallback_pack.md)。

## 核心脚本

| 脚本 | 用途 |
|------|------|
| `scripts/parse_reviews.py` | 解析 Sorftime Review JSON |
| `scripts/parse_review_source_pack.py` | 解析本地 Review 证据包 |
| `scripts/generate_keyword_csv.py` | 生成关键词标准 CSV |
| `scripts/generate_community_csv.py` | 生成社区标准 CSV |
| `scripts/validate_deliverables.py` | 校验 MD + CSV + fallback 证据包 |

Windows 用户见 [`scripts/WINDOWS_USAGE.md`](./scripts/WINDOWS_USAGE.md)。

## 交付物

- 一份 Markdown 验证报告
- 五个标准 CSV
- 若走 fallback，再附一份可核查的 `review_source_pack`

所有 CSV 都会统一输出以下核查字段：

- `数据来源`
- `来源类型`
- `来源链接/查询词`
- `原始文件名`
- `采集时间`

## 上下游

- **上游**：`zach-product-research`、`zach-competitor-deep-dive`
- **下游**：`zach-new-product-listing-writer`

## 如果安装或运行出错，直接让 AI 帮你排查

把下面这段直接发给你的 AI，并把报错信息、截图或终端输出一起贴上：

```text
我已经安装了 `zach-feature-demand-validator`，但现在遇到了问题。请你直接帮我排查并尽量修复：

1. 先判断是 skill 文件缺失、依赖缺失、Sorftime MCP 未连接、Web 搜索链路异常，还是当前 IDE 没有正确加载
2. 自动检查当前工作区里和 `zach-feature-demand-validator` 相关的文件、脚本、references 和依赖
3. 如果可以自动修复，就直接修复
4. 修复后告诉我还需要重启 IDE、重新加载工作区，还是重新运行哪个命令
5. 最后给我一个最短的验证步骤，确认这个 skill 已经能用了
```

## 关于作者

关注「**Zach的进化笔记**」，获取 AI x 跨境电商的实战经验、工具和方法论：

<img src="../../assets/traffic/wechat-official-account.jpg" width="200" alt="公众号二维码" />

扫码加入交流群，一起交流 AI + 跨境电商的实战玩法：

<img src="../../assets/traffic/wechat-group.jpeg" width="200" alt="交流群二维码" />
