# 数据契约

## 单知识点请求

```json
{
  "schemaVersion": "fact-check-x/authority-request@1",
  "requestId": "K1",
  "title": "用户问题或总标题",
  "comparisonStatus": "conflict",
  "knowledgePoint": {"id": "K1", "description": "原子事实", "role": "direct", "core": true},
  "claims": {"doubao": {"covered": true, "claim": "...", "sourceLevel": "nonofficial", "faithfulness": "supported"}},
  "cloudPayload": {
    "title": "用户问题或总标题",
    "knowledgePoint": {"id": "K1", "description": "原子事实"},
    "differingClaims": [{"platform": "doubao", "claim": "..."}]
  },
  "trustedAnchor": {"eligible": false}
}
```

`differingClaims` 只在 `comparisonStatus=conflict|partial|mostly_consensus` 且至少两家主张确实不同时允许出现。一致、单方覆盖时必须省略。`cloudPayload` 不得包含完整原答案或无关知识点。

`sourceLevel=official|dknow_trusted_search_official` 且所附正文忠实时可进入直接准确；其中 `dknow_trusted_search_official` 表示深知晓或深知晓（深度溯源）的可信搜索官方材料，不以 `.gov` 域名或外链是否返回作为降级条件。深度溯源不继承普通深知晓结果，但自身材料满足锚点条件时可独立使用 `dknow_exempt`。`sourceLevel=nonofficial` 即使内容忠实，也必须由独立权威证据验证后进入间接准确。最终报告的官方验证依据严格按各平台 `verdict.evidenceIds` 映射，不得默认取证据列表第一项。

## 取证结果

`fact-check-x/authority-evidence@1`：

```json
{
  "requestId": "K1",
  "status": "verified",
  "searchMode": "trusted_search",
  "requestCount": 1,
  "attemptCount": 1,
  "query": "由 cloudPayload 构造的查询",
  "evidence": [{"id": "E1", "title": "...", "url": "https://...", "date": "...", "body": "官方原文"}]
}
```

`searchMode`：`trusted_search` 或 `dknow_exempt`。免查时 `requestCount=0`、`attemptCount=0`；其余知识点的逻辑搜索任务 `requestCount=1`，技术故障自动重试时由 `attemptCount` 记录实际尝试次数，最多 3 次。

## 单点裁决结果

`fact-check-x/authority-result@1` 保留请求、证据、搜索模式、请求次数、权威结论和逐平台类别。服务错误不得写成事实错误；重试后仍失败时不生成裁决结果。证据不足写入 `resolution=insufficient_evidence|partially_resolved` 和 `evidenceGaps`，但结果状态仍为 `completed`。

## 汇总结果

最终平台表现报告接受统一入口生成的 `fact-check-x/verification@2`，其中每个知识点带一个 `authority` 单点结果，并包含：

```json
{
  "finalAnswer": {
    "status": "verified|partially_verified|insufficient_evidence",
    "answer": "按知识点顺序合并的权威核验答案",
    "knowledgePointIds": ["K1"],
    "excludedKnowledgePointIds": []
  }
}
```

`finalAnswer` 只合并已有足够证据完成裁决的 `authoritativeFinding`，不接受脱离知识点另写的结论。证据不足知识点进入 `excludedKnowledgePointIds` 和顶层 `evidenceGaps`，不进入确定答案或准确率分母，也不阻断第四步。
