# 实现细节：CLI 行为与响应字段

本文档描述 `yescan` CLI 的内部行为，供需要理解工作原理的开发者参考。

---

## 1. 执行流程

```
用户/Agent 调用
  → yescan --scene <scene> --path/--url <input> [--output <dir>] [--set key=value]
  → 加载凭证（SCAN_WEBSERVICE_KEY）
  → 根据 scene_configs 构建请求参数
  → POST https://scan-business.quark.cn/vision
  → 解析响应 JSON
  → 根据场景类型处理输出（stdout JSON / 落盘图片 / 落盘文档）
```

## 2. 响应结构

### 成功响应（OCR 类场景）

> **注意**：OCR 类场景的 `code` 为字符串 `"00000"`，而图像/文档类场景的 `code` 为数字 `0`，判断时需注意类型差异。

```json
{
  "code": "00000",
  "message": null,
  "data": {
    // 各场景返回不同字段，如：
    // general-ocr: "content" (纯文本)
    // table-ocr: "tables" (表格结构)
    // idcard-ocr: "name", "idNumber", "address" 等
  }
}
```

### 图像/文档类输出（落盘后）

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "path": "/tmp/imgs/<Unix时间戳>_<16位随机十六进制串>.<扩展名>"
  }
}
```

### 错误响应

```json
{
  "code": "A0100",
  "message": "SCAN_WEBSERVICE_KEY 未配置...",
  "data": null
}
```

## 3. 场景类型与输出行为

| 场景类型 | 输出方式 | 输出位置 |
|---|---|---|
| OCR 识别 | JSON 打印到 stdout | 不落盘（除 pic-translate）；指定 `--output` 时保存 JSON 到指定目录 |
| 图像增强 | 图片落盘 | 系统临时目录下的 `imgs/` 子目录（如 `/tmp/imgs/`）或 `--output` 目录 |
| 文档转换 | 文档落盘 | 系统临时目录下的 `documents/` 子目录（如 `/tmp/documents/`）或 `--output` 目录 |
| AIGC 生成 | 图片落盘 | 系统临时目录下的 `imgs/` 子目录（如 `/tmp/imgs/`）或 `--output` 目录 |

## 4. 关键约定

- OCR 场景直接返回 API 原始响应的 `data` 字段，不做二次加工。
- **pic-translate 场景例外**：API 返回 `data.ImageInfo[0].ResImageBase64`，CLI 将其解码落盘并注入 `data.translated_image_path`，同时剔除 `ImageInfo` 字段避免 base64 噪音。
- 图像/文档类输出的文件名格式：`<Unix时间戳>_<16位随机十六进制串>.<扩展名>`。
- 多步 Pipeline 时，前一步的 `data.path` 作为下一步的 `--path` 输入。

## 5. 错误码速查

| 错误码 | 含义 | 常见原因 |
|---|---|---|
| A0100 | 凭证错误 | SCAN_WEBSERVICE_KEY 未配置或无效 |
| A0201 | 缺少图片输入 | 未提供 --url 或 --path |
| A0211 | 配额不足 | API 额度用尽，需充值 |
| INVALID_SCENE | 场景名无效 | --scene 值不在可用场景列表中 |
| FILE_ERROR | 文件校验失败 | 文件不存在、超过 5MB 或格式不支持 |
