# 示例：驾驶证识别（driver-license-ocr）

适用：驾驶证图片，提取证号、姓名、住址、有效期、准驾车型等字段。

---

## 用户输入示例

> 读一下这张驾驶证：`/Users/me/Desktop/driver-license.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "driver-license-ocr" --path "/Users/me/Desktop/driver-license.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "name": "张三",
    "licenseNumber": "110108199001150012",
    "address": "北京市海淀区中关村大街1号",
    "vehicleClass": "C1",
    "issueDate": "2015-06-20",
    "expiryDate": "2025-06-20"
  }
}
```

## 用户可见结果

> 识别结果已返回，原样展示给用户。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "driver-license-ocr" --url "https://example.com/driver.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "driver-license-ocr" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景

- 驾驶证正本/副本照片
- 身份核验、交通管理

## 不适合此场景

- 行驶证 → 使用 `vehicle-license-ocr`
- 身份证 → 使用 `idcard-ocr`
