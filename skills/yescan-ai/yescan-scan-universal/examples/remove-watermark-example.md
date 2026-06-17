# 示例：图像去水印（remove-watermark）

适用：图片中有文字水印、Logo 标记等需要去除的干扰元素。

---

## 用户输入示例

> 帮我把这张图片右下角的网站水印去掉：`/Users/me/Desktop/photo-with-watermark.png`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "remove-watermark" --path "/Users/me/Desktop/photo-with-watermark.png" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "path": "/tmp/imgs/1728912345_x7y8z9.png"
  }
}
```

## 用户可见结果

> 水印已去除：`/tmp/imgs/1728912345_x7y8z9.png`，可直接打开查看。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "remove-watermark" --url "https://example.com/watermarked.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "remove-watermark" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景的素材特征

- 图片含有半透明文字水印
- 图片含有 Logo 标记覆盖
- 图片含有时间戳/网址等叠加标记

## 相关场景

- 去除手写笔迹 → `remove-handwriting`
- 去除拍摄阴影 → `remove-shadow`
- 去除屏幕摩尔纹 → `remove-screen-pattern`
- 去除文档底色 → `remove-background-color`
