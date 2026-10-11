# Typography

Numeric scale (all 30 styles): see `tokens.md`.

## The five roles

| Role | Purpose | Notes |
|---|---|---|
| **Display** | largest text on screen; short, important text or numerals | works best on large screens. Free to use expressive fonts — handwritten, script. Set the matching optical size. |
| **Headline** | short, high-emphasis text on **smaller** screens | marks primary passages or important regions. Expressive typefaces OK **if** line height and letter spacing are adjusted to keep readability. |
| **Title** | medium-emphasis, relatively short | divides secondary passages/regions. **Use caution** with expressive/display/handwritten/script fonts. |
| **Body** | longer passages | Use typefaces intended for body. **Avoid expressive or decorative fonts** — hard to read at small sizes. |
| **Label** | text inside components; very small text like captions | Buttons use **label large**. |

Each role has large/medium/small. No product uses all 15 — select the styles you need. When reducing
the scale, keep **impactful contrast between sizes; avoid small differences.**

### Documented role assignments

| Element | Style |
|---|---|
| Button label | **label large** |
| Navigation bar destination text | label |
| Top app bar title | title |
| Category header (e.g. "Top News") | title |
| Article/news card title | title |
| Dialog heading | headline |
| Contact card name | headline |
| Music player timecode | label |
| Article body copy | body |
| Card hero figure/statement | display |

Roles describe *size* (small/medium/large), which lets them adapt and respond to the device or
context. Align type with Material Symbols for cohesion. In space-constrained regions a thinner
**width** axis fits more characters (e.g. a label under a bottom-nav icon) — but avoid wide styles
where space is tight, like a top app bar.

## Emphasized styles — the core expressive typography tool

15 emphasized styles were added alongside the 15 baseline styles. Same size and line height; higher
weight plus minor tracking adjustments. **Baseline and emphasized are meant to be used together** —
emphasized is not a replacement scale.

Swap the token, don't restyle:

```
baseline    md.sys.typescale.display-large
emphasized  md.sys.typescale.emphasized.display-large
```

**Material components do not use emphasized styles by default.** You opt in per element.

### Where emphasized styles belong

Recommended for **selection, actions, headlines, and editorial treatments**. Works well with:

- Badges
- Buttons (primary actions)
- Extended FAB
- Selected list items
- Selected menu items

Two independent axes for deciding where to apply it:

- **Weight** — apply emphasized to text that already carries weight (medium, bold) to reinforce hierarchy.
- **Context** — apply emphasized selectively to communicate hierarchy or state: selected states,
  unread messages, key interactions.

Both can be used at the same time.

The purpose is hierarchy, not decoration: emphasized type "reinforces the information hierarchy and
draws attention to important actions, like 'begin recording,' or information, like unread messages."

## Brand vs plain typeface

The scale has two typeface slots:

- **Brand** — larger styles (headline, display). Focus on **expression**.
- **Plain** — smaller styles (body, label). Focus on **readability**.
- Roboto is the default for both.

Replacing Roboto boosts brand expression; on emphasized styles it makes important text stand out
more. Baseline and emphasized sets may use **different** typefaces (e.g. Baskervville + Jacquard).

## Default typefaces

| Font | Character | Axes |
|---|---|---|
| **Roboto** | default for Android and the M3 typescale; 3,300+ glyphs | static |
| **Roboto Flex** | extended weights/widths + size-specific designs; 900+ glyphs (Latin, Greek, Cyrillic) | Slant, Width, Weight, Grade, Optical Size, plus advanced: XOPQ (thick stroke), YOPQ (thin stroke), XTRA (counter width), YTUC (uppercase height), YTLC (lowercase height), YTAS (ascender), YTDE (descender), YTFI (figure height) |
| **Roboto Serif** | comfortable reading; usable in app interfaces | weights + widths across a broad size range |
| **Roboto Mono** | monospaced; for code and aligned numbers | Weight, Italic |
| **Noto Sans** | global fallback; 150+ scripts | Width, Weight, Italic |

Static fonts (Roboto) are applied by default to all M3 components. **Variable fonts are not yet part
of the M3 typescale** — including Roboto Flex and Google Sans Flex. Google Sans Flex has six
variable axes; Roboto Flex can express a range of emotional states on its own.

### Fallback chain

Roboto Flex → Roboto → Noto Sans collection. Confirm with engineering that fallback is wired up.

## Customizing type styles

1. Change the **brand** and **plain** typeface tokens if using a different typeface.
2. Adjust line height and letter spacing to refine. **Avoid changing type size** — it affects how
   components render and reflow.
3. Repeat for **both** baseline and emphasized sets, keeping emphasized visually consistent (e.g.
   all wider than baseline).

Heavier fonts may need wider letter spacing; fonts with long ascenders/descenders need different line
heights.

⚠️ Customizing the type scale or individual styles may prevent you from receiving typography token
updates from Material.

## Editorial treatments

Standalone, showcase moments **driven by type**: dynamic, attention-grabbing custom sizes — larger
display type, a blockier look. They should **depart from purely functional layouts** and from basic
stages in a user flow. In the expressive system, editorial treatments combine with motion, shape, or
color to create product-wide **hero moments**. Type can freely dominate the screen.

Three sanctioned uses:

1. **Celebrating content** — dramatically take over the screen to mark a user action, memory, or
   preference. Match the type to the tone: narrow and thin for serenity; bolder and italicized for
   liveliness.
2. **Voice of the user** — let users personalize typography, or adjust text from their input. Use
   customization selectively to frame the user's mood.
3. **Bespoke functionality** — express a unique function (e.g. width and weight axes increase as
   light brightness increases).

### Best practices

- Ensure consistency between similar-looking editorial moments — **create tokens for each**.
- Match the emotional tone of the text to the task.
- **Don't mix multiple or clashing styles in the same layout.**
- **Don't mimic personalization theming.**
- Editorial treatments **shouldn't be used in labels or just to give information.**

### Using variable axes for editorial treatments

| Axis | What it does | Cautions |
|---|---|---|
| **Weight** | overall stroke thickness; variable fonts give a continuous range | Light weights struggle on low-resolution displays at small sizes — use light weights only at large sizes like display. Excessive weight at small sizes hurts readability (e.g. bold nav bar labels). |
| **Grade** | secondary optical weight modifier, independent of weight; **doesn't change letter widths or line breaks** | Roboto Flex offers +150 and −200 grade. Use a **negative grade in dark mode** to counteract text appearing heavier. Grade can change emphasis without reflowing text. |
| **Width** | horizontal space taken; Roboto Flex ranges **25–150** | Narrow fits more characters (good for small labels). **Avoid wide styles in tight space** like a top app bar. |
| **Optical size** | versions optimized for different sizes | Match optical size to type size. **Don't use large optical sizes at small type sizes.** |

## Readability

- **Line height ratio ~1.2×** type size for large type (title, headline, display).
- **Line height ratio ~1.5×** type size for small copy (body, label). Too tight undermines flow; too
  loose breaks cohesion.
- Use **tabular (monospaced) figures** rather than proportional digits in tables and anywhere values
  change often, like clocks — prevents layout shift and keeps values optically aligned.

## Typesetting

Two methods; pick by platform.

- **Padding + bounding boxes** — web and iOS. Line height = bounding box height; text is vertically
  centered via CSS half-leading. Vertical position is controlled indirectly through the box and font
  metrics. Measure spacing from bounding box height plus top/bottom padding.
- **Baseline** — Android and platform-agnostic specs. Line height = baseline-to-baseline distance;
  spacing = distance from a reference point to the baseline. For centering, specify center alignment
  rather than measuring to the baseline.

## Accessibility

- Contrast: **3:1 for large text, 4.5:1 for small text.**
- Default text color is **on surface**; **on surface variant** is a strong alternative.
- Hyperlinks on a surface use **primary**; **tertiary** makes links less prominent. **Hyperlinked
  text must also be underlined.**
