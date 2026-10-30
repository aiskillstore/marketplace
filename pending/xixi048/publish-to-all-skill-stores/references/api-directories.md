# API 目录：第四条线，别和技能商店混着做

> 时间基准：2026-10-28～30，条目均为当天实测。
> 这条线在旧版清单里**整条缺失**——商店收的是 SKILL.md，目录站收的是「一个能调的 HTTP 端点 + 一份 OpenAPI」。

## 一、先确认你手上到底有没有「API」

技能商店、MCP 目录、API 目录是三条线，判断标准只有一条：

| 线 | 交付物 | 典型渠道 |
|---|---|---|
| 技能商店 | `SKILL.md`（方法论） | skillstore、ClawHub、WorkBuddy 开放平台 |
| MCP 目录 | 一个跑着的 MCP server | 官方 Registry、mcp.so、Glama |
| **API 目录** | **HTTP 端点 + OpenAPI/llms.txt** | public-apis、Agent402、RapidAPI、扣子插件商店 |

**没有公开 HTTP 端点就不用看这一篇。** 反过来，只要有端点，这条线是**唯一能全自动**的一条：
一条 POST 或一条 PR 就能进，不需要登录，也不需要移植。

## 二、全自动（一条命令 / 一条 PR）

| 渠道 | 提交动作 | 回执 | 验证 |
|---|---|---|---|
| **Agent402** | `POST https://agent402.tools/api/index/register`<br>body `{"origin":"https://<domain>"}` | `listed:true` + `toolCount` + `networks` + `routable` + `health` | ✅ 实测 |
| **public-apis** | GitHub PR，在 `Art & Design` 分类按**字母序**插一行 | PR 号 | ✅ 实测 PR #8482 |
| **public-api-lists** | GitHub PR，加一行 | PR 号 | △ |
| **APIs.guru** | GitHub PR，`APIs/<provider>/<api>/<version>/openapi.yaml` | PR 号 | ⚠️ CI 校验极严 |
| **langchain**（相关 awesome 列表） | GitHub PR | PR 号 | △ |
| **x402.new** | 自动抓，无需提交 | — | △ |
| **x402-trust** | 在站点放 `.well-known/` 声明 | — | △ |
| **apis.io** | `POST` 一份 `apis.json`（人工审核，需邮箱） | 邮件 | △ |

### Agent402 的读法

返回里最该盯的不是 `listed`，是这两个：

- `toolCount` —— 它从你的 OpenAPI 里数出来的工具数。**数不对说明 OpenAPI 写得不对**
  （实测同一站点从 6 涨到 13，是因为补了端点文档，不是它自己变的）。
- `routable` + `health` —— 它会真的探一遍所有 402 路由。`health < 1` 就是有端点挂了。

它有 15 分钟的重新读取冷却，**不要连着猛刷**；它自己的爬虫也会周期性重读。

### public-apis 的坑

- fork 出来的远端默认可能被 `insteadOf` 改写成 ghfast 镜像，**推不上去**。
  提交前先 `git remote set-url origin git@github.com:<user>/<repo>.git`。
- 条目必须**按字母序**插，插错位置是 maintainer 最常见的打回理由。

## 三、需账号（登录态我替不了）

| 渠道 | 量级 | 形态 |
|---|---|---|
| **RapidAPI** | 800 万开发者 | 需商家账号，可挂付费 |
| **Postman API Network** | 月 100 万 | 需账号 + OpenAPI 集合 |
| publicapis.io / apilist.fun / publicapis.dev | 中 | 表单，需邮箱/账号 |
| AI Agent Store / ProductHunt / DevHunt | 中 | 表单 + 审核 |

## 四、需钱包签名

| 渠道 | 卡点 |
|---|---|
| **x402scan** | 要用**收款钱包**签 SIWx |
| **CDP Bazaar / agentic.market** | **被真实支付过一次才进索引**（自付约 $0.10） |

这两类不是登录问题，是**链上身份**问题，必须用户本人的钱包。

## 五、国内：只有一条路能走通

**实测结论：阿里云云市场 / A集市 / 聚合数据等全部要求企业资质**（正规公司 + 10 人以上团队 + 1 年经验），
个人开发者是死路，不用试。

**扣子插件商店是国内唯一支持个人开发者上架自有 HTTP API 的渠道。** 它收 OpenAPI，
走「资源库 → +资源 → 插件 → 导入 OpenAPI → 调试 → 发布 → 上架」，
完整实测流程见 [coze-plugin.md](coze-plugin.md)。

待查（未实测）：Gitee 镜像 + 开源中国收录、百度千帆、智谱组件广场、掘金/CSDN 技术曝光。

## 六、提交前必须满足的四条

目录站评审真的会连一次，跟 MCP 目录是同一套标准：

1. **`/openapi.json` 可公开访问**，端点数与文档一致（Agent402 的 `toolCount` 就是照这个数的）
2. **`/llms.txt` 存在**（llmstxt.org 约定），写清定位、入口选择、限流、给 AI 的引用要求
3. **免费端点不需要任何 token 就能调通**——付费端点（402）会被目录站的调试环节判失败
4. **描述里不写会过期的固定数量**，目录站会把描述快照进索引，数字一变就失真

> 第 3 条是扣子插件商店白跑三轮的原因：付费 analyze（402）过不了「全部工具试运行」，
> 只能停用或给它开免费额度。详见 [coze-plugin.md](coze-plugin.md)。
