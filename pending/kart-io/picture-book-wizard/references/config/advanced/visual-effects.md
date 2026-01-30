# Visual Effects Configuration

## Special Visual Effects for Banana Nano

This guide provides technical keywords and techniques for generating challenging visual effects that require specific prompting strategies.

---

## Reflections (倒影/反射)

Reflections are one of the most challenging effects to generate correctly. Use these techniques to ensure proper reflection rendering.

### Water Reflections

**Critical Keywords** (MUST include for reflections):
```
mirror reflection in water, symmetrical reflection, perfect mirror surface, reflection clearly visible, mirrored image below, vertical symmetry
```

**Enhanced Prompt Structure for Reflections**:
```
[Subject], [subject's reflection perfectly mirrored in water below], mirror-like water surface, clear symmetrical reflection, [subject] and reflection both visible, vertical flip reflection
```

**Pond Reflection Template**:
```
A 5-year-old Chinese girl named Yueyue, [details], standing/kneeling at pond edge, her perfect mirror reflection visible in the crystal clear water below, both Yueyue and her reflection clearly visible in frame, mirror-like water surface, symmetrical vertical reflection, reflection shows identical details (pigtails, outfit, face), water acting as perfect mirror
```

**Key Principles**:
1. **Explicitly state "reflection"** multiple times
2. **Use "mirror" keywords** (mirror-like, mirrored, perfect mirror)
3. **Specify "both visible"** (subject AND reflection)
4. **Add "symmetrical" or "vertical symmetry"**
5. **Describe reflection details** (what appears in reflection)
6. **Placement**: Put reflection keywords EARLY in prompt (higher weight)

### Reflection Mistakes to Avoid

❌ **Too vague**: "water with reflection"
✅ **Specific**: "perfect mirror reflection in water, both Yueyue and her mirrored image visible"

❌ **Buried late**: "...soft lighting, with some reflection"
✅ **Early placement**: "Yueyue with her mirror reflection in water, [then other details]"

❌ **Single mention**: "reflection in water"
✅ **Reinforced**: "mirror reflection, symmetrical reflection, reflection clearly visible"

### Scene-Specific Reflection Parameters

**Pond Scene with Reflection**:
```
crystal clear pond water acting as perfect mirror, Yueyue's complete reflection mirrored below her, symmetrical vertical reflection showing pigtails and yellow sweater, mirror-like still water surface, both subject and reflection in frame, dual image composition
```

**Additional Modifiers**:
- `still water` (reduces ripples that break reflections)
- `calm surface` (emphasizes flatness needed for reflections)
- `glass-like water` (reinforces mirror quality)
- `undisturbed water` (prevents distortion)

---

## Transparency and Layers

### Water Transparency

**For Clear Water Effects**:
```
transparent crystal clear water, see-through water showing pebbles below, visible through water, transparency effect, clear as glass
```

**Layered Visibility**:
```
lotus leaves floating on surface, pebbles visible through transparent water, multiple depth layers, foreground-midground-background separation
```

### Clay Style Transparency

Note: Clay style naturally has matte, opaque surfaces. For transparency in clay style:
```
translucent clay material, light passing through, semi-transparent effect, backlit clay showing inner glow
```

---

## Light Effects

### Glow and Luminescence

**Tech Style Glow** (easiest):
```
glowing elements, neon glow, light emission, self-illuminated, radiant glow, light bloom effect
```

**Stars Glow**:
```
glowing stars emitting soft light, star light radiating outward, luminous celestial bodies, stars with visible glow aura, light rays from stars
```

**Subtle Natural Glow** (harder):
```
gentle ambient glow, soft diffused light, subtle luminescence, warm glow surrounding
```

### Dappled Light (Forest Scenes)

**Sunlight Through Trees**:
```
dappled sunlight filtering through canopy, sun rays breaking through leaves, spotted light pattern on ground, light and shadow interplay, god rays through branches
```

**Key Elements**:
- Specify light source (sun through leaves)
- Describe pattern (spotted, dappled, rays)
- Mention where it lands (ground, character)

---

## Material-Specific Effects

### Clay Style Effects

**Fingerprint Textures**:
```
visible fingerprints in clay surface, hand-sculpted texture showing finger marks, tactile clay impressions, sculpting marks visible
```

**Matte vs Glossy**:
- Default: `matte clay finish, soft non-reflective surface`
- Wet clay: `slightly glossy wet clay, subtle sheen on surface`

### Tech Style Effects

**Holographic Elements**:
```
holographic projection, translucent hologram, see-through digital display, layered holographic effect, transparent floating interface
```

**Circuit Glow**:
```
glowing circuit paths, neon circuit lines, illuminated pathways, light traveling through circuits, pulsing glow along circuits
```

### Ink Style Effects

**Ink Wash Gradients**:
```
flowing ink gradients, wet-on-wet watercolor effect, ink bleeding into paper, smooth wash transitions, gradient from dark to light ink
```

**Mist and Atmosphere**:
```
ethereal mist surrounding, ink wash mist effect, atmospheric fog, soft misty atmosphere, mist rendered in ink wash technique
```

---

## Motion and Action

### Water Ripples

**Static Ripples** (easier):
```
gentle concentric ripples, circular ripple pattern, ripples frozen in time, ripple rings on water surface
```

**Dynamic Ripples** (harder):
```
ripples actively spreading, water disturbance in motion, expanding ripple waves, movement captured in ripples
```

**Ripples + Reflection**:
```
slight ripples on water surface while maintaining mirror reflection, subtle water movement with reflection still visible, gentle ripples not breaking the mirrored image
```

### Motion Blur

**For Action Scenes**:
```
motion blur on moving elements, speed lines, dynamic movement, blur suggesting motion, action captured with movement trails
```

---

## Composition Techniques

### Dual Focus (Subject + Reflection)

**Composition Keywords**:
```
split composition, vertical symmetry, top and bottom balance, dual subject framing, mirror composition, subject and reflection equally prominent
```

**Camera Angle for Reflections**:
```
slight overhead angle showing both subject and water reflection, camera positioned to capture both top and mirrored bottom, elevated perspective revealing reflection
```

### Depth of Field

**Shallow DOF** (subject focus):
```
shallow depth of field, subject in sharp focus, background softly blurred, bokeh background, foreground emphasis
```

**Deep DOF** (everything sharp):
```
deep depth of field, everything in focus, sharp foreground to background, complete scene clarity, no blur
```

**For Reflections**: Use DEEP depth of field so both subject and reflection are sharp.

---

## Troubleshooting Visual Effects

### If Reflections Don't Appear

**Add these keywords** (in order of effectiveness):
1. `perfect mirror reflection in water`
2. `both [subject] and reflection visible in frame`
3. `symmetrical vertical reflection`
4. `water surface acting as mirror`
5. `dual image composition`
6. Move reflection keywords to FIRST third of prompt

**Reflection Boost Combo**:
```
[Subject] with perfect mirror reflection clearly visible in still water below, mirror-like water surface creating symmetrical reflection, both subject above and mirrored image below in frame
```

### If Transparency Not Working

**For water transparency**:
1. Use `crystal clear transparent water`
2. Add `see-through water showing [what's beneath]`
3. Specify what should be visible: `pebbles visible through clear water`

### If Glow Effects Weak

**Boost glow**:
1. Increase intensity words: `intense glow`, `strong luminescence`, `bright emission`
2. Add bloom: `light bloom effect`, `glow halo`
3. Specify light spread: `glow radiating outward`, `light spreading from source`

---

## Prompt Assembly with Visual Effects

### Standard Assembly Order

```
[Character Anchor] + [Character Pose/Action] + [VISUAL EFFECT] + [Scene Elements] + [Style Keywords] + [Rendering Parameters] + [Atmosphere]
```

**Note**: Place critical visual effects (like reflections) EARLY, right after character and pose.

### Example: Reflection Scene

**Optimized Order**:
```
A 5-year-old Chinese girl named Yueyue, round face, rosy cheeks, two pigtails with red ribbons, wearing yellow sweater and denim overalls,

kneeling at pond edge leaning forward,

her perfect mirror reflection clearly visible in the still water below, both Yueyue and her symmetrical reflection in frame, mirror-like water surface,

crystal clear pond, lotus leaves floating, smooth pebbles,

hand-sculpted claymation style, physical clay textures,

soft natural lighting, octane render, 8k resolution,

sense of discovery and wonder
```

**Keywords Placement**:
- Character: Words 1-25
- Pose: Words 26-35
- **Reflection (CRITICAL)**: Words 36-60 ⭐
- Scene: Words 61-75
- Style: Words 76-85
- Rendering: Words 86-95
- Atmosphere: Words 96-100

---

## Visual Effects Checklist

Before finalizing a prompt with special effects, verify:

**For Reflections**:
- [ ] "Reflection" mentioned at least 3 times
- [ ] "Mirror" keywords included
- [ ] "Both [subject] and reflection visible" stated
- [ ] Reflection description in first 60 words
- [ ] Water described as "still" or "calm"
- [ ] "Symmetrical" or "vertical symmetry" included

**For Transparency**:
- [ ] "Transparent" or "see-through" included
- [ ] What's visible through transparency specified
- [ ] Material properties mentioned (glass-like, clear)

**For Glow**:
- [ ] Light source identified
- [ ] "Glow" or "luminescent" used
- [ ] Intensity descriptors included (soft/strong)
- [ ] Bloom or halo effects mentioned if strong glow

**For Complex Scenes**:
- [ ] Only 1-2 special effects per prompt (don't overload)
- [ ] Critical effect placed early in prompt
- [ ] Effect-specific technical terms used
- [ ] Style compatibility checked

---

## Style-Specific Effect Capabilities

### What Works Best in Each Style

| Effect | Clay | Tech | Ink |
|--------|------|------|-----|
| Reflections | ⭐⭐ Good | ⭐⭐⭐ Excellent | ⭐⭐⭐ Excellent |
| Transparency | ⭐ Limited | ⭐⭐⭐ Excellent | ⭐⭐ Good |
| Glow | ⭐ Limited | ⭐⭐⭐ Excellent | ⭐ Limited |
| Mist/Atmosphere | ⭐⭐ Good | ⭐⭐ Good | ⭐⭐⭐ Excellent |
| Motion Blur | ⭐⭐ Good | ⭐⭐⭐ Excellent | ⭐⭐ Good |
| Texture Detail | ⭐⭐⭐ Excellent | ⭐⭐ Good | ⭐⭐ Good |

**Recommendation**: Choose effects that align with style strengths.

---

## Advanced: Combining Multiple Effects

### Reflection + Ripples

**Balanced Approach**:
```
gentle ripples on water surface while mirror reflection still clearly visible, slight water movement not breaking the mirrored image, subtle ripples with maintained reflection clarity
```

**Key**: Emphasize reflection is maintained despite ripples.

### Transparency + Layers

**Depth Layers**:
```
transparent clear water in foreground, lotus leaves floating on surface in midground, pebbles visible through water in background, multiple depth layers with clarity
```

### Glow + Reflection (Tech/Stars)

**Glowing Reflection**:
```
glowing holographic stars above with their luminous reflections mirrored in water below, both glowing subject and glowing reflection visible, neon light reflected in mirror-like surface
```

---

## Quick Reference: Effect Keywords

### Must-Have Keywords by Effect

**Reflections**:
- `mirror reflection`
- `both [X] and reflection visible`
- `symmetrical reflection`
- `still water`

**Transparency**:
- `transparent`, `see-through`
- `visible through`
- `crystal clear`

**Glow**:
- `glowing`, `luminescent`
- `light emission`
- `glow effect`

**Mist**:
- `ethereal mist`
- `atmospheric fog`
- `misty atmosphere`

**Dappled Light**:
- `dappled sunlight`
- `light filtering through`
- `sun rays`

---

## Testing and Iteration

If an effect doesn't generate correctly:

1. **Simplify**: Remove other complex elements
2. **Intensify**: Add more keywords for the effect
3. **Reposition**: Move effect keywords earlier
4. **Specify**: Add more specific technical details
5. **Reference**: Look for successful examples and copy structure

**Example Iteration**:

❌ Attempt 1: "Yueyue at pond with her reflection"
❌ Attempt 2: "Yueyue at pond, water shows reflection"
✅ Attempt 3: "Yueyue at pond edge, her perfect mirror reflection visible in still water below, both Yueyue and symmetrical reflection in frame"

The key is **specificity and reinforcement**.
