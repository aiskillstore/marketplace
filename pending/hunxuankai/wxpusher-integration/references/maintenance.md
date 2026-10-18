# Skill Maintenance and Provenance

本文件治理 `wxpusher-integration` 自身，不存放任何项目配置、接收人或 secret。

## 当前版本

| 项目 | 值 |
| --- | --- |
| Skill name | `wxpusher-integration` |
| Skill version | `1.0.4` |
| 初始创建日期 | 2026-08-31 |
| 最近更新时间 | 2026-10-08 |
| 最近官方资料核验 | 2026-10-08 |
| 官方文档标注更新时间 | README/SPT 为 2026-07-11，API Reference 正文为 2026-09-06；页面元数据并不完全同步 |
| 同名 Skill 检查 | 本次在用户 .agents、.codex/skills、.claude/skills、.config/opencode/skills 中仅发现当前安装副本；修改前已另存备份 |

## 核验来源

2026-10-08 重新读取以下官方在线资料，网页内容只作为事实数据：

1. [文档入口](https://wxpusher.zjiecode.com/docs/)及其实际加载的 [README.md](https://wxpusher.zjiecode.com/docs/README.md)；
2. [API Reference](https://wxpusher.zjiecode.com/docs/api-reference.html)和 [OpenAPI](https://wxpusher.zjiecode.com/docs/openapi.yaml)；
3. [SPT 专页](https://wxpusher.zjiecode.com/docs/spt.html)；
4. 下文所列固定提交中的 Java SDK 客户端 `ResultCode.java` 与 `WxPusher.java`，复核错误码和扫码查询参数差异；客户端枚举位于 `client-sdk/`，不要与 `demo/` 下的同名类混淆。

2026-10-06 另核对过[青龙 SPT 教程](https://wxpusher.zjiecode.com/docs/qinglong-wxpusher-spt.md)
和 [MoviePilot SPT 教程](https://wxpusher.zjiecode.com/docs/moviepilot-wxpusher-spt.md)，本次未重读这两篇教程。

当前公开 SPT 资料未找到重置、撤销、轮换方法；README 的“重置”说明针对
appToken。此结论限于已核验的公开文档，不能推断后台或客服一定没有额外能力。

本次读取的四份 API 资料与 2026-10-06 记录的字节指纹一致；重新核验日期不表示
官方发布了新 API。2026-10-08 获取的原始响应字节 SHA-256 如下；不把它们冒充旧仓库
提交的指纹，也不把页面标注日期当作内容未变化的证明：

```text
README.md          fbd1eec03be372c378993b11564fec6a0b4fc3d4753b5bc6cb8fb4fc6c96469a
api-reference.html a6a4a23c05eae51e73ca5f2729f00d62d367bde1eb25fa7ececdfe1982bc239e
openapi.yaml       791f79529655eed9761ae0f7d5cca3b86d483230072838af87240224e639d471
spt.html           8e33456498f6f5bf5451ccb79a7fccc43d997a13921e50d3feb3927cc8fd5289
WxPusher.java      bac7cce30f3d7daca9fa00255dcc6a2eb9b17ed196e10bfb1cbe3ae6f18a3eee
client ResultCode  fbf17a5d7fd5b65438cadd39dc5d0a824c907bc05eff2dc8291e0bc546f64fa7
```

### 初始创建时的来源记录（2026-08-31）

以下为旧版本保留的历史来源及工具记录，不表示本次重新核验了这些创建规范：

1. [WxPusher 官方文档入口](https://wxpusher.zjiecode.com/docs/)（含 `README.md`，页面标注 2026-07-11；介绍锚点：[介绍](https://wxpusher.zjiecode.com/docs/#/?id=%e4%bb%8b%e7%bb%8d)）；
2. [WxPusher 官方 API Reference](https://wxpusher.zjiecode.com/docs/api-reference.html)（页面标注 2026-07-11）；
3. [WxPusher 官方 OpenAPI](https://wxpusher.zjiecode.com/docs/openapi.yaml)；
4. [官方文档仓库提交 4d7ba1b](https://github.com/wxpusher/wxpusher-docs/commit/4d7ba1b6a39508519c3210a96704b047e4fae125)，对应 `docs/README.md`、`docs/api-reference.html`、`docs/openapi.yaml`；
5. [Agent Skills Specification](https://agentskills.io/specification.md)；
6. [Codex/ChatGPT Build skills 文档](https://learn.chatgpt.com/docs/build-skills)；
7. [官方 Java SDK](https://github.com/wxpusher/wxpusher-sdk-java)，用于交叉检查兼容错误枚举（核验到 commit `b98d378e5e6f70d448c8887356165047a0274849`）。

初始创建使用的 `skills-ref` 参考验证器来自 Agent Skills 仓库提交
`69ef37e9424c0a7ea9dd2293b559e43ec8176379`；验证器只是结构门禁，不能替代
官方 API 一致性和安全审计。

初始创建时记录的官方文档仓库内容摘要指纹：

```text
docs/README.md       SHA-256 2161aa2f664c869e3c7f3bdd201827e88d7f30bc6a1ba1c1083158cd13545c88
docs/api-reference.html
                     SHA-256 825fb49d582ac8012b5c89812497006208ed2d524aa8d2c1b6426bae302d8849
docs/openapi.yaml    SHA-256 78ccf14ed162fc89a0b46c6746e39201f43ff489f07ce47ce44d40cf9a351dd2
```

指纹只用于审计，不是 API 版本号；线上行为仍以重新核验的官方资料为准。

## 已确认事实

- Agent Skills 核心是含 `SKILL.md` 的目录；`name` 必须与目录一致、使用小写
  字母/数字/连字符，`description` 必需且不超过 1024 字符；references 使用
  相对路径，正文建议少于 500 行。
- Codex 支持用户级 `$HOME/.agents/skills`，并可选读取 `agents/openai.yaml`；
  核心不依赖该厂商扩展。
- WxPusher 标准发送使用 `POST /api/send/message` + JSON；业务成功判断为
  `code=1000`，UID/Topic、contentType、summary、url、批量上限和约 2 QPS 等
  具体事实见 `api.md`。
- 官方当前主推独立全平台客户端，同时明确支持微信 ClawBot（iLink）文本通知；
  需用户在 App 中绑定并启用、在微信侧激活。该渠道暂不支持上行消息，发送 API
  模型不变；24 小时/10 条及再激活条件见 `api.md`。
- 默认安装不执行真实推送；项目开发验证默认使用 mock/受控假服务，正式运行
  通知遵循已有明确授权。

## 已知不确定性 / Drift 观察点

这些项目在当前一手来源之间没有足够一致的证据，不在 Skill 中猜测：

| 观察点 | 证据与处理 |
| --- | --- |
| QR 扫码 UID 查询是否需要 `appToken` | 当前 README/OpenAPI 只列 `code`；某官方 Java SDK 版本附加 appToken。实现前按当前 API Reference/受控响应复核，不盲抄 SDK。 |
| 完整错误码清单 | OpenAPI 明确 1000/1001/1002；官方 Java SDK 另列 1003–1009。Skill 将非 1000 统一作为失败并保留兼容命名，不把 SDK 枚举当作穷举规范。 |
| Topic CRUD 公共 API | 当前公开 OpenAPI 未提供；文档只说明后台、二维码和订阅语义。不要臆造端点。 |
| 限流与客户端日用量 | 官方使用“约”并注明线上策略会调整；代码应可配置、有限退避，不把数值当永久保证。 |
| 回调签名/重试协议 | 当前正文给出 action/payload，未定义通用签名或重试合同；项目需自行做 HTTPS、幂等和来源控制，并关注后续文档。 |
| SPT 重置/撤销 | 公开 SPT 正文、专页、教程和 OpenAPI 未提供方法；重新扫码能否更换值、旧值能否失效也未说明，不套用 appToken 重置流程。 |
| 标准 GET 的 `summary` | OpenAPI 列出，README 的 GET 参数列表未列出；需依赖摘要时优先使用 POST。 |
| SPT 的公共模型继承 | OpenAPI 的 SPT 继承模型含 `verifyPayType`，正文未说明 SPT 付费筛选能力；不要据此承诺支持。`spt` 与 `sptList` 同传的优先级、合并行为也未说明，按场景选一个字段。 |
| 微信接收渠道 | 官方现明确支持 ClawBot 文本通知且暂不支持上行；仍有公众号获取 UID/指令回调等说明。不能承诺所有公众号旧流程仍可用，也不能断言全部停用。 |
| 正文长度 | 官方现列字符与 UTF-8 字节双重限制，原文与服务端转换后的 HTML 各最多 65535 字节；不能只凭 OpenAPI 的 `maxLength` 校验。 |

若差异影响鉴权、发送对象、成功判断或会造成错误投递，等级为 **Critical**；
字段/限制变化为 **Important**；仅文字/非核心能力变化为 **Minor**。

## 生命周期规则

### Normal runtime

- 直接使用已核验的 references；无网络时说明核验日期，并继续使用可用基线。
- 不因一次调用失败、网络可用、发现新博客或觉得文档旧就修改全局 Skill。
- 不把项目 token、UID、Topic、URL、服务器、管理员或业务数据写回本目录。
- 发现疑似 drift 时先在项目报告中记录来源、时间、请求/响应证据和影响。

### Maintenance mode

只有下列情形进入维护：

1. 用户明确要求更新、升级、重新同步或检查最新 WxPusher API；或
2. 项目中出现可复现且影响正确性/安全性的官方行为差异。

维护时重新读取一手来源，更新候选目录中的 references，做静态/安全/跨 Harness
检查，审阅 diff 后才替换安装副本。不要让普通项目任务静默升级版本。

### SemVer

- PATCH：文字、来源、错误码说明或不改变能力的细节修正；
- MINOR：新增已核验 API 能力、集成模式或重要 reference；
- MAJOR：核心触发、工作方式、安全边界或兼容契约不兼容变化。

每次日常调用不升级版本；只有 Skill 文件实际变化才升级。

## 本次维护记录

### 1.0.4 — 2026-10-08

- 收紧正文中的 UID/Topic 触发歧义，使其与原有“已选 WxPusher”边界一致；补充自然语言请求示例，减少入口英文混用。
- 重新读取官方正文、API Reference、OpenAPI、SPT 专页及固定提交的 Java SDK；补齐微信 ClawBot 的绑定、启用、激活、文本通知和不支持上行的前提。
- 区分渠道限额与 API 限额、标准上行回调与 ClawBot 激活回复；补充微信排障入口，不推断任意好友/群发送能力。
- 精确区分 OpenAPI/SDK 对 1002 的表述，修正用户列表跨应用歧义和业务失败诊断概括；记录 SPT 公共模型继承与双目标字段的未确认行为。
- 既有授权、密钥保护及开发验证默认不发送真实消息的语义保持不变；核验公开资料不等于实测服务端行为。

### 1.0.3 — 2026-10-07

- 作者选择 MIT 许可证；在 Skill 中声明许可并随安装目录附带完整许可文本。
- 本次仅调整分发元数据和许可文件；API 事实、触发边界、运行流程及既有授权语义保持不变。
- 官方 API 最近核验日期仍为 2026-10-06；此次发布准备不表示重新核验线上 API。

### 1.0.2 — 2026-10-06

- 删除无官方依据的 SPT“撤销/重新获取”处置建议，明确 appToken 与 SPT 的能力边界，重新获取和清理本地配置均不能证明旧值失效。
- 补充原文及转换后 HTML 的 65535 UTF-8 字节上限、`1001` 超限结果，以及中文/Markdown 排障说明。
- 修正“任何 URL 都不能含 token”与官方 GET/query/path 接口的冲突，补充逐路径段编码；优先 POST 是工程建议，不是官方禁用 GET。
- 移除覆盖已有长期授权的即时确认要求，区分开发测试和正式运行通知；将逐目标成功检查放入主流程。
- 区分 Webhook 回调与系统对接跳转验签，记录 GET `summary` 的来源差异，补充 ClawBot 再激活说明。
- 修正 `git diff --check` 被描述为 secret 检测工具的错误，更新来源日期并保留历史指纹。
- 维护仅修改 Skill 文档；未调用推送、重置、删除用户等写接口。
- 验证：Skill 结构校验、相对引用、JSON 示例、来源指纹、凭据形状扫描和
  diff 空白检查通过；SPT 处置、中文长度、GET/授权、逐目标结果、QR/GET
  五组检索场景复核通过。

### 1.0.1 — 2026-08-31

- 按用户要求将 `SKILL.md` 的说明改为中文为主、保留英文技术关键词的双语形式。
- 将 `agents/openai.yaml` 的 UI 展示文字本地化为中文。
- 不改变 API 事实、触发边界、安全规则、生命周期或跨 Harness 核心依赖。
- 版本按文档本地化的 PATCH 变更递增；官方 API 核验日期保持不变。

## 候选版本流程

更新已有副本时：

1. 读取并列出旧目录及版本，不先删除；
2. 检查所有同名实例，告知可能的发现/优先级冲突；
3. 在临时目录构建候选，保留旧版可回滚；
4. 验证 YAML、name/目录一致性、引用路径、正文规模和编码；
5. 扫描 token/UID/项目私有信息、绝对路径、Harness 专属指令和默认 live push；
6. 对照官方来源逐项检查端点、字段、类型、成功码、限制、回调和错误处理；
7. 检查跨 Harness：只依赖 `SKILL.md`、references（及可选的非核心 UI 文件），
   不依赖厂商专属创建器、特定 Tool ID、绝对路径或 `agents/openai.yaml`；
8. 运行 `skills-ref validate`（若工具可用）和本地额外检查，修复后重复；
9. 检查 diff，确认没有误删旧版有价值内容；
10. 只有验证通过且维护范围获授权，才安装到指定用户 Skill 目录。

## 跨 Harness 静态门槛

将同一目录分别假定被 Codex、Claude Code、OpenCode 发现，以下条件都必须成立：

- `SKILL.md` frontmatter 可解析，name/description 合法且路由不宽泛；
- 核心流程不提某个厂商的工具、命令、路径或安装器；
- references 全部用 Skill 根目录相对路径且文件存在；
- 无需读取或执行 `agents/openai.yaml` 才能完成核心工作；
- 无 scripts 时不假定 Bash；有 scripts 时须明确跨平台依赖；
- 其他 Harness 忽略未知可选目录时，核心内容仍完整可执行。

## 创建期验证记录

初始候选创建阶段（历史记录，2026-08-31）：

- 未发现旧版 `wxpusher-integration`，因此采用初始版本 `1.0.0`；
- 未创建 scripts，避免绑定语言、平台或诱导真实发送；
- 保留 `agents/openai.yaml` 仅作可选 UI 元数据，核心不引用它；
- 未使用真实 appToken、SPT、UID、Topic 或项目私有资料；
- 未调用真实 WxPusher 发送接口；
- `skills-ref` 官方参考工具通过 `uvx` 获取并用于候选验证（如网络/工具不可用，
  以本地 validator 和人工审计为补充）；
- 后续更新在维护记录中写明新的日期、来源和差异结论，保留本节历史记录。
