# 示例：增值税发票识别（vat-invoice-ocr）

适用：增值税发票图片，提取销售方、购买方、金额、税额等字段。

---

## 用户输入示例

> 提取这张增值税发票的信息：`/Users/me/Desktop/invoice.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "vat-invoice-ocr" --path "/Users/me/Desktop/invoice.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "invoiceCode": "044001900111",
    "invoiceNumber": "12345678",
    "invoiceDate": "2024-03-15",
    "sellerName": "杭州某科技有限公司",
    "buyerName": "北京某集团有限公司",
    "totalAmount": "10000.00",
    "tax": "1300.00",
    "totalWithTax": "11300.00"
  }
}
```

## 用户可见结果

> 识别结果已返回，原样展示给用户。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "vat-invoice-ocr" --url "https://example.com/invoice.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "vat-invoice-ocr" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景

- 增值税专用/普通发票
- 财务报销自动化
- 税务管理

## 不适合此场景

- 英文发票 → 使用 `commercial-invoice-ocr`
- 火车票 → 使用 `train-ticket-ocr`
