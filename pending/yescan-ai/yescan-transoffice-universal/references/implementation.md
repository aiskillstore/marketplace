# 客户端脚本实现细节

本文档说明 `scripts/scan.py` 在调用夸克扫描王服务 API 之外所做的本地处理，以及最终返回给 Agent 的 JSON 结构。SKILL.md 只保留对 Agent 执行必要的摘要。

---

## 1. 执行流程

```
Agent
  └─▶ python3 scripts/scan.py --scene <X> --url|--path|--base64 <input>
         ├─ 1) common/validators.py        校验入参
         ├─ 2) common/ocr_client.py        请求 scan-business.quark.cn
         ├─ 3) common/result_handlers.py   解析 API 响应
         ├─ 4) common/file_saver.py        若含 FileBase64 → 解码落盘
         └─ 5) 标准输出返回 JSON
```

## 2. 响应 JSON 字段

成功响应（`code == "00000"`）一般形如：

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "FileBase64": "<...原始 base64...>",
    "path": "/tmp/1728912345_a1b2c3.docx"
  }
}
```

| 字段 | 来源 | 说明 |
|---|---|---|
| `code` | API | `"00000"` 表示成功，其他为错误码（见 TROUBLESHOOTING.md） |
| `message` | API | 文本描述 |
| `data.FileBase64` | API | 转换后文档的 BASE64 编码 |
| `data.path` | **客户端脚本追加** | `file_saver.py` 解码 `FileBase64` 后的本地文件绝对路径 |

> **关键约定**：`path` 字段由 `scan.py` 主动写入，与模型/平台无关，不依赖任何外部介入。Agent 只需直接展示该路径，无需自行解码 BASE64。

## 3. `file_saver.py` 的行为约束

- 仅当 `code == "00000"` 且 `data.FileBase64` 非空时触发保存
- 输出目录：系统临时目录（`tempfile.gettempdir()`，macOS/Linux 为 `/tmp`，Windows 为 `%TEMP%`）
- 文件名：`<unix_timestamp>_<6位随机串>.<ext>`，扩展名根据 scene 推断（`image-to-excel` → `.xlsx`，依此类推）
- 通过 magic byte 校验解码后的内容确为对应文档格式（防止中间错位）
- 写入失败会在响应中以 `code != "00000"` 形式返回，不会抛出未处理异常

## 4. `--platform` 字段的用途

`--platform <AGENT_NAME>` 仅用于在请求头中标识来源 Agent（如 `claudecode`、`qoderWork`、`coze`、`community` 等），便于服务端做调用统计与限流策略。**不影响识别效果，也不会作为业务参数透传给模型**。

## 5. 错误处理原则

- 网络/超时错误：返回 `code != "00000"`，`data` 为 `null`，由 Agent 原样透出
- 入参缺失：脚本本地直接返回错误，不发起 API 调用
- 不进行自动重试，避免重复扣额度与放大幻觉
