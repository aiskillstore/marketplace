# Character Extension Guide / 角色扩展指南

**Version**: 1.0
**Purpose**: Define standards for adding new characters to ensure consistency and prevent uncontrolled content.
**Design Pattern**: Layer 1 (Hard-coded) - All characters must be pre-defined and validated.

---

## Overview / 概述

This guide ensures:
- ✅ **Consistency**: All characters follow the same definition structure
- ✅ **Completeness**: No missing attributes that cause rendering issues
- ✅ **Safety**: Characters are validated before use
- ✅ **Brand Identity**: All characters maintain Picture Book Wizard aesthetic

**CRITICAL RULE**: Only characters defined in this system can be used. Custom/arbitrary characters are FORBIDDEN.

---

## I. Character Definition Template (必填模板)

Every character MUST have ALL of the following sections. Incomplete definitions will be REJECTED.

### 1.1 Required Sections Checklist

| Section | Required | Description |
|---------|----------|-------------|
| **Character ID** | ✅ MUST | Lowercase English identifier (e.g., `yueyue`) |
| **Profile** | ✅ MUST | Age, gender, personality, traits |
| **Visual Identity** | ✅ MUST | Character Anchor prompt string |
| **Detailed Appearance** | ✅ MUST | Face, hair, clothing, height, build |
| **Signature Features** | ✅ MUST | 2-3 features that MUST appear in every image |
| **Best For** | ✅ MUST | Story types this character suits |
| **Chinese Name** | ✅ MUST | Characters + pinyin + meaning |
| **Age Adaptation Rules** | ✅ MUST | How character changes at different ages |
| **CCLP Compatibility** | ✅ MUST | Which CCLP levels are valid |

---

### 1.2 Template Structure

```markdown
## [Character Name] ([Chinese Name]) - `[character_id]`

### Profile

| Attribute | Value |
|-----------|-------|
| **Character ID** | `[lowercase_english_id]` |
| **Age** | [X] years old / [X]岁 |
| **Gender** | [Boy/Girl] / [男孩/女孩] |
| **Personality** | [3 traits in English] / [3个中文特质] |
| **Key Traits** | [Behavioral traits] |

### Visual Identity - Character Anchor

**MANDATORY Prompt String** (must be used in EVERY image):
```
A [age]-year-old Chinese [boy/girl] named [Name], [face shape], [facial features], [hair description with signature element], wearing [clothing with signature element]
```

**Example**:
```
A 5-year-old Chinese girl named Yueyue, round face, rosy cheeks, two pigtails with red ribbons, wearing yellow sweater and denim overalls
```

### Detailed Appearance

| Feature | Description | Signature? |
|---------|-------------|------------|
| **Face** | [Shape, expression, cheeks] | |
| **Hair** | [Style, color, accessories] | ⭐ if signature |
| **Clothing** | [Top, bottom, shoes] | ⭐ if signature |
| **Height** | [Range in cm] | |
| **Build** | [Body type for age] | |

### Signature Features (MUST INCLUDE)

These features MUST appear in EVERY image of this character:

1. ⭐ **[Feature 1]**: [Description] - [Chinese description]
2. ⭐ **[Feature 2]**: [Description] - [Chinese description]
3. ⭐ **[Feature 3]** (optional): [Description]

**Signature Check Rule**:
```
if image does NOT contain ALL signature features:
    REGENERATE image
```

### Best For

| Story Type | Suitability | Reason |
|------------|-------------|--------|
| [Type 1] | ⭐⭐⭐ | [Why this character fits] |
| [Type 2] | ⭐⭐ | [Reason] |
| [Type 3] | ⭐ | [Reason] |

### Chinese Name

| Component | Value |
|-----------|-------|
| **Characters** | [汉字] |
| **Pinyin** | [pīnyīn] |
| **Meaning** | [Cultural meaning and significance] |

### Age Adaptation Rules

**Base Age**: [X] years old

**Adaptation Table**:
| Target Age | Appearance Changes | Behavior Changes |
|------------|-------------------|------------------|
| [Base-2] to [Base] | [How character looks at this age] | [Age-appropriate behavior] |
| [Base+1] to [Base+3] | [Older appearance] | [More mature behavior] |
| [Base+4] to [Base+6] | [Significantly older] | [Independent, complex] |

**Signature Preservation**:
At ALL ages, these signature features MUST be maintained:
- [Signature 1] - always present
- [Signature 2] - may adapt but core element preserved

### CCLP Compatibility

| CCLP Level | Compatible? | Notes |
|------------|-------------|-------|
| STRICT | ✅/❌ | [What stays fixed] |
| MODERATE | ✅/❌ | [What can change] |
| FLEXIBLE | ✅/❌ | [Adaptation limits] |
```

---

## II. Character Registration Process (角色注册流程)

### 2.1 Registration Steps

```
Step 1: Create Character Definition
├── Fill ALL sections of template
├── No placeholders or TBD allowed
└── Chinese and English both required

Step 2: Validation Check
├── Run completeness validation
├── Check for conflicts with existing characters
└── Verify signature features are unique

Step 3: Add to Character Registry
├── Update characters.md with new character
├── Update character-advisor.md selection matrix
├── Update content-safety-validation.md allowed list

Step 4: Create Example Prompts
├── Generate 3+ test prompts
├── Verify consistent rendering
└── Document edge cases

Step 5: Activate Character
├── Add to SKILL.md character list
├── Update all documentation
└── Character now available for use
```

### 2.2 Validation Rules

**Completeness Check**:
```python
def validate_character_definition(character):
    required_fields = [
        "character_id",
        "age",
        "gender",
        "personality",
        "visual_anchor",
        "signature_features",  # Must have 2-3
        "best_for",
        "chinese_name",
        "age_adaptation",
        "cclp_compatibility"
    ]

    for field in required_fields:
        if field not in character or character[field] is None:
            REJECT(f"Missing required field: {field}")

    if len(character["signature_features"]) < 2:
        REJECT("Must have at least 2 signature features")

    return True
```

**Uniqueness Check**:
```python
def check_character_uniqueness(new_character, existing_characters):
    # Character ID must be unique
    if new_character.id in [c.id for c in existing_characters]:
        REJECT("Character ID already exists")

    # Signature features should not overlap significantly
    for existing in existing_characters:
        overlap = signature_overlap(new_character, existing)
        if overlap > 0.5:  # More than 50% overlap
            WARN("Signature features too similar to: " + existing.id)

    return True
```

---

## III. Character Registry (角色注册表)

### 3.1 Current Registered Characters

| ID | Name | Age | Status | Added |
|----|------|-----|--------|-------|
| `yueyue` | 悦悦 | 5 | ✅ Active | v1.0 |
| `xiaoming` | 小明 | 6 | ✅ Active | v1.0 |
| `lele` | 乐乐 | 3 | ✅ Active | v1.0 |
| `meimei` | 美美 | 4 | ✅ Active | v1.0 |
| `grandma` | 奶奶 | 65 | ✅ Active (Supporting) | v1.1 |

### 3.2 Planned Characters (NOT YET AVAILABLE)

| ID | Name | Age | Status | ETA |
|----|------|-----|--------|-----|
| `mom` | 妈妈 | 35 | 🔜 Planned | Phase 2 |
| `dad` | 爸爸 | 37 | 🔜 Planned | Phase 2 |
| `grandpa` | 爷爷 | 68 | 🔜 Planned | Phase 2 |
| `teacher` | 老师 | 30 | 🔜 Planned | Phase 3 |

### 3.3 Reserved Character IDs

These IDs are reserved and CANNOT be used for custom characters:

```
Reserved: yueyue, xiaoming, lele, meimei, grandma, grandpa,
          mom, dad, teacher, uncle, aunt, friend, pet, animal
```

---

## IV. Forbidden Character Patterns (禁止的角色模式)

### 4.1 Absolutely Forbidden

| Pattern | Reason | Detection |
|---------|--------|-----------|
| **Arbitrary names** | Uncontrolled identity | Not in registry |
| **Celebrity names** | Copyright/inappropriate | Name matching |
| **Fictional characters** | Copyright violation | Name matching |
| **Adult-only characters** | Inappropriate for children | Age/role check |
| **Violent characters** | Safety violation | Trait analysis |
| **Stereotyped characters** | Discrimination risk | Trait analysis |

### 4.2 Detection Rules

```python
def validate_character_request(requested_character):
    # Must be in registry
    if requested_character not in CHARACTER_REGISTRY:
        REJECT("Unknown character. Available: yueyue, xiaoming, lele, meimei, grandma")

    # Check for forbidden names in custom text
    if is_celebrity_name(requested_character):
        REJECT("Celebrity names are not allowed")

    if is_fictional_character(requested_character):
        REJECT("Fictional characters from other media are not allowed")

    return True
```

### 4.3 Fallback Behavior

When invalid character is requested:

```
Input: /picture-book-wizard watercolor meadow 5 小红

Response:
⚠️ 角色验证失败 / Character Validation Failed

错误: "小红" 不是已注册的角色
Error: "小红" is not a registered character

可用角色 / Available Characters:
- yueyue (悦悦) - 5岁女孩，好奇温柔
- xiaoming (小明) - 6岁男孩，爱冒险
- lele (乐乐) - 3岁男孩，天真活泼
- meimei (美美) - 4岁女孩，创意艺术

请选择一个已注册的角色继续。
Please select a registered character to continue.
```

---

## V. Signature Feature Enforcement (签名特征强制)

### 5.1 Why Signature Features Matter

Signature features ensure:
- **Brand recognition**: Readers recognize Yueyue by her red ribbons
- **Consistency**: Same character looks the same across all pages
- **Quality control**: Missing features = regenerate image

### 5.2 Signature Feature Rules

**Rule 1**: Every image MUST include ALL signature features
```
if "red ribbons" not in yueyue_image:
    REGENERATE
```

**Rule 2**: Signature features can adapt but NOT disappear
```
STRICT CCLP: Exact signature features (red ribbons exactly as defined)
MODERATE CCLP: Signature preserved, minor variations (ribbons slightly different shade)
FLEXIBLE CCLP: Core element preserved (SOMETHING red in hair, if not ribbons)
```

**Rule 3**: Signature checklist in every prompt
```
Before generating, verify prompt includes:
□ Yueyue: "two pigtails with red ribbons"
□ Xiaoming: "short neat black hair with side part, blue t-shirt"
□ Lele: "chubby round face, red striped shirt"
□ Meimei: "long ponytail with colorful hairclip, pink flower dress"
□ Grandma: "gray hair in bun, warm smile, traditional clothing"
```

---

## VI. Adding a New Character (新角色添加示例)

### Example: Adding "Mom" Character

```markdown
## Mom (妈妈) - `mom`

### Profile

| Attribute | Value |
|-----------|-------|
| **Character ID** | `mom` |
| **Age** | 35 years old / 35岁 |
| **Gender** | Woman / 女性 |
| **Personality** | Caring, patient, capable / 关爱、耐心、能干 |
| **Key Traits** | Nurturing, organized, warm presence |

### Visual Identity - Character Anchor

```
A 35-year-old Chinese woman, gentle oval face, warm smile, shoulder-length black hair often in low ponytail, wearing comfortable home clothes (soft cardigan and simple pants) or casual dress
```

### Detailed Appearance

| Feature | Description | Signature? |
|---------|-------------|------------|
| **Face** | Gentle oval, warm smile, kind eyes | |
| **Hair** | Shoulder-length black, often low ponytail | ⭐ |
| **Clothing** | Soft cardigan OR apron when cooking | ⭐ |
| **Height** | 160-165cm | |
| **Build** | Average, healthy adult woman | |

### Signature Features (MUST INCLUDE)

1. ⭐ **Warm smile**: Gentle, kind expression - 温暖微笑，慈祥表情
2. ⭐ **Practical clothing**: Cardigan or apron - 实用服装，开衫或围裙
3. ⭐ **Low ponytail** (when hair visible): Simple, practical - 低马尾（如头发可见）

### Best For

| Story Type | Suitability | Reason |
|------------|-------------|--------|
| Family bonding | ⭐⭐⭐ | Natural nurturing role |
| Cooking/Kitchen | ⭐⭐⭐ | Traditional family activity |
| Care/Comfort | ⭐⭐⭐ | Supportive presence |
| Teaching moments | ⭐⭐ | Educational guidance |

### Chinese Name

| Component | Value |
|-----------|-------|
| **Characters** | 妈妈 |
| **Pinyin** | māma |
| **Meaning** | Mother, the primary caregiver |

### Age Adaptation Rules

**Base Age**: 35 years old (fixed for consistency)

**Note**: Adult characters do NOT age-adapt like child characters. Mom always appears as a mature adult in her 30s.

### CCLP Compatibility

| CCLP Level | Compatible? | Notes |
|------------|-------------|-------|
| STRICT | ✅ | Fixed appearance, signature features |
| MODERATE | ✅ | Clothing changes OK (home vs outdoor) |
| FLEXIBLE | ✅ | Seasonal clothing adaptation |
```

---

## VII. Integration Checklist (集成检查清单)

When adding a new character, update ALL of these:

- [ ] `characters.md` - Add complete character definition
- [ ] `character-advisor.md` - Update selection matrix
- [ ] `content-safety-validation.md` - Add to allowed list
- [ ] `SKILL.md` - Update Available Characters section
- [ ] `style-assistant.md` - Add character-style compatibility (if relevant)
- [ ] `CCLP-FLEXIBILITY.md` - Add CCLP rules for new character
- [ ] Create 3+ example prompts and verify rendering
- [ ] Document any special rules or edge cases

---

## VIII. Quality Control (质量控制)

### Pre-Release Validation

Before a new character is activated:

1. **Definition Completeness**: All template sections filled
2. **Signature Uniqueness**: No overlap with existing characters
3. **Rendering Test**: 10+ images generated with consistent results
4. **CCLP Test**: All three levels produce valid images
5. **Age Adaptation Test**: Multiple ages render correctly
6. **Multi-Character Test**: Works alongside existing characters
7. **Style Compatibility**: Works with all 18 styles

### Post-Release Monitoring

After activation:

1. Track user feedback on new character
2. Monitor for rendering inconsistencies
3. Update documentation as needed
4. Refine signature features if issues arise

---

## References / 参考文档

- Character definitions: `characters.md`
- Character advisor: `character-advisor.md`
- CCLP protocol: `CCLP-FLEXIBILITY.md`
- Content safety: `content-safety-validation.md`
- Main workflow: `../../SKILL.md`
