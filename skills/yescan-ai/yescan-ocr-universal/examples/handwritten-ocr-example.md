# 示例：手写文档识别（handwritten-ocr）

适用：各类中英文手写内容，如学生作答、作文、会议记录、手写账单等。

---

## 用户输入示例

> 帮我把这张手写笔记转成文字：`/Users/me/Desktop/handnote.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "handwritten-ocr" --path "/Users/me/Desktop/handnote.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "content": "今天的会议重点：\n1. 产品上线时间定在下周三\n2. 需要完成用户测试报告\n3. UI 细节需要和设计确认"
  }
}
```

## 用户可见结果

> 识别结果已返回，原样展示给用户。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "handwritten-ocr" --url "https://example.com/note.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "handwritten-ocr" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景

- 手写笔记、作业、试卷作答
- 潦草字迹或非标准书写
- 会议白板手写内容

## 不适合此场景

- 印刷体文字 → 使用 `general-ocr`
- 需要提取表格结构 → 使用 `table-ocr`
