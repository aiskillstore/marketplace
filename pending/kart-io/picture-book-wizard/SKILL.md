---
name: picture-book-wizard
description: A specialized skill for generating high-quality, consistent children's bilingual picture books using 'banana nano'. Supports 18 visual styles across 4 categories (7 core children's book styles, 5 atmospheric styles, 5 Chinese cultural styles, 1 specialized), 12 scenes (5 nature + 7 cultural), age-driven dynamic content system (ages 3-12), and expanded learning domains (science, math, history, psychology, etc.). Use when the user wants to create picture book stories, prompts, or learning materials.
argument-hint: "[style] [scene] [age] [pages-optional] [character-optional]"
---

# Picture Book Wizard / 绘本魔法师

A professional picture book creation skill that generates bilingual (Chinese/English) educational content with optimized image prompts for the 'banana nano' generator.

专业的绘本创作技能，生成中英双语教育内容，并为 'banana nano' 生成器优化图像提示词。

---

## Language Versions / 语言版本

| Language | File | Description |
|----------|------|-------------|
| **English** | [`SKILL-en.md`](./SKILL-en.md) | Full documentation in English |
| **中文** | [`SKILL-zh.md`](./SKILL-zh.md) | 完整中文文档 |

---

## Quick Start / 快速开始

**Usage / 用法**: `/picture-book-wizard [style] [scene] [age] [pages-optional] [character-optional] [soul-optional]`

### Examples / 示例
```bash
# Age-Based Generation / 基于年龄生成
/picture-book-wizard watercolor meadow 4
/picture-book-wizard clay forest 8 5
/picture-book-wizard nianhua kitchen 10 7 xiaoming

# With Soul Elements / 带灵魂元素
/picture-book-wizard watercolor forest 8 yueyue emotion:curious
/picture-book-wizard storybook meadow 5 theme:friendship

# With Multi-Character / 带多角色
/picture-book-wizard watercolor kitchen 6 yueyue with:grandma theme:family
```

---

## Available Styles / 可用风格 (18 total)

| Category | Styles |
|----------|--------|
| **Core / 核心** | `storybook`, `watercolor`, `gouache`, `crayon`, `colored-pencil`, `clay`, `paper-cut` |
| **Atmospheric / 氛围** | `dreamy`, `fairytale`, `collage`, `fabric`, `felt` |
| **Chinese Cultural / 中国文化** | `ink`, `ink-line`, `nianhua`, `porcelain`, `shadow-puppet` |
| **Specialized / 专业** | `tech` |

---

## Available Characters / 可用角色

| Character | Age | Personality |
|-----------|-----|-------------|
| `yueyue` 悦悦 | 5yo | Curious and gentle / 好奇温柔 (Default) |
| `xiaoming` 小明 | 6yo | Adventurous and energetic / 爱冒险有活力 |
| `lele` 乐乐 | 3yo | Cheerful and innocent / 开朗天真 |
| `meimei` 美美 | 4yo | Creative and imaginative / 有创意爱想象 |

---

## For Complete Documentation / 完整文档

Please refer to the language-specific files:

- **English**: [`SKILL-en.md`](./SKILL-en.md)
- **中文**: [`SKILL-zh.md`](./SKILL-zh.md)
