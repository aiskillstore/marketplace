# 示例：通用文字提取（general-ocr）

适用：通用文字识别（兜底场景），当不属于上述任何具体场景时使用。

---

## 用户输入示例

> 把这张图转成文字：`/Users/me/Desktop/screenshot.png`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "general-ocr" --path "/Users/me/Desktop/screenshot.png" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "content": "2024年度工作总结\n\n一、项目进展\n本年度共完成 12 个项目交付，客户满意度达 95%。\n\n二、团队建设\n新增成员 5 人，团队规模扩展至 20 人。"
  }
}
```

## 用户可见结果

> 识别结果已返回，原样展示给用户。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "general-ocr" --url "https://example.com/text-image.png" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "general-ocr" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景

- 截图中的文字
- 印刷体文档（无特定类型）
- 用户仅表达"提取文字"意图

## 不适合此场景

- 手写内容 → 使用 `handwritten-ocr`
- 表格数据 → 使用 `table-ocr`
- 证件/票据 → 使用对应的专用场景
