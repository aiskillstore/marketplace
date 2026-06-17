# 示例：提取线稿（extract-lineart）

适用：从图片中提取纯线条轮廓，去掉颜色，用于上色练习或艺术创作。

---

## 用户输入示例

> 从这张动漫图片中提取纯线稿，去掉颜色：`/Users/me/Desktop/anime-character.png`

## Agent 应执行的命令

```bash
python3 scripts/scan.py --scene "extract-lineart" --path "/Users/me/Desktop/anime-character.png" --platform "claudecode"
```

## 期望响应

```json
{
  "code": "00000",
  "message": "success",
  "data": {
    "path": "/tmp/imgs/1728912345_y7z8a9.png"
  }
}
```

## 用户可见结果

> 线稿已提取：`/tmp/imgs/1728912345_y7z8a9.png`，纯黑白线条，可用于上色练习。

---

## 多种输入形式

**URL 类型：**

```bash
python3 scripts/scan.py --scene "extract-lineart" --url "https://example.com/illustration.png" --platform "claudecode"
```

**BASE64 类型：**

```bash
python3 scripts/scan.py --scene "extract-lineart" --base64 "iVBORw0KGgo..." --platform "claudecode"
```

## 适合此场景的素材特征

- 动漫/插画图片需要提取轮廓线
- 实物照片转黑白线条图
- 设计稿提取结构线用于二次创作

## 相关场景

- 转素描风格（保留明暗关系）→ `sketch-drawing`
- 画质增强（不改变风格）→ `image-hd-enhance`
