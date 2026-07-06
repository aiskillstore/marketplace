# 示例：营业执照识别（business-license-ocr）

适用：营业执照图片，提取统一社会信用代码、名称、法定代表人、经营范围等字段。

---

## 用户输入示例

> 识别这张营业执照：`/Users/me/Desktop/license.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "business-license-ocr" --path "/Users/me/Desktop/license.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "creditCode": "91110108MA01ABCD5X",
    "companyName": "北京某某科技有限公司",
    "type": "有限责任公司",
    "legalRepresentative": "张三",
    "registeredCapital": "1000万元",
    "businessScope": "技术开发、技术咨询、技术服务"
  }
}
```

## 用户可见结果

> 识别结果已返回，原样展示给用户。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "business-license-ocr" --url "https://example.com/license.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "business-license-ocr" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景

- 营业执照正本/副本照片
- 企业身份核验
- 工商注册自动化

## 不适合此场景

- 学位证 → 使用 `degree-certificate-ocr`
- 身份证 → 使用 `idcard-ocr`
