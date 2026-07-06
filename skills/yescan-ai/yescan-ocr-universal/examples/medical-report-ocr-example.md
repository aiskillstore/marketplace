# 示例：医疗报告单识别（medical-report-ocr）

适用：医疗报告单/化验单图片，提取检验项目、结果、参考值等字段。

---

## 用户输入示例

> 读一下这张化验单：`/Users/me/Desktop/medical-report.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "medical-report-ocr" --path "/Users/me/Desktop/medical-report.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "patientName": "王五",
    "reportDate": "2024-03-15",
    "items": [
      {"name": "白细胞计数", "result": "6.8", "unit": "10^9/L", "reference": "3.5-9.5"},
      {"name": "血红蛋白", "result": "145", "unit": "g/L", "reference": "130-175"}
    ]
  }
}
```

## 用户可见结果

> 识别结果已返回，原样展示给用户。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "medical-report-ocr" --url "https://example.com/report.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "medical-report-ocr" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景

- 血液检验报告单
- 各类医疗检查报告
- 健康数据分析

## 不适合此场景

- 处方笺手写内容 → 使用 `handwritten-ocr`
- 表格形式报告需还原格式 → 使用 `table-ocr`
