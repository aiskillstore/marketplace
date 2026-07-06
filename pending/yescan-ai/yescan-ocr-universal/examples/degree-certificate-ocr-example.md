# 示例：学位证识别（degree-certificate-ocr）

适用：学位证书图片，提取学校、姓名、专业、学历、证书编号等字段。

---

## 用户输入示例

> 识别这张学位证的内容：`/Users/me/Desktop/degree.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "degree-certificate-ocr" --path "/Users/me/Desktop/degree.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "school": "北京大学",
    "name": "赵六",
    "gender": "男",
    "major": "计算机科学与技术",
    "degree": "工学学士",
    "certificateNumber": "2023110101001234",
    "issueDate": "2023-06-25"
  }
}
```

## 用户可见结果

> 识别结果已返回，原样展示给用户。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "degree-certificate-ocr" --url "https://example.com/degree.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "degree-certificate-ocr" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景

- 学位证/毕业证照片
- 企业人才信息录入
- 学历核验

## 不适合此场景

- 营业执照 → 使用 `business-license-ocr`
- 其他证件 → 使用对应场景
