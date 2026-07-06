# 示例：表格识别（table-ocr）

适用：图片中的各类表格，如 Excel/Word 表格、票据单据、手写表格、检查报告单等。

---

## 用户输入示例

> 提取这张表格里的数据：`/Users/me/Desktop/report-table.png`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "table-ocr" --path "/Users/me/Desktop/report-table.png" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "tables": [
      {
        "cells": [
          {"row": 0, "col": 0, "text": "姓名"},
          {"row": 0, "col": 1, "text": "部门"},
          {"row": 1, "col": 0, "text": "张三"},
          {"row": 1, "col": 1, "text": "技术部"}
        ]
      }
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
python3 scripts/scan.py --scene "table-ocr" --url "https://example.com/table.png" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "table-ocr" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景

- Excel/Word 表格截图
- 票据单据中的表格
- 手写表格、检查报告单

## 不适合此场景

- 纯文字内容无表格 → 使用 `general-ocr`
- 需要转为 Excel 文件 → 使用 `yescan-transoffice-universal` 技能
