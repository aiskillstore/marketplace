# 示例：图片翻译（pic-translate）

适用：将图片中的文字翻译为其他语言，生成保留原图排版的译文图片。

---

## 用户输入示例

> 帮我翻译一下这张英文菜单：`/Users/me/Desktop/menu.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "pic-translate" --path "/Users/me/Desktop/menu.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "translated_image_path": "/tmp/imgs/1728912345_a1b2c3d4e5f67890.png",
    "content": "Menu\nCoffee - $5\nTea - $3"
  }
}
```

## 用户可见结果

> 翻译完成，译图已保存：`/tmp/imgs/1728912345_a1b2c3d4e5f67890.png`，可直接打开查看。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "pic-translate" --url "https://example.com/menu.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "pic-translate" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景

- 外文菜单、路标、说明书翻译
- 需要保留原图排版的翻译
- 跨语言沟通场景

## 不适合此场景

- 只需提取文字不翻译 → 使用 `general-ocr`
- 需要增强图片画质 → 使用 `yescan-scan-universal` 技能
