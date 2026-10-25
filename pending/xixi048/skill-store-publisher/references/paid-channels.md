# 付费渠道与定价

**默认立场：能收费的渠道就收费。** 免费渠道留引流版，付费渠道挂完整版或 Pro 版；
同一个技能在不同渠道是不同 SKU，不必同价。

## 一、哪些渠道真能收到钱

| 渠道 | 收费方式 | 分成（开发者拿） | 准入门槛 | 能不能脚本设价 |
|---|---|---|---|---|
| **skillbay.sh** | 一次性 / 订阅 | **100%（平台 0 抽成）** | 邀请制：先提交 → 人工审 → 发邀请 → Stripe 结算 | ❌ 需 seller 账号 + Stripe onboarding |
| **扣子 Coze** | 按次（可低至 ¥0.5/次）/ 月订阅 | 约 **70%** | 需入驻商户 `code.coze.cn/merchant-management` | ❌ 需平台侧操作 |
| **阿里云百炼 Agent Store** | 打赏 + API 收费 + 分润 | 未公开 | 需阿里云账号 + 商品审核 | ❌ |
| **GPT Store** | 订阅分成 | 开发者 **85%**（平台抽 15%） | 需 ChatGPT Plus + Builder Profile | ❌ |
| **Windows Agent Store** | 应用内购买 | 开发者 **85%** | 需微软开发者账号 | ❌ |
| **Dify 市场** | 自接支付 | 私有部署 **0%** | 自部署 | ✅（自己写支付） |

**共同点：定价动作全部发生在"账号/商户"层，不在"提交"层。**
匿名提交接口（skillstore / skillsmd / skillbay quick）**都设不了价**——
skillstore 与 skillsmd 干脆只做免费收录。

所以正确做法是：**先用匿名 API 抢免费的曝光位，同时把付费 listing 的字段全部填好，
等账号/邀请到位后一次粘贴。**

## 二、skillbay.sh 的定价字段（照抄即可）

上架 listing 走 `POST /api/v1/sellers/{org}/listings`（multipart，需 session 或 bearer）。
`SkillForm` 关键字段：

| 字段 | 约束 | 建议值（本技能实测） |
|---|---|---|
| `title` | 3–80 字符 | `create-all-cg-save` |
| `summary` | ≤140 字符 | 一句话说清"给谁、解决什么" |
| `description` | 20–20000 字符 | 用 STORE-LISTING 里的长描述 |
| `category` | 枚举 slug | `coding & dev tools` / `games` |
| `price` | **整数美元**，0=免费，上限 10000 | **5**（≈¥35） |
| `examples` | JSON 数组，1–5 条，每条 `{prompt, without, with, notes?, model?}` | **必填项**，没有 example 不能提交审核 |
| `file` | zip，SKILL.md 在**单一顶层文件夹**根部，≤25 MB | `dist/<name>-skillroot.zip` |

定价经验值：

- 低于 **$3** 会被默认当成"自用玩具"，反而不如免费
- **$5** 是"有人真会买"的最低舒适区
- 拆 SKU 比抬价有效：核心免费引流 → Pro 适配器包 **$6.9** → 数据集/ID 库 **$5.9**

## 三、分成对照（同样收 $5，实际到手）

| 渠道 | 平台抽成 | 到手 |
|---|---|---|
| skillbay.sh | 0% | $5.00（Stripe 手续费另计） |
| GPT Store | 15% | $4.25 |
| 扣子 Coze | 约 30% | $3.50 |
| Windows Agent Store | 15% | $4.25 |

## 四、合规红线（写进 listing 的 Scope Guard）

- 不承诺破解、不绕过 DRM、不涉及联机/排行榜/反作弊
- 明确"只处理用户自己合法拥有的副本"
- 含脚本的技能主动披露：零依赖、无网络、无动态执行、写入前强制备份
- 审核索要补充材料时，**加说明而不是删功能**——安全能力就是卖点
