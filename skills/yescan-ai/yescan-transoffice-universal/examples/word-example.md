# 示例：图片转 Word（image-to-word）

适用：以文字段落为主的图片，例如会议纪要、合同、产品说明书、长文章截图。

---

## 用户输入示例

> 把这张会议记录的拍照转成 Word：`/Users/me/Desktop/meeting.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "image-to-word" --path "/Users/me/Desktop/meeting.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "FileBase64": "UEsDBBQABg...（已省略）",
    "path": "/tmp/1728912345_def456.docx"
  }
}
```

## 用户可见结果

> 已转换完成：`/tmp/1728912345_def456.docx`，可直接用 Word / WPS / Pages 打开编辑。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "image-to-word" --url "https://example.com/contract.png" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "image-to-word" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景的素材特征

- 段落型文字内容、标题层级清晰
- 中英文混排可以处理
- 含少量表格也可以，但更复杂的表格优先用 `image-to-excel`

## 不适合此场景

- 纯表格 → 用 `image-to-excel`
- 仅需保留版面外观，不需编辑文字 → 用 `image-to-pdf`
- 仅想提取纯文本 → 改用 `yescan-ocr-universal`
