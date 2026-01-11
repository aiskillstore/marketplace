# PPT 生图方法论

基于 ASCII PPT 框架 + Gemini 生图的实践经验。

## 核心流程

```
ASCII 框架 → 提取文字+布局 → 构造 prompt → Gemini 生图
```

## 风格选择

| 风格 | 适用场景 | prompt 关键词 |
|-----|---------|--------------|
| 扁平插画风 | 封面、痛点页、场景示意 | `Flat design, clean vectors, soft pastel colors, minimal shadows, 2D style` |
| 等距视图风 | 文件结构图、流程图 | `Isometric 3D illustration, soft gradients, clean geometric shapes` |
| 科技渐变风 | 封面、章节分隔页背景 | `Abstract technology background, gradient, flowing lines, subtle glow effects` |
| 卡通人物风 | 痛点表情、状态展示 | `Cute cartoon character, chibi style, simple expressions, pastel colors` |
| 线条图标风 | 步骤示意、功能对比 | `Minimal line art icons, thin stroke, monochrome with accent color` |

## 让文字正确的技巧

AI 生图文字容易出错，以下技巧可提高准确率：

### 1. 用引号包裹具体文字

```
❌ 写上标题和副标题
✅ Center large title text "Skills" in bold white font
```

### 2. 明确指定位置

```
❌ 文字在图中
✅ Center / below / bottom right corner / top left
```

### 3. 明确指定样式

```
❌ 大标题小标题
✅ bold white font / smaller white text / 48px
```

### 4. 完整示例

```
Center large title text "Skills" in bold white font,
subtitle below "像管理笔记一样管理提示词" in smaller white text,
bottom right corner small text "成峰 / 2025.12"
```

## Prompt 模板

### 封面页 (cover)

```
Flat design presentation cover slide, clean minimalist vector style,
[背景描述] background with [装饰元素].
Center large title text "[主标题]" in bold white font,
subtitle below "[副标题]" in smaller white text,
bottom right corner small text "[署名]",
modern tech aesthetic, 16:9 ratio
```

### 章节分隔页 (section)

```
[风格] presentation section divider,
[背景色] gradient background,
large centered text "[章节号]" and "[章节标题]",
clean minimalist design, no other elements, 16:9 ratio
```

### 内容页配图 (content)

```
[风格] illustration, [主题描述],
[颜色方案] color palette,
no text, suitable for presentation slide,
clean background, 4:3 ratio
```

### 金句页 (quote)

```
[风格] presentation quote slide,
[背景描述] background,
centered text "[金句内容]" in elegant white font,
inspirational atmosphere, 16:9 ratio
```

## 注意事项

1. **中文文字有随机性** - 同样的 prompt 可能需要 2-3 次才正确
2. **复杂文字建议后期加** - 只让 AI 生成背景，文字用设计软件
3. **检查生成结果** - 每次都要核对文字是否正确
4. **保持风格统一** - 同一套 PPT 使用相同的风格关键词

## 案例参考

见 `案例/` 文件夹。
