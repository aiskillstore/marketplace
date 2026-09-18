# RTC 文档检索与原文核验

本 reference 用于需要核对当前 RTC 文档的咨询。命令只读、无需项目配置或登录，不会
读取或转发 AppKey、Signin 凭据和 `.env.local` 内容。

配置生成和校验使用 `voice-agent-config-validation.md` 中限定的证据流程。

## 推荐路径：精确目录 → fetch

常见 AI 音视频互动主题先读取 [topic-doc-catalog.md](topic-doc-catalog.md)，执行一次精确标题过滤：

```bash
vertc docs list --query "配置语音合成 TTS" --limit 10 --format json
```

从 `documents[]` 中选择标题与 catalog 的 `expected_title` 唯一匹配的 ID，再用 `--match`
定向读取。接口契约可能很长，文件大小不能作为排除条件。用精确文档和 matched excerpt 控制
返回内容；网页 URL 中的数字 ID 不能用于 `docs fetch`。

## 无精确路由时：search → fetch

1. 用用户问题中的产品名、API 名或症状执行一次检索：

   ```bash
   vertc docs search "publish audio Web SDK" --limit 10 --format json
   ```

2. 按返回顺序查看 `results[].id`、`score` 和 `snippets`。`--limit` 只在本地截取服务端排序，
   默认 10、最大 50；snippet 仅用于选择精确 ID，不能当作正文证据。
3. 对最相关的精确 ID 获取原始 Markdown。只需定向章节时，对每个精确词重复传入 `--match`：

   ```bash
   vertc docs fetch <doc-id-from-results.id> \
     --match "publish audio" --match "Web SDK" --format json
   ```

   `fetch` 不承担搜索，`doc-id` 必须原样取自 `results[].id`。采用定向正文前确认
   `complete=true`，且实际采用正文的 `matched_terms` 并集覆盖所需精确词；`bytes` 与 `sha256`
   标识完整原文。需要阅读全文时去掉 `--match`，以 `data.content` 为准；面向人直接阅读可改用
   `--format pretty`。
4. 证据足以回答时立即停止；否则只 fetch 下一篇确有必要的候选，不反复改写 query 或遍历结果。

用户要求开放式探索或浏览目录时使用：

```bash
vertc docs list --query "audio" --offset 0 --limit 20 --format json
```

`list` 读取索引后，在本地按标题和摘要过滤、分页，结果不按相关性排序。用户要求继续时再读下一页。

## 参数合同与一次纠错

- `search` 接收一个位置参数 query：`vertc docs search "<query>"`。
- `fetch` 接收一个位置参数 doc ID：`vertc docs fetch <results[].id>`。ID 也可以来自 `list` 的
  `documents[].id`；`--match` 可重复传入。`--url`、`--query` 和网页路径均无效。
- `list` 使用 `--query`，不接收位置参数。
- `docs` 命令只读，`--dry-run` 不校验参数，也不会替代实际读取。

遇到 `vertc.docs.invalid_argument` 或 `vertc.cli.invalid_flag` 时，按
`error.details.usage/example` 纠正一次语法，保持 query 和 doc ID 不变。旧版 CLI 未返回这些字段时，
运行一次 `vertc docs <search|fetch|list> --help`；纠正后仍失败则停止。

## 输出与失败路由

- JSON 成功结果在 stdout 单一 envelope 的 `data` 中；重试进度和警告只在 stderr。
- `vertc.docs.document_not_found`：回到 search/list 获取当前精确 ID，不猜测路径。
- `vertc.docs.tool_schema_changed`、`vertc.docs.unsupported_protocol`：停止自动解释，报告服务契约
  已变化，等待 CLI 或服务更新。
- `vertc.docs.timeout`、`vertc.docs.request_failed`、`vertc.docs.rate_limited`：可按错误提示稍后重试；
  不要把网络失败解释为产品不支持。
- 其他 `vertc.docs.*` 错误先按稳定 `error.code` 分流，禁止把原始响应、query、session 或正文
  复制进日志。

## 离线与降级

该命令不提供缓存或隐式摘要。服务不可达时，显式告诉用户“当前实时文档未核验”，再按需求：

- 使用本 Skill 已内嵌的 `capabilities.md`、`voicechat-api.md` 等 reference，并同时说明其中的
  `verified_at` 或可信状态；
- 使用用户已提供的文档正文继续分析；
- 若结论依赖当前版本、计费、配额、模型兼容或公测状态，则等待恢复后重试，不用旧资料给出
  确定性结论。

不要自动切换 endpoint，不要要求用户提供鉴权 header，也不要通过 query 携带凭据或个人信息。
