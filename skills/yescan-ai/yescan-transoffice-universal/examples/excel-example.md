# 示例：图片转 Excel（image-to-excel）

适用：包含表格、报表、销售/财务数据的图片。

---

## 用户输入示例

> 帮我把这张财务报表截图转成 Excel：`/Users/me/Desktop/finance.png`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "image-to-excel" --path "/Users/me/Desktop/finance.png" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "FileBase64": "UEsDBBQABg...（已省略）",
    "path": "/tmp/1728912345_a1b2c3.xlsx"
  }
}
```

## 用户可见结果

> 已转换完成：`/tmp/1728912345_a1b2c3.xlsx`，可直接用 Excel / WPS / Numbers 打开。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "image-to-excel" --url "https://example.com/sales.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "image-to-excel" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景的素材特征

- 含明显的表格线 / 行列结构
- 单元格内容清晰、非倾斜
- 单页表格优先；多页或合并单元格也支持但还原率会下降

## 不适合此场景

- 纯文本段落 → 用 `image-to-word`
- 复杂版面（图文混排）+ 仅需视觉归档 → 用 `image-to-pdf`
