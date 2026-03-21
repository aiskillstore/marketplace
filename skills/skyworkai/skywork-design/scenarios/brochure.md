# Brochure

## Triggers

brochure, pamphlet, leaflet, tri-fold, bi-fold, flyer, booklet, handout

## Defaults

- **Resolution**: `2K`

## Formats & Image Count

Generate **one image per physical side**, with all panels of that side composed together in a single image.

| Format | Images | Aspect ratio | Description |
|--------|--------|-------------|-------------|
| Single page / Flyer | 1 | `3:4` | All content on one image |
| Bi-fold | 2 | `16:9` | Outside (front + back side by side), Inside (inside-left + inside-right side by side) |
| Tri-fold | 2 | `21:9` | Outside (3 panels side by side), Inside (3 panels side by side) |
| Multi-page booklet | 1 per spread | `16:9` | Each 2-page spread as one image |

This approach ensures visual consistency within each side and reduces generation calls.

## Consistency Strategy

A brochure is a multi-panel system — visual inconsistency between panels destroys professionalism instantly.

**If the user provides brand assets or a reference image** (logo, brand guidelines, existing design):
1. Use them as `--input-image` for every generation
2. Extract the visual DNA: color palette, typography style, layout density, mood
3. Maintain the established brand language — do not introduce new visual elements

**If the user provides NO reference**:
1. Generate the **outside face first** — this sets the entire visual direction: color palette, typography style, imagery mood, layout density
2. Do NOT proceed to the inside face until the user approves the outside direction
3. Use the approved outside face as `--input-image` when generating the inside face

## Workflow

### Step 1: Clarify Scope

Before generating, confirm with the user:
- **Format**: single page, bi-fold, tri-fold, or booklet (how many pages?)
- **Content**: what text/information goes on each panel? (get the actual copy or at minimum the topic per panel)
- **Tone**: corporate, playful, luxurious, informational, promotional?
- **Brand assets**: any existing logo, colors, or style to match?

### Step 2: Outside Face

Generate the outside face as a single image with all panels composed together.
- **Bi-fold** (`16:9`): left half = back cover, right half = front cover. Name: `...-outside.png`
- **Tri-fold** (`21:9`): left = back cover, center = front flap, right = front cover. Name: `...-outside.png`
- The front cover area must be the visual hero — it establishes the design direction
- Describe the full layout in the prompt: "a tri-fold brochure outside face, 3 panels side by side separated by subtle fold lines, left panel is the back cover with contact info, center panel is the front flap with a teaser, right panel is the front cover with the main headline and hero image"
- Wait for user approval before continuing

### Step 3: Inside Face

Generate the inside face as a single image, using the outside face as `--input-image`.
- **Bi-fold** (`16:9`): left = inside-left, right = inside-right. Name: `...-inside.png`
- **Tri-fold** (`21:9`): left = inside-left, center = inside-center, right = inside-right. Name: `...-inside.png`
- Describe: "a tri-fold brochure inside face, 3 panels side by side separated by subtle fold lines, matching the style of the reference image, left panel covers [topic], center panel covers [topic], right panel covers [topic]"

## Design Thinking

1. **Design for the fold** — In bi-fold and tri-fold formats, the fold line is a real physical constraint. Include subtle fold line indicators in the prompt. Critical content must not straddle the fold. The front panel is the first impression; the first inner panel revealed on opening is the "aha" moment
2. **Sequential storytelling** — A brochure is read in a specific physical order. Design the content flow to match: hook (front cover) → expand (inner panels) → convince (data/testimonials) → act (back cover CTA). Each panel should make the reader want to see the next
3. **One hero per panel** — Each panel gets one dominant visual or message. Competing elements on the same panel create confusion. If you have 4 key messages and 4 panels, the layout is obvious — one per panel
4. **Print thinking** — Brochures are physical objects. Design for how they'll be held, folded, and read. Consider that colors look different on paper than on screen — bright neon colors often print poorly; rich, slightly muted tones print beautifully
5. **The back cover matters** — Many designers neglect it. The back is often the first thing someone sees on a desk or shelf. A clean back with logo, tagline, and contact info reinforces brand presence. Never leave it as an afterthought

## Aesthetics Guidelines

- **Cross-panel color system**: Define a primary background color, a secondary accent, and a text color. Use these consistently across ALL panels. Do not introduce a new color on the inside that wasn't established on the outside
- **Typography discipline**: One heading font, one body font, applied identically across all panels. Heading size, body size, and line spacing should be uniform. Describe these in every prompt: "bold sans-serif headings, regular serif body text"
- **Image style consistency**: If the outside uses photography, the inside uses photography. If the outside uses illustration, the inside uses illustration. Never mix photographic and illustrated imagery in the same brochure
- **Layout grid**: All panels should share the same margin width, column structure, and content alignment. Describe the grid: "each panel has centered single-column layout with generous margins"
- **Visual breathing room**: Each panel needs whitespace. For text-heavy panels, increase margins rather than shrink type size. Cramped panels signal amateur design
- **Print-safe colors**: Avoid pure RGB brights that can't reproduce in CMYK. Specify "print-ready" in the prompt. Rich blacks, deep navies, and warm neutrals look premium in print

## Prompt Rules

- Describe ALL panels of the side in a single prompt: "3 panels side by side, separated by subtle fold lines"
- Specify what content goes in each panel by position: "left panel shows..., center panel shows..., right panel shows..."
- Put all text content in double quotes for accurate rendering
- Always pass the outside face via `--input-image` when generating the inside face
- Use the same style/mood phrase for both sides — copy-paste, don't paraphrase
