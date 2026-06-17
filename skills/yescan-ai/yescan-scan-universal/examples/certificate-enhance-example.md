# 示例：证件票据增强（certificate-enhance）

适用：模糊、光线不佳或细节不清的证件及票据照片。

---

## 用户输入示例

> 这张身份证照片有点模糊，请优化一下让字迹更清晰：`/Users/me/Desktop/id-card.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "certificate-enhance" --path "/Users/me/Desktop/id-card.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "path": "/tmp/imgs/1728912345_h5j6k7.png"
  }
}
```

## 用户可见结果

> 证件照已增强：`/tmp/imgs/1728912345_h5j6k7.png`，文字与关键信息清晰可辨。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "certificate-enhance" --url "https://example.com/invoice.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "certificate-enhance" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景的素材特征

- 身份证、护照、驾照等证件照片
- 发票、收据等票据照片
- 光线不足或反光导致细节模糊

## 不适合此场景

- 需要识别证件上的文字信息 → 使用 `yescan-ocr-universal` 技能
- 需要去除手写批注 → `remove-handwriting`
- 整体画质增强（非证件类）→ `image-hd-enhance`
