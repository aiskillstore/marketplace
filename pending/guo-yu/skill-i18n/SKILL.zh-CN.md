---
name: skill-i18n
description: 将 SKILL.md 和 README.md 翻译成多语言版本，便于国际化分享技能
---

# Skill i18n

将技能文档文件（SKILL.md、README.md）翻译成多种语言，让技能更容易与国际用户分享。

## 使用方法

| 命令 | 说明 |
|------|------|
| `/skill-i18n` | 翻译当前技能目录中的文件 |
| `/skill-i18n <skill-name>` | 翻译指定技能的文件 |
| `/skill-i18n config` | 配置默认语言和文件类型 |
| `/skill-i18n --lang zh-CN,ja` | 翻译到指定语言（用于集成） |
| `/skill-i18n --files SKILL.md,README.md` | 翻译指定文件 |

## 支持的语言

| 语言 | 代码 | 输出文件 |
|------|------|----------|
| 简体中文 | `zh-CN` | `SKILL.zh-CN.md` |
| 日本語 | `ja` | `SKILL.ja.md` |
| 한국어 | `ko` | `SKILL.ko.md` |
| Español | `es` | `SKILL.es.md` |
| 自定义 | 用户定义 | `SKILL.<code>.md` |

## 配置

所有设置存储在 `~/.claude/skill-i18n-config.json`：

```json
{
  "default_languages": ["zh-CN", "ja"],
  "default_files": ["SKILL.md"],
  "skills_config": {
    "port-allocator": {
      "languages": ["zh-CN", "ja", "ko"],
      "files": ["SKILL.md", "README.md"]
    }
  }
}
```

**配置字段：**

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `default_languages` | 默认翻译的语言 | `["zh-CN", "ja"]` |
| `default_files` | 默认翻译的文件 | `["SKILL.md"]` |
| `skills_config` | 每个技能的配置 | `{}` |

## 执行步骤

### 命令: `/skill-i18n`

翻译当前技能目录中的文件：

1. **检测当前目录**
   ```bash
   # 检查当前目录是否包含 SKILL.md
   if [ ! -f SKILL.md ]; then
     echo "Error: SKILL.md not found in current directory"
     exit 1
   fi
   ```

2. **加载配置**
   ```bash
   # 读取配置文件
   CONFIG=$(cat ~/.claude/skill-i18n-config.json 2>/dev/null || echo '{}')

   # 从目录获取技能名称
   SKILL_NAME=$(basename "$(pwd)")

   # 检查技能特定配置
   SKILL_CONFIG=$(echo "$CONFIG" | jq -r ".skills_config[\"$SKILL_NAME\"] // null")
   ```

3. **首次运行选择（如果没有配置）**

   如果该技能没有配置，显示 TUI 选择界面：

   ```json
   {
     "questions": [
       {
         "question": "应该生成哪些语言？",
         "header": "语言",
         "multiSelect": true,
         "options": [
           { "label": "简体中文 (zh-CN)", "description": "简体中文" },
           { "label": "日本語 (ja)", "description": "日语" },
           { "label": "한국어 (ko)", "description": "韩语" },
           { "label": "Español (es)", "description": "西班牙语" }
         ]
       },
       {
         "question": "应该翻译哪些文件？",
         "header": "文件",
         "multiSelect": true,
         "options": [
           { "label": "SKILL.md", "description": "技能文档（推荐）" },
           { "label": "README.md", "description": "仓库说明文件" }
         ]
       }
     ]
   }
   ```

4. **保存配置**
   ```bash
   # 保存选择到配置文件以便将来使用
   jq --arg skill "$SKILL_NAME" \
      --argjson langs '["zh-CN", "ja"]' \
      --argjson files '["SKILL.md"]' \
      '.skills_config[$skill] = {"languages": $langs, "files": $files}' \
      ~/.claude/skill-i18n-config.json > tmp.json && mv tmp.json ~/.claude/skill-i18n-config.json
   ```

5. **执行翻译**
   - 为每个选定的文件和语言生成翻译
   - 参见下面的"翻译规则"部分

### 命令: `/skill-i18n <skill-name>`

翻译指定技能的文件：

1. **搜索技能位置**
   ```bash
   # 在常见位置搜索
   SKILL_PATH=""

   # 检查 ~/.claude/skills/
   if [ -d ~/.claude/skills/"$SKILL_NAME" ]; then
     SKILL_PATH=~/.claude/skills/"$SKILL_NAME"
   fi

   # 检查代码仓库（如果已配置）
   if [ -z "$SKILL_PATH" ] && [ -d ~/Codes/skills/"$SKILL_NAME" ]; then
     SKILL_PATH=~/Codes/skills/"$SKILL_NAME"
   fi

   if [ -z "$SKILL_PATH" ]; then
     echo "Error: Skill '$SKILL_NAME' not found"
     exit 1
   fi
   ```

2. **执行翻译**（与默认命令相同）

### 命令: `/skill-i18n config`

配置默认设置：

1. **显示当前配置**
   ```bash
   echo "Current configuration:"
   cat ~/.claude/skill-i18n-config.json | jq .
   ```

2. **通过 AskUserQuestion 进行交互式配置**
   ```json
   {
     "questions": [
       {
         "question": "为新技能选择默认语言：",
         "header": "默认值",
         "multiSelect": true,
         "options": [
           { "label": "简体中文 (zh-CN)", "description": "简体中文" },
           { "label": "日本語 (ja)", "description": "日语" },
           { "label": "한국어 (ko)", "description": "韩语" },
           { "label": "Español (es)", "description": "西班牙语" }
         ]
       }
     ]
   }
   ```

3. **更新配置文件**

### 命令行参数

用于与其他技能集成（如 share-skill）：

| 参数 | 说明 | 示例 |
|------|------|------|
| `--lang <codes>` | 逗号分隔的语言代码 | `--lang zh-CN,ja,ko` |
| `--files <names>` | 逗号分隔的文件名 | `--files SKILL.md,README.md` |
| `--skill <name>` | 目标技能名称 | `--skill port-allocator` |
| `--no-prompt` | 跳过 TUI，直接使用参数/配置 | 用于自动化工作流 |
| `--overwrite` | 覆盖现有翻译 | 跳过确认 |

**优先级顺序：**
1. 命令行参数（最高优先级）
2. `skills_config` 中的技能特定配置
3. 全局 `default_languages` 和 `default_files`
4. 交互式 TUI 选择（如果没有配置）

**集成示例：**
```bash
# share-skill 内部调用 skill-i18n
/skill-i18n --lang zh-CN,ja --files SKILL.md --skill port-allocator --no-prompt
```

## 翻译规则

### 保持不变

以下元素不能翻译：

- **代码块**（```bash、```json 等）
- **文件路径**（`~/.claude/settings.json`、`~/Codes/skills/`）
- **命令名称**（`/port-allocator`、`/skill-i18n`、`git push`）
- **技术标识符**（变量名、JSON 键）
- **URL 和链接**

### 自然翻译

- 根据目标语言调整句子结构
- 使用适当的礼貌程度：
  - 日语：礼貌体（です/ます）
  - 中文：标准书面语
  - 韩语：礼貌体（합니다/습니다）
  - 西班牙语：正式的 usted 形式
- 适当本地化示例

### Frontmatter 处理

```yaml
---
name: port-allocator          # 保持不变（标识符）
description: 翻译这部分        # 翻译成目标语言
---
```

### 风格适配

不同语言可能使用不同的视觉风格：

| 语言 | 表情符号使用 | 示例 |
|------|-------------|------|
| 中文 (zh-CN) | 常用 | ✅ 正确 / ❌ 错误 |
| 日语 (ja) | 少用 | 正しい / 間違い |
| 韩语 (ko) | 适度 | ✅ 올바름 / ❌ 잘못됨 |
| 西班牙语 (es) | 少用 | Correcto / Incorrecto |

如果项目中有现有的翻译模式，请遵循它们。

## 输出格式

### 翻译成功

```
Translation complete

Skill: port-allocator
Source: SKILL.md

Generated:
  - SKILL.zh-CN.md (简体中文)
  - SKILL.ja.md (日本語)

Config saved for: port-allocator
Next run will auto-translate to: zh-CN, ja
```

### 检测到现有文件

```
Existing translations detected:
  - SKILL.zh-CN.md (modified 2 days ago)
  - SKILL.ja.md (modified 2 days ago)

Options:
  [ ] Overwrite all
  [ ] Skip existing
  [ ] Select individually
```

### 配置已保存

```
Configuration updated

Default languages: zh-CN, ja
Default files: SKILL.md

Skill-specific config:
  port-allocator: zh-CN, ja, ko (SKILL.md, README.md)
  share-skill: zh-CN, ja (SKILL.md)
```

## 与 share-skill 集成

skill-i18n 与 share-skill 集成用于文档生成：

```bash
# share-skill docs 带 i18n
/share-skill docs --i18n

# 内部调用：
/skill-i18n --lang <configured-langs> --files SKILL.md --no-prompt
```

当 share-skill 检测到 `--i18n` 参数时：
1. 检查 skill-i18n 是否可用
2. 加载语言配置
3. 调用 skill-i18n 生成翻译
4. 将翻译文件包含在文档网站中

## 注意事项

1. **源文件安全** - 永远不会覆盖源 `SKILL.md` 文件
2. **首次运行提示** - 首次翻译需要选择语言
3. **每个技能配置** - 不同技能可以有不同的语言设置
4. **增量更新** - 仅在源文件比翻译文件新时才翻译
5. **集成友好** - 命令行参数允许其他技能调用 skill-i18n
