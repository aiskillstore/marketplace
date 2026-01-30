# Picture Book Wizard

[English](#english) | [中文](#中文)

---

## English

A Claude Code skill for generating high-quality, consistent children's bilingual picture books with AI image prompts.

### Features

- **18 Visual Styles** across 4 categories:
  - Core Children's Book: storybook, watercolor, gouache, crayon, colored-pencil, clay, paper-cut
  - Atmospheric: dreamy, fairytale, collage, fabric, felt
  - Chinese Cultural: ink, ink-line, nianhua, porcelain, shadow-puppet
  - Specialized: tech

- **12 Core Scenes**: meadow, pond, rice-paddy, stars, forest, kitchen, courtyard, market, temple, festival, grandma-room, kindergarten

- **Age-Driven Content System** (ages 3-12): Auto-adjusts page count, vocabulary, and learning objectives

- **Character Consistency Lock Protocol (CCLP 4.0)**: Ensures consistent character appearance across multi-page stories

- **Bilingual Output**: Chinese/English with accurate pinyin and tone marks

- **Optimized for 'banana nano'**: Image prompts designed for AI image generation

### Installation

1. Clone the repository:
```bash
git clone https://github.com/kart-io/picture-skills.git
```

2. Copy the skill to your Claude Code skills directory:
```bash
cp -r picture-skills/.claude/skills/picture-book-wizard ~/.claude/skills/
```

3. The skill is now available in Claude Code.

### Usage

Basic syntax:
```bash
/picture-book-wizard [style] [scene] [age] [pages-optional] [character-optional]
```

#### Examples

```bash
# Age-based generation (recommended)
/picture-book-wizard watercolor meadow 4
/picture-book-wizard clay forest 8 5
/picture-book-wizard nianhua kitchen 10 7 xiaoming

# With soul elements (emotion, theme)
/picture-book-wizard watercolor forest 8 yueyue emotion:curious
/picture-book-wizard storybook meadow 5 theme:friendship

# With multi-character
/picture-book-wizard watercolor kitchen 6 yueyue with:grandma theme:family

# Helper commands
/picture-book-wizard help:style warm cozy
/picture-book-wizard help:character age:4 theme:creative
```

### Available Characters

| Character | Age | Personality |
|-----------|-----|-------------|
| Yueyue (悦悦) | 5 | Curious and gentle (Default) |
| Xiaoming (小明) | 6 | Adventurous and energetic |
| Lele (乐乐) | 3 | Cheerful and innocent |
| Meimei (美美) | 4 | Creative and imaginative |

Supporting characters: grandma, dad, mom, grandpa, sibling
Animal companions: cat, dog, rabbit, chick, duckling, etc.

### Project Structure

```
picture-skills/
├── .claude/skills/picture-book-wizard/
│   ├── SKILL.md              # Skill definition (required)
│   ├── engine/               # Python rule engine
│   ├── scripts/              # Automation scripts
│   ├── references/           # Reference materials
│   │   ├── config/           # Configuration files
│   │   ├── examples/         # Working examples
│   │   └── guides/           # Documentation
│   └── assets/               # Static resources
│       └── templates/        # Output templates
├── output/                   # Generated content
│   └── picture-books/
└── scripts/                  # Project utilities
```

### Output

Generated stories are saved to:
```
./output/picture-books/[YYYY-MM]/[style]-[scene]-[character]-[pages]-[timestamp].md
```

Each output includes:
- Bilingual story text (Chinese/English)
- Learning focus with Chinese characters
- Optimized image prompts for AI generation
- Character consistency markers

### Configuration

Detailed configuration files are located in `.claude/skills/picture-book-wizard/references/config/`:

| Category | Files |
|----------|-------|
| Core | characters.md, styles.md, scenes.md, age-system.md |
| CCLP | character-consistency-lock.md, CCLP-FLEXIBILITY.md |
| Advanced | story-soul.md, scene-matching.md, reality-validation.md |

### Specification Compliance

This project follows the [Anthropic Agent Skills Specification](https://agentskills.io/specification) with:
- Progressive disclosure architecture
- Standard directory structure
- Clear separation of concerns

### License

MIT License

---

## 中文

一个 Claude Code 技能，用于生成高质量、角色一致的儿童双语绘本及 AI 图像提示词。

### 特性

- **18 种视觉风格**，分为 4 大类：
  - 核心绘本风格：故事书、水彩、水粉、蜡笔、彩铅、黏土、剪纸
  - 氛围增强风格：梦幻、童话、拼贴、布艺、毛毡
  - 中国文化风格：水墨、白描、年画、青花瓷、皮影
  - 特殊风格：科技

- **12 个核心场景**：草地、池塘、稻田、星空、森林、厨房、庭院、市场、寺庙、节日、奶奶房间、幼儿园

- **年龄驱动内容系统**（3-12岁）：自动调整页数、词汇和学习目标

- **角色一致性锁定协议 (CCLP 4.0)**：确保多页故事中角色外观一致

- **双语输出**：中文/英文，带准确拼音和声调

- **针对 'banana nano' 优化**：专为 AI 图像生成设计的提示词

### 安装

1. 克隆仓库：
```bash
git clone https://github.com/kart-io/picture-skills.git
```

2. 将技能复制到 Claude Code 技能目录：
```bash
cp -r picture-skills/.claude/skills/picture-book-wizard ~/.claude/skills/
```

3. 技能现已在 Claude Code 中可用。

### 使用方法

基本语法：
```bash
/picture-book-wizard [风格] [场景] [年龄] [页数-可选] [角色-可选]
```

#### 示例

```bash
# 基于年龄生成（推荐）
/picture-book-wizard watercolor meadow 4
/picture-book-wizard clay forest 8 5
/picture-book-wizard nianhua kitchen 10 7 xiaoming

# 带灵魂元素（情感、主题）
/picture-book-wizard watercolor forest 8 yueyue emotion:curious
/picture-book-wizard storybook meadow 5 theme:friendship

# 多角色
/picture-book-wizard watercolor kitchen 6 yueyue with:grandma theme:family

# 帮助命令
/picture-book-wizard help:style warm cozy
/picture-book-wizard help:character age:4 theme:creative
```

### 可用角色

| 角色 | 年龄 | 性格 |
|------|-----|------|
| 悦悦 (Yueyue) | 5岁 | 好奇温柔（默认） |
| 小明 (Xiaoming) | 6岁 | 爱冒险、精力充沛 |
| 乐乐 (Lele) | 3岁 | 开朗天真 |
| 美美 (Meimei) | 4岁 | 富有创意和想象力 |

配角：奶奶、爸爸、妈妈、爷爷、兄弟姐妹
动物伙伴：猫、狗、兔子、小鸡、小鸭等

### 项目结构

```
picture-skills/
├── .claude/skills/picture-book-wizard/
│   ├── SKILL.md              # 技能定义（必需）
│   ├── engine/               # Python 规则引擎
│   ├── scripts/              # 自动化脚本
│   ├── references/           # 参考资料
│   │   ├── config/           # 配置文件
│   │   ├── examples/         # 示例
│   │   └── guides/           # 文档
│   └── assets/               # 静态资源
│       └── templates/        # 输出模板
├── output/                   # 生成内容
│   └── picture-books/
└── scripts/                  # 项目工具
```

### 输出

生成的故事保存至：
```
./output/picture-books/[YYYY-MM]/[风格]-[场景]-[角色]-[页数]-[时间戳].md
```

每个输出包含：
- 双语故事文本（中文/英文）
- 学习重点及汉字
- 优化的 AI 图像生成提示词
- 角色一致性标记

### 配置

详细配置文件位于 `.claude/skills/picture-book-wizard/references/config/`：

| 类别 | 文件 |
|------|------|
| 核心 | characters.md, styles.md, scenes.md, age-system.md |
| CCLP | character-consistency-lock.md, CCLP-FLEXIBILITY.md |
| 高级 | story-soul.md, scene-matching.md, reality-validation.md |

### 规范合规

本项目遵循 [Anthropic Agent Skills 规范](https://agentskills.io/specification)：
- 渐进式披露架构
- 标准目录结构
- 清晰的关注点分离

### 许可证

MIT License

---

## Contributing

Contributions are welcome! Please read the documentation in `references/guides/` before submitting PRs.

## Links

- **Repository**: https://github.com/kart-io/picture-skills
- **Specification**: https://agentskills.io/specification
