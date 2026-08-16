# Seedream 典型场景示例

本文档包含 Seedream Skill 的各种使用场景示例，供开发和测试参考。

---

## 场景 1: 简单文生图

**用户输入:**
```
给我画一只可爱的英短蓝猫，趴在洒满阳光的木质窗台上
```

**参数映射:**
```javascript
{
  prompt: "一只可爱的英短蓝猫，趴在洒满阳光的木质窗台上，背景是模糊的城市街景，暖色调，电影质感，8K分辨率",
  size: "2K",
  mode: "text-to-image",
  optimize: true
}
```

---

## 场景 2: 生成一组连贯图

**用户输入:**
```
生成一组共4张治愈系插画，主题为同一间咖啡馆的四季变迁
```

**参数映射:**
```javascript
{
  prompt: "生成4张一组的连贯插画：同一间温馨咖啡馆的四季变迁。第1张春天樱花飘落，第2张夏天阳光斑驳，第3张秋天金黄落叶，第4张冬天温暖雪景。统一吉卜力画风，保持构图和色彩一致，温暖明亮",
  size: "2K",
  sequential: true,  // 连贯组图模式
  count: 4,
  optimize: true
}
```

---

## 场景 3: 图生图

**用户输入:**
```
[发了一张图片] 参考这张图的构图，把风格换成赛博朋克，保持主体不变
```

**参数映射:**
```javascript
{
  prompt: "赛博朋克风格，霓虹灯，雨夜，高科技感，蓝色紫色调",
  reference_images: ["data:image/jpeg;base64,..."],
  mode: "image-to-image",
  reference_strength: 0.7,
  optimize: true
}
```

---

## 完整参数参考

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `prompt` | string | - | ✅ 图片描述提示词 |
| `mode` | string | `text-to-image` | 生成模式：`text-to-image` / `image-to-image` |
| `size` | string | `2K` | 分辨率：`2K` / `3K` / 具体像素值 |
| `sequential` | boolean | `false` | 是否生成一组连贯图片（风格保持一致） |
| `count` | integer | `4` | 连贯图数量（1~15张） |
| `reference_images` | array | - | 参考图片列表（最多 14 张） |
| `reference_strength` | number | `0.7` | 参考图影响强度（0~1） |
| `optimize` | boolean | `true` | 是否自动优化提示词 |
| `watermark` | boolean | `true` | 是否添加水印 |
| `stream` | boolean | `auto` | 流式输出（sequential=true 时自动开启） |
| `enable_web_search` | boolean | `false` | 是否开启联网搜索（实时新闻、赛事等） |
| `response_format` | string | `jpeg` | 图片格式：`png` / `jpeg` |

