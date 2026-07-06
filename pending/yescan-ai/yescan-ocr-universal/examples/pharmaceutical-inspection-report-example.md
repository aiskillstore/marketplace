# 示例：药检报告识别（pharmaceutical-inspection-report）

适用：药品检验报告单图片，提取药品名称、批号、检验项目、检验结果、标准值及结论等字段。

---

## 用户输入示例

> 识别这张药检报告的内容：`/Users/me/Desktop/pharma-report.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "pharmaceutical-inspection-report" --path "/Users/me/Desktop/pharma-report.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "drugName": "阿莫西林胶囊",
    "batchNumber": "20240315",
    "manufacturer": "某某制药有限公司",
    "items": [
      {"name": "性状", "result": "白色粉末", "standard": "白色或类白色粉末", "conclusion": "合格"},
      {"name": "含量测定", "result": "98.5%", "standard": "95.0%-105.0%", "conclusion": "合格"}
    ],
    "overallConclusion": "本品按国家药品标准检验，结果符合规定"
  }
}
```

## 用户可见结果

> 识别结果已返回，原样展示给用户。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "pharmaceutical-inspection-report" --url "https://example.com/pharma.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "pharmaceutical-inspection-report" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景

- 药品检验报告单照片
- 药品质量追溯
- GMP 合规审计

## 不适合此场景

- 医疗检验报告（血常规等）→ 使用 `medical-report-ocr`
- 表格形式报告需还原格式 → 使用 `table-ocr`
