# 示例：火车票识别（train-ticket-ocr）

适用：火车票图片，提取出发站、到达站、车次、票价等字段。

---

## 用户输入示例

> 读一下这张火车票：`/Users/me/Desktop/ticket.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "train-ticket-ocr" --path "/Users/me/Desktop/ticket.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "ticketNumber": "E123456789",
    "departure": "北京南",
    "arrival": "上海虹桥",
    "trainNumber": "G1",
    "departureTime": "2024-03-15 08:00",
    "price": "553.00",
    "seatType": "二等座",
    "passengerName": "张三"
  }
}
```

## 用户可见结果

> 识别结果已返回，原样展示给用户。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "train-ticket-ocr" --url "https://example.com/ticket.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "train-ticket-ocr" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景

- 纸质/电子火车票照片
- 企业出行报销

## 不适合此场景

- 增值税发票 → 使用 `vat-invoice-ocr`
- 机票/其他票据 → 暂不支持
