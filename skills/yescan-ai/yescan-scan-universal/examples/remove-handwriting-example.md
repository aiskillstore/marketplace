# 示例：图像去手写（remove-handwriting）

适用：将已填写的手写笔迹从印刷文档图像中清除，还原为干净空白文档。

---

## 用户输入示例

> 把这张做过的试卷上的手写答案去掉，还原成空白卷子：`/Users/me/Desktop/answered-exam.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "remove-handwriting" --path "/Users/me/Desktop/answered-exam.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "path": "/tmp/imgs/1728912345_p8q9r0.png"
  }
}
```

## 用户可见结果

> 手写内容已去除：`/tmp/imgs/1728912345_p8q9r0.png`，印刷文字完整保留。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "remove-handwriting" --url "https://example.com/filled-form.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "remove-handwriting" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景的素材特征

- 已填写答案的试卷/作业
- 有手写批注的印刷文档
- 有涂鸦/划痕的书页

## 不适合此场景

- 去除水印/Logo → `remove-watermark`
- 去除拍摄阴影 → `remove-shadow`
- 试卷整体增强（保留手写内容）→ `exam-enhance`
