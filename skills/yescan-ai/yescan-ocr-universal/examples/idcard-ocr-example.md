# 示例：身份证识别（idcard-ocr）

适用：身份证图片，提取姓名、身份证号、地址等结构化字段。

---

## 用户输入示例

> 帮我读一下这张身份证：`/Users/me/Desktop/idcard.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "idcard-ocr" --path "/Users/me/Desktop/idcard.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "name": "张三",
    "gender": "男",
    "ethnicity": "汉",
    "birthday": "1990-01-15",
    "address": "北京市海淀区中关村大街1号",
    "idNumber": "110108199001150012"
  }
}
```

## 用户可见结果

> 识别结果已返回，原样展示给用户。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "idcard-ocr" --url "https://example.com/idcard.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "idcard-ocr" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景

- 身份证正面/反面照片
- 需要提取证件关键字段
- 身份核验、实名认证场景

## 不适合此场景

- 其他证件（驾驶证/行驶证）→ 使用对应场景
- 只需提取图片中文字 → 使用 `general-ocr`
