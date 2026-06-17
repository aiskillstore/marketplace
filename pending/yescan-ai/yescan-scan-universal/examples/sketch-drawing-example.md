# 示例：素描速写（sketch-drawing）

适用：将普通照片转换为铅笔素描或速写风格图像。

---

## 用户输入示例

> 把这张人物照片转换成铅笔素描风格：`/Users/me/Desktop/portrait.jpg`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "sketch-drawing" --path "/Users/me/Desktop/portrait.jpg" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "path": "/tmp/imgs/1728912345_m4n5p6.png"
  }
}
```

## 用户可见结果

> 素描转换完成：`/tmp/imgs/1728912345_m4n5p6.png`，可直接打开查看。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "sketch-drawing" --url "https://example.com/photo.jpg" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "sketch-drawing" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景的素材特征

- 人物肖像照（半身/全身均可）
- 风景照片需要艺术效果
- 静物/建筑照转手绘风

## 相关场景

- 提取线稿（去掉颜色只留轮廓线条）→ `extract-lineart`
- 画质增强（不改变风格只提升清晰度）→ `image-hd-enhance`
