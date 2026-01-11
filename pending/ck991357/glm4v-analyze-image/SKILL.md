---
name: glm4v_analyze_image
description: 智谱AI的视觉语言模型，用于图像分析、内容识别和视觉问答
tool_name: glm4v_analyze_image
category: vision
priority: 7
tags: ["image-analysis", "vision", "recognition", "visual-qa", "multimodal"]
version: 1.0
---

# GLM-4V图像分析工具指南

## 核心能力
- 图像内容识别和描述
- 视觉问答和推理
- 图像细节分析
- 多模态理解和生成

## 调用规范
```json
{
  "tool_name": "glm4v_analyze_image",
  "parameters": {
    "model": "glm-4v-flash",
    "image_url": "图片URL",
    "prompt": "分析提示语"
  }
}
```

以下是调用 `glm4v_analyze_image` 工具的**正确**和**错误**示例。请务必遵循正确格式。

## ✅ 正确示例
```json
{"model": "glm-4v-flash", "image_url": "https://path/to/image.jpg", "prompt": "Describe this image."}
```

## ❌ 错误示例 (请避免以下常见错误)

- **缺少引号或逗号:** 
  ```json
  {"model": "glm-4v-flash", "image_url": "https://path/to/image.jpg", "prompt": "Describe this image."}
  ```
  (缺少 `}`)

- **参数名错误:** 
  ```json
  {"img_url": "https://path/to/image.jpg"}
  ```
  (应为 "image_url" 而非 "img_url")

- **模型名称错误:** 
  ```json
  {"model": "glm4v-flash", "image_url": "https://path/to/image.jpg", "prompt": "Describe this image."}
  ```
  (应为 "glm-4v-flash")
  
## 关键指令
1. **模型选择**: 使用 `glm-4v-flash` 模型
2. **图片格式**: 支持常见图片格式（JPEG, PNG, WebP等）
3. **提示语设计**: 清晰具体的分析指令
4. **URL有效性**: 确保图片URL可公开访问

## 使用场景

### 图像描述
```json
{
  "tool_name": "glm4v_analyze_image",
  "parameters": {
    "model": "glm-4v-flash", 
    "image_url": "https://example.com/image.jpg",
    "prompt": "详细描述这张图片的内容"
  }
}
```

### 视觉问答
```json
{
  "tool_name": "glm4v_analyze_image",
  "parameters": {
    "model": "glm-4v-flash",
    "image_url": "https://example.com/image.jpg", 
    "prompt": "图片中有多少人？他们在做什么？"
  }
}
```

### 细节分析
```json
{
  "tool_name": "glm4v_analyze_image",
  "parameters": {
    "model": "glm-4v-flash",
    "image_url": "https://example.com/image.jpg",
    "prompt": "分析图片中的文字内容和技术细节"
  }
}
```

## 最佳实践

### 提示语设计
- **具体明确**: "描述图片中人物的动作和表情"
- **任务导向**: "识别图片中的所有物体并分类"
- **细节要求**: "注意颜色、形状、空间关系等细节"

### 错误处理
- 检查图片URL是否有效
- 确认图片格式支持
- 处理网络超时情况

## 能力范围
- ✅ 物体识别和分类
- ✅ 场景理解和描述  
- ✅ 文字识别（OCR）
- ✅ 情感和氛围分析
- ✅ 技术细节提取

## 限制说明
- ❌ 不能处理敏感或不当内容
- ❌ 图片大小和分辨率有限制
- ❌ 实时视频流不支持
- ❌ 3D模型分析不支持

## 性能优化
- 使用合适的图片尺寸
- 提供具体的分析需求
- 分步骤进行复杂分析
- 结合其他工具进行验证
