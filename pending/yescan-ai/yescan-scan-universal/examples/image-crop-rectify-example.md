# 示例：图像裁剪矫正（image-crop-rectify）

适用：拍歪的文档照片，需要透视校正、水平对齐并裁掉多余边缘。

---

## 用户输入示例

> 这张照片拍歪了，帮我把文档扶正并裁掉多余的桌子背景：`/Users/me/Desktop/tilted-doc.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "image-crop-rectify" --path "/Users/me/Desktop/tilted-doc.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "path": "/tmp/imgs/1728912345_v4w5x6.png"
  }
}
```

## 用户可见结果

> 已矫正裁剪：`/tmp/imgs/1728912345_v4w5x6.png`，文档规整为标准矩形。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "image-crop-rectify" --url "https://example.com/tilted.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "image-crop-rectify" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景的素材特征

- 倾斜拍摄的文档/合同/书页
- 有透视变形的白板/黑板拍照
- 包含多余桌面/背景边缘的文档照片

## 不适合此场景

- 需要去除阴影/水印等瑕疵 → 使用对应的 `remove-*` 场景
- 需要画质增强 → `image-hd-enhance`
- 需要转为 Office 文档 → 使用 `yescan-transoffice-universal` 技能
