# Content Safety Validation / 内容安全验证

**Version**: 1.0
**Purpose**: Prevent generation of inappropriate, unsafe, or uncontrollable content in children's picture books.
**Priority**: CRITICAL - Must be checked BEFORE any content generation.

---

## Overview / 概述

This validation system ensures all generated content is:
- ✅ **Safe** for children (ages 3-12)
- ✅ **Educational** and age-appropriate
- ✅ **Culturally respectful** and non-controversial
- ✅ **Within system boundaries** (controlled parameters only)

All validations are **hard-coded rules** (Layer 1) - no AI flexibility allowed for safety rules.

---

## I. Forbidden Content (禁止内容) ❌

### 1. Violence & Danger (暴力与危险)

**ABSOLUTELY FORBIDDEN** (绝对禁止):
- ❌ Physical violence between characters (hitting, kicking, fighting)
- ❌ Weapons of any kind (knives, guns, swords, even toy weapons)
- ❌ Blood, injuries, or wounds
- ❌ Death or dying (except natural concepts like fallen leaves, seasons)
- ❌ Hunting or killing animals
- ❌ Dangerous activities without supervision (climbing high, fire play, water danger)
- ❌ Bullying or aggressive behavior
- ❌ Scary monsters or threatening creatures

**ALLOWED ALTERNATIVES** (允许的替代):
- ✅ Characters disagreeing, then resolving through communication
- ✅ Gentle competition (racing, games) without aggression
- ✅ Natural challenges (weather, terrain) that are safely overcome
- ✅ Friendly animals, even large ones (gentle bear, kind wolf)

---

### 2. Fear & Horror (恐惧与恐怖)

**ABSOLUTELY FORBIDDEN** (绝对禁止):
- ❌ Horror elements (ghosts, zombies, skeletons)
- ❌ Nightmares or scary dream content
- ❌ Dark threatening imagery
- ❌ Loud scary sounds or sudden frights
- ❌ Abandonment or being lost (without quick resolution)
- ❌ Separation anxiety triggers
- ❌ Kidnapping or stranger danger scenarios

**ALLOWED ALTERNATIVES** (允许的替代):
- ✅ Mild challenges that are quickly resolved
- ✅ Gentle night scenes with stars and moon (peaceful, not scary)
- ✅ Being temporarily lost but quickly found by family
- ✅ Overcoming small fears with support

---

### 3. Inappropriate Themes (不当主题)

**ABSOLUTELY FORBIDDEN** (绝对禁止):
- ❌ Romance or romantic relationships between children
- ❌ Adult relationships or marriage themes
- ❌ Body exposure or inappropriate clothing
- ❌ Toilet humor beyond age-appropriate (potty training OK for ages 3-4)
- ❌ Substance references (alcohol, smoking, drugs)
- ❌ Gambling or betting
- ❌ Money obsession or greed themes
- ❌ Social status discrimination
- ❌ Gender stereotypes (girls only cook, boys only play sports)

**ALLOWED ALTERNATIVES** (允许的替代):
- ✅ Friendship between children
- ✅ Family love and bonding
- ✅ Healthy eating and exercise
- ✅ Sharing and kindness
- ✅ All characters can do any activity regardless of gender

---

### 4. Political & Religious Sensitivity (政治与宗教敏感)

**ABSOLUTELY FORBIDDEN** (绝对禁止):
- ❌ Political figures or symbols (any country)
- ❌ National flags or anthems (except neutral cultural context)
- ❌ Religious doctrine or proselytizing
- ❌ Religious conflicts or comparisons
- ❌ Controversial historical events
- ❌ Territorial disputes or map controversies
- ❌ Military or war content
- ❌ Ethnic stereotypes or discrimination

**ALLOWED ALTERNATIVES** (允许的替代):
- ✅ Cultural traditions (food, clothing, festivals) presented respectfully
- ✅ Temple scenes as cultural/architectural education (not religious instruction)
- ✅ Historical figures for educational purposes (inventors, artists) - neutrally presented
- ✅ Celebrating diversity without comparison or judgment

---

### 5. Commercial & Brand Content (商业与品牌)

**ABSOLUTELY FORBIDDEN** (绝对禁止):
- ❌ Brand names or logos (no "Nike", "McDonald's", etc.)
- ❌ Product placement or advertising
- ❌ Celebrity or influencer references
- ❌ Popular media characters (Disney, Marvel, etc.)
- ❌ Video game references
- ❌ Social media or app references
- ❌ Consumerism or "must have" messaging

**ALLOWED ALTERNATIVES** (允许的替代):
- ✅ Generic items (sneakers, not "Nikes"; burger, not "McDonald's")
- ✅ Original characters from this system only
- ✅ Educational content about creating/making things
- ✅ Appreciating what one has

---

## II. Input Validation Rules (输入验证规则)

### 1. Style Validation

**Allowed Values** (18 styles only):
```
Core: storybook, watercolor, gouache, crayon, colored-pencil, clay, paper-cut
Atmospheric: dreamy, fairytale, collage, fabric, felt
Chinese Cultural: ink, ink-line, nianhua, porcelain, shadow-puppet
Specialized: tech (with restrictions)
```

**Validation Rule**:
```python
if style not in ALLOWED_STYLES:
    REJECT with message: "未知风格。请从18种可用风格中选择。"
    SUGGEST: closest_match or list all styles
```

**Tech Style Restrictions**:
- ⚠️ Maximum 5-10% of pages
- ⚠️ Only for ages 5-6+
- ⚠️ Must be combined with warm elements
- ⚠️ Not recommended as primary style

---

### 2. Character Validation (角色验证)

**CRITICAL**: Character validation is essential to prevent uncontrolled content.

#### 2.1 Character Registry

**Allowed Values** (Only registered characters):
```
Main Characters:
- yueyue (悦悦) - 5岁女孩
- xiaoming (小明) - 6岁男孩
- lele (乐乐) - 3岁男孩
- meimei (美美) - 4岁女孩

Supporting Characters:
- grandma (奶奶) - 65岁奶奶 [Phase 1 Active]

Future Characters (NOT YET AVAILABLE):
- mom (妈妈) - Phase 2
- dad (爸爸) - Phase 2
- grandpa (爷爷) - Phase 2
- teacher (老师) - Phase 3
```

#### 2.2 Validation Rules

**Rule 1: Registry Check**
```python
ALLOWED_CHARACTERS = ["yueyue", "xiaoming", "lele", "meimei", "grandma"]
FUTURE_CHARACTERS = ["mom", "dad", "grandpa", "teacher"]

if character not in ALLOWED_CHARACTERS:
    if character in FUTURE_CHARACTERS:
        REJECT → "该角色尚未开放。当前可用: yueyue, xiaoming, lele, meimei, grandma"
    else:
        REJECT → "未知角色。请从已注册角色中选择。"
```

**Rule 2: Arbitrary Name Detection**
```python
# Common arbitrary name patterns to detect
ARBITRARY_PATTERNS = [
    r"小[红蓝绿黄白黑]",  # 小红, 小蓝, etc.
    r"阿[强伟明华]",       # 阿强, 阿伟, etc.
    r"[A-Z][a-z]+",       # English arbitrary names (John, Mary)
]

for pattern in ARBITRARY_PATTERNS:
    if matches(character, pattern) and character not in ALLOWED_CHARACTERS:
        REJECT → "不允许使用自定义角色名。请使用系统注册的角色。"
```

**Rule 3: Celebrity/Fictional Character Detection**
```python
FORBIDDEN_NAMES = [
    # Celebrities
    "周杰伦", "刘德华", "成龙", "Taylor", "Beyonce",
    # Fictional characters
    "哈利波特", "蜘蛛侠", "艾莎", "Elsa", "SpiderMan",
    "小猪佩奇", "熊大", "熊二", "光头强",
    # Historical/Political figures
    "毛泽东", "孙中山", "Lincoln", "Obama"
]

if character in FORBIDDEN_NAMES or similar_to(character, FORBIDDEN_NAMES):
    REJECT → "不允许使用名人、虚构角色或历史人物名称。"
```

#### 2.3 Custom Character Prevention

**Why Forbidden**:
- 🚫 **Consistency risk**: Arbitrary characters have no defined appearance
- 🚫 **CCLP failure**: No signature features to enforce
- 🚫 **Brand dilution**: Inconsistent visual identity
- 🚫 **Legal risk**: May inadvertently use copyrighted names

**Detection Strategy**:
```python
def is_valid_character(input_name):
    # Normalize input
    name = normalize(input_name.lower())

    # Check against registry
    if name in CHARACTER_REGISTRY:
        return True

    # Check for similar matches (typos)
    closest = find_closest_match(name, CHARACTER_REGISTRY)
    if similarity(name, closest) > 0.8:
        SUGGEST → f"您是否想使用 '{closest}'?"
        return False

    # Reject arbitrary names
    REJECT → "未注册的角色。请使用: yueyue, xiaoming, lele, meimei, grandma"
    return False
```

#### 2.4 Signature Feature Enforcement

Each registered character has mandatory signature features:

| Character | Signature Features | Must Include |
|-----------|-------------------|--------------|
| **yueyue** | 红丝带双马尾, 黄毛衣 | ✅ Every image |
| **xiaoming** | 侧分短发, 蓝色T恤 | ✅ Every image |
| **lele** | 圆嘟嘟脸, 红条纹衫 | ✅ Every image |
| **meimei** | 彩发夹长马尾, 粉色碎花裙 | ✅ Every image |
| **grandma** | 灰发发髻, 温暖微笑 | ✅ Every image |

**Signature Validation**:
```python
def validate_prompt_has_signatures(prompt, character):
    signatures = CHARACTER_SIGNATURES[character]
    for signature in signatures:
        if signature not in prompt:
            WARN → f"缺少签名特征: {signature}"
            AUTO_ADD signature to prompt
    return prompt
```

#### 2.5 Error Messages

**Unknown Character**:
```
⚠️ 角色验证失败 / Character Validation Failed

错误: "[input]" 不是已注册的角色
Error: "[input]" is not a registered character

可用角色 / Available Characters:
• yueyue (悦悦) - 5岁女孩，好奇温柔
• xiaoming (小明) - 6岁男孩，爱冒险
• lele (乐乐) - 3岁男孩，天真活泼
• meimei (美美) - 4岁女孩，创意艺术
• grandma (奶奶) - 65岁，温暖智慧 [配角]

请选择已注册角色继续。
```

**Future Character**:
```
⚠️ 角色尚未开放 / Character Not Yet Available

"mom" (妈妈) 计划在 Phase 2 开放。

当前可用角色:
• yueyue, xiaoming, lele, meimei, grandma

请使用当前可用角色，或等待后续版本更新。
```

**Forbidden Name**:
```
⚠️ 禁止使用的角色名 / Forbidden Character Name

不允许使用名人、虚构角色或历史人物名称。
Celebrity, fictional, and historical figure names are not allowed.

请使用系统注册的角色:
• yueyue, xiaoming, lele, meimei, grandma
```

#### 2.6 Reference

For adding new characters to the registry, see:
`references/config/character-extension.md`

---

### 3. Age Validation

**Allowed Range**: 3-12 years

**Validation Rules**:
```python
if age < 3:
    REJECT with message: "年龄必须至少3岁。本系统为3-12岁儿童设计。"

if age > 12:
    REJECT with message: "年龄不能超过12岁。本系统为3-12岁儿童设计。"

if age not integer:
    REJECT with message: "年龄必须是整数（如：5，不是5.5）。"
```

---

### 4. Scene Validation

**Core Scenes** (HIGH validation):
```
Nature: meadow, pond, rice-paddy, stars, forest
Cultural: kitchen, courtyard, market, temple, festival, grandma-room, kindergarten
```

**Extended Scenes** (require matching):
- Must match to one of 12 core scenes
- Similarity score > 40% required
- User confirmation required for non-core scenes

**Forbidden Scene Concepts**:
- ❌ Hospitals, doctor's offices (medical anxiety)
- ❌ Police stations, prisons (fear associations)
- ❌ Battlefields, military bases
- ❌ Bars, nightclubs, casinos
- ❌ Haunted houses, graveyards
- ❌ Abandoned buildings
- ❌ Deep caves (danger)
- ❌ High cliffs without safety

**Validation Rule**:
```python
if scene in FORBIDDEN_SCENES:
    REJECT with message: "此场景不适合儿童绘本。请选择其他场景。"
    SUGGEST: appropriate alternatives
```

---

### 5. Theme Validation

**Allowed Themes**:
```
Positive: growth, friendship, nature, family, courage, creativity,
         discovery, kindness, sharing, helping, learning, curiosity,
         patience, gratitude, respect, cooperation
```

**Forbidden Themes**:
```
Negative: revenge, jealousy, greed, deception, hatred, fear,
          competition (aggressive), exclusion, mockery
```

**Validation Rule**:
```python
if theme in FORBIDDEN_THEMES:
    REJECT with message: "此主题不适合儿童绘本。"
    SUGGEST: positive_alternative
    # Examples:
    # revenge → forgiveness
    # jealousy → appreciation
    # greed → sharing
    # deception → honesty
```

---

### 6. User Text Input Validation

**Free-text fields** (story descriptions, custom elements):

**Must Filter**:
- ❌ Profanity in any language
- ❌ Adult content keywords
- ❌ Violence keywords
- ❌ Political keywords
- ❌ Brand/commercial names

**Validation Process**:
```python
def validate_user_text(text):
    # Check against forbidden word list
    for word in FORBIDDEN_WORDS:
        if word in text.lower():
            REJECT with message: "输入包含不适当内容。请修改。"
            return False

    # Check for suspicious patterns
    if contains_url(text):
        REJECT with message: "不允许包含网址链接。"
        return False

    if contains_email(text):
        REJECT with message: "不允许包含电子邮件地址。"
        return False

    return True
```

---

## III. Age-Appropriate Content Gates (年龄适当性门控)

### Content Complexity by Age

| Age | Max Pages | Vocabulary | Themes Allowed | Complexity |
|-----|-----------|------------|----------------|------------|
| 3-4 | 1-3 | HSK 1 | Basic (sharing, family, animals) | Very Simple |
| 5-6 | 3-5 | HSK 1-2 | + Friendship, nature, courage | Simple |
| 7-8 | 5-7 | HSK 2-3 | + Discovery, problem-solving | Moderate |
| 9-10 | 7-10 | HSK 3-4 | + History, psychology basics | Advanced |
| 11-12 | 10-15 | HSK 4+ | + Philosophy, interdisciplinary | Complex |

### Theme Restrictions by Age

**Ages 3-4 ONLY**:
- ✅ Family, animals, colors, shapes, basic emotions
- ❌ Complex social dynamics, abstract concepts

**Ages 5-6 ADD**:
- ✅ Friendship, simple courage, nature exploration
- ❌ Loss, complex emotions, historical events

**Ages 7-8 ADD**:
- ✅ Problem-solving, discovery, basic science
- ❌ Deep philosophical questions, complex history

**Ages 9+ ADD**:
- ✅ History (age-appropriate), psychology basics, complex themes
- Still ❌ All forbidden content in Section I

---

## IV. Output Validation (输出验证)

### Pre-Generation Check

Before generating any content, verify:

```python
def pre_generation_validate(params):
    checks = [
        validate_style(params.style),
        validate_scene(params.scene),
        validate_age(params.age),
        validate_character(params.character),
        validate_theme(params.theme),
        validate_user_text(params.custom_text),
        check_age_appropriate_theme(params.age, params.theme),
    ]

    if not all(checks):
        ABORT_GENERATION
        REPORT_VALIDATION_ERRORS
        return False

    return True
```

### Post-Generation Check

After generating content, verify:

```python
def post_generation_validate(content):
    # Scan generated text
    if contains_forbidden_words(content.text):
        FLAG and REGENERATE

    # Check image prompts
    if contains_forbidden_visual_elements(content.image_prompts):
        FLAG and REGENERATE

    # Verify age appropriateness
    if not age_appropriate(content, params.age):
        FLAG and SIMPLIFY

    return True
```

---

## V. Validation Workflow Integration

### Position in SKILL.md

Insert as **Step 0 (Mandatory Pre-Check)** before any other processing:

```
### 0. Content Safety Validation (必须检查)

**CRITICAL**: This check runs BEFORE any content generation.

1. Validate all input parameters against allowed values
2. Check for forbidden content keywords
3. Verify age-appropriate theme combination
4. Reject invalid inputs with clear error messages

If ANY validation fails:
- STOP processing immediately
- Report specific validation error
- Suggest valid alternatives
- Do NOT proceed to content generation
```

### Error Message Format

```
⚠️ 内容安全验证失败 / Content Safety Validation Failed

错误类型 / Error Type: [FORBIDDEN_CONTENT | INVALID_INPUT | AGE_INAPPROPRIATE]

详情 / Details:
[specific error message in bilingual format]

建议 / Suggestion:
[how to fix the issue]

请修改后重试。/ Please modify and try again.
```

---

## VI. Quick Reference Checklist (速查清单)

### Before Generation, Verify:

- [ ] Style is one of 18 allowed styles
- [ ] Scene is core 12 or valid matched scene
- [ ] Age is 3-12 integer
- [ ] Character is from allowed list
- [ ] Theme is positive/educational
- [ ] No forbidden content keywords
- [ ] Age-theme combination is appropriate
- [ ] No commercial/brand references
- [ ] No political/religious sensitivity
- [ ] No violence/fear elements

### Red Flags to Reject Immediately:

- 🚩 Violence, weapons, blood
- 🚩 Horror, scary elements
- 🚩 Adult/romantic themes
- 🚩 Political content
- 🚩 Brand names
- 🚩 Custom characters (not in system)
- 🚩 Age < 3 or > 12
- 🚩 Unknown style/scene

---

## VII. Escalation Protocol (升级协议)

### When to Escalate (何时升级)

If validation is uncertain:
1. **Ask user for clarification** before proceeding
2. **Default to stricter interpretation** when in doubt
3. **Never generate questionable content** - always err on side of caution

### Borderline Cases

| Situation | Decision |
|-----------|----------|
| User requests "fighting" | REJECT - suggest "friendly competition" |
| User requests "scary story" | REJECT - suggest "exciting adventure" |
| User requests unknown character | REJECT - list available characters |
| User requests adult theme | REJECT - explain this is for children |
| User requests brand name | REJECT - suggest generic alternative |

---

## References / 参考文档

- Reality validation rules: `reality-validation.md`
- Age system: `age-system.md`
- Character definitions: `characters.md`
- Style definitions: `styles.md`
- Architecture design: `../guides/ARCHITECTURE-DESIGN-ANALYSIS.md`
