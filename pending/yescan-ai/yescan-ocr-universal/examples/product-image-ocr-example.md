# 示例：商品图片识别（product-image-ocr）

适用：商品图片或包装照片，提取商品名称、品牌、规格、成分等文字信息。

---

## 用户输入示例

> 这是什么商品？帮我识别一下：`/Users/me/Desktop/product.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "product-image-ocr" --path "/Users/me/Desktop/product.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "content": "品牌：农夫山泉\n品名：天然矿泉水\n规格：550ml\n产地：浙江省杭州市\n保质期：24个月"
  }
}
```

## 用户可见结果

> 识别结果已返回，原样展示给用户。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "product-image-ocr" --url "https://example.com/product.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "product-image-ocr" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景

- 商品包装、标签照片
- 商品信息录入
- 品牌/规格识别

## 不适合此场景

- 纯文字内容 → 使用 `general-ocr`
- 发票/票据 → 使用对应场景
