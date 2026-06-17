# 示例：图像去阴影（remove-shadow）

适用：文档或图像中因拍摄角度、光线产生的阴影，需要获得均匀亮度的扫描效果。同类场景：去屏纹（remove-screen-pattern）、去底色（remove-background-color）。

---

## 用户输入示例

> 这张纸拍出来有大片阴影，请帮我去除阴影变平整：`/Users/me/Desktop/shadow-doc.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "remove-shadow" --path "/Users/me/Desktop/shadow-doc.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "path": "/tmp/imgs/1728912345_s1t2u3.png"
  }
}
```

## 用户可见结果

> 阴影已去除：`/tmp/imgs/1728912345_s1t2u3.png`，亮度均匀、文字清晰。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "remove-shadow" --url "https://example.com/shadow.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "remove-shadow" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景的素材特征

- 手机拍文档时手/手机遮挡产生的阴影
- 光线不均匀导致局部偏暗
- 书页翻拍时书脊处的阴影

## 相关场景

- 去屏纹（翻拍屏幕的摩尔纹）→ `remove-screen-pattern`
- 去底色（彩色背景转白底黑字）→ `remove-background-color`
- 去水印 → `remove-watermark`
- 去手写 → `remove-handwriting`
