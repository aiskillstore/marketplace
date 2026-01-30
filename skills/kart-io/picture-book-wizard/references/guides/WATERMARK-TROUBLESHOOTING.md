# Watermark Troubleshooting Guide

**Version**: 1.0
**Created**: 2026-01-11
**Purpose**: Diagnose and fix watermark issues in generated picture book images

---

## 🚨 The Watermark Problem

### Why Watermarks Appear

AI image generators (including banana nano) may add watermarks/signatures/text overlays for several reasons:

1. **Default Protection**: Generators protect their output by default
2. **Style Recognition**: Digital/tech styles trigger automatic watermarking
3. **Weak Directives**: Simple "no watermark" is often insufficient
4. **Placement Issues**: Directives buried mid-prompt get ignored
5. **Missing Positive Framing**: Lacking "professional publication" context

---

## 🔍 Quick Diagnosis

### Check Your Prompt

**Step 1: Locate watermark directive**

Look for watermark prevention at the END of your prompt. It should be the LAST thing before the prompt ends.

✅ **Correct Placement**:
```
...traditional courtyard, warm lighting, octane render, 8k resolution, warm atmosphere, clean professional picture book illustration, pristine image quality, no watermark, no text, no signature, no logo, no branding, clean professional image
```

❌ **Wrong Placement** (directive too early):
```
...traditional courtyard, no watermark, clean image, warm lighting, octane render, 8k resolution, warm atmosphere
```

---

**Step 2: Check directive strength**

Compare your directive to the three levels:

**Level 1** (Standard - 20 words):
```
clean professional picture book illustration, pristine image quality, no watermark, no text, no signature, no logo, no branding, clean professional image
```

**Level 2** (Enhanced - 35 words):
```
clean professional children's book illustration, publication-ready quality, pristine unmarked image, full bleed composition, no watermark, no text overlays, no signatures, no artist marks, no logos, no branding, no copyright symbols, no website URLs, clean professional image
```

**Level 3** (Maximum - 50 words):
```
professionally published children's picture book illustration, commercial print quality, pristine unmarked image, full bleed edge-to-edge composition, absolutely no watermarks, no text overlays of any kind, no signatures, no artist marks, no logos, no branding elements, no copyright symbols, no website URLs, no social media handles, no QR codes, clean professional publication-ready image
```

If your directive is weaker than Level 1, that's likely the problem.

---

**Step 3: Check style risk**

High-risk styles that often get watermarked:
- ❗ `tech` (科技风格)
- ❗ Digital art styles
- ❗ Modern/contemporary styles
- ❗ Photorealistic styles

Low-risk styles:
- ✅ `watercolor` (水彩)
- ✅ `clay` (粘土)
- ✅ `gouache` (水粉)
- ✅ `ink` (水墨)
- ✅ `nianhua` (年画)
- ✅ `storybook` (经典绘本)

If using high-risk style with Level 1 directive, upgrade to Level 2.

---

## 🛠️ Fix Strategies

### Fix #1: Upgrade Directive Level

**If watermark appears with Level 1** → Upgrade to Level 2

**Before** (Level 1 failed):
```
...warm atmosphere, no watermark, clean image
```

**After** (Level 2):
```
...warm atmosphere, clean professional children's book illustration, publication-ready quality, pristine unmarked image, full bleed composition, no watermark, no text overlays, no signatures, no artist marks, no logos, no branding, no copyright symbols, no website URLs, clean professional image
```

---

### Fix #2: Correct Placement

**If directive is NOT the last thing** → Move to absolute end

**Before** (wrong placement):
```
...Yueyue with red ribbons, no watermark, clean image, traditional courtyard, warm lighting, 8k resolution
```

**After** (correct placement):
```
...Yueyue with red ribbons, traditional courtyard, warm lighting, 8k resolution, clean professional picture book illustration, pristine image quality, no watermark, no text, no signature, no logo, no branding, clean professional image
```

---

### Fix #3: Add Positive Framing

**If missing "clean professional" framing** → Add before negative directives

**Before** (only negative):
```
...warm atmosphere, no watermark, no text, clean image
```

**After** (positive + negative):
```
...warm atmosphere, clean professional picture book illustration, pristine image quality, no watermark, no text, no signature, no logo, no branding, clean professional image
```

The positive framing signals "professional publication standard" to the generator.

---

### Fix #4: Switch to Lower-Risk Style

**If tech/digital style keeps watermarking** → Try traditional style

**Before** (tech style, high watermark risk):
```
/picture-book-wizard tech laboratory 8 5 xiaoming
```

**After** (watercolor, low risk):
```
/picture-book-wizard watercolor meadow 8 5 xiaoming
```

Traditional art styles (watercolor, clay, gouache) are much less prone to watermarking.

---

### Fix #5: Add Spatial Directives

**If corner/edge watermarks persist** → Add composition protection

**Add to directive**:
```
full bleed composition, edge-to-edge artwork, complete image coverage
```

**Full example**:
```
...warm atmosphere, clean professional picture book illustration, pristine image quality, full bleed composition, no watermark, no text, no signature, no logo, no branding, clean professional image
```

This prevents generators from adding watermarks in "empty" corner spaces.

---

## 📋 Step-by-Step Repair Process

### For Existing Watermarked Prompts

**Step 1: Identify current level**

Read your prompt's ending. What do you have?
- Nothing or just "no watermark" → You're at Level 0 (inadequate)
- "no watermark, clean image" → Level 0.5 (weak)
- Full Level 1 → Check if it's at the END
- Full Level 2 → Should work unless very high-risk

---

**Step 2: Determine target level**

Ask:
- Using tech/digital style? → Level 2 minimum
- Commercial project? → Level 2
- Standard traditional style? → Level 1
- Previous attempts failed? → Upgrade one level

---

**Step 3: Rebuild prompt ending**

1. Copy everything BEFORE watermark directive
2. Delete old watermark directive
3. Add appropriate level directive at THE VERY END
4. Verify nothing comes after it

**Template**:
```
[Character] + [Action] + [Scene] + [Style] + [Rendering] + [Atmosphere] + [WATERMARK DIRECTIVE - LAST]
```

---

**Step 4: Test**

Generate image with new prompt. Check for:
- ✅ No watermark text
- ✅ No signature/artist name
- ✅ No logos/branding
- ✅ No corner text overlays
- ✅ Clean professional appearance

If watermark still appears → Upgrade to next level and retry.

---

## 🎯 Real Examples

### Example 1: Basic Fix (Level 0 → Level 1)

**BEFORE** (watermark appeared):
```
Watercolor illustration, 5-year-old girl Yueyue with red ribbon pigtails, yellow sweater, kneeling in meadow discovering seed, soft lighting, 8k, no watermark
```

**AFTER** (Level 1 added):
```
Watercolor illustration, 5-year-old girl Yueyue with red ribbon pigtails, yellow sweater, kneeling in meadow discovering seed, soft lighting, octane render, 8k resolution, warm atmosphere, clean professional picture book illustration, pristine image quality, no watermark, no text, no signature, no logo, no branding, clean professional image
```

**Result**: ✅ Watermark removed

---

### Example 2: High-Risk Style (Tech → Level 2)

**BEFORE** (tech style, watermark appeared even with Level 1):
```
Tech style illustration, 8-year-old boy Xiaoming exploring digital lab, neon lighting, glossy surfaces, 8k, clean professional picture book illustration, no watermark, clean image
```

**AFTER** (Level 2 for tech style):
```
Tech style illustration, 8-year-old boy Xiaoming exploring digital lab, ambient glow lighting with neon accents, glossy reflective surfaces, octane render, 8k resolution, futuristic atmosphere, clean professional children's book illustration, publication-ready quality, pristine unmarked image, full bleed composition, no watermark, no text overlays, no signatures, no artist marks, no logos, no branding, no copyright symbols, no website URLs, clean professional image
```

**Result**: ✅ Watermark removed

---

### Example 3: Multi-Character Scene (Placement Fix)

**BEFORE** (directive in wrong place):
```
Nianhua illustration, 8-year-old Meimei with rainbow hairclip, red qipao, 65-year-old grandmother with silver bun, burgundy Tang suit, no watermark, clean image, sitting at table, warm courtyard, festival lanterns, 8k resolution
```

**AFTER** (moved to end):
```
Nianhua illustration, 8-year-old Meimei with rainbow hairclip, red qipao, sitting at table with excited expression, 65-year-old grandmother with silver bun, round glasses, burgundy Tang suit, serving dumplings with warm smile, tender family interaction, traditional courtyard, festival lanterns, vibrant festive colors, octane render, 8k resolution, warm family atmosphere, clean professional picture book illustration, pristine image quality, no watermark, no text, no signature, no logo, no branding, clean professional image
```

**Result**: ✅ Watermark removed

---

## 🔄 Progressive Escalation

If watermarks persist, escalate through levels:

### Attempt 1: Level 1 (Standard)
```
clean professional picture book illustration, pristine image quality, no watermark, no text, no signature, no logo, no branding, clean professional image
```

**Wait for result**

---

### Attempt 2: Level 2 (Enhanced)
```
clean professional children's book illustration, publication-ready quality, pristine unmarked image, full bleed composition, no watermark, no text overlays, no signatures, no artist marks, no logos, no branding, no copyright symbols, no website URLs, clean professional image
```

**Wait for result**

---

### Attempt 3: Level 3 (Maximum)
```
professionally published children's picture book illustration, commercial print quality, pristine unmarked image, full bleed edge-to-edge composition, absolutely no watermarks, no text overlays of any kind, no signatures, no artist marks, no logos, no branding elements, no copyright symbols, no website URLs, no social media handles, no QR codes, clean professional publication-ready image
```

**Wait for result**

---

### Attempt 4: Style Switch

If Level 3 fails → Switch to traditional style:
- tech → watercolor
- digital → clay
- modern → storybook/gouache

Traditional physical medium styles are inherently less prone to watermarking.

---

## 📊 Quick Reference Table

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Small text in corner | Weak directive | Upgrade to Level 1 |
| Signature/artist name | Missing "no artist marks" | Add to directive or use Level 2 |
| Logo/brand visible | Missing "no logos" | Ensure included in directive |
| "Generated by..." text | Missing "no text overlays" | Upgrade to Level 2 |
| Watermark on tech style | High-risk style | Always use Level 2+ for tech |
| Watermark mid-image | Placement wrong | Move directive to ABSOLUTE END |
| Persistent watermark | Need stronger directive | Escalate to next level |
| Watermark on all attempts | Generator issue or style | Switch to traditional style |

---

## ✅ Prevention Checklist

**Before generating any image**, verify:

- [ ] **Directive level appropriate**:
  - Traditional styles → Level 1
  - Tech/digital styles → Level 2
  - Commercial projects → Level 2

- [ ] **Directive placement correct**:
  - Located at ABSOLUTE END of prompt
  - Nothing follows after it

- [ ] **Positive framing included**:
  - "clean professional picture book illustration"
  - "pristine image quality" or "publication-ready quality"

- [ ] **Negative directives comprehensive**:
  - Minimum: no watermark, no text, no signature, no logo, no branding
  - Enhanced: + no text overlays, no artist marks, no copyright symbols

- [ ] **Token budget managed**:
  - Level 1: ~20 words
  - Level 2: ~35 words
  - Level 3: ~50 words
  - Adjust other content if needed

---

## 🆘 If Nothing Works

### Last Resort Options

**1. Generator Settings**
- Check if banana nano has watermark toggle in settings
- Contact support about disabling watermarks

**2. Alternative Generators**
- Try different AI art generators
- Some have better watermark suppression

**3. Post-Processing**
- As absolute last resort, use image editing to remove watermarks
- Not ideal, may affect image quality

**4. Style Substitution**
- Always try traditional styles (watercolor, clay) first
- These physical medium styles rarely get watermarked

---

## 📚 Related Documentation

- **rendering.md**: Complete watermark prevention system with all 3 levels
- **SKILL.md**: Workflow integration and requirements
- **output-format.md**: Proper prompt structure
- **multi-character-usage-examples.md**: Examples showing correct directive usage

---

## 🎓 Understanding Why This Works

### The Psychology of AI Generators

**Positive Framing** ("clean professional picture book illustration"):
- Signals "commercial publication standard"
- Tells generator this is professional work, not practice/amateur
- Professional work doesn't get watermarked

**Multiple Negative Directives** ("no watermark, no text, no signature..."):
- Covers all watermark variations
- Generator checks each: watermark? no. text? no. signature? no.
- Comprehensive blocking

**Placement at End**:
- Last instruction has highest weight
- Generator's final check before output
- "What's the last thing I was told? Don't add watermark"

**Spatial Directives** ("full bleed composition"):
- Removes "empty spaces" where watermarks hide
- Forces generator to fill entire canvas
- No room for corner text

---

**Version**: 1.0
**Status**: ✅ Active - Use immediately for all watermark issues
**Last Updated**: 2026-01-11
