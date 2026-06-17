# 示例：文档去底色（remove-background-color）

适用：带彩色背景的文档截图/照片，需要转换为纯白背景 + 黑色文字的清晰版本。

---

## 用户输入示例

> 把这张红头文件的红色背景去掉，变成白底黑字：`/Users/me/Desktop/red-doc.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "remove-background-color" --path "/Users/me/Desktop/red-doc.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "path": "/tmp/imgs/1728912345_j6k7l8.png"
  }
}
```

## 用户可见结果

> 底色已去除：`/tmp/imgs/1728912345_j6k7l8.png`，纯白背景、黑色文字，便于阅读和打印。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "remove-background-color" --url "https://example.com/colored-bg.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "remove-background-color" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景的素材特征

- 红头文件/彩色背景公文
- 灰色/黄色底色的截图
- 古文书页（米色/棕色背景）

## 不适合此场景

- 去除拍摄阴影 → `remove-shadow`
- 去除屏幕摩尔纹 → `remove-screen-pattern`
- 去除水印/Logo → `remove-watermark`
