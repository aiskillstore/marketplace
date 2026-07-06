# 示例：公式识别（formula-ocr）

适用：数学/化学公式图片，解析为 LaTeX 代码或结构化数据。

---

## 用户输入示例

> 把这张公式图片转成 LaTeX：`/Users/me/Desktop/formula.png`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "formula-ocr" --path "/Users/me/Desktop/formula.png" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "content": "\\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}"
  }
}
```

## 用户可见结果

> 识别结果已返回，原样展示给用户。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "formula-ocr" --url "https://example.com/formula.png" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "formula-ocr" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景

- 数学公式（分数、矩阵、分段函数）
- 化学方程式
- 学术论文中的公式截图

## 不适合此场景

- 纯文字题目 → 使用 `question-ocr`
- 手写内容（非公式）→ 使用 `handwritten-ocr`
