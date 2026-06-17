# 示例：扫描文件（scan-document）

适用：通用文档图片优化（兜底场景），当不属于上述任何具体场景时使用。

---

## 用户输入示例

> 优化一下这张文档图片，让它看起来更专业：`/Users/me/Desktop/document.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "scan-document" --path "/Users/me/Desktop/document.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "path": "/tmp/imgs/1728912345_n9m0p1.png"
  }
}
```

## 用户可见结果

> 文档已优化：`/tmp/imgs/1728912345_n9m0p1.png`，画面更清晰整洁。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "scan-document" --url "https://example.com/doc.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "scan-document" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景的素材特征

- 通用文档照片（无明确的特定瑕疵类型）
- 用户仅表达"优化"意图，未指定具体处理方式
- 杂志/书籍/通知等混合内容页面

## 不适合此场景

- 有明确瑕疵（阴影/水印/手写）→ 使用对应的 `remove-*` 场景
- 需要合同专用优化 → `scan-contract`
- 需要提取文字 → 使用 `yescan-ocr-universal` 技能
- 需要转为 Office 文档 → 使用 `yescan-transoffice-universal` 技能
