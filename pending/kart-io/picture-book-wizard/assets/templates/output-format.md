# Output Format Template

## Standard Output Structure

Every picture book page must follow this consistent format:

```markdown
📖 **故事 / Story:**
[Chinese text here]
[English translation here]

---

🔤 **拼音 / Pinyin:**
[Pinyin annotation of Chinese text]

---

✨ **学习要点 / Learning Point:**
[Character] ([pinyin]) - [English meaning]

---

🎨 **Banana Nano Prompt:**
[Complete VCP-locked image generation prompt]

---
```

## Section Details

### 1. 📖 Story Section (故事 / Story)

**Purpose**: Present the bilingual narrative content

**Requirements**:
- Chinese text comes first (on its own line)
- English translation follows (on its own line)
- Keep sentences simple and child-appropriate
- Use repetitive language patterns
- Age target: 3-6 years old

**Guidelines**:
- Sentence length: 5-12 words per language
- Vocabulary: Basic, everyday words
- Structure: Subject-Verb-Object preferred
- Tone: Warm, engaging, wonder-filled

**Example**:
```
悦悦在草地上发现了一颗小种子。
Yueyue found a tiny seed on the meadow.
```

---

### 2. 🔤 Pinyin Section (拼音)

**Purpose**: Provide pronunciation guide for Chinese learners

**Requirements**:
- Include tone marks (ā, á, ǎ, à)
- Match exactly with the Chinese text above
- Use proper spacing between words/phrases
- Follow standard pinyin romanization rules

**Guidelines**:
- Proper names: Capitalize (Yuèyuè)
- Standard words: Lowercase
- Word grouping: Follow meaning clusters
- Punctuation: Match Chinese text

**Example**:
```
Yuèyuè zài cǎodì shàng fāxiànle yī kē xiǎo zhǒngzi.
```

---

### 3. ✨ Learning Point Section (学习要点)

**Purpose**: Highlight a key Chinese character for educational focus

**Requirements**:
- Select ONE character most relevant to the scene/story
- Provide the character, pinyin, and English meaning
- Choose characters appropriate for early learners
- Optionally include additional learning objectives (logic, objects, social)

**Standard Format**:
```
[字] ([pinyin]) - [English meaning]
```

**Extended Format** (with additional objectives):
```
汉字 (Character): [字] ([pinyin]) - [English meaning]
逻辑 (Logic): [logical concept or reasoning]
```

Or:
```
汉字 (Character): [字] ([pinyin]) - [English meaning]
物品 (Object): [object name and usage description]
```

**Character Selection Priority**:
1. Nouns related to scene (grass, water, star, tree)
2. Verbs related to action (find, see, walk)
3. Adjectives describing environment (big, small, green)
4. Basic characters suitable for young learners (HSK 1-2 level)

**Additional Learning Objectives** (Optional - see `config/learning-objectives.md`):
- Logic (逻辑): Cause-effect, sequence, problem-solving
- Objects (物品): Tools, utensils, traditional items and their usage
- Social (社交): Sharing, helping, cooperation
- Emotional (情感): Feelings, empathy
- Safety (安全): Rules, hygiene, health
- Science (科学): Nature, growth, observation

**Example (Standard)**:
```
草 (cǎo) - grass
```

**Example (Extended with Logic)**:
```
汉字 (Character): 长 (zhǎng) - grow
逻辑 (Logic): 种子 + 水 + 阳光 → 生长 (seed + water + sun → growth)
```

**Example (Extended with Object)**:
```
汉字 (Character): 筷 (kuài) - chopsticks
物品 (Object): 筷子是中国传统餐具，用来夹食物 (Chopsticks are traditional Chinese utensils used to pick up food)
```

---

### 4. 🎨 Banana Nano Prompt Section

**Purpose**: Provide complete, VCP-locked image generation prompt

**Requirements**:
- Must include Character Anchor
- Must include Scene-specific details
- Must include Style keywords
- Must include Rendering parameters
- Length: 150-250 words optimal

**Structure**:
```
[Character Anchor], [action/pose], [scene environment elements], [scene-specific details], [style keywords], [rendering parameters], [atmospheric effects].
```

**Components Checklist**:
- [ ] Character description (Yueyue's appearance)
- [ ] Character pose/action
- [ ] Scene environment (meadow, pond, etc.)
- [ ] Scene-specific visual details
- [ ] Style keywords (clay/tech/ink)
- [ ] Rendering anchor (octane render, 8k, etc.)
- [ ] Atmospheric description

**Example**:
```
A 5-year-old Chinese girl named Yueyue, round face, rosy cheeks, two pigtails with red ribbons, wearing yellow sweater and denim overalls, kneeling on lush green grass meadow, discovering a tiny seed, hand-sculpted claymation style, physical clay textures, tiny hand-pressed wildflowers scattered around, soft studio lighting, octane render, macro texture details, 8k resolution, warm and inviting atmosphere.
```

---

## Complete Example Output

### Clay Style Meadow Scene

```markdown
📖 **故事 / Story:**
悦悦在草地上发现了一颗小种子。
Yueyue found a tiny seed on the meadow.

---

🔤 **拼音 / Pinyin:**
Yuèyuè zài cǎodì shàng fāxiànle yī kē xiǎo zhǒngzi.

---

✨ **学习要点 / Learning Point:**
草 (cǎo) - grass

---

🎨 **Banana Nano Prompt:**
A 5-year-old Chinese girl named Yueyue, round face, rosy cheeks, two pigtails with red ribbons, wearing yellow sweater and denim overalls, kneeling on lush green grass meadow, discovering a tiny seed, hand-sculpted claymation style, physical clay textures, tiny hand-pressed wildflowers scattered around, soft studio lighting, octane render, macro texture details, 8k resolution, warm and inviting atmosphere.

---
```

---

## Optional Sections

### Story Summary (故事总结) - For Multi-Page Stories

**When to Include**: REQUIRED for all multi-page stories (3, 5, or 7 pages)

**Purpose**: Provide a comprehensive summary of the complete story arc, learning outcomes, and thematic takeaway

**Format**:
```markdown
## 📚 故事总结 / Story Summary

### 完整故事 / Complete Story
[2-3 sentence summary of the full narrative arc in Chinese]
[2-3 sentence summary in English]

### 学习成果 / Learning Outcomes
**汉字学习 (Characters Learned)**:
- Page 1: [字] ([pinyin]) - [meaning]
- Page 2: [字] ([pinyin]) - [meaning]
- Page 3: [字] ([pinyin]) - [meaning]
[Continue for all pages]

**主题 (Theme)**: [Main theme of the story, e.g., "Growth and patience" / "成长与耐心"]

**核心价值 (Core Value)**: [Key lesson or value, e.g., "Taking care of nature" / "爱护自然"]

### 延伸活动建议 / Extension Activities
1. [Activity suggestion 1 - hands-on or discussion]
2. [Activity suggestion 2 - creative or observational]
3. [Activity suggestion 3 - family or group activity]

### 适合年龄 / Age Suitability
**推荐年龄 (Recommended Age)**: [e.g., 4-6岁 / 4-6 years old]
**角色 (Character)**: [Character name and why suitable]
**学习重点 (Learning Focus)**: [Primary learning objective achieved]
```

**Example Summary (3-Page Seed Growth Story)**:
```markdown
## 📚 故事总结 / Story Summary

### 完整故事 / Complete Story
悦悦在草地上发现了一颗小种子，她小心地把种子种在土里，每天浇水照顾。经过耐心等待，种子发芽长大，开出了美丽的小花。
Yueyue found a tiny seed on the meadow, carefully planted it in the soil, and watered it every day. After patient waiting, the seed sprouted and grew into a beautiful little flower.

### 学习成果 / Learning Outcomes
**汉字学习 (Characters Learned)**:
- Page 1: 草 (cǎo) - grass
- Page 2: 种 (zhòng) - plant/grow
- Page 3: 花 (huā) - flower

**主题 (Theme)**: Growth and patience / 成长与耐心

**核心价值 (Core Value)**: Taking care of living things requires patience and consistent care / 照顾生命需要耐心和持续关爱

### 延伸活动建议 / Extension Activities
1. **种植活动**: 和孩子一起种一颗豆子或花种，每天观察记录 (Planting Activity: Plant a bean or flower seed together, observe and record daily)
2. **成长日记**: 画出种子到花朵的成长过程 (Growth Journal: Draw the growth process from seed to flower)
3. **户外探索**: 去公园寻找不同的种子和花朵 (Outdoor Exploration: Go to a park to find different seeds and flowers)

### 适合年龄 / Age Suitability
**推荐年龄 (Recommended Age)**: 4-6岁 / 4-6 years old
**角色 (Character)**: 悦悦 (Yueyue) - 温柔耐心的性格适合照顾植物的故事
**学习重点 (Learning Focus)**: 植物生长过程、耐心品质、自然观察 (Plant growth process, patience, nature observation)
```

---

### Additional Learning Points (Optional)

When appropriate, you may add:

**Related Vocabulary** (相关词汇):
```
- [Character 1] ([pinyin]) - [meaning]
- [Character 2] ([pinyin]) - [meaning]
```

**Cultural Note** (文化注释):
```
[Brief cultural context or interesting fact]
```

**Extension Activity** (延伸活动) - Single Page:
```
[Simple activity suggestion for parents/teachers]
```

---

## Quality Standards

### Story Quality Checklist
- [ ] Age-appropriate language (3-6 years)
- [ ] Culturally authentic
- [ ] Grammatically correct in both languages
- [ ] Natural-sounding translations (not word-for-word)
- [ ] Engaging and wonder-filled tone

### Technical Quality Checklist
- [ ] Pinyin includes all tone marks
- [ ] Learning point character appears in the story
- [ ] Prompt includes all VCP components
- [ ] Formatting follows template exactly
- [ ] Emojis used for section headers

### Educational Quality Checklist
- [ ] Clear learning objective
- [ ] Character appropriate for learner level
- [ ] Repetition supports learning
- [ ] Visual-text alignment strong
- [ ] Cultural authenticity maintained

### Educational Content Reality Validation (🆕 Critical for Quality Control)

**Purpose**: Ensure educational content is scientifically accurate and doesn't teach incorrect information to children.

**Validation Required When**:
- Age 7+ with discovery/science themes
- Any age with science learning domains
- Nature scenes (meadow, pond, forest, stars, rice-paddy)
- Multi-page stories with educational continuity

#### Reality Validation Checklist by Age Group

**Ages 3-4 (Early Childhood)**:
- [ ] Observable elements match toddler height/reach (~90-100cm)
- [ ] Objects described are visible at child's eye level
- [ ] No microscopic details without magnification context
- [ ] Cause-effect relationships are simple and direct
- [ ] Fantasy elements clearly in imaginative play context (not taught as fact)

**Ages 5-6 (Preschool)**:
- [ ] Observable elements match preschool height/reach (~105-115cm)
- [ ] Seasonal elements consistent (spring flowers, autumn leaves, etc.)
- [ ] Simple scientific observations are factually accurate
- [ ] Basic cause-effect follows natural laws (water flows down, objects fall)
- [ ] No teaching of misconceptions as facts (even if simplified)

**Ages 7-8 (Early Elementary) - HIGH PRIORITY**:
- [ ] **MANDATORY** scientific accuracy for discovery/science themes
- [ ] All plant/animal anatomy descriptions are correct
- [ ] Observable vs. non-observable distinction clear (e.g., bark texture ✅, growth rings on living trees ❌)
- [ ] Physics follows real-world rules (gravity, light, motion)
- [ ] Educational objectives teach correct facts, no oversimplifications that mislead

**Ages 9-12 (Late Elementary/Pre-teen) - HIGHEST PRIORITY**:
- [ ] **CRITICAL** scientific rigor required
- [ ] Advanced concepts are factually accurate (cells, ecosystems, physics principles)
- [ ] Terminology is scientifically correct
- [ ] Complex cause-effect relationships follow natural laws
- [ ] No magical thinking presented as science

#### Scene-Specific Reality Validation

**Nature Scenes** (Meadow, Pond, Forest, Stars, Rice Paddy):
- [ ] Cross-referenced scene's Observable Elements section in `references/config/scenes.md`
- [ ] All visual descriptions in ✅ "Visible & Accurate" list
- [ ] NO elements from ❌ "NOT Visible (Common Errors)" list
- [ ] Seasonal consistency maintained
- [ ] Plant/animal behavior realistic

**Cultural Scenes** (Kitchen, Courtyard, Market, Temple, Festival, Grandma-Room, Kindergarten):
- [ ] Cultural practices accurately represented
- [ ] Observable items correctly described (furniture, tools, decorations)
- [ ] Traditional practices shown with respect
- [ ] Modern vs. traditional elements consistent with scene
- [ ] No cultural stereotypes or misconceptions

#### Common Error Patterns to Avoid (Red Flags 🚩)

**Biological Errors**:
- 🚩 ❌ "growth rings visible on living tree bark" → ✅ CORRECT: "rough bark texture with moss"
- 🚩 ❌ "looking at plant roots underground" → ✅ CORRECT: "carefully digs to see roots"
- 🚩 ❌ "seeing inside the flower" → ✅ CORRECT: "counting petals on the flower"
- 🚩 ❌ "flowers blooming in snow" → ✅ CHECK: only winter-blooming species (plum)

**Physical Errors**:
- 🚩 ❌ "objects floating without support" → ✅ CORRECT: "balloon floats up (helium lighter than air)"
- 🚩 ❌ "water flowing uphill" → ✅ CORRECT: "water flows downhill into pond"
- 🚩 ❌ "stars visible in bright daylight" → ✅ CORRECT: "stars appear after sunset"
- 🚩 ❌ "clear reflection in rippling water" → ✅ CORRECT: "reflection distorts in ripples"

**Observational Errors**:
- 🚩 ❌ "seeing microscopic bacteria" → ✅ CORRECT: "washing hands removes germs (invisible)"
- 🚩 ❌ "looking inside solid objects" → ✅ CORRECT: use cut/open context
- 🚩 ❌ "3-year-old reaching high tree branch" → ✅ CORRECT: match height to age (~90cm reach)
- 🚩 ❌ "seeing through thick walls" → ✅ CORRECT: "hearing sounds from inside"

**Common Sense Errors**:
- 🚩 ❌ "wild bear in kitchen" → ✅ CORRECT: "bear in forest"
- 🚩 ❌ "bright sunshine at midnight" → ✅ CORRECT: "moonlight at night"
- 🚩 ❌ "rain falling indoors" → ✅ CORRECT: rain through open window/hole (context)

#### Error Reporting Process

**If Scientific Error Discovered**:
1. **Immediate**: Flag the error and do NOT generate incorrect content
2. **Document**: Note specific error and why it's incorrect
3. **Correct**: Use Observable Elements guidance to find accurate alternative
4. **Regenerate**: Create new prompt with scientifically accurate description
5. **Report** (for continuous improvement): See `reality-validation.md` Section IX for error reporting template

**Example Error Correction Process**:

**Original Error**:
```
Story: "悦悦看见树的年轮在树皮上。"
Prompt: "examining tree trunk with visible circular growth rings on bark"
❌ ERROR: Growth rings NOT visible on bark-covered living trees
```

**Correction Process**:
1. **Identify**: Growth rings only visible on cut wood, not living bark
2. **Reference**: Check `scenes.md` Forest → Observable Elements → "rough bark texture" ✅
3. **Alternative**: Use "bark texture, moss, knots" OR "fallen log with cut end"
4. **Regenerate**:
   - Story: "悦悦触摸树皮，感觉粗糙的纹理。" (Yueyue touches bark, feels rough texture)
   - Prompt: "examining tree trunk with rough ridged bark, green moss patches"
   OR
   - Story: "悦悦看见倒下的树桩上的年轮。" (Yueyue sees growth rings on fallen stump)
   - Prompt: "kneeling beside fallen log, examining circular growth rings on cut end"

**Reference Files**:
- **Validation Rules**: `references/config/reality-validation.md`
- **Scene Observable Elements**: `references/config/scenes.md` (all 12 scenes)
- **Age-Appropriate Guidelines**: `references/config/age-system.md`

---

## Formatting Notes

### Markdown Styling
- Use `---` horizontal rules between sections
- Bold the section headers with `**text**`
- Emojis at start of each section header
- One blank line between sections

### Text Styling
- Chinese and English on separate lines in Story section
- Maintain consistent spacing
- Use proper punctuation for each language
- Keep prompt as single paragraph

### Consistency
- Always use the same emoji for each section
- Keep section order consistent
- Maintain the same header format
- Use identical spacing patterns

---

## Variations by Purpose

### For Digital Display
- Standard format as shown above
- Full color emoji support
- Regular line spacing

### For Print Publication
- Consider replacing emojis with text labels
- Adjust line spacing for print
- May need larger font considerations
- Include page number if part of series

### For Audio Companion
- Story section remains primary
- May abbreviate prompt section
- Emphasize pinyin for pronunciation guide

---

## File Output Specification

### Markdown File Creation

**When to Create**: ALWAYS create a markdown file for generated content

**File Naming Convention**:
```
[style]-[scene]-[character]-[timestamp].md

Examples:
- clay-meadow-yueyue-20260110.md
- nianhua-kitchen-xiaoming-20260110-143522.md
- paper-cut-festival-meimei-3pages-20260110.md
```

**Naming Components**:
- **style**: Style code (clay, tech, ink, paper-cut, nianhua, porcelain, shadow-puppet)
- **scene**: Scene code (meadow, pond, rice-paddy, stars, forest, kitchen, courtyard, market, temple, festival, grandma-room, kindergarten)
- **character**: Character code (yueyue, xiaoming, lele, meimei)
- **pages** (optional): Add "-3pages", "-5pages", or "-7pages" for multi-page stories
- **timestamp**: YYYYMMDD or YYYYMMDD-HHMMSS format

**File Location**:
```
./output/picture-books/[YYYY-MM]/
```

Create monthly subdirectories for organization:
```
./output/picture-books/
  ├── 2026-01/
  │   ├── clay-meadow-yueyue-20260110.md
  │   ├── nianhua-kitchen-xiaoming-20260115.md
  │   └── paper-cut-festival-meimei-3pages-20260120.md
  ├── 2026-02/
  └── ...
```

**File Content Structure**:

```markdown
# [Story Title] / [故事标题]

**Generated**: [Date and Time]
**Style**: [Style name]
**Scene**: [Scene name]
**Character**: [Character name]
**Pages**: [Number]

---

[If single page]
[Full page content with all sections]

[If multi-page]
## Page 1 / 第一页

[Page 1 content]

---

## Page 2 / 第二页

[Page 2 content]

---

[Continue for all pages...]

---

[Story Summary section for multi-page stories]

---

## Generation Info / 生成信息

- **Generator**: Picture Book Wizard (Claude Code Skill)
- **Model**: [Model used]
- **Timestamp**: [ISO timestamp]
- **Configuration**: [style]/[scene]/[character]/[pages]
```

**Example File Header**:
```markdown
# Seed Discovery / 种子的发现

**Generated**: 2026-01-10 14:35:22
**Style**: Clay (粘土风格)
**Scene**: Meadow (草地)
**Character**: Yueyue (悦悦)
**Pages**: 1

---
```

**Example Multi-Page File Header**:
```markdown
# The Seed's Journey / 种子的旅程

**Generated**: 2026-01-10 15:20:00
**Style**: Clay (粘土风格)
**Scene**: Meadow (草地)
**Character**: Yueyue (悦悦)
**Pages**: 3
**Theme**: Growth and Patience / 成长与耐心

---
```

### File Creation Process

1. **Generate Content**: Create all pages and summary first
2. **Assemble File**: Compile content with headers and metadata
3. **Ensure Directory**: Create monthly directory if doesn't exist
4. **Write File**: Save with proper naming convention
5. **Confirm to User**: Show file path and brief summary

**User Notification Format**:
```
✅ Picture book created successfully!

📁 **File**: ./output/picture-books/2026-01/clay-meadow-yueyue-20260110.md
📖 **Title**: Seed Discovery / 种子的发现
🎨 **Style**: Clay
🌿 **Scene**: Meadow
👧 **Character**: Yueyue
📄 **Pages**: 1

Content includes:
- Bilingual story (Chinese/English)
- Pinyin pronunciation guide
- Learning point: 草 (cǎo) - grass
- Banana Nano image prompt
```

**Multi-Page Notification**:
```
✅ Picture book story created successfully!

📁 **File**: ./output/picture-books/2026-01/clay-meadow-yueyue-3pages-20260110.md
📖 **Title**: The Seed's Journey / 种子的旅程
🎨 **Style**: Clay
🌿 **Scene**: Meadow
👧 **Character**: Yueyue
📄 **Pages**: 3
🎯 **Theme**: Growth and Patience

Content includes:
- 3 complete story pages
- Characters learned: 草 (grass), 种 (plant), 花 (flower)
- Story summary with learning outcomes
- Extension activities for parents/teachers
```

---

## Summary

This template provides the complete structure for generating Picture Book Wizard content with:
- Standard bilingual format (Chinese/English/Pinyin)
- Chinese character learning points
- Optional learning objectives (logic, objects, social, etc.)
- Banana Nano optimized prompts
- Story summaries for multi-page content
- Markdown file output with organized storage

All content should follow this template for consistency and quality assurance.
