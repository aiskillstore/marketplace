# Effort 參數（Beta）| Effort Parameter (Beta)

Effort 參數控制模型花費 token 的積極程度。

The effort parameter controls how eagerly the model spends tokens.

**遷移時添加設定為 `"high"` 的 effort。這是 Opus 4.5 最佳效能的預設配置。**

**Add effort set to `"high"` during migration. This is the default configuration for best performance with Opus 4.5.**

Effort 影響所有類型的 token：思考、文字回應和函數呼叫。

Effort affects all token types: thinking, text responses, and function calls.

## Effort 級別 | Effort Levels

| Effort 級別 Level | 用途 Purpose |
|-------------------|--------------|
| `high` | 最佳效能，深度推理（預設）Best performance, deep reasoning (default) |
| `medium` | 成本/延遲與效能的平衡 Balance of cost/latency vs. performance |
| `low` | 簡單、大量的查詢；顯著節省 token Simple, high-volume queries; significant token savings |

## 實作方式 | Implementation

需要在 API 呼叫中使用 beta 標誌 `effort-2025-11-24`。

Requires beta flag `effort-2025-11-24` in API calls.

### Python SDK

```python
response = client.messages.create(
    model="claude-opus-4-5-20251101",
    max_tokens=1024,
    betas=["effort-2025-11-24"],
    output_config={
        "effort": "high"  # or "medium" or "low" | 或 "medium" 或 "low"
    },
    messages=[...]
)
```

### TypeScript SDK

```typescript
const response = await client.messages.create({
    model: "claude-opus-4-5-20251101",
    max_tokens: 1024,
    betas: ["effort-2025-11-24"],
    output_config: {
        effort: "high"  // or "medium" or "low" | 或 "medium" 或 "low"
    },
    messages: [...]
});
```

### 原始 API | Raw API

```json
{
    "model": "claude-opus-4-5-20251101",
    "max_tokens": 1024,
    "anthropic-beta": "effort-2025-11-24",
    "output_config": {
        "effort": "high"
    },
    "messages": [...]
}
```

## Effort 與 Thinking Budget 的關係 | Effort vs. Thinking Budget

Effort 獨立於 thinking budget 分配運作。高 effort 但沒有 thinking token 會產生更多輸出 token，但不會有內部推理 token。

Effort operates independently from thinking budget allocation. High effort without thinking tokens produces more output tokens but no internal reasoning tokens.

## 建議 | Recommendations

1. 先決定 effort 級別，然後設定 thinking budget
   Determine effort level first, then set thinking budget
2. 最佳結果：高 effort + 高 thinking budget
   Optimal results: high effort + high thinking budget
3. 成本/延遲優化：中等 effort
   Cost/latency optimization: medium effort
4. 簡單大量查詢：低 effort
   Simple high-volume queries: low effort
