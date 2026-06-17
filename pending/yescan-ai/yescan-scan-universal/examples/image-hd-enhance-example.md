# 示例：画质增强（image-hd-enhance）

适用：模糊、昏暗、老旧或低分辨率的照片/文档图片。

---

## 用户输入示例

> 这张文档照片太模糊了，帮我增强一下画质：`/Users/me/Desktop/blurry-doc.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "image-hd-enhance" --path "/Users/me/Desktop/blurry-doc.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "path": "/tmp/imgs/1728912345_a1b2c3.png"
  }
}
```

## 用户可见结果

> 已增强完成：`/tmp/imgs/1728912345_a1b2c3.png`，可直接打开查看。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "image-hd-enhance" --url "https://example.com/blurry.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "image-hd-enhance" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景的素材特征

- 图片内容模糊、光线不足、对比度低
- 老旧照片需要修复清晰度
- 低分辨率文档照片需提升可读性

## 不适合此场景

- 需要去除特定瑕疵（水印/手写/阴影）→ 使用对应的 `remove-*` 场景
- 需要转换为 Office 文档 → 使用 `yescan-transoffice-universal` 技能
- 需要提取文字 → 使用 `yescan-ocr-universal` 技能
