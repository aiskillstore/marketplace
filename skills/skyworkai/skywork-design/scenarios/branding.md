# Branding / Visual Identity (VI)

## Triggers

branding, brand identity, VI, visual identity, brand guidelines, brand kit, brand system, style guide

## Defaults

- **Aspect ratio**: varies per deliverable (see table)
- **Resolution**: `2K`

## Consistency Strategy

A brand system demands the highest level of visual consistency — every deliverable must feel like it was designed by the same studio in the same session.

**If the user provides a logo or brand assets**:
1. Use them as `--input-image` for all subsequent deliverables
2. Extract the visual DNA: primary/secondary colors (describe exact hues), style mood (minimal, playful, corporate, etc.), shape language (rounded, angular, geometric)
3. Skip logo generation (deliverable 1) and begin from color palette or whichever deliverable is needed
4. Carry the user's existing visual language — do not reinvent it

**If the user provides NO existing assets**:
1. Start with brand discovery: ask about industry, target audience, brand personality (3-5 adjectives), competitors to differentiate from
2. Generate the logo first (following [logo.md](logo.md) guidance) — the logo is the seed from which all other brand elements grow
3. Once the user approves the logo, derive everything else from it

## Deliverables

Generate in this order. Each step uses `--input-image` from the previous to maintain consistency.

| # | Deliverable | Ratio | Description |
|---|---|---|---|
| 1 | Logo mark | `1:1` | Core brand symbol (see [logo.md](logo.md)) |
| 2 | Color palette card | `3:2` | Primary, secondary, accent colors with hex values shown as labeled swatches |
| 3 | Typography showcase | `3:2` | Heading + body font pairing shown in sample text hierarchy |
| 4 | Pattern / texture | `1:1` | Repeatable brand pattern derived from logo shapes or brand motifs |
| 5 | Stationery mockup | `3:4` | Business card, letterhead, envelope on a styled flat-lay |
| 6 | Brand guidelines page | `3:4` | Summary layout showing logo usage rules, color specs, and type hierarchy |

Not all deliverables are always needed. Ask the user which items they want. If unclear, generate deliverables 1-5 (skip the guidelines page unless requested).

## Design Thinking

1. **Brand personality drives everything** — Before any visual work, define 3-5 personality adjectives (e.g., "bold, modern, trustworthy"). Every design choice — color, shape, typography — must trace back to these words
2. **Differentiate, don't decorate** — Research the competitive landscape. If every competitor uses blue and sans-serif, the new brand needs a reason to follow suit or a strategy to stand apart. Ask the user about key competitors
3. **System over individual pieces** — A brand is not a logo + some colors. It's a system where every element reinforces the others. The pattern echoes the logo shapes; the color palette reflects the logo colors; the typography matches the logo's personality
4. **Constraint breeds cohesion** — Fewer colors, fewer fonts, fewer design elements = stronger brand recognition. Resist the urge to add variety; embrace deliberate limitation
5. **Test across touchpoints mentally** — Before finalizing, imagine the brand on a website header, a mobile app icon, a product label, a social media post, and a conference badge. If it breaks at any touchpoint, simplify

## Aesthetics Guidelines

- **Color system**: Define exactly 1 primary color, 1-2 secondary colors, and 1-2 neutral tones. Every color must have a purpose (primary = brand recognition, secondary = accents/CTAs, neutrals = background/text). Describe colors with precise hue names, not just "blue" — say "deep navy blue" or "electric cyan"
- **Typography pairing**: Choose one display/heading font and one body font. They should contrast in weight/style but share a visual kinship (similar x-height, complementary proportions). Describe the fonts by character: "geometric sans-serif with uniform stroke width" not just "modern font"
- **Logo-derived patterns**: Brand patterns should be abstracted from logo geometry — repeated shapes, rotated elements, or deconstructed forms from the mark. This creates subliminal brand recognition without showing the logo itself
- **Mockup realism**: Stationery and application mockups should feel physically real — paper texture, subtle shadows, realistic perspective. This elevates perceived brand quality. Specify material finish: "matte uncoated paper", "glossy card stock", "embossed letterpress"
- **Whitespace as brand signal**: Premium brands use generous whitespace; energetic brands can be denser. The amount of whitespace IS a brand decision. Define it and enforce it consistently
- **Visual rhythm**: Repeated spacing, consistent margins, and aligned elements across all deliverables create the invisible grid that holds a brand together. Describe the layout structure explicitly in each prompt

## Prompt Rules

- Use the **same style descriptors** (color names, style keywords, mood adjectives) across every prompt — copy-paste, don't paraphrase
- Always pass previous output via `--input-image` when generating subsequent deliverables
- Describe colors with exact hue names: "warm coral #FF6B6B" not just "red"
- Include brand personality adjectives in every prompt: "reflecting a bold, modern, trustworthy brand identity"
- For stationery mockups: specify material, finish, and scene context ("on a marble desk with soft natural light")
