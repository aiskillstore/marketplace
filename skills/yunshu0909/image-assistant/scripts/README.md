# APIMart 批量出图（本地脚本）

这个目录用于“阶段4 Prompt Pack 已确认后”的批量出图。

## 1) 配置

把配置写到 `scripts/apimart.env`（建议只放在本地，不要公开或提交）：

- 示例：`scripts/apimart.env.example`

## 2) 输入（JSONL）

一行一张图（每行一个 JSON），最少需要 `prompt`：

```jsonl
{"id":"01","prompt":"...","size":"16:9","n":1,"resolution":"2K","model":"gemini-3-pro-image-preview","pad_url":""}
```

## 3) 运行

```bash
python3 scripts/apimart_batch_generate.py \
  --config scripts/apimart.env \
  --input out/apimart.requests.jsonl
```

输出默认写到 `outputs/`。输出目录内只会包含：

- `run.json`：本次批量的**请求 + 返回（含 task 轮询结果/图片 URL）**汇总
- 最终图片文件：与 `id` 对应命名（不再生成 `requests/`、`responses/` 等子目录）
