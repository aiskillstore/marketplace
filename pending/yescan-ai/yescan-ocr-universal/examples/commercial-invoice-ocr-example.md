# 示例：英文发票识别（commercial-invoice-ocr）

适用：英文商业发票图片，提取发票号、日期、买卖双方信息、金额等字段。

---

## 用户输入示例

> 提取这张英文发票的信息：`/Users/me/Desktop/commercial-invoice.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "commercial-invoice-ocr" --path "/Users/me/Desktop/commercial-invoice.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "invoiceNumber": "INV-2024-0315",
    "invoiceDate": "March 15, 2024",
    "seller": "ABC Corp.",
    "buyer": "XYZ Ltd.",
    "totalAmount": "USD 5,280.00",
    "items": [
      {"description": "Widget A", "quantity": "100", "unitPrice": "52.80"}
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
python3 scripts/scan.py --scene "commercial-invoice-ocr" --url "https://example.com/invoice-en.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "commercial-invoice-ocr" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景

- 英文商业发票
- 跨境贸易单证处理
- 海外费用报销

## 不适合此场景

- 中文增值税发票 → 使用 `vat-invoice-ocr`
- 火车票 → 使用 `train-ticket-ocr`
