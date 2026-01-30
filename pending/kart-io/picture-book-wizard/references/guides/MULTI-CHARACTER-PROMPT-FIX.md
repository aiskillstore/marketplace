# Multi-Character Prompt Fix Guide

**Version**: 1.0
**Created**: 2026-01-11
**Purpose**: Fix the multi-character prompt generation issue where supporting characters lack detailed visual anchors

---

## 🔍 Problem Summary

### Issue Identified

When generating multi-character picture book stories (involving family members like Dad, Mom, Grandma, siblings), the image prompts **lack detailed visual descriptions** for supporting characters.

**Example of WRONG prompt**:
```
...Meimei [full detailed 150-word description]...
Dad's silhouette visible in background holding lighting stick near large firework base
```

**Example of CORRECT prompt**:
```
...Meimei [full detailed 150-word description]...
35-year-old Chinese father with short neat black hair, friendly warm face, navy blue polo shirt, casual pants, standing in background holding lighting stick near large firework base with encouraging smile
```

### Consequences

- **Inconsistent character appearance**: Each generation produces different-looking family members
- **Breaks visual continuity**: Multi-page stories show different Dads/Moms on each page
- **Poor user experience**: Generated images don't match story context

---

## ✅ Solution: Complete Visual Anchor System

### New Supporting Character Anchors

All supporting characters now have **3 levels of detail**:

| Character | Full Anchor | Simplified Anchor | Background Mention |
|-----------|------------|-------------------|-------------------|
| **Grandma (奶奶)** | 150 words | 50 words | 10 words |
| **Dad (爸爸)** | 150 words | 40 words | 10 words |
| **Mom (妈妈)** | 150 words | 40 words | 10 words |
| **Younger Sibling** | 100 words | 30 words | 10 words |

---

## 📋 Anchor Selection Rules

### When to Use Each Level

**1. Full Anchor (150 words)** - Use when:
- Character is PRIMARY focus of the page
- Character is performing main action
- Character's emotion/expression is story-critical
- First introduction of character in multi-page story

**2. Simplified Anchor (40-50 words)** - Use when:
- Character is SECONDARY/supporting role
- Character is actively participating but not main focus
- Character's face is clearly visible
- Character is in foreground or mid-ground

**3. Background Mention (10 words)** - Use ONLY when:
- Character is TRUE silhouette (back turned, far distance)
- Character's face is NOT visible
- Character is environmental element, not story-active
- Must explain WHY face is not visible (e.g., "back turned to firework")

### ⚠️ CRITICAL RULE

**NEVER use generic descriptions** like:
- ❌ "father figure in background"
- ❌ "mother visible"
- ❌ "grandmother, mother, father, and sibling sitting together"
- ❌ "family members gathered"

**ALWAYS use specific visual anchors**:
- ✅ "35-year-old father with short neat black hair, navy polo shirt, warm smile"
- ✅ "33-year-old mother with shoulder-length ponytail, light pink sweater, gentle expression"
- ✅ "65-year-old grandmother with silver bun, round glasses, burgundy Tang suit, patient smile"

---

## 🛠️ Prompt Assembly Instructions

### Single Supporting Character Prompt

**Structure** (300-350 words):
```
[Primary Character Full Anchor - 150 words] +
[Primary Character Action/Pose + Emotion] +
[Supporting Character Simplified Anchor - 40 words] +
[Supporting Character Action/Pose + Emotion] +
[Interaction Description - relationship visible] +
[Scene Elements] +
[Style Keywords] +
[Color Mood] +
[Pacing Visual Cues] +
[Rendering Parameters] +
[Atmosphere] +
[No Watermark]
```

**Example - Meimei + Dad**:
```
Nianhua style children's picture book illustration,

an 8-year-old Chinese girl named Meimei, heart-shaped face with fair skin, large expressive brown eyes with long lashes and slightly cat-like shape, thin delicate black eyebrows, small petite nose, small rosebud mouth with thin lips, slight dimple on left cheek only, long black hair in high ponytail positioned at crown of head to mid-back secured with rainbow pattern plastic hairclip (SIGNATURE), bangs cut straight across forehead, naturally straight and shiny hair, wearing festive crimson red silk qipao dress with golden chrysanthemum embroidery and mandarin collar, dress hem to knees with traditional frog button closures, bright red velvet Mary Jane shoes with golden buckles, white lace-trimmed socks, slender build approximately 125cm tall, graceful school-age proportions,

thrilled excited expression with sparkling eyes gazing upward and joyful open-mouthed smile, dynamic pose with both hands raised clapping together at chest level, body slightly tilted back looking up at sky,

35-year-old Chinese father with short neat black hair in modern style, friendly warm face with kind eyes and gentle smile, wearing navy blue polo shirt and dark casual pants, comfortable sneakers, average healthy build approximately 175cm tall,

standing in background near large firework base, holding lighting stick with proud encouraging expression, watching daughter's reaction with warm fatherly smile,

loving father-daughter interaction visible through shared excitement and connection,

traditional Beijing courtyard at night, magnificent giant golden peony firework bursting in upper sky, deep indigo night sky background, red lanterns glowing warmly on courtyard eaves, stone ground reflecting golden light,

vibrant festive New Year painting colors with brilliant golds and reds against dark blue night, bold clean black outlines, dynamic asymmetrical composition with firework as focal point, flat decorative folk art style,

octane render, dramatic contrast between dark night and brilliant firework illumination, 8k resolution, age-appropriate for 7-9 years, explosive joyful celebration atmosphere, peak excitement mood,

no watermark, clean image
```

---

### Multiple Supporting Characters Prompt

**Structure** (350-400 words max):
```
[Primary Character Full Anchor - 150 words] +
[Primary Character Action/Emotion] +
[Secondary Character 1 Simplified Anchor - 40 words] +
[Secondary Character 1 Action] +
[Secondary Character 2 Simplified Anchor - 40 words] +
[Secondary Character 2 Action] +
[Background Characters Brief - 30 words total] +
[Family Relationship Description] +
[Scene Elements] +
[Style + Color + Mood + Rendering] +
[No Watermark]
```

**Example - Family Gathering (Meimei + Mom + Dad + Grandma + Sibling)**:
```
Nianhua style children's picture book illustration,

an 8-year-old Chinese girl named Meimei, [full 150-word anchor description],

sitting on small traditional red wooden stool at low round table, right hand holding chopsticks bringing dumpling toward mouth, left hand supporting small red porcelain bowl, warm happy content expression with bright smile and relaxed joyful eyes,

beside her 33-year-old Chinese mother with shoulder-length black hair in neat ponytail, gentle kind face, light pink comfortable knit sweater, simple casual beige pants, slender graceful build, serving dumplings from bamboo steamer with tender caring expression,

across table 35-year-old Chinese father with short neat black hair, friendly warm face, navy blue polo shirt, dark casual pants, laughing warmly while watching family with proud happy smile,

65-year-old grandmother with silver-gray hair in traditional bun, round old-fashioned glasses, burgundy Tang suit, sitting contentedly at table head with peaceful loving expression, 5-year-old younger sister with pigtails and pink dress playing with chopsticks nearby,

warm loving multi-generational family interaction showing togetherness and reunion,

traditional Beijing courtyard at night, steaming bamboo dumpling steamers on red lacquered round wooden table, small red porcelain teacups, colorful fireworks bursting in upper night sky,

vibrant festive New Year painting colors with warm reds and golds, bold clean black outlines, balanced composition with family group in lower two-thirds,

octane render, layered warm lighting from lanterns and fireworks creating cozy atmosphere, 8k resolution, age-appropriate for 7-9 years, harmonious family togetherness atmosphere,

no watermark, clean image
```

---

## 🔧 How to Fix Existing Stories

### Step-by-Step Repair Process

**For stories already generated with generic character descriptions:**

1. **Identify all pages with multiple characters**
   - Look for mentions of "Dad", "Mom", "Grandma", "sibling", "family members"

2. **Check current prompt quality**
   - ❌ Generic: "Dad's silhouette", "mother figure", "family gathered"
   - ❌ Missing: No description at all
   - ✅ Correct: Full visual anchor with specific details

3. **Select appropriate anchor level**
   - Is character's face visible? → Minimum Simplified Anchor (40 words)
   - Is character active in scene? → Simplified or Full Anchor
   - Is character truly background silhouette? → Brief mention BUT explain why

4. **Insert anchor from supporting-characters.md**
   - Copy appropriate anchor (Full, Simplified, or Background)
   - Adjust for scene context (emotion, action, clothing if needed)

5. **Verify token budget**
   - Total prompt should be 350-400 words maximum
   - Primary character: ~150 words
   - Each supporting character: ~40 words
   - Scene/style/rendering: ~100 words

6. **Test prompt**
   - Generate image
   - Verify all characters appear as described
   - Check visual consistency with other pages

---

## 📊 Quick Reference Table

### Character Anchor Templates

#### Grandma (奶奶)

**Full (150w)**:
```
A 65-year-old Chinese grandmother (Nǎinai), kind elderly face with gentle wrinkles and soft smile lines, silver-gray hair in neat traditional low bun (signature feature - MUST include), warm brown eyes behind round old-fashioned glasses (signature feature - MUST include), wearing deep burgundy traditional Tang-style jacket with mandarin collar and decorative frog buttons, matching loose-fitting pants, traditional black cloth shoes, slightly plump comforting figure, medium height with slightly bent posture, soft nurturing appearance, gentle welcoming expression
```

**Simplified (50w)**:
```
65-year-old Chinese grandmother with silver hair in traditional bun, round old-fashioned glasses, burgundy Tang suit, warm gentle smile
```

---

#### Dad (爸爸)

**Full (150w)**:
```
A 35-year-old Chinese father (Bàba), friendly warm face with kind eyes and gentle smile, square jawline, clean-shaven or short neat beard, short black hair in neat modern style with slight natural side part (signature feature - MUST include), warm dark brown eyes showing kindness and energy, wearing simple solid navy blue polo shirt, clean dark casual pants, comfortable sneakers, average healthy build approximately 175cm tall, natural father figure proportions, active energetic appearance, approachable caring expression
```

**Simplified (40w)**:
```
35-year-old Chinese father with short neat black hair, friendly face, navy polo shirt, casual pants, warm caring smile
```

**Background (10w)**:
```
father figure standing in background with [reason for limited visibility]
```

---

#### Mom (妈妈)

**Full (150w)**:
```
A 33-year-old Chinese mother (Māma), gentle kind face with soft features and warm loving expression, delicate facial structure with natural beauty, shoulder-length black hair in soft waves or neat low ponytail with simple hair clip (signature feature - MUST include), warm dark brown eyes showing tenderness and caring gaze, slight smile lines, wearing soft light pink comfortable knit sweater, simple casual beige pants, comfortable flat shoes, slender graceful build approximately 165cm tall, natural mother figure proportions, gentle nurturing appearance, tender caring expression
```

**Simplified (40w)**:
```
33-year-old Chinese mother with shoulder-length black hair in ponytail, gentle face, light pink sweater, warm loving smile
```

**Background (10w)**:
```
mother figure in background with [reason for limited visibility]
```

---

#### Grandpa (爷爷)

**Full (150w)**:
```
A 67-year-old Chinese grandfather (Yéye), kind weathered elderly face with deep smile lines showing character and wisdom, fair skin with age spots, short gray-white hair in traditional neat style with receding hairline (signature feature - MUST include), warm brown eyes with crow's feet when smiling, bushy gray eyebrows, optional short neat white beard or clean-shaven, wearing dark gray traditional Tang suit with mandarin collar and fabric button closures, matching loose-fitting pants, traditional black cloth shoes, slightly thin but healthy elderly build approximately 170cm tall, slightly stooped posture from age, strong hands showing life of work, gentle wise expression
```

**Simplified (40w)**:
```
67-year-old Chinese grandfather with short gray-white hair, weathered kind face, dark gray Tang suit, gentle wise smile
```

---

### Animal Character Anchor Templates (🆕 Version 3.2)

#### Cat (小黑 - Black Cat)

**Full (80w)**:
```
A small domestic black cat named Xiǎo Hēi, sleek jet-black fur with healthy shine (signature feature - MUST include), bright golden-yellow eyes with vertical pupils showing curiosity, pink nose and inner ears, white whiskers, long elegant tail, slender graceful feline build approximately 25cm tall at shoulder, typical house cat proportions, [emotion-appropriate posture like ears forward alert OR sitting peacefully OR playing with paws]
```

**Simplified (30w)**:
```
Small black cat with sleek jet-black fur, bright golden eyes, pink nose, elegant tail, [emotion posture]
```

---

#### Dog (大黄 - Golden Dog)

**Full (80w)**:
```
A medium-sized friendly dog named Dà Huáng, fluffy golden-yellow fur with soft texture (signature feature - MUST include), warm brown eyes showing loyalty and friendliness, black wet nose, floppy soft ears, long wagging tail, sturdy friendly build approximately 50cm tall at shoulder, typical medium dog proportions, [emotion posture like tail wagging excitedly OR sitting attentively OR play bow position]
```

**Simplified (30w)**:
```
Medium golden-yellow dog with fluffy fur, warm brown eyes, floppy ears, wagging tail, [emotion posture]
```

---

#### Rabbit (小白兔 - White Rabbit)

**Full (70w)**:
```
A small fluffy rabbit named Xiǎo Bái Tù, pure snow-white soft fur (signature feature - MUST include), long upright pink-lined ears, pink twitching nose, gentle red eyes, small fluffy cotton-ball tail, soft round body approximately 20cm tall when sitting, typical rabbit proportions, [emotion posture like ears up alert OR sitting peacefully OR standing on hind legs]
```

**Simplified (25w)**:
```
Small white rabbit with fluffy white fur, long ears, pink nose, gentle red eyes, [emotion posture]
```

---

#### Butterfly (蝴蝶)

**Full (50w)**:
```
A colorful butterfly, delicate wings with vibrant pattern (specify: orange and black monarch pattern OR yellow swallowtail with black stripes OR white cabbage butterfly), thin black body and antennae, wingspan approximately 8-10cm, graceful flight pattern, [landing on flower OR flying around child OR resting with wings open]
```

**Simplified (20w)**:
```
Colorful [specify pattern] butterfly with delicate wings, thin body, [flight behavior]
```

---

#### Frog (青蛙)

**Full (60w)**:
```
A small green frog, smooth moist green skin, large bulging eyes, wide mouth, four webbed feet, sitting in classic frog pose with bent legs, approximately 5-8cm body length, typical frog proportions, [emotion posture like sitting on lily pad OR jumping into water OR catching insect]
```

**Simplified (25w)**:
```
Small green frog with smooth green skin, large eyes, webbed feet, [behavior]
```

---

#### Chick (小鸡)

**Full (60w)**:
```
A small fluffy yellow chick, soft downy yellow feathers covering round body, tiny orange beak, black beady eyes full of energy, tiny orange legs and feet, approximately 8cm tall, baby chicken proportions, [emotion posture like pecking ground curiously OR chirping with open beak OR nestled in child's hands]
```

**Simplified (25w)**:
```
Small fluffy yellow chick with downy feathers, tiny orange beak, black eyes, [behavior]
```

---

## Animal-Child Interaction Examples

### Example 1: Child + Pet Cat

```
Watercolor children's book illustration,

5-year-old Chinese girl Yueyue, round face with rosy cheeks, large brown almond eyes, two high pigtails with bright red ribbon bows (signature), jet black hair, wearing bright yellow knit sweater, denim overalls, white sneakers, chubby preschooler build 105cm tall,

kneeling on grass with gentle caring expression, right hand extended softly toward cat, left hand on knee, curious loving gaze,

small domestic black cat Xiǎo Hēi, sleek jet-black fur with healthy shine, bright golden-yellow eyes with vertical pupils showing curiosity, pink nose, white whiskers, long elegant tail, approaching child cautiously with tail up showing trust, ears forward interested,

tender child-animal connection showing kindness and gentle interaction,

green meadow background, scattered wildflowers, soft grass, afternoon warm sunlight,

soft watercolor with gentle blends, warm color palette with yellows greens and black accents,

octane render, natural warm lighting, 8k resolution, age-appropriate for 3-6 years,

no watermark, clean image
```

**Token Count**: ~300 words ✅

---

### Example 2: Child + Wild Butterfly

```
Gouache children's book illustration,

7-year-old Chinese boy Xiaoming, round face with fair skin, bright brown almond eyes, short neat black hair with side part (signature), wearing bright royal blue t-shirt, khaki shorts, canvas sneakers, average 6-year-old build 115cm tall,

standing in meadow with amazed wonder expression, both arms slightly raised, eyes wide following butterfly's flight, mouth open in delighted "wow",

colorful monarch butterfly with vibrant orange wings and black vein patterns, delicate thin black body and antennae, wingspan 10cm, gracefully flying in spiral pattern around child's head landing briefly on extended finger,

magical discovery moment showing child-nature wonder and gentle observation,

sunny meadow with purple wildflowers, green grass, blue sky background,

rich gouache colors with vibrant oranges blues and greens, slightly impressionistic style,

octane render, bright natural sunlight, 8k resolution, age-appropriate 7-9 years,

no watermark, clean image
```

**Token Count**: ~280 words ✅

---

### Example 3: Child + Grandparent + Pet

```
Storybook children's illustration,

4-year-old Chinese girl Meimei, heart-shaped face, large expressive brown eyes with cat-like shape, long black hair in high ponytail with rainbow hairclip (signature), wearing pastel pink dress with flower print, white sandals, slender 4-year-old build 100cm tall,

sitting cross-legged on floor with excited joyful expression, both hands clapping together, laughing with delight,

67-year-old Chinese grandfather with short gray-white hair, weathered kind face, dark gray Tang suit, sitting on low stool nearby with warm gentle smile, hand extended holding toy for dog,

medium golden-yellow dog Dà Huáng with fluffy fur, warm brown eyes, floppy ears, wagging tail excitedly, standing on hind legs doing trick for treat, front paws up,

warm multi-generational family moment with pet showing love play and connection,

traditional courtyard interior, wooden furniture, warm afternoon light through window,

classic storybook illustration style with warm colors, grandfather-grandchild-pet harmony,

octane render, soft indoor lighting, 8k resolution, age-appropriate 3-6 years,

no watermark, clean image
```

**Token Count**: ~320 words ✅

---



**Full - Brother (100w)**:
```
A young Chinese boy (younger brother), approximately [age] years old, round chubby face with big curious eyes, small button nose, sweet innocent smile, short black hair in simple bowl cut, wearing bright blue t-shirt, comfortable shorts, sneakers, small toddler proportions, energetic playful appearance, cheerful expression
```

**Full - Sister (100w)**:
```
A young Chinese girl (younger sister), approximately [age] years old, round sweet face with large expressive eyes, small delicate features, innocent cheerful smile, shoulder-length black hair in two small pigtails with pink hair ties, wearing cute pink dress, Mary Jane shoes, small young child proportions, playful gentle appearance, happy expression
```

**Simplified (30w)**:
```
Young [brother/sister] approximately [age] years old with round face, short black hair, bright [color] clothing, cheerful smile
```

---

## ✅ Quality Verification Checklist

**Before finalizing any multi-character prompt**, verify:

### Character Description Quality
- [ ] **Every visible character has visual anchor** (NOT generic "father figure" or "family members")
- [ ] **Signature features included** for each character (hair, face, outfit specifics)
- [ ] **Age-appropriate proportions** described (height, build)
- [ ] **Emotional expressions** specified for each character (not just primary)
- [ ] **Clothing details** provided (color, style, accessories)

### Interaction Quality
- [ ] **Character relationships** explicitly stated (father-daughter, grandmother-grandchild)
- [ ] **Interaction poses/actions** described for each character
- [ ] **Emotional connection** visible through expressions and body language
- [ ] **Spatial arrangement** clear (who is where in composition)

### Technical Quality
- [ ] **Total word count** within 350-400 limit
- [ ] **Token allocation** appropriate (150 primary, 40 each supporting, 100 scene/style)
- [ ] **"no watermark, clean image"** included at end
- [ ] **Scene elements** don't overwhelm character descriptions

### Consistency Quality (Multi-Page Stories)
- [ ] **Same anchor used** for each character across all pages (visual continuity)
- [ ] **Signature features** maintained (Grandma's bun+glasses, Dad's hair, etc.)
- [ ] **CCLP level** appropriate (STRICT for 3-5 pages, MODERATE for 5-10, FLEXIBLE for 10+)
- [ ] **Clothing consistency** logical (same outfit unless narrative reason to change)

---

## 🚨 Common Mistakes to Avoid

### ❌ Mistake 1: Generic Descriptions
**Wrong**:
```
Dad's silhouette visible in background
```
**Right**:
```
35-year-old Chinese father with short neat black hair, navy polo shirt, standing in background holding lighting stick with proud smile (face partially visible in firework glow)
```

---

### ❌ Mistake 2: Missing Key Details
**Wrong**:
```
mother sitting at table
```
**Right**:
```
33-year-old Chinese mother with shoulder-length black hair in ponytail, gentle face, light pink sweater, sitting at table serving dumplings with warm caring expression
```

---

### ❌ Mistake 3: No Emotional Expression
**Wrong**:
```
father standing nearby
```
**Right**:
```
35-year-old Chinese father with short neat black hair, friendly face, navy polo shirt, standing nearby with proud encouraging smile watching daughter's excitement
```

---

### ❌ Mistake 4: Token Budget Imbalance
**Wrong** (too much on scene, too little on characters):
```
Meimei [150w] ... Dad [10w] ... elaborate courtyard with detailed architecture, ornate decorations, intricate window patterns, traditional furniture, hanging lanterns in various styles, stone pathways, decorative plants, carved wooden pillars... [150w scene description]
```
**Right** (balanced allocation):
```
Meimei [150w] ... Dad [40w] ... traditional Beijing courtyard at night, red lanterns, wooden architecture, stone ground [40w scene]
```

---

### ❌ Mistake 5: Forgetting Signature Features
**Wrong**:
```
grandmother with gray hair, wearing traditional clothing
```
**Right**:
```
65-year-old grandmother with silver-gray hair in neat traditional low bun (SIGNATURE), round old-fashioned glasses (SIGNATURE), burgundy Tang suit
```

---

## 📝 Implementation Workflow

### For NEW Stories

**Step 1: Identify all characters in story**
- Primary protagonist (e.g., Meimei)
- Supporting characters (e.g., Dad, Mom, Grandma)
- Background characters (e.g., younger sibling, other children)

**Step 2: Determine anchor level for each page**
- Page 1: Only Meimei → Full anchor for Meimei only
- Page 2: Meimei + Dad (active) → Full Meimei + Simplified Dad
- Page 3: Meimei + background children → Full Meimei + brief children mention
- Page 4: Meimei + entire family → Full Meimei + Simplified Mom/Dad/Grandma + brief sibling
- Page 5: Meimei with family in background → Full Meimei + brief family silhouettes

**Step 3: Assemble prompt using templates**
- Copy appropriate anchor from supporting-characters.md
- Insert into prompt structure
- Add emotion/action specific to scene
- Verify token budget (350-400w total)

**Step 4: Verify quality checklist**
- Run through all checklist items above
- Ensure CCLP consistency across pages
- Confirm "no watermark" at end

**Step 5: Generate and review**
- Generate image
- Check character appearance matches anchors
- Verify emotional expressions match story
- Confirm visual consistency with previous pages

---

### For EXISTING Stories (Repair)

**Step 1: Audit current prompts**
- Identify pages with multiple characters
- Flag generic descriptions ("Dad's silhouette", "family members")
- Note missing visual anchors

**Step 2: Determine appropriate fixes**
- Check if character face is actually visible in scene
- If visible → Replace generic with Simplified Anchor (40w)
- If truly silhouette → Keep brief but add context (why not visible)

**Step 3: Rebuild prompts**
- Replace generic descriptions with proper anchors
- Maintain original scene/style/mood descriptions
- Keep within 350-400w budget

**Step 4: Test consistency**
- Regenerate images for fixed pages
- Compare with original pages
- Verify character consistency across story

---

## 📈 Success Metrics

**A properly fixed multi-character prompt should**:
- ✅ Every visible character has specific visual description
- ✅ Character appearance consistent across multiple pages
- ✅ Emotional expressions match story context
- ✅ Family relationships visually clear
- ✅ No generic "figure in background" descriptions
- ✅ Token budget balanced (characters + scene + style)
- ✅ Professional picture book quality output

---

## 🎯 Summary: The Core Fix

**Problem**: Supporting characters lack detailed visual anchors
**Solution**: Use 3-level anchor system (Full 150w / Simplified 40w / Background 10w)
**Rule**: NEVER use generic descriptions - ALWAYS use specific visual anchors from supporting-characters.md
**Quality**: Every visible character must have detailed visual description

**File Reference**: `.claude/skills/picture-book-wizard/references/config/supporting-characters.md`

---

## 📚 Related Documentation

- **SKILL.md**: Main workflow and parameter usage
- **supporting-characters.md**: Complete character anchor definitions
- **relationship-dynamics.md**: Multi-character interaction logic
- **character-consistency-lock.md**: CCLP protocol for visual consistency
- **output-format.md**: Complete prompt assembly structure

---

**Version**: 1.0
**Last Updated**: 2026-01-11
**Status**: ✅ Active - Implement immediately for all multi-character stories
