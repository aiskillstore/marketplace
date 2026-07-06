# 示例：港澳通行证识别（travel-permit-ocr）

适用：港澳通行证图片，提取姓名、证件号码、签发机关、有效期限等字段。

---

## 用户输入示例

> 读一下这张港澳通行证：`/Users/me/Desktop/permit.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "travel-permit-ocr" --path "/Users/me/Desktop/permit.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "name": "王五",
    "permitNumber": "C12345678",
    "issueAuthority": "公安部出入境管理局",
    "issueDate": "2023-03-15",
    "expiryDate": "2033-03-14"
  }
}
```

## 用户可见结果

> 识别结果已返回，原样展示给用户。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "travel-permit-ocr" --url "https://example.com/permit.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "travel-permit-ocr" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景

- 港澳通行证照片
- 出入境管理、身份核验

## 不适合此场景

- 身份证 → 使用 `idcard-ocr`
- 护照或签证 → 暂不支持
