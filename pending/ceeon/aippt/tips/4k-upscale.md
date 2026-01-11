# 4K 高清化

将低分辨率图片增强为 4K 超清图片。

## 完整流程

### 1. 上传图片获取 URL

优先使用 PicGo：
```bash
curl -s -X POST "http://127.0.0.1:36677/upload" \
  -H "Content-Type: application/json" \
  -d '{"list":["/绝对路径/image.png"]}'
```

### 2. 调用 4K 模型生成

```bash
curl -s -X POST "https://ismaque.org/v1/images/generations" \
  -H "Authorization: Bearer API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3-pro-image-preview-4k",
    "prompt": "图片URL 4K增强",
    "size": "3:4",
    "n": 1
  }'
```

### 3. 下载保存

从响应中提取 `data[0].url`，下载到本地：
```bash
curl -s -o "output_4k.png" "生成的图片URL"
```

## 尺寸选择

根据原图比例选择合适的 size：

| 原图比例 | size 参数 | 输出分辨率 |
|---------|----------|-----------|
| 竖版（手机截图） | `3:4` | 3584 × 4800 |
| 横版 | `4:3` | 4800 × 3584 |
| 正方形 | `1:1` | 4096 × 4096 |
| 宽屏 | `16:9` | 4800 × 2704 |

## 批量处理

可以并行处理多张图片：
1. 先批量上传所有图片到图床
2. 并行调用 API 生成 4K 版本
3. 批量下载结果

## 提示词技巧

- 简洁有效：`4K增强`
- 保持内容：`4K超清增强，保持内容不变`
- 如需修改文字，参考 `chinese-text.md`
