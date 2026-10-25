# 解锁计划与差分结果的 JSON 结构

两个文件在我们的流水线里先后出现：

```
save_diff.py  →  xxx.diff.json   （观测：哪些字节变了）
infer_plan.py →  xxx-plan.json   （行动：具体要怎么改）
                 └─ rgss_save.py 也能直接产出同结构的 plan.json
apply_plan.py  消费 xxx-plan.json
```

## diff.json

```jsonc
{
  "kind": "allcg-diff",
  "version": 1,
  "created": "2026-10-26T04:26:52",
  "before": { "path": "A.save", "size": 617987, "sha256": "…" },
  "after":  { "path": "B.save", "size": 617987, "sha256": "…" },
  "params": { "gap": 8, "max_run": 64, "ignore": [] },
  "size_delta": 0,
  "runs": [
    {
      "offset": 790,            // 十进制字节偏移
      "length": 1,
      "before_hex": "46",       // 解锁前
      "after_hex":  "54",       // 解锁后
      "before_ascii": "F",      // 可打印时给出，否则为 null
      "after_ascii":  "T"
    }
  ]
}
```

> 偏移统一使用**十进制**存储，CLI 打印时才转成十六进制。

## plan.json

```jsonc
{
  "kind": "allcg-plan",
  "version": 1,
  "created": "2026-10-26T04:26:52",
  "target": "D:/games/x/Save01.rvdata2",   // 绝对路径
  "sha256_before": "…",                     // 写入前的完整性锚点
  "engine": "rgss3-switches",               // 可选，标记来源
  "description": "NTRPG2: 全部 RGSS 开关置 ON",

  "inference": {                            // 可选，记录推断依据便于复盘
    "start": 790, "stride": 1,
    "off_hex": "46", "on_hex": "54",
    "observed_offsets": [790, 792],
    "source_diffs": ["B.save"]
  },

  "patches": [
    {
      "offset": 790,
      "before_hex": "46",        // 期望的原字节
      "after_hex":  "54",        // 要写入的字节
      "require_before": true,    // true 时校验原字节，不匹配就跳过
      "note": "switch[2] -> true"
    }
  ],

  "backup_path": "D:/games/x/Save01.rvdata2.allcg-bak-20261026-042652",
  "backup_sha256": "…"
}
```

### 字段约定

| 字段 | 说明 |
|---|---|
| `target` | 必须是绝对路径。`apply_plan.py` 拒绝相对路径，防止在错误的 cwd 下动错文件 |
| `sha256_before` | 写入前校验。与目标不符**直接拒绝执行**，避免把针对旧存档的计划打到新存档上 |
| `patches[].require_before` | 建议保持 `true`：字节不匹配说明计划不适用于该存档，宁可跳过也不要写坏 |
| `patches[].before_hex` / `after_hex` | 长度相等时为等长替换（最安全）；不等长时整个文件会被重建 |
| `backup_path` / `backup_sha256` | 执行 apply 后回填。回滚依赖这两个字段，不要手改 |

### 长度变化的补丁

`after_hex` 比 `before_hex` 长时文件会被拉长，比它短时会被缩短。
`apply_plan.py` 默认拒绝，需要显式 `--allow-resize`。

安全的前提是目标格式的容忍度：

- **Ruby Marshal**：顺序自描述、无全局偏移表与校验和 → 长度变化安全
- **带长度前缀 / 内部指针 / 校验和的格式**（Marshal 的 `TYPE_USRDEF`、很多自定义二进制）→ 危险，改长度必须同步修前缀，否则存档损坏
