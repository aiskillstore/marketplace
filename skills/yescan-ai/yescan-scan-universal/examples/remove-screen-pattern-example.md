# 示例：图像去屏纹（remove-screen-pattern）

适用：翻拍屏幕（手机、电脑显示器、投影仪）时产生的摩尔纹、反光、彩色条纹。

---

## 用户输入示例

> 这张对着电脑屏幕拍的照片有很多波纹，请帮我消除屏纹：`/Users/me/Desktop/screen-photo.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "remove-screen-pattern" --path "/Users/me/Desktop/screen-photo.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "path": "/tmp/imgs/1728912345_f3g4h5.png"
  }
}
```

## 用户可见结果

> 屏纹已消除：`/tmp/imgs/1728912345_f3g4h5.png`，文字清晰无干扰。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "remove-screen-pattern" --url "https://example.com/moire.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "remove-screen-pattern" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景的素材特征

- 翻拍电脑/手机屏幕产生的摩尔纹
- 拍摄投影仪画面产生的彩色条纹
- 屏幕反光导致的局部过曝

## 不适合此场景

- 拍摄纸质文档的阴影 → `remove-shadow`
- 去除彩色文档底色 → `remove-background-color`
- 去除水印/Logo → `remove-watermark`
