# Extending Picture Book Wizard

This guide explains how to extend the Picture Book Wizard skill with new styles, scenes, soul elements, multi-character features, and more.

**Version**: 3.0 (Complete System: Skeleton + Soul + Multi-Character 🆕)

## Table of Contents

- [Before You Begin](#before-you-begin)
- [Adding a New Style](#adding-a-new-style)
- [Adding a New Scene](#adding-a-new-scene)
- [Adding Soul Elements](#adding-soul-elements) 🆕
- [Adding Supporting Characters](#adding-supporting-characters) 🆕
- [Adding Relationship Types](#adding-relationship-types) 🆕
- [Modifying Characters](#modifying-characters)
- [Adding New Languages](#adding-new-languages)
- [Customizing Rendering Parameters](#customizing-rendering-parameters)
- [Creating Custom Templates](#creating-custom-templates)
- [Testing Your Extensions](#testing-your-extensions)

---

## Before You Begin

### Prerequisites

1. **Understand the Architecture**: Read `references/guides/design.md` first
   - Especially the "Three-Layer Architecture" section 🆕
   - Understand Skeleton (structure) vs. Soul (life) vs. Multi-Character (social) 🆕
2. **Review Existing Configs**: Study `references/config/` files to understand patterns
   - Skeleton Layer: styles.md, scenes.md, age-system.md, characters.md
   - Soul Layer: story-soul.md 🆕
   - Multi-Character Layer: supporting-characters.md, relationship-dynamics.md 🆕
3. **Test Current Functionality**: Try all existing combinations before extending
4. **Backup**: Make a copy of the skill directory before modifying

### Extension Philosophy

- **Modular**: Add new files rather than modifying existing ones when possible
- **Consistent**: Follow existing patterns and templates
- **Tested**: Test new additions with multiple combinations
- **Documented**: Update relevant documentation
- **Coherent**: Ensure new elements work harmoniously with existing system 🆕
- **Age-Appropriate**: Consider developmental stages when adding elements 🆕

---

## Adding a New Style

Adding a new visual style (e.g., "watercolor", "pixel-art", "3d-render") involves 4 steps:

### Step 1: Add Style Definition to `references/config/styles.md`

Open `references/config/styles.md` and add a new section following this template:

```markdown
### X. [Style Name] ([中文名]) - `style-code`

**Description**: [One-sentence description of the style]

**Category**: [Core Children's Book / Atmospheric Enhancement / Chinese Cultural / Specialized]

**Visual Characteristics**:
- [Characteristic 1]
- [Characteristic 2]
- [Characteristic 3]
- [Characteristic 4]
- [Characteristic 5]

**Technical Keywords**:
```
[keyword 1], [keyword 2], [keyword 3], [keyword 4]
```

**Best For**:
- [Use case 1]
- [Use case 2]
- [Use case 3]

**Color Palette**:
- [Color 1]
- [Color 2]
- [Color 3]
- [Color 4]

**Soul Element Compatibility**: 🆕
- Works well with: [emotion], [theme], [pacing]
- Avoid with: [conflicting elements]
```

**Example: Adding "Watercolor" Style**

```markdown
### 4. Watercolor (水彩画风格) - `watercolor`

**Description**: Soft watercolor painting with flowing pigments and wet-on-wet techniques

**Category**: Core Children's Book Style (⭐⭐⭐ Highly Recommended)

**Visual Characteristics**:
- Transparent layered washes
- Soft edges with color bleeding
- White paper showing through
- Loose, flowing composition
- Organic color transitions

**Technical Keywords**:
```
watercolor painting style, transparent washes, soft flowing edges, color bleeding effect, wet-on-wet technique, paper texture visible, loose artistic brush strokes
```

**Best For**:
- Gentle, dreamy stories
- Soft emotional moments
- Nature scenes with movement
- Impressionistic narratives

**Color Palette**:
- Soft pastels
- Transparent layers
- Natural pigment colors
- White paper base
- Subtle color gradients

**Soul Element Compatibility**: 🆕
- Works well with: calm, wonder emotions; nature, discovery themes; gentle, building pacing
- Avoid with: Very bold/aggressive emotions (better suited for gouache/vibrant styles)
```

### Step 2: Add Style-Specific Rendering to `references/config/rendering.md`

Open `references/config/rendering.md` and add a rendering specification for your new style:

```markdown
### Watercolor Style Rendering
```
octane render, soft natural lighting, transparent watercolor layers, paper texture visible, 8k resolution, artistic composition, flowing color blends, no watermark, clean image
```

**Additional Parameters**:
- Transparent layered washes
- Soft edge bleeding
- White paper texture base
- Organic color transitions

**Lighting Notes**:
- Soft, diffused natural light
- No harsh shadows
- Emphasis on color luminosity
- Light, airy atmosphere

**CRITICAL**: All rendering anchors MUST include `no watermark, clean image`
```

### Step 3: Test Scene and Soul Compatibility 🆕

Test your new style with:
1. All 12 existing scenes
2. Representative soul element combinations

| Scene | Watercolor Compatibility | Best Soul Combinations |
|-------|-------------------------|------------------------|
| Meadow | ⭐⭐⭐ Excellent | calm + nature + gentle pacing |
| Pond | ⭐⭐⭐ Excellent | wonder + discovery + gentle |
| Forest | ⭐⭐⭐ Excellent | curious + nature + building |
| Kitchen | ⭐⭐ Good | warm + family + gentle |

Add this table to `references/config/scenes.md` in the Scene Compatibility section.

### Step 4: Update SKILL.md

Open `SKILL.md` and update the styles list in the appropriate category:

```markdown
**I. Core Children's Book Styles** (⭐⭐⭐ Highly Recommended):
- `storybook` - Classic children's storybook illustration
- `watercolor` - Soft watercolor with gentle blends
- `gouache` - Opaque gouache with rich colors
...
```

Also update the Style Anchors section under VCP.

### Step 5: Create Example

Create `references/examples/watercolor-pond.md` demonstrating the new style with soul elements:

```markdown
# Example: Watercolor Style Pond Scene with Calm Soul

**Configuration**: `watercolor` + `pond` + age 5 + `calm emotion` + `nature theme`

---

📖 **故事 / Story:**
悦悦静静地坐在水塘边，看着水面上的倒影。
Yueyue sits quietly by the pond, watching reflections on the water.

---

🔤 **拼音 / Pinyin:**
Yuèyuè jìngjìng de zuò zài shuǐtáng biān, kànzhe shuǐmiàn shàng de dàoyǐng.

---

✨ **学习要点 / Learning Point:**
水 (shuǐ) - water

---

🎨 **Banana Nano Prompt:**
A 5-year-old Chinese girl named Yueyue, round face, rosy cheeks, two pigtails with red ribbons, wearing yellow sweater and denim overalls, sitting peacefully beside crystal clear pond with relaxed posture and soft gentle smile (calm emotion), looking at her reflection in water, watercolor painting style, transparent layered washes, soft flowing edges with color bleeding, lotus leaves in gentle greens and blues, water ripples in loose brush strokes, paper texture visible, fresh natural color palette (serene blues, soft greens), soft natural lighting, gentle peaceful atmosphere, octane render, 8k resolution, wet-on-wet technique, serene and gentle mood (calm pacing), no watermark, clean image.

---

## Notes on This Example

**Why This Combination Works**:
- Watercolor's fluid nature perfect for water scenes
- Calm emotion expressed through relaxed posture
- Nature theme evident in observation activity
- Gentle pacing matches watercolor's soft aesthetic
- Fresh color palette reinforces peaceful mood

**Soul Elements Applied**:
- **Emotion (Calm)**: "peaceful", "relaxed posture", "soft gentle smile"
- **Theme (Nature)**: Observation of natural reflection
- **Pacing (Gentle)**: "peacefully", "soft", "serene"
- **Color (Fresh)**: "serene blues, soft greens"
```

### Step 6: Test and Validate

Generate content with the new style and verify:
- [ ] Style keywords appear in prompt
- [ ] Rendering parameters appropriate including watermark prevention
- [ ] Character consistency maintained
- [ ] Soul elements integrate smoothly
- [ ] Output quality meets standards
- [ ] Works with multiple scenes and soul combinations

---

## Adding a New Scene

Adding a new scene (e.g., "beach", "mountain", "city") involves similar steps:

### Step 1: Add Scene to `references/config/scenes.md`

```markdown
### 13. Beach (海滩) - `beach`

**Category**: Nature Scene

**Environment**: Sandy shore with ocean waves

**Visual Elements**:
- Soft golden sand with texture
- Gentle ocean waves
- Seashells scattered on shore
- Blue ocean and sky
- Horizon line visible

**Atmosphere**:
- Open and expansive
- Fresh and breezy
- Playful and relaxing
- Eye-level perspective

**Educational Focus**:
- Ocean and water
- Sand and shore
- Marine concepts
- Summer activities

**Suggested Chinese Characters**:
- 海 (hǎi) - ocean/sea (HSK 1)
- 沙 (shā) - sand (HSK 2)
- 浪 (làng) - wave (HSK 2)
- 贝 (bèi) - shell (HSK 2)

**Scene-Specific Details**:
```
sandy beach shore, gentle ocean waves, seashells scattered, soft golden sand texture, blue ocean horizon, fresh coastal atmosphere
```

**Soul Element Affinity**: 🆕
- **Emotions**: Joyful (playing), calm (watching waves), wonder (discovering shells)
- **Themes**: Nature, discovery, creativity
- **Narratives**: Journey (exploring shore), cumulative (collecting shells)
- **Pacing**: Lively (playing), gentle (peaceful observation)
- **Color**: Fresh & natural, warm & bright, vibrant
```

### Step 2: Test Style and Soul Compatibility 🆕

Test beach scene with all existing styles and soul combinations:

| Style | Beach Compatibility | Best Soul Combinations |
|-------|-------------------|------------------------|
| Clay | ⭐⭐⭐ Excellent | joyful + discovery + lively |
| Watercolor | ⭐⭐⭐ Excellent | calm + nature + gentle |
| Ink | ⭐⭐ Good | reflective + nature + circular |
| Tech | ⭐ Fair | (Beach doesn't align well with tech) |

Add this to the compatibility table in `references/config/scenes.md`.

### Step 3: Update SKILL.md

```markdown
**Available Scenes**:
- **Nature** (6): `meadow`, `pond`, `rice-paddy`, `stars`, `forest`, `beach`
- **Cultural & Daily Life** (7): `kitchen`, `courtyard`, `market`, `temple`, `festival`, `grandma-room`, `kindergarten`
```

### Step 4: Create Example with Soul Elements

Create `references/examples/watercolor-beach-joyful.md` demonstrating scene with soul integration.

### Step 5: Test Chinese Characters

Ensure suggested characters (海, 沙, 浪, 贝) are:
- [ ] Age-appropriate (HSK 1-3)
- [ ] Visually present in scene
- [ ] Contextually relevant
- [ ] Properly pronounced in pinyin
- [ ] Support story themes

---

## Adding Soul Elements

**New in Version 3.0**: Soul elements bring stories to life. Here's how to extend them.

### Adding a New Emotion

Emotions define the character's emotional state and overall atmosphere.

#### Step 1: Add to `references/config/story-soul.md`

```markdown
#### 1.8 Excited (兴奋)
- **Chinese**: 兴奋、激动、期待
- **Characteristics**: Energetic, enthusiastic, anticipatory, thrilled
- **Character Expression**: Wide smile, bouncing movement, clasped hands, sparkling eyes
- **Scene Atmosphere**: Dynamic energy, bright lighting, movement lines
- **Color Influence**: Bright oranges, energetic yellows, vibrant reds
- **Age Suitability**: All ages (3-12), especially 4-8
- **Example Story**: Getting a surprise gift, going on a trip, achieving a goal

**Prompt Integration**:
- Character: "excited bouncing movement, wide enthusiastic smile, sparkling eyes"
- Atmosphere: "energetic thrilled atmosphere, anticipatory mood"
- Body language: "clasped hands, jumping with joy, eager forward-leaning posture"

**Compatible With**:
- Themes: discovery, friendship, creativity, courage
- Narratives: journey, quest, cumulative
- Pacing: lively, building
- Colors: vibrant, warm-bright

**Avoid With**:
- Pacing: gentle (conflicting energy)
- Colors: serene (mismatched mood)
```

#### Step 2: Add Age-Appropriate Guidelines

In the "Integration with Age System" section of `story-soul.md`:

```markdown
#### Ages 5-6 (Preschool)
**Recommended Combinations**:
- **Emotion**: Joyful, Curious, Warm, Wonder, **Excited** 🆕
...
```

#### Step 3: Define Compatibility Rules

Add to the "Story Soul Selection System" section:

```markdown
**Excited Emotion Auto-Selection Rules**:
- Age 3-6: Pair with joyful themes (birthday, celebration)
- Age 7-10: Pair with discovery, achievement themes
- Best narratives: journey, cumulative, quest
- Best pacing: lively, building
- Best colors: vibrant, warm-bright
```

#### Step 4: Test Integration

Create test stories with the new emotion:
- [ ] Different age groups (3-12)
- [ ] Multiple themes
- [ ] Various narratives
- [ ] Different pacing types
- [ ] Multiple color moods

#### Step 5: Create Example

Create `references/examples/storybook-meadow-excited-3pages.md`:

```markdown
# Example: Excited Emotion in Multi-Page Story

**Soul Configuration**:
- Emotion: **Excited** 🆕
- Theme: Discovery
- Narrative: Journey
- Pacing: Building
- Color: Vibrant

**Page 1**: "Yueyue heard about a magical flower in the meadow, her eyes sparkling with excitement..."
**Page 2**: "She bounced along the path, eager to find it, clasping her hands in anticipation..."
**Page 3**: "Finally! The flower glowed before her, and Yueyue jumped with joy..."

**Soul Integration Notes**:
- Excited emotion visible in: "sparkling eyes", "bouncing", "clasping hands", "jumped with joy"
- Building pacing: Anticipation → Search → Discovery
- Vibrant colors: "bright yellows", "energetic oranges", "vivid greens"
```

---

### Adding a New Theme

Themes define the core message or value of the story.

#### Step 1: Add to `references/config/story-soul.md`

```markdown
#### 2.9 Perseverance (坚持)
- **Chinese**: 坚持、毅力、不放弃
- **Core Message**: Persistence, determination, not giving up despite challenges
- **Key Elements**: Multiple attempts, obstacles, eventual success, learning from failure
- **Age Suitability**: Ages 5-12 (requires understanding of challenge/persistence)
  - Ages 5-6: Simple persistence (trying again after failing)
  - Ages 7-8: Multiple attempts, learning from mistakes
  - Ages 9-12: Long-term persistence, strategic adjustments
- **Example Stories**: Learning to ride a bike, solving a puzzle, finishing a project

**Prompt Integration**:
- Story context: "attempting multiple times", "not giving up", "learning from each try"
- Scene elements: "obstacles", "challenges", "signs of effort"
- Props: "tools for multiple attempts", "progress indicators"

**Compatible With**:
- Emotions: brave, reflective, curious
- Narratives: problem-solving, transformation, quest
- Pacing: building, varied
- Colors: vibrant, earthy, warm-bright

**Avoid With**:
- Emotions: calm (lacks challenge energy)
- Pacing: gentle (needs dynamic tension)
```

#### Step 2: Map to Age Groups

Add age-specific applications in `story-soul.md`:

```markdown
#### Ages 7-8 (Early Elementary)
**Recommended Combinations**:
- **Theme**: Discovery, Growth, Courage, Friendship, **Perseverance** 🆕
...
```

#### Step 3: Create Thematic Story Arcs

Document narrative patterns for the new theme:

```markdown
**Perseverance Theme - Story Patterns**:

**3-Page Pattern**:
1. Initial attempt → failure
2. Second attempt with adjustment → progress
3. Final attempt → success and reflection

**5-Page Pattern**:
1. Introduction of challenge
2. First attempt → failure
3. Learning/adjustment
4. Second attempt → progress
5. Success and understanding of perseverance

**7-Page Pattern**:
1. Challenge introduction
2. First attempt → failure
3. Reflection and learning
4. Second attempt → partial success
5. New strategy
6. Third attempt → success
7. Celebration and lesson learned
```

#### Step 4: Test with Soul Combinations

Test perseverance theme with:
- [ ] brave + problem-solving + building + vibrant
- [ ] curious + transformation + varied + fresh
- [ ] reflective + quest + circular + earthy

---

### Adding a New Narrative Structure

Narrative structures define how story events unfold.

#### Step 1: Add to `references/config/story-soul.md`

```markdown
#### 3.7 Mystery (解密)
- **Chinese**: 解密、揭秘、发现真相
- **Pattern**: Question → Clues → Investigation → Revelation
- **Structure**: Mystery appears → gather clues → test hypotheses → discover answer
- **Best For**: Curious/reflective emotions, Discovery/Nature themes
- **Age Suitability**: Ages 7-12 (requires logical thinking)
- **Example**: Why do flowers close at night? → observe → test → discover answer

**Page-by-Page Flow**:
- **Page 1**: Mystery question introduced ("Why does the pond sparkle at night?")
- **Page 2**: Observation and clue gathering ("Yueyue noticed tiny creatures...")
- **Page 3**: Investigation and testing ("She watched closely as darkness fell...")
- **Page 4** (optional): More clues discovered
- **Page 5**: Revelation and understanding ("Fireflies! They make the water sparkle!")

**Prompt Integration**:
- Page 1 pose: "questioning expression, head tilted in curiosity"
- Page 2 pose: "observing closely, taking notes, examining details"
- Page 3 pose: "focused investigative posture, pointing at discovery"
- Final pose: "enlightened joyful expression, understanding gesture"

**Compatible With**:
- Emotions: curious, reflective, wonder
- Themes: discovery, nature, growth
- Pacing: building, varied
- Colors: fresh, vibrant, dreamy

**Avoid With**:
- Ages 3-6 (too complex logically)
- Emotions: joyful (needs investigative focus)
- Pacing: gentle (needs dynamic progression)
```

#### Step 2: Define Narrative Beats

```markdown
**Mystery Narrative - Beat Structure**:

**Setup Beat** (Page 1):
- Introduce mystery/question
- Show character's curiosity
- Establish what needs to be discovered

**Investigation Beat** (Pages 2-3):
- Character gathers clues
- Observations and experiments
- Hypotheses tested

**Revelation Beat** (Final Page):
- Discovery moment
- Understanding achieved
- Lesson learned
```

#### Step 3: Create Multi-Page Example

Create `references/examples/watercolor-pond-mystery-5pages.md` demonstrating the new narrative structure with full soul integration.

---

### Adding a New Pacing Type

Pacing controls story rhythm and energy flow.

#### Step 1: Add to `references/config/story-soul.md`

```markdown
#### 4.6 Rhythmic (韵律)
- **Chinese**: 韵律、节奏感、重复变化
- **Characteristics**: Repetitive pattern with variations, musical quality, predictable rhythm
- **Page Progression**: Pattern established → repeat with variation → repeat with variation → satisfying conclusion
- **Sentence Rhythm**: Repetitive structure with changing content ("Yueyue saw..., Yueyue heard..., Yueyue felt...")
- **Best For**: Joyful/wonder emotions, learning through repetition
- **Age Suitability**: Ages 3-6 (love repetition and pattern)
- **Visual Pacing**: Similar compositions with element variations, consistent framing
- **Example**: Exploring senses story, counting story, color identification story

**Prompt Integration**:
- Consistent framing: "similar composition to previous page"
- Visual rhythm: "repetitive visual pattern with [element] variation"
- Predictable structure: "maintaining visual continuity"

**Compatible With**:
- Emotions: joyful, wonder, calm
- Themes: discovery, nature, creativity
- Narratives: cumulative, cycle
- Colors: any palette with consistency

**Avoid With**:
- Ages 9-12 (prefer sophisticated pacing)
- Narratives: problem-solving (needs dynamic tension)
```

#### Step 2: Define Visual Rhythm Rules

```markdown
**Rhythmic Pacing - Visual Patterns**:

**Consistent Elements**:
- Character pose similarity (with variation)
- Same viewing angle
- Consistent background structure
- Repeated color scheme

**Variation Elements**:
- Different objects of focus
- Changing weather/time
- New characters introduced
- Evolving emotions

**Example Pattern**:
- Page 1: Yueyue looks at red flower
- Page 2: Yueyue looks at blue butterfly (same pose, different subject)
- Page 3: Yueyue looks at yellow sun (same pattern continues)
- Page 4: Yueyue has discovered many beautiful things (pattern conclusion)
```

---

### Adding a New Color Mood

Color moods define the emotional color palette.

#### Step 1: Add to `references/config/story-soul.md`

```markdown
#### 5.8 Mystical & Enchanted (神秘梦幻)
- **Chinese**: 神秘梦幻
- **Primary Colors**: Deep purples, midnight blues, silver, subtle pinks, twilight indigo
- **Psychological Effect**: Mystery, magic, wonder, enchantment, ethereal quality
- **Best For**: Wonder/curious emotions, magical/discovery themes
- **Age Appeal**: Ages 5-10 (magical thinking peak)
- **Lighting**: Moonlight, starlight, magical glow, twilight atmosphere
- **Example Palette**: #4B0082 (indigo), #9370DB (medium purple), #C0C0C0 (silver), #191970 (midnight blue)

**Prompt Integration**:
- "mystical color palette with deep purples and midnight blues"
- "silver moonlight glow creating enchanted atmosphere"
- "twilight indigo sky with subtle pink highlights"
- "ethereal magical lighting"

**Scene Applications**:
- Stars scene: Perfect natural fit
- Forest scene: Twilight/magical forest
- Pond scene: Moonlit reflection magic
- Meadow scene: Night-time wonder

**Compatible With**:
- Emotions: wonder, curious, calm
- Themes: discovery, nature, creativity
- Narratives: journey, quest, transformation
- Pacing: gentle, building, circular

**Avoid With**:
- Bright daytime scenes (conflicts with twilight palette)
- Very young ages 3-4 (may be too dark/scary)
- Joyful emotion (needs brighter palette)
```

#### Step 2: Define Color Relationships

```markdown
**Mystical Color Mood - Hex Values & Relationships**:

**Primary Palette**:
- Indigo: #4B0082 (mysterious depth)
- Medium Purple: #9370DB (magical warmth)
- Midnight Blue: #191970 (night sky)
- Silver: #C0C0C0 (moonlight, starlight)
- Twilight Pink: #FFB6C1 (gentle highlight)

**Supporting Colors**:
- Dark Slate Blue: #483D8B (shadows)
- Plum: #DDA0DD (magical accent)
- Periwinkle: #CCCCFF (ethereal light)

**Lighting Strategy**:
- Key light: Silver/moonlight
- Fill light: Subtle purples
- Accents: Twilight pink highlights
- Shadows: Deep indigo/midnight blue
```

---

### Soul Element Compatibility Testing

When adding ANY soul element, test compatibility:

#### Compatibility Matrix Template

Create a test document:

```markdown
# [New Element] Compatibility Testing

## Skeleton Compatibility

### Styles (18 total):
- [ ] Storybook: ⭐⭐⭐ / ⭐⭐ / ⭐
- [ ] Watercolor: ⭐⭐⭐ / ⭐⭐ / ⭐
- [ ] Gouache: ⭐⭐⭐ / ⭐⭐ / ⭐
[... test all 18 styles]

### Scenes (12 total):
- [ ] Meadow: ⭐⭐⭐ / ⭐⭐ / ⭐
- [ ] Pond: ⭐⭐⭐ / ⭐⭐ / ⭐
[... test all 12 scenes]

### Age Groups:
- [ ] Ages 3-4: Appropriate / Not suitable
- [ ] Ages 5-6: Appropriate / Not suitable
- [ ] Ages 7-8: Appropriate / Not suitable
- [ ] Ages 9-10: Appropriate / Not suitable
- [ ] Ages 11-12: Appropriate / Not suitable

## Soul Compatibility

### Emotions (7 existing + new):
- [ ] Joyful: Compatible / Avoid
- [ ] Calm: Compatible / Avoid
- [ ] Curious: Compatible / Avoid
- [ ] Brave: Compatible / Avoid
- [ ] Warm: Compatible / Avoid
- [ ] Wonder: Compatible / Avoid
- [ ] Reflective: Compatible / Avoid

### Themes (8 existing + new):
[... list all themes]

### Narratives (6 existing + new):
[... list all narratives]

### Pacing (5 existing + new):
[... list all pacing types]

### Colors (7 existing + new):
[... list all color moods]

## Test Combinations

### Recommended Combos:
1. [New Element] + [emotion] + [theme] + [narrative] + [pacing] + [color]
2. [Test combo 2]
3. [Test combo 3]

### Avoid Combos:
1. [New Element] + [conflicting element] - Reason: [why]
2. [Avoid combo 2]

## Integration Notes:
- How element affects character expressions
- How element influences scene atmosphere
- How element integrates with pacing
- How element works with color psychology
```

---

## Adding Supporting Characters

**New in Version 3.0**: Supporting characters enable multi-character stories with authentic social interactions. Here's how to add new supporting characters.

### Prerequisites

Before adding a supporting character, consider:
- **Role**: What relationship dynamic does this character enable? (intergenerational, peer, authority)
- **Age**: What age group benefits most from this character?
- **Themes**: Which themes does this character naturally support? (family, friendship, kindness)
- **Cultural Authenticity**: Does this character accurately represent cultural roles?

### Step 1: Define Character in `references/config/supporting-characters.md`

Follow the Grandma template structure:

```markdown
## [Character Name] ([Chinese Name])

### Basic Information
- **English Name**: [Name]
- **Chinese Name**: [Chinese] ([Pinyin])
- **Age**: [Age] years old
- **Role**: [Family member / Community member / Peer]
- **Relationship Type**: [Primary relationship types this character enables]

### Physical Appearance

**Signature Features** (MUST maintain consistency):
1. [Feature 1 - most distinctive]
2. [Feature 2 - very recognizable]
3. [Feature 3 - consistent element]

**Detailed Description**:
- **Face**: [face description]
- **Hair**: [hair description]
- **Eyes**: [eye description]
- **Build**: [body type]
- **Clothing**: [typical outfit]
- **Accessories**: [signature items]

### Character Anchors

**Primary Anchor** (150 words - for protagonist stories):
```
[Full detailed description with all signature features and soul expression]
```

**Secondary Anchor** (50 words - for supporting role):
```
[Essential features only, simplified for multi-character prompts]
```

### Soul Expressions

For each of the 7 emotions, define how this character expresses it:

**1. Joyful (快乐)**:
- Expression: [facial expression]
- Body language: [posture/gesture]
- Interaction style: [how they share joy]

[Continue for all 7 emotions...]

### Scene Compatibility

**Highly Compatible Scenes**:
- [Scene 1]: [Why compatible]
- [Scene 2]: [Why compatible]

**Moderately Compatible Scenes**:
- [Scene 3]: [Conditions]

**Not Recommended Scenes**:
- [Scene X]: [Why not]

### Theme Compatibility

**Natural Themes** (Auto-suggestion triggers):
- [Theme 1]: [Why natural fit]
- [Theme 2]: [Why natural fit]

**Compatible Themes**:
- [Theme 3]: [Works well with]

**Avoid Themes**:
- [Theme X]: [Why incompatible]

### Narrative Compatibility

**Best Narrative Structures**:
- [Narrative 1]: [How character fits]
- [Narrative 2]: [How character fits]

### Age Suitability

**Optimal Ages**: [Age range]
- **Ages 3-4**: [Limited usage notes]
- **Ages 5-6**: [Good for...]
- **Ages 7-8**: [Excellent for...]
- **Ages 9-12**: [Works well for...]

### Auto-Suggestion Logic

Define when system should suggest this character:

```markdown
**Trigger Conditions**:
1. IF theme = "[theme]" → Suggest [character]
2. IF scene = "[scene]" AND age >= X → Suggest [character]
3. IF emotion = "[emotion]" + theme = "[theme]" → Suggest [character]
```

**Example**:
```
**Trigger Conditions**:
1. IF theme = "family" → Suggest Mom
2. IF scene = "kitchen" AND theme = "family" → Suggest Mom
3. IF scene = "kindergarten" → Suggest Teacher
```
```

### Step 2: Add Character to SKILL.md

Update the character list in SKILL.md:

```markdown
**Supporting Characters** (🆕 Multi-Character System):
- `grandma` (奶奶) - 65-year-old grandmother, warm and wise (Phase 1 MVP)
- `mom` (妈妈) - 35-year-old mother, caring and supportive (Phase 2) 🆕
- Coming in future phases: Dad, Grandpa, Teacher, Community members

**Multi-Character Usage**:
- Use `with:[character]` to add supporting character
- System auto-suggests based on theme/scene
- Example: `/picture-book-wizard watercolor kitchen 6 yueyue with:mom theme:family`
```

### Step 3: Define Relationship Patterns

In `references/config/relationship-dynamics.md`, add relationship patterns for this character:

```markdown
### [Character] Relationship Patterns

**Pair (Intergenerational/Peer)**:
- With [protagonist]: [Interaction dynamic]
- Scene examples: [scenes where they interact]
- Teaching-learning dynamic: [who teaches/learns]

**Family (If applicable)**:
- With [other family members]: [family role]
- Family configuration: [typical family groupings]

**Compatible Protagonists**:
- [Protagonist 1]: [Why compatible]
- [Protagonist 2]: [Why compatible]
```

### Step 4: Create Test Example

Create `references/examples/[style]-[scene]-[protagonist]-[newcharacter]-[pages]pages.md`:

```markdown
# Example: [Protagonist] + [New Character] in [Scene]

**Soul Configuration**:
- Emotion: [emotion]
- Theme: [theme appropriate for new character]
- Narrative: [structure]
- Pacing: [pacing]
- Color: [color mood]
- Relationship: Pair (Intergenerational/Peer) 🆕

**Character Relationship**: [Protagonist] + [New Character]

[Include complete 3-page story demonstrating]:
- Character consistency (signature features maintained)
- Natural interaction
- Teaching-learning or support dynamic
- Theme appropriate for this relationship
- Soul integration across both characters
```

### Step 5: Test Integration

Create test stories across:
- [ ] Multiple themes (family, friendship, kindness, etc.)
- [ ] Multiple scenes (compatible scenes)
- [ ] Multiple ages (appropriate age ranges)
- [ ] Multiple protagonists (all 4 main characters)
- [ ] Multiple soul combinations
- [ ] Multiple relationship dynamics (pair, family if applicable)

### Step 6: Update Auto-Suggestion Logic

Ensure SKILL.md orchestrator includes:

```python
# Pseudo-code for auto-suggestion
IF theme IN ["family", "warm", "kindness"] AND scene = "kitchen":
    SUGGEST [new_character]
    NOTIFY user with context about why suggestion makes sense

IF user accepts OR doesn't specify otherwise:
    relationship = "pair"
    characters = [protagonist, new_character]
    PROCEED with multi-character generation
```

---

## Adding Relationship Types

**New in Version 3.0**: Relationship types define how characters interact. Currently implemented: Solo, Pair. Future: Family, Group.

### When to Add a New Relationship Type

Add a new relationship type when:
- New character count needed (current: 1 for solo, 2 for pair)
- New interaction pattern emerged (teaching-learning, cooperative, competitive)
- New social dynamic needed (family unit, peer group, community)

### Step 1: Define in `references/config/relationship-dynamics.md`

```markdown
### X. [Relationship Name] ([Chinese]) - `relationship-code`

**Chinese**: [Chinese terms]

**Pattern**: [Description of interaction pattern]

**Character Count**: X

**Focus**:
- [Focus area 1]
- [Focus area 2]
- [Focus area 3]

**Best For**:
- **Themes**: [compatible themes]
- **Narratives**: [compatible narratives]
- **Emotions**: [compatible emotions]
- **Ages**: [suitable age ranges]

**Interaction Patterns**:

**A. [Sub-pattern 1]**:
- [Description]
- Example: [example]
- Ages: [ages]

**B. [Sub-pattern 2]**:
- [Description]
- Example: [example]
- Ages: [ages]

**Example Scenarios**:
- [Scenario 1]
- [Scenario 2]
- [Scenario 3]

**Prompt Structure**:
```
[Primary Character Anchor - X words] +
[Primary Action] +
[Secondary Character Anchor - Y words] +
[Tertiary Character Anchor - Z words if >2] +
[Relationship Description] +
[Shared Space Description] +
...
```
```

### Step 2: Define Compatibility Matrices

Add compatibility matrices in `relationship-dynamics.md`:

```markdown
### [New Relationship] × Theme Compatibility

| Theme | Compatibility | Notes |
|-------|--------------|-------|
| [Theme 1] | ✅✅ Excellent | [Why] |
| [Theme 2] | ✅ Good | [Why] |
| [Theme 3] | ⚠️ Limited | [Conditions] |
| [Theme 4] | ❌ Avoid | [Why not] |

### [New Relationship] × Age Suitability

| Age Range | Suitability | Notes |
|-----------|------------|-------|
| Ages 3-4 | [✅/⚠️/❌] | [Cognitive ability notes] |
| Ages 5-6 | [✅/⚠️/❌] | [Social understanding] |
| Ages 7-12 | [✅/⚠️/❌] | [Complex interaction handling] |
```

### Step 3: Define Prompt Assembly Structure

Document how to assemble prompts for this relationship type:

```markdown
### Prompt Assembly for [New Relationship]

**Structure**:
```
[Character 1 Anchor - X words] +
[Character 1 Action] +
[Character 2 Anchor - Y words] +
[Character 2 Action] +
[Character 3 Anchor - Z words if applicable] +
[Relationship Dynamic Description] +
[Shared Activity/Space] +
[Scene Elements] +
[Style] +
[Soul Elements] +
[Rendering Parameters] +
[No Watermark]
```

**Length Budget**: X-Y words total

**Key Principles**:
1. [Principle 1]
2. [Principle 2]
3. [Principle 3]
```

### Step 4: Update SKILL.md Workflow

Add relationship type handling to SKILL.md:

```markdown
**Relationship Dynamics** (🆕 Multi-Character): `solo` (default), `pair`, `family`, `group`, `[new-type]` 🆕

**[New Type] Relationship**:
- Pattern: [description]
- Character count: X
- Best for: [themes/ages]
- Example: `/picture-book-wizard [style] [scene] [age] relationship:[new-type]`
```

### Step 5: Implement Auto-Detection

Add logic to detect when this relationship should be suggested:

```python
# Pseudo-code
IF [condition 1] AND [condition 2]:
    relationship = "[new-type]"
    SUGGEST appropriate characters
    NOTIFY user of relationship type selection
```

### Step 6: Create Test Examples

Create multiple test stories demonstrating:
- [ ] Different character combinations
- [ ] Multiple themes compatible with relationship
- [ ] Various age appropriateness levels
- [ ] Different narrative structures
- [ ] Various soul element combinations
- [ ] Successful prompt assembly (within token limits)

### Step 7: Test Edge Cases

- [ ] Token limit management (especially for 3+ characters)
- [ ] Visual clarity (not too crowded)
- [ ] Age appropriateness (cognitive load)
- [ ] Character feature consistency across all characters
- [ ] Interaction visibility (relationships clear in prompts)

---

## Modifying Characters

To modify an existing character or add a new character:

### Option A: Update Existing Character

Edit `references/config/characters.md`:

1. **Update Visual Description**: Modify physical appearance section
2. **Update Character Anchor**: Revise the prompt template
3. **Update Soul Expression Guide**: How character expresses each emotion 🆕
4. **Update Outfit**: Change clothing if needed
5. **Test All Combinations**: Regenerate examples to ensure consistency

**Warning**: Changing the character affects ALL existing content. Consider versioning.

#### Adding Soul Expressions to Character 🆕

For each emotion, define how the character expresses it:

```markdown
### Yueyue's Soul Expressions

**Joyful**:
- "big bright smile, dancing movement"
- "clapping hands, joyful laughter"
- "bouncing with excitement"

**Calm**:
- "soft gentle smile, relaxed posture"
- "peaceful sitting, serene expression"
- "gentle breathing, tranquil atmosphere"

**Curious**:
- "wide-eyed expression, leaning forward"
- "pointing with interest, examining closely"
- "head tilted in questioning manner"

[... define all 7 emotions]
```

### Option B: Add Additional Character

To support multiple characters:

1. Update `references/config/characters.md` with new character profile
2. Add character to SKILL.md character selection parameter
3. Define soul expressions for new character
4. Create examples demonstrating new character
5. Test with all soul combinations

**Example Usage**:
```
/picture-book-wizard watercolor meadow 5 xiaoming emotion:brave
/picture-book-wizard clay forest 7 meimei theme:creativity
```

#### New Character Template

```markdown
### [Character Name] ([Chinese Name]) - `character-code`

**Age**: [X] years old
**Gender**: [Boy/Girl]
**Personality**: [2-3 key traits]

**Physical Appearance**:
- Face: [description]
- Hair: [signature hairstyle]
- Eyes: [description]
- Signature Feature: [MUST INCLUDE - never changes]

**Default Outfit**:
- Top: [description]
- Bottom: [description]
- Shoes: [description]
- Accessories: [any items]

**Character Anchor**:
```
A [age]-year-old Chinese [boy/girl] named [Name], [face description], [signature feature - MUST INCLUDE], wearing [outfit description]
```

**Personality-Story Fit**:
- Best scenes: [scenes that match personality]
- Best themes: [themes that match character]
- Best emotions: [natural emotional expressions]

**Soul Expressions**: 🆕
- Joyful: [how character shows joy]
- Calm: [how character shows calm]
- Curious: [how character shows curiosity]
- Brave: [how character shows bravery]
- Warm: [how character shows warmth]
- Wonder: [how character shows wonder]
- Reflective: [how character shows reflection]

**Age Adaptation**:
When used with age-driven system, character adapts:
- Ages 3-4: [toddler adaptations]
- Ages 5-6: [preschool version - default]
- Ages 7-8: [early elementary adaptations]
- Ages 9-10: [upper elementary adaptations]
- Ages 11-12: [early adolescent adaptations]
```

---

## Adding New Languages

Currently supports Chinese + English. To add a third language:

### Step 1: Extend Output Template

Edit `assets/templates/output-format.md`:

```markdown
📖 **故事 / Story / Histoire:**
[Chinese text]
[English text]
[French text]

---

🔤 **拼音 / Pinyin:**
[Pinyin for Chinese]

🇫🇷 **Prononciation:**
[Pronunciation guide for French]

---

✨ **学习要点 / Learning Point / Point d'apprentissage:**
[Character] ([pinyin]) - [English] - [French]

**Theme (主题 / Theme / Thème)**: [Theme in all languages] 🆕
**Emotion (情绪 / Emotion / Émotion)**: [Emotion in all languages] 🆕
```

### Step 2: Create Language Config

Create `references/config/languages.md`:

```markdown
# Language Configuration

## Supported Languages

### 1. Chinese (中文)
- Primary language
- Includes Hanzi characters
- Pinyin pronunciation guide
- Target: Young learners (3-12 years)
- Soul element terminology: 情绪, 主题, 叙事, 节奏, 色彩

### 2. English
- Translation of Chinese content
- Simple, child-friendly language
- Educational support language
- Soul element terminology: emotion, theme, narrative, pacing, color

### 3. French (Français)
- Additional translation
- Simple, child-friendly language
- [Specify target audience]
- Soul element terminology: émotion, thème, récit, rythme, couleur

## Translation Guidelines
[Guidelines for maintaining quality across languages]

## Soul Element Translation Guidelines: 🆕
- Emotion names must convey same psychological meaning
- Theme translations should maintain core values
- Narrative structure names should be descriptive
- Pacing terms should reflect rhythm/energy
- Color mood names should evoke same feeling
```

### Step 3: Update Workflow

Modify SKILL.md to generate trilingual content in step 3, ensuring soul elements are properly translated.

---

## Customizing Rendering Parameters

To optimize for a different image generator (e.g., "Stable Diffusion" instead of "banana nano"):

### Step 1: Create Generator Profile

Create `references/config/generators/stable-diffusion.md`:

```markdown
# Stable Diffusion Rendering Parameters

## Standard Parameters
```
high quality, detailed, 4k, trending on artstation, no watermark
```

**CRITICAL**: All generator profiles MUST include watermark prevention directives.

## Style-Specific Adjustments

### Clay Style
```
3d render, octane, clay material, studio lighting, high quality, no watermark, clean image
```

### Watercolor Style
```
watercolor painting, soft washes, paper texture, artistic, high quality, no watermark, clean image
```

## Soul Element Integration

### Emotion Expression
- Joyful: "happy expression, cheerful atmosphere"
- Calm: "peaceful expression, serene atmosphere"
[... define for all emotions]

### Color Mood Application
- Vibrant: "bright saturated colors, high contrast"
- Serene: "soft muted colors, gentle tones"
[... define for all color moods]

## Prompt Structure for Stable Diffusion
```
[Subject with emotion] [Action matching narrative] [Environment with theme] [Style] [Color mood] [Pacing cues] [Quality Tags] [No Watermark]
```
```

### Step 2: Update Main Config

Add generator selection to SKILL.md:

```markdown
**Generator**: `banana-nano` (default), `stable-diffusion`, `midjourney`
```

### Step 3: Conditional Assembly

Modify prompt assembly logic to select appropriate rendering parameters based on generator choice, ensuring soul elements are properly integrated.

---

## Creating Custom Templates

To create alternative output formats (e.g., for print vs. digital):

### Step 1: Create New Template

Create `assets/templates/output-format-print.md`:

```markdown
# Print-Optimized Output Format

## Differences from Standard

- No emojis (replaced with text labels)
- Larger font considerations
- Page numbers included
- Print-friendly formatting
- Soul elements clearly labeled 🆕

## Format

```
STORY (故事):
[Chinese text]
[English text]

PINYIN (拼音):
[Pinyin text]

LEARNING POINT (学习要点):
[Character] ([pinyin]) - [meaning]

STORY SOUL (故事灵魂): 🆕
- EMOTION: [emotion name]
- THEME: [theme name]
- NARRATIVE: [narrative type]
- PACING: [pacing type]
- COLOR MOOD: [color mood]

IMAGE PROMPT:
[Banana nano prompt with soul integration]

PAGE NUMBER: __
```
```

### Step 2: Document Usage

Add section to usage-guide.md explaining when to use each template and how soul elements are displayed.

---

## Testing Your Extensions

### Checklist for New Styles

- [ ] Style definition added to `references/config/styles.md` with category
- [ ] Rendering parameters added to `references/config/rendering.md` with watermark prevention
- [ ] Soul compatibility documented
- [ ] Compatibility table updated in `references/config/scenes.md`
- [ ] SKILL.md updated with new style name in appropriate category
- [ ] At least one example created with soul elements in `references/examples/`
- [ ] Tested with minimum 3 different scenes
- [ ] Tested with 3 different soul combinations
- [ ] Character consistency maintained in all tests
- [ ] Documentation updated in usage-guide.md

### Checklist for New Scenes

- [ ] Scene definition added to `references/config/scenes.md` with category
- [ ] Suggested characters appropriate (HSK 1-3)
- [ ] Scene-specific details comprehensive
- [ ] Soul element affinity documented
- [ ] Compatibility tested with all style categories
- [ ] SKILL.md updated with new scene name
- [ ] At least one example created with soul elements
- [ ] Educational focus clearly defined
- [ ] Visual elements distinctive
- [ ] Works with multiple soul combinations

### Checklist for New Soul Elements 🆕

- [ ] Element added to `references/config/story-soul.md` with complete specification
- [ ] Age-appropriate guidelines defined for all age groups
- [ ] Compatibility rules documented (compatible/avoid)
- [ ] Prompt integration examples provided
- [ ] Tested with multiple skeleton combinations (styles, scenes, ages)
- [ ] Tested with other soul element combinations
- [ ] Multi-page story example created demonstrating element
- [ ] Auto-selection rules added (if applicable)
- [ ] Character expression guide updated (how to express element)
- [ ] Color/atmosphere integration documented
- [ ] usage-guide.md and design.md updated

### Checklist for Character Modifications

- [ ] `references/config/characters.md` updated
- [ ] Character Anchor revised
- [ ] Soul expression guide added/updated for all 7 emotions
- [ ] All examples regenerated and verified
- [ ] Consistency rules clearly documented
- [ ] Signature features identified and preserved
- [ ] Age adaptation guidelines provided
- [ ] Tested with all soul element combinations

---

## Best Practices for Extension

### 1. Start Small
Add one element at a time. Test thoroughly before adding more. For soul elements, start with one dimension (e.g., emotion) before adding to other dimensions.

### 2. Follow Patterns
Look at existing implementations and follow the same structure. Pay special attention to how existing soul elements are integrated.

### 3. Document As You Go
Update docs immediately, not after completion. Document compatibility rules as you discover them.

### 4. Test Combinations
Don't just test your new element in isolation. Test it combined with:
- Existing skeleton elements (all styles, all scenes, all ages)
- Existing soul elements (all emotions, themes, narratives, pacing, colors)
- Edge cases (unusual but valid combinations)

### 5. Maintain Consistency
Ensure new additions align with existing VCP and quality standards. Soul elements should integrate seamlessly.

### 6. Create Examples
A good example is worth 1000 words of documentation. Include soul element integration in all examples.

### 7. Consider Age Appropriateness
Soul elements must be developmentally appropriate:
- Ages 3-4: Simple, concrete concepts
- Ages 5-6: Emerging complexity
- Ages 7-8: More sophisticated understanding
- Ages 9-10: Abstract concepts accessible
- Ages 11-12: Philosophical themes possible

### 8. Test Emotional Coherence 🆕
When combining soul elements, ensure they work together:
- Emotion should match theme
- Narrative should support theme delivery
- Pacing should reinforce emotion
- Color should enhance mood
- No conflicting elements

---

## Extension Examples

### Example 1: Adding "Excited" Emotion (Soul Element)

1. **Add to `references/config/story-soul.md`** under Emotion section
2. **Define characteristics**: Enthusiastic, bouncing, wide smile
3. **Map compatibility**: Works with discovery, creativity, friendship themes
4. **Avoid**: Gentle pacing (energy mismatch), serene colors (mood conflict)
5. **Create test**: `watercolor-meadow-excited-5pages.md`
6. **Define prompt integration**: "excited bouncing movement, wide enthusiastic smile"
7. **Document age suitability**: All ages, peak 4-8
8. **Update auto-selection rules**: Excited pairs with lively pacing, vibrant colors

**Result**: Users can now specify `/picture-book-wizard watercolor meadow 6 emotion:excited`

### Example 2: Adding "Perseverance" Theme (Soul Element)

1. **Add to `references/config/story-soul.md`** under Theme section
2. **Define core message**: Not giving up despite challenges
3. **Map to narratives**: Problem-solving, transformation, quest
4. **Define story patterns**: Initial failure → learning → success
5. **Create examples**: Multi-page stories showing persistence arc
6. **Map to ages**: Best for 5-12 (requires challenge understanding)
7. **Document emotional pairing**: Brave, reflective emotions work well

**Result**: System can auto-select perseverance theme or user can specify theme:perseverance

### Example 3: Adding "Garden" Scene (Skeleton Element with Soul Affinity)

1. **Add to `references/config/scenes.md`** under Nature category
2. **Define visual elements**: Cultivated flowers, pathways, garden tools
3. **Suggest characters**: 花 (flower), 园 (garden), 土 (soil)
4. **Document soul affinity**: Calm, wonder emotions; nature, creativity themes
5. **Test style compatibility**: Watercolor (⭐⭐⭐), Clay (⭐⭐⭐), Ink (⭐⭐)
6. **Create `clay-garden-calm-3pages.md`** demonstrating garden with calm emotion
7. **Update SKILL.md**: Add garden to nature scenes list

**Result**: Users can use `/picture-book-wizard watercolor garden 5 emotion:calm theme:nature`

---

## Getting Help with Extensions

### Questions to Ask

- Does this follow existing patterns (skeleton and soul)?
- Have I tested all necessary combinations (including soul elements)?
- Is the documentation clear and complete?
- Does it maintain character and brand consistency?
- Are soul elements coherent when combined?
- Is it age-appropriate across target range?
- Will this scale if we add more elements later?
- Does watermark prevention work correctly?

### Resources

- **Architecture**: `references/guides/design.md` (especially Two-Layer Architecture section)
- **Usage Patterns**: `references/guides/usage-guide.md`
- **Skeleton Configs**: `references/config/styles.md`, `scenes.md`, `age-system.md`, `characters.md`
- **Soul Config**: `references/config/story-soul.md` 🆕
- **Examples**: All files in `references/examples/` (especially multi-page with soul elements)

---

## Common Extension Scenarios

### Scenario 1: "I want to add a seasonal variant"

**Solution A (Scene Approach)**:
- Add to scenes: `meadow-spring`, `meadow-summer`, `meadow-autumn`, `meadow-winter`
- Document soul affinity for each season

**Solution B (New Dimension)**:
- Create `references/config/seasons.md` as new skeleton dimension
- Define how seasons interact with soul elements
- Update prompt assembly to include seasonal elements

### Scenario 2: "I want to support different age groups" ✅ Already Implemented

**Current Solution**: Use age-driven system (ages 3-12 with 5 groups)
- Auto page count
- Auto learning domains
- Age-appropriate soul element combinations
- Character age adaptation

### Scenario 3: "I want to add more emotions to scenes" ✅ Soul System

**Solution**: Soul elements already address this!
- 7 emotions available (can add more using this guide)
- Emotions integrate with character expressions
- Compatible with all skeleton elements

### Scenario 4: "I want to create stories with specific moral lessons"

**Solution**: Use Theme soul element
- 8 themes available (growth, friendship, courage, etc.)
- Can add new themes using soul element extension guide
- Themes automatically integrate with narrative and pacing

### Scenario 5: "I want to add sound/music elements"

**Solution**: Create new soul dimension
1. Create `Audio Atmosphere` section in `story-soul.md`
2. Define: quiet, lively-music, nature-sounds, rhythmic-beats, silent
3. Map compatibility with existing soul elements
4. Add to prompt assembly: "[audio atmosphere cue]"
5. Test integration with all combinations

### Scenario 6: "I want to add relationship dynamics (solo, pair, group)"

**Solution**: Extend character system or create new soul dimension
1. Add `Relationship` dimension to `story-soul.md`:
   - Solo (solitary exploration)
   - Pair (friendship, teamwork)
   - Group (community, collaboration)
2. Map to themes: Pair → friendship, Group → community
3. Update character anchor to include relationship context
4. Test with all combinations

---

## Conclusion

The modular two-layer architecture makes extensions straightforward:

### For Skeleton Elements (Structure):
1. **Identify** what you want to add (style, scene, age feature)
2. **Follow** the existing template for that element type
3. **Document** soul element affinity
4. **Test** with multiple soul combinations
5. **Validate** quality and consistency

### For Soul Elements (Life):
1. **Identify** which soul dimension (emotion, theme, narrative, pacing, color)
2. **Define** complete specification with compatibility rules
3. **Map** to age groups and skeleton elements
4. **Test** integration with existing system
5. **Document** prompt integration and examples
6. **Validate** emotional coherence

### Key Principles:
- **Modular**: Changes are isolated
- **Tested**: All combinations verified
- **Documented**: Clear specifications
- **Consistent**: Follows patterns
- **Coherent**: Soul elements work harmoniously 🆕
- **Age-Appropriate**: Developmentally suitable 🆕

Remember: Good extensions are modular, tested, documented, coherent, and consistent with existing patterns. Soul elements must work together as a system, not as independent variables.

**Version 3.0**: Complete extension guide for Skeleton + Soul system
