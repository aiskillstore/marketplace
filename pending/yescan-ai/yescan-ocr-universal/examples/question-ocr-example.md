# 示例：题目识别（question-ocr）

适用：习题/考题图片，提取题目文本（不含解答），保留题号和题干结构。

---

## 用户输入示例

> 提取这道题的关键信息：`/Users/me/Desktop/exam-question.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "question-ocr" --path "/Users/me/Desktop/exam-question.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "content": "3. 已知函数 f(x) = x² - 2x + 1，求：\n(1) f(x) 的最小值\n(2) 当 x ∈ [-1, 3] 时，f(x) 的值域"
  }
}
```

## 用户可见结果

> 识别结果已返回，原样展示给用户。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "question-ocr" --url "https://example.com/question.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "question-ocr" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景

- 试卷/练习册中的题目
- 教育题库构建
- 仅需题干文本（不含答案）

## 不适合此场景

- 需要识别公式 → 使用 `formula-ocr`
- 手写作答内容 → 使用 `handwritten-ocr`
