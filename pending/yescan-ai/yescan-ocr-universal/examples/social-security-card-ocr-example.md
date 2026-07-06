# 示例：社保卡识别（social-security-card-ocr）

适用：社保卡图片，提取姓名、社会保障号码、卡号等结构化字段。

---

## 用户输入示例

> 识别这张社保卡的信息：`/Users/me/Desktop/shebao.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "social-security-card-ocr" --path "/Users/me/Desktop/shebao.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "name": "李四",
    "socialSecurityNumber": "110108199203201234",
    "cardNumber": "A12345678",
    "gender": "女",
    "issueDate": "2020-06-01"
  }
}
```

## 用户可见结果

> 识别结果已返回，原样展示给用户。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "social-security-card-ocr" --url "https://example.com/shebao.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "social-security-card-ocr" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景

- 社保卡正面照片
- 需要提取社保号、卡号等字段
- 社保业务办理、身份核验

## 不适合此场景

- 身份证 → 使用 `idcard-ocr`
- 其他证件 → 使用对应场景
