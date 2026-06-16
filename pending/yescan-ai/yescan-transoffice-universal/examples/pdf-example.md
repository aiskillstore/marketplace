# 示例：图片转 PDF（image-to-pdf）

适用：手写笔记、合同照片、设备铭牌、白板草图等需以 PDF 形式归档的内容。

---

## 用户输入示例

> 把这张手写课堂笔记图片转成 PDF：`/Users/me/Desktop/notes.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "image-to-pdf" --path "/Users/me/Desktop/notes.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "FileBase64": "JVBERi0xLjQKJ...（已省略）",
    "path": "/tmp/1728912345_ghi789.pdf"
  }
}
```

## 用户可见结果

> 已转换完成：`/tmp/1728912345_ghi789.pdf`，PDF 保留了原始版面与手写视觉效果。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "image-to-pdf" --url "https://example.com/whiteboard.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "image-to-pdf" --base64 "/9j/4AAQSkZJRg..." --platform "claudecode"
```

## 适合此场景的素材特征

- 需要保持与原图一致的视觉外观（手写、签名、印章）
- 图文混排、版面复杂、不需要后续编辑文字
- 准备纳入文档管理系统 / 邮件附件 / 法务归档

## 不适合此场景

- 需要后续编辑表格 → 用 `image-to-excel`
- 需要编辑文字段落 → 用 `image-to-word`
- 图片本身有水印 / 阴影 → 先用 `yescan-scan-universal` 清理
