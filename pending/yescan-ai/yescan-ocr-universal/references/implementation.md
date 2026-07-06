# 实现细节：客户端脚本行为与响应字段

本文档描述 `scripts/scan.py` 的内部行为，供需要理解脚本工作原理的开发者参考。

---

## 1. 执行流程

```
用户/Agent 调用
  → python3 scripts/scan.py --scene <scene> --url/--path/--base64 <input>
  → 加载凭证（SCAN_WEBSERVICE_KEY）
  → 构建请求参数（aiApiKey, dataType, scene, dataBase64/dataUrl）
  → POST https://scan-business.quark.cn/vision
  → 解析响应 JSON
  → 输出结果到 stdout
```

## 2. 响应结构

### 成功响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    // 各场景返回不同字段，如：
    // general-ocr: "content" (纯文本)
    // table-ocr: "tables" (表格结构)
    // idcard-ocr: "name", "idNumber", "address" 等
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

## 3. 关键约定

- OCR 场景直接返回 API 原始响应的 `data` 字段，不做二次加工。
- **pic-translate 场景例外**：API 返回 `data.ImageInfo[0].ResImageBase64`，`save_translated_image_from_result` 处理后会将其解码落盘并注入 `data.translated_image_path`，同时剔除 `ImageInfo` 字段。
- 文件名格式：`<时间戳>_<16位随机十六进制串>.<扩展名>`（仅 pic-translate 涉及）。

## 4. 错误码速查

| 错误码 | 含义 | 常见原因 |
|---|---|---|
| A0100 | 凭证错误 | SCAN_WEBSERVICE_KEY 未配置或无效 |
| A0201 | 缺少图片输入 | 未提供 --url/--path/--base64 |
| A0211 | 配额不足 | API 额度用尽，需充值 |
| INVALID_SCENE | 场景名无效 | --scene 值不在 scene_configs.py 中 |
