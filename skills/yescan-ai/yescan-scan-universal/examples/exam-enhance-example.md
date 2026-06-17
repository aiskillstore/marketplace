# 示例：考试增强（exam-enhance）

适用：手写笔记、试卷、教材等学习资料的照片，需要去噪、背景纯净化。

---

## 用户输入示例

> 把这张拍糊了的试卷变清晰，去掉背景噪音：`/Users/me/Desktop/exam-photo.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "exam-enhance" --path "/Users/me/Desktop/exam-photo.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "path": "/tmp/imgs/1728912345_e2f3g4.png"
  }
}
```

## 用户可见结果

> 试卷已增强：`/tmp/imgs/1728912345_e2f3g4.png`，背景纯净、文字清晰，可直接打开查看。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "exam-enhance" --url "https://example.com/exam.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "exam-enhance" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景的素材特征

- 手写笔记照片（背景有格线、灰底）
- 试卷拍照（光线不均、有阴影）
- 教材翻拍（有手指遮挡边缘、弯曲变形）

## 不适合此场景

- 仅需提升清晰度而无需去噪 → `image-hd-enhance`
- 需要去除手写笔迹还原空白卷 → `remove-handwriting`
- 需要提取文字内容 → 使用 `yescan-ocr-universal` 技能
