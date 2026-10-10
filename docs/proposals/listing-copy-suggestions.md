# Skill 介绍修改建议：用户提交、维护者审核、独立文案修订

状态：**方案 + 本地静态交互原型，待 Lukin 看实际流程；未接入线上、未开放、未获合并上线或生产操作许可。**

本地试玩：在仓库根目录运行 `python3 -m http.server 8765 --bind 127.0.0.1`，访问 `http://127.0.0.1:8765/docs/proposals/listing-copy-demo.html`，按页面内的用户建议 → 审核 → 模拟发布操作体验。Python 只提供本地静态文件，原型仅在浏览器内存模拟；没有外部网络/API、写入或认证。不要用 `0.0.0.0` 暴露服务。

### 当前可看的原型

- [离线交互式 HTML 演示](./listing-copy-demo.html)：用户建议、差异预览、维护者审核、独立发布三屏；状态只在当前页面内存模拟，刷新即重置，完全不调用网络或保存数据。演示中发布状态是虚构占位值，不是发布事实。
- 状态/字段离线契约：`../../scripts/listing-copy-demo-contract.mjs`；Node.js 内置测试覆盖白名单、保护字段、身份主体、审核分离、过期基础与只读源数据不变量。
- 原型代码与契约都不是生产 UI/API/身份认证；页面角色与发布回执均为显式合成演示值。

负责人：Cody（设计/实现）；产品范围决定：Lukin；实现独立验收：Ada。
关联：[文案 PR #3699](https://github.com/aiskillstore/marketplace/pull/3699)、[pending Issue #3703](https://github.com/aiskillstore/marketplace/issues/3703)。沿用任务 #6286 的文案方案切片，不新建重复责任。

## 1. 一页结论

**建议做用户可见的“建议修改介绍”，不是让用户直接编辑商品或审计。**

- 所有登录用户可提建议；有 GitHub 仓库维护权限证据的用户标为“已核验仓库维护者”，其他人是“社区建议者”。两者都必须经过维护者审核。
- 先只支持英文基础介绍；提供修改前后差异、修改理由、依据和进度。一次建议对应一个 Skill、一个基础版本。
- 接受建议不会立即改线上；审核通过后由独立发布步骤生效，成功回读前显示“已批准，待发布”。
- **推荐把人工文案作为独立修订层保存，不改原 `skill-report.json`。** 包、审计、限制条款和来源校验保持原样；自动同步不会覆写人工修订。
- 第一切片用 PR3699 的文案做预填提案/演示；不直接合并那个受来源门禁阻止的报告变更，不冒用 Skillstore App。
- 当前 draft PR 包含方案文档、可本地试玩的静态演示和离线状态契约，不包含线上页面/API、数据库迁移、门禁修改或生产发布。

### 请 Lukin 看这三个产品选择

推荐默认选择：**登录用户都可建议 + 全量维护者审查 + 独立展示文案修订层**。

1. 入口对所有登录用户开放，还是第一期仅对已核验的仓库维护者开放？推荐前者，未核验者明确标社区建议。
2. 首期是否仅支持英文基础介绍？推荐是；各语言独立提案/翻译审核后续再做。
3. 是否接受“网页介绍可有已审核人工修订，原包/原审计报告不跟着改”？推荐是，页面标明“维护者审核的介绍”。

这些是方案评审点，不代表现已批准实施；没有必要为方案编写或只读研究再申请一次许可。

## 2. 现状证据与缺口

以下是源码事实，不冒充已部署状态。

**Marketplace：**基线 `755bc353599695fcfc6bbf0c0c9a76fd3e6a4897`。
- [publication-provenance.yml](https://github.com/aiskillstore/marketplace/blob/755bc353599695fcfc6bbf0c0c9a76fd3e6a4897/.github/workflows/publication-provenance.yml) 对 `skills/**` / `pending/**` 变更要求 trusted App 身份和规定分支。文案与审计存于同份报告，不存在已核实的纯文案例外。
- PR3699 head `268edece37b97b1ba6daa5e310845ea8b3390b70` 只改报告中的十个 content 键，非 content 及 content.limitations 不变。其 [来源检查失败](https://github.com/aiskillstore/marketplace/actions/runs/37605501944)不是 schema 校验失败。

**网站仓库：**已检查源码 revision `d4ac9fc88c34bc4364fc3a88f571d846acad3274`。
- [详情页 server load](https://github.com/aiskillstore/skillstore/blob/d4ac9fc88c34bc4364fc3a88f571d846acad3274/src/routes/%5B%5Blocale%3Dlocale%5D%5D/skills/%5Bslug%5D/%2Bpage.server.ts) → [详情 API](https://github.com/aiskillstore/skillstore/blob/d4ac9fc88c34bc4364fc3a88f571d846acad3274/src/routes/api/skills/%5Bslug%5D/%2Bserver.ts) → [catalog-detail](https://github.com/aiskillstore/skillstore/blob/d4ac9fc88c34bc4364fc3a88f571d846acad3274/src/lib/server/catalog-detail.ts)，当前从 `skill_ai_content` 读取介绍，调用 [content-resolver](https://github.com/aiskillstore/skillstore/blob/d4ac9fc88c34bc4364fc3a88f571d846acad3274/src/lib/server/content-resolver.ts) 处理 locale 回退。
- 详情 API 有 KV 缓存和既有 cache invalidation 路径，且支持 Agent Markdown 输出。不能只改 UI 而让 API/Markdown 留旧文案。
- [投稿 API](https://github.com/aiskillstore/skillstore/blob/d4ac9fc88c34bc4364fc3a88f571d846acad3274/src/routes/api/submit/%2Bserver.ts) 已有投稿状态、限流和投稿人 GitHub 身份记录；[favorite API](https://github.com/aiskillstore/skillstore/blob/d4ac9fc88c34bc4364fc3a88f571d846acad3274/src/routes/api/skills/%5Bslug%5D/favorite/%2Bserver.ts) 有服务端认证使用例子。可复用认证/限流能力，不把包投稿状态表硬塞成文案审批表。
- 尚未核实可复用的维护者后台角色/RLS/审批 UI、GitHub repository 权限连接器、线上迁移状态及能力绑定。实现前读取对应源码/测试并验证；没有就按最小权限新增，不能认为登录=维护者或有 provider token 就有仓库权利。

## 3. 用户看到什么（静态线框，不是可运行产品）

### 详情页入口

```text
agy-worker                       已发布包 v0.22.0 · 仅 Codex
[安装] [查看审计] [建议修改介绍]

Antigravity delegation with independent verification
… 当前公开介绍 …
介绍：自动生成 / 经维护者审核修订（修订 3）
```

未登录点入口 → 登录后回到该 Skill，不在公开缓存页内嵌个人草稿。功能未开放时不出现入口。安装、审计、支持工具等仍来自原权威投影。

### 用户提案页

```text
建议修改介绍 — agy-worker
基础：包 v0.22.0 · artifact rN · 文案修订 N
身份：社区建议者 / 已核验仓库维护者（展示核验时间）
提示：这不会直接修改线上页面，不会修改包或安全审计。

栏目              当前内容                  你的建议
展示标题          Delegate Repository…      Antigravity delegation…
简介              Complex repository…       Delegate repository work…
使用场景 / 示例 / FAQ                       [逐项编辑]

修改理由 [例如：删掉重复说明，让适用场景更清楚]
依据链接 [可选；仅保存链接，不自动访问任意 URL]
[预览差异] [提交审核]

只读：包版本、支持工具、来源、审计、安全限制
发现这些有误？[报告技术/审计问题]（走既有问题渠道）
```

在预览中逐字段显示新增/删改，提示 capabilities/FAQ/prompt 中仍不能隐含改变支持范围。提交后页面显示建议编号、当前状态和拒绝/需修改理由；不会显示“已上线”。

### 维护者审核页

```text
文案建议 #S123 · agy-worker · 待审核
提交者：GitHub 登录身份（核验来源/时间） · 类别：社区/仓库维护者
绑定包/来源/hash/基础文案指纹：一致 ✓ / 已过期 !

[当前线上] | [建议版本] | [字段差异]
自动校验：仅允许字段 ✓ · schema/长度 ✓ · 受保护字段不变 ✓
人工清单：不夸大能力；不承诺安全；不新增执行权限；与绑定包一致

审核理由 [必填]
[请求修改] [拒绝] [批准待发布]

批准后：显示发布进度/失败原因/真实版本回读；有发布权限者才见 [发布]
```

作者修改已提交内容时产生新 revision，旧批准失效。维护者修稿也产生新 revision；第一期采用保守规则：修改者不能审核自己的那次 revision。纯社区建议不公开为“作者声明”。

## 4. 字段白名单（第一版提议）

服务端按完整字段路径白名单处理，拒绝任意 JSON Patch 路径和未知键。未改字段不覆盖，数组按整个字段替换并展示逐项差异。

| 范围 | 路径 | 规则 |
|---|---|---|
| 可以建议 | `content.user_title`, `value_statement` | 只改展示名称/简介，不改安装 slug、包名或能力边界 |
| 可以建议但人工核对 | `content.actual_capabilities`, `use_cases`, `prompt_templates`, `output_examples`, `best_practices`, `anti_patterns`, `faq` | 对照当前包；不得以提示词、例子或 FAQ 夹带额外授权、危险链接或新的支持能力 |
| 首期不开放用户编辑 | `content.seo_keywords` | 可随人工审核提出专门修订，但不借入口堆词；自动生成规则先保持。PR3699 的此字段变化不自动全量采纳 |
| 永不由本入口修改 | `content.limitations`；其余未列入字段 | 不削弱限制；技术纠错走另一个流程 |
| 永不由本入口修改 | `meta`, `skill`, `security_audit` 及其他顶层字段、包文件、hash、签名、来源、版本、支持工具、安全徽章、可见性/安装策略 | 原来源及审计流程仍是唯一写入方 |

上述“可以建议”不是自动正确。HTML、脚本、隐藏指令和任意嵌套数据均不接受；用现有安全渲染器渲染有限文本，不执行文案。结构/字符/数组项上限以现有 schema 为上限；暂定请求体最多 32 KiB、每个账号同时最多 5 个待审建议、同一 Skill 仅 1 个活动建议/账号，频率限制先复用现有组件。阈值可评审，不为此新增通用风控平台。

## 5. 身份、归属和权限

- 登录使用现有服务端认证；客户端传来的 userId、GitHub 用户名、author 字段、邮箱不构成身份或归属证明。
- 所有登录用户可以成为建议者，因此归属验证失败不必扩大 OAuth scope 才能提交；显示“社区建议”，不冒充作者。
- “仓库维护者已核验”只依据服务端通过受治理 GitHub 连接器得到的**稳定仓库 ID**与当前用户对该仓库的维护/写权限证据；个人仓库可由经核实 GitHub subject 与 repo owner stable ID 匹配。不能只比显示名；组织成员身份本身不够。
- 核验记录保存最小标识、判断、时间，不保存 token 到业务表/日志。改名保留 stable ID；转移/权限撤销需重验，失效降级社区身份。此标识不授予发布权限。
- 提交者只能读写自己的草案、撤回未发布建议；不能设置 reviewer/status/published revision。维护者权限来自服务端明确角色，审批与发布均再次校验。
- 强制会话/CSRF 与同源检查、对象级授权、数据库最小权限/RLS；不以 UI 隐藏按钮代替后端校验。自己提交或实质修改的 revision 不自审。外部内容作为数据，不对模型发号施令。

## 6. 为什么推荐独立文案修订层

| 选项 | 好处 | 代价/风险 | 结论 |
|---|---|---|---|
| 不加功能、继续 GitHub Issue | 最小改动 | 无明确接纳和生效路径，问题重复 | 可临时收集，不是长期方案 |
| 改写报告 `content`，经受信 App 导入 | 兼容当前同步表 | 需新增精确 provenance 例外；可能影响依赖报告的审计/签名消费者；下次生成覆写；会依赖当前故障的整包同步 | 不作为首选，不能仅假冒 App 或放开 fork |
| **独立已审核文案修订层** | 原包/报告不变，人工版本留痕、可撤回，分离生成与编辑 | 新增少量文案数据、读路径组合与缓存处理 | **推荐** |

建议存储（命名是设计，不宣称已存在）：
- `listing_copy_suggestions`：skill_id、提交者、基础 artifact/来源及报告指纹、基础 effective copy revision/hash、白名单 delta、理由、输入 revision/digest、状态、审批角色与时间、GitHub PR 来源可选。
- `listing_copy_revisions`：不可变被批准的 delta 与内容 digest、绑定 artifact/report、审批证据、前一文案修订。
- 每 Skill 有当前 effective copy pointer，通过数据库事务比较并交换；复用现有可靠发布/异步作业机制，若不存在则新增限于该文案的持久发布记录，不能用“发出请求”冒充成功。

状态：`draft → submitted → changes_requested / rejected / approved → publishing → published`。
另有 `withdrawn` 和 `needs_rebase`；发布失败保留 approved revision 与失败记录，只重试同一幂等发布单元。支持重复提交键，审批绑定 proposal revision/digest；读到基础变化返回 409/needs_rebase，而非覆盖。

### 生效不变量

1. 在事务中读取当前 artifact/source/report hash 与基础文案指纹，重新校验白名单、审核权限和已批准内容 digest；一致才切换文案 revision pointer。相同批准重复发布不产生重复修订/通知。
2. 不写 `skills` 的安装字段、不改 `skill_ai_content` 生成原文、不改报告或审计；文案消费者只合成视图。
3. 一旦生成原文或 artifact/source/report 指纹变化，旧文案不自动沿用；读路径停止应用该覆盖层，标记 needs_rebase，恢复生成原文。修改者看到旧 delta，可针对新基础重新提交。
4. 审核、指针提交、缓存失效分别记账。指针已提交但缓存失败时不能重复创建修订，只补同一 revision 的缓存步骤；对用户状态保持 publishing，直到目标 public API/网页读回预期 revision（不以一次HTTP200判成功）。回读与基础变化竞争时转 needs_rebase，不强行重试旧稿。
5. 新字段返回 `copyRevision` / `copySource`（proposed additive contract）；输入型建议/审核接口均私有且 no-store，不进入公共缓存。

## 7. 数据流、展示范围与语言

```text
用户登录 → 读取当前可见 Skill + base fingerprints → 建议草稿/提交
       → 服务端字段/身份/限流校验 → 维护者差异审核
       → 已批准且冻结的修订 → 发布角色执行 CAS
       → 文案 pointer 提交 → 精确 Skill 缓存失效 → public readback
       → published（不写包、不运行审计、不重跑全量 sync）

生成原文/新包仍走现有 trusted-App 链路
       → 原有同步 → 基础指纹变化 → 旧人工修订暂停 → 重新审查
```

接入点推荐 `catalog-detail/content-resolver` 的服务端共享读路径，而非每个前端组件打补丁；实施前盘点所有调用者。

- 英文详情页、详情 JSON 与由该 payload 渲染的 Agent Markdown、详情 SEO 使用同一 effective copy。
- 搜索卡片、推荐/Pack 内 Skill 摘要、分享图等如另读原文，需明确沿用 package name/description 而非冒充最新 editorial copy，或接入同一 reader；不能把“全站都改了”作为第一期未证实承诺。
- 安装 manifest、下载包、包 README、审计页、安装建议与安全徽章**不读取该文案覆盖层**。人工介绍不成为执行指令或安全证据。
- 首期只提交英文。人工改过字段对应的旧翻译不再算有效：缺少绑定当前 copy revision 的翻译时，按字段回退到已审核英文并提示“该段暂以英文显示”。未改字段沿用现有翻译；limitations 从原始受保护链路加载。不得将新英文与无标识的旧翻译组合成“已翻译新稿”。
- 不在首期触发批量 AI 翻译；后续翻译也要绑定 revision、防过期覆盖，并分别验收。

### 建议 API（待核对命名，不是现有端点）

- `POST /api/skills/:slug/copy-suggestions`：认证、base tuple、allowed delta、reason、幂等键；201 返回 suggestion/revision，超限429、基础变更409、非白名单422、未授权401/403。
- `GET/PATCH /api/me/copy-suggestions/:id`：对象级权限；PATCH仅草稿/需修改状态且绑定 expectedRevision；提交/撤回采用明确动作，不接受任意status更新。
- 审核/发布在受保护的维护者接口；服务端 allowlist 动作、角色与 revision 检查，不能复用用户可写PATCH来改批准状态。
- 请求体限额、错误码、过期冲突、nonce/幂等、超时与并发测试在实现 PR 固化。外部GitHub核验超时降级社区身份；发布权限未知则拒绝。

## 8. PR #3699 如何接入

1. 保留 fork PR 及作者归属历史。不直接合并其 `skill-report.json` 修改、不重新包装成 source-monitor PR。
2. 以 exact head `268edece37b97b1ba6daa5e310845ea8b3390b70` 与原基础做机械 diff，重验非 content 和 limitations 不变；把白名单字段变化导入**维护者代录的建议草案**，来源链接指向原 PR。提交者记录为导入的维护者，原作者是明确的 source attribution，不伪造作者登录提交。
3. `seo_keywords` 在首期白名单之外，不静默丢弃或自动通过：草案注明未采纳这部分，维护者在 PR 上说明；其余文案逐项审查，必要时请求作者调整。
4. 绑定导入时线上实际 artifact/report/有效文案，若与 PR 原基础不同先标 needs_rebase。不得把 v0.22.0 文案覆盖后来批准的新包。
5. 产品范围获批、功能经独立验收并获上线授权后，才发布该文案 revision。真实网页/API回读通过，评论具体采纳字段及保留原包/审计的证据；作者确认或维护者完成告知后，可将原 PR 关闭为“已通过文案修订接纳”，**不是报告 PR 已合并**。

这条流程不解除 Issue3703 的旧 pending 阻塞，也不执行 provider恢复。#6285 与 #6286 新投稿替换约束保持：恢复 provider 后不得顺带发布被取代的 v0.24.0。新的文案功能不能作为绕过当前生产故障的直接写库入口。

## 9. 实施切片、验证与回滚

这是估时/范围建议，不是已开始全部实施的承诺；批准实施后沿用 #6286 登记明确下一切片。

| 切片 | 可看见的结果 | AI主动工作估时 | 依赖 |
|---|---|---|---|
| 本次方案 PR | 本文与三张线框，字段和流程可评审 | 当前交付 | 无生产操作 |
| S1：离线演示/契约 | PR3699白名单diff导入fixture、基础指纹/状态机/防越权测试，用户与审核页只读演示 | 2–4小时 | 产品字段/受众决定 |
| S2：最小垂直切片 | 认证提交→维护者审查→revision CAS→共享reader→cache/readback，在隔离环境演示 | 1–2工作日 | 当前auth/RLS/审核角色/缓存接口调查，可能重估 |
| S3：受控上线 | migration、权限核验、关闭默认开关下验证，再分批开放 | 另行估计 | CEO上线授权、生产连接器、独立验收、故障边界核清 |

只复用现有依赖/认证/渲染器/缓存设施，不新增服务或新token体系。生产等待不算主动实现时间。

**必须先红后绿的验收项：**
- 未登录、伪造author/role/owner、越权读写他人草稿、自审、撤销权限、超配额、CSRF均拒绝。
- 每个禁止字段、未知键、嵌套字段逃逸/原型污染、过长文本、HTML/脚本都拒绝或安全渲染；当前包、报告、审计与limitations前后字节/语义不变。
- 修改建议/基础变化使旧批准失效；双审核、双发布、retry、cache失败、回滚都不重复新增revision或破坏较新版本。
- 普通建议者与已核验维护者UI区分正确，不能因勾选作者而提权；登录、差异预览、请求修改、发布中与发布成功至少覆盖一条关键E2E。
- public JSON/网页/Agent Markdown同revision；旧翻译正确回退，个人草稿不进缓存；manifest/下载/审计不受影响。
- 后续自动生成或新包发布不覆写人工历史，也不把旧revision继续错误展示。
- PR3699 fixture证明按选择字段导入、未采纳SEO明确列出、禁止字段不变；关闭原PR前有public source-of-truth回读。

**回滚：**暂停入口与publisher，保留建议/审核历史；服务端读开关禁用覆盖层回到原生成文案，失效相关缓存并回读。撤销某条已发布文案需角色核验和对当前pointer的CAS，记录撤销理由；不能删除审计历史、回退包或 resurrect 旧pending。基础版本不同不能简单切回旧copy pointer。

## 10. 本次完成与未知

2026-10-09：Lukin 已明确批准开始 S1 离线演示，不再等待重复批准。当前交付待 Ada 独立验收；S2/S3 不在本次授权范围。

已完成：方案和静态交互演示；固定 PR3699 `268edece37b97b1ba6daa5e310845ea8b3390b70` 的九项白名单文案 fixture，原文来自固定 base `4ac52da14aa9a0249c404cfd9e66486e701ce8fa`。采集时逐项比较非 content 内容及 limitations 相等；fixture 保留两份原报告 SHA256、非 content 规范化 hash 和 SEO 未采纳清单，不保留审计正文。artifact r7 / copy r2 为合成编号，不是生产数据。

本地 `CI=true node --test scripts/tests/listing-copy-demo-contract.test.mjs` **18/18 PASS、零跳过**：字段类型/长度/禁止键、伪造模拟角色/标签、自审、修订后批准失效、批准绑定、基础过期、独立发布、重复动作确定性拒绝、保护字段与源对象不变。重复批准/发布不会静默重放；重复修订无内容变化也拒绝。纯函数只描述单进程模拟，不能代替服务端权限、并发 CAS、RLS 或密码学签名。

已通过真实无登录态本地浏览器交互检查（agent-browser 独立 session）：固定文案逐字段 diff → 提交 → 请求修改 → revision2 → 批准但公共原文不变 → 再修改清除批准 → 重审 → publishing → 合成回执 → 模拟 public 改变；基础变化后恢复原文，批准到发布之间基础变化进入 needs_rebase；刷新全部重置。390px 视口无横向溢出。静态服务仅白名单提供 HTML 和两个本地模块，未查询生产。共100条浏览器命令含动作前 snapshot、两类模拟身份标签、状态断言与5张截图，原始证据保存在共享 review 区，未发布为公开截图链接。

### 复验步骤
1. 按文首命令启动本地静态服务器。选择社区/已核验维护者模拟身份；标签不授予审核权。标题、简介和其余七项 JSON 已预填 PR3699 文案。
2. 点“预览差异”，展开各字段。原始 limitations 与保持不变的 SEO 单独展示。填写理由后“提交审核”。
3. 切换维护者页，填写理由，点“请求修改”；回用户页改标题后再次提交，同一演示建议修订号递增。批准后公共页仍显示原文。
4. 批准后再改字段并提交，旧批准清除；重审后分别点“模拟独立发布者开始发布”和“模拟回执完成”。仅最后一步改变模拟公共页。
5. 批准后点“模拟基础文案版本变化”再开始发布，应进入 needs_rebase；已模拟发布后基础变化也回退原文。刷新复位。

未完成/N/A（本切片之外）：真实登录/API、持久化、数据库 migration/RLS、GitHub维护权限核验、跨表事务、缓存/回滚/多用户并发、生产回读及发布。模拟 actor registry、审批绑定字符串及回执不具有生产安全效力。最终开放、policy/绑定变更、合并上线仍须分别获对应授权；PR3699 和 Issue3703 的实际生产目标没有因此完成。
