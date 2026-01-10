---
name: landing-page-design
description: Create high-converting, visually distinctive landing pages. Use when building marketing pages, product launches, SaaS homepages, or any single-page conversion-focused website. Guides section-by-section composition with anti-AI-slop principles.
---

# Landing Page Design

## Overview
Build landing pages that convert AND captivate. This skill combines conversion-focused structure with distinctive visual design to create pages that stand out in an AI-saturated world. The goal: pages worth $50-100 that you'd be proud to sell.

## MANDATORY: Vibe Discovery (Do This First)

**BEFORE writing any code, you MUST run the Vibe Discovery process.** This isn't a lookup table - it's a creative prompt that generates a UNIQUE aesthetic direction every time.

The goal: No two landing pages should look alike, even for similar products.

---

### The Vibe Discovery Process

**Ask the user these questions, then SYNTHESIZE a unique direction. Don't just map answers to presets.**

#### Step 1: Gather Context (Ask These)

**Q1: What's one real-world place or object this brand would be?**
> Not "what industry" - an actual specific thing. A Tokyo convenience store at 2am. A grandmother's kitchen. A brutalist parking garage. A coral reef. The cockpit of a 747. A flea market in Marrakech. A 1970s recording studio.

**Q2: What's the ONE emotion someone should feel in the first 3 seconds?**
> Pick ONE: Calm. Energized. Curious. Trusted. Delighted. Impressed. Rebellious. Nostalgic. Inspired. Amused. Sophisticated. Welcomed. Intrigued. Confident.

**Q3: Pick TWO unexpected influences to collide:**
> Examples: "medical packaging + skateboard graphics", "spreadsheets + street art", "luxury hotel + punk zine", "NASA mission control + kindergarten", "Japanese convenience store + Victorian library"

**Q4: What should this page NEVER be mistaken for?**
> Name 2-3 specific things to actively avoid. "A crypto project", "A wellness app", "Something made by a bank", "Anything with purple gradients"

#### Step 2: Invent The Aesthetic (Don't Look Up - Create)

Based on the answers, CREATE a unique vibe by deciding:

**COLOR INVENTION** (Don't use memorized palettes - derive from the place/object)
- What colors exist in that real-world place/object from Q1?
- Extract 3-4 colors that feel authentic to that reference
- Invent specific hex codes fresh - don't reuse codes from previous projects
- Name your palette something evocative (not "blue and orange" but "Midnight Bodega" or "Rust Belt Morning")

**TYPOGRAPHY INVENTION** (Match the voice to the collision)
- What would text sound like in that place?
- Find a display font that embodies the collision from Q3
- Don't default to your usual choices - browse Google Fonts with fresh eyes
- Consider: weight, width, contrast, quirks

**LAYOUT INVENTION** (Derive from the physical space)
- How is space organized in that place from Q1?
- Is it cramped or expansive? Grid-like or organic? Vertical or horizontal?
- What unexpected layout choice would embody the collision from Q3?

**MOTION INVENTION** (Match the emotion)
- How does the emotion from Q2 move?
- Calm = barely perceptible. Energized = kinetic. Sophisticated = slow and deliberate.
- What's ONE signature motion that defines this page?

#### Step 3: Write Your Vibe Spec

Before coding, write this out explicitly:

```
VIBE NAME: [Invent a 2-3 word name]
REFERENCE: [The place/object from Q1]
EMOTION: [From Q2]
COLLISION: [From Q3]
ANTI-PATTERNS: [From Q4]

COLORS:
- Primary: [hex] - [why this color]
- Secondary: [hex] - [why]
- Background: [hex] - [why]
- Accent: [hex] - [why]
- Palette name: [evocative name]

TYPOGRAPHY:
- Display: [specific font name] - [why it fits]
- Body: [specific font name] - [why]
- Character: [describe the voice]

LAYOUT:
- Density: [sparse/balanced/dense]
- Shapes: [sharp/rounded/organic/mixed]
- Signature element: [one unusual layout choice]

MOTION:
- Level: [still/subtle/moderate/dynamic/chaotic]
- Signature animation: [one specific animation that defines this]

WILDCARD:
- One unexpected detail that doesn't "match" but makes it memorable
```

#### Step 4: The Freshness Check

Before proceeding, verify:
- [ ] I did NOT reuse hex codes from my last 3 projects
- [ ] I did NOT default to my "comfortable" fonts (check: am I using Inter? Nunito? Space Grotesk? If yes, find something else)
- [ ] The collision from Q3 is actually visible in my choices
- [ ] Someone could NOT mistake this for my previous landing pages
- [ ] I included a wildcard that surprises even me

---

### Example Vibe Discovery

**Q1 - Place/Object:** "A Japanese train station at rush hour"

**Q2 - Emotion:** "Confident"

**Q3 - Collision:** "Transit signage + haute couture"

**Q4 - Never mistaken for:** "A meditation app, anything whimsical, startup-bro tech"

**Generated Vibe Spec:**

```
VIBE NAME: Shinjuku Runway
REFERENCE: Japanese train station at rush hour
EMOTION: Confident
COLLISION: Transit signage + haute couture
ANTI-PATTERNS: No soft gradients, no playful illustrations, no rounded friendly shapes

COLORS:
- Primary: #1a1a1a - the black of train doors
- Secondary: #f5f5f0 - platform concrete, worn smooth
- Background: #fafaf8 - fluorescent-lit white
- Accent: #e60012 - JR line red, commanding attention
- Palette name: "Platform Edge"

TYPOGRAPHY:
- Display: Darker Grotesque - confident, slightly condensed, European edge
- Body: Noto Sans JP - clean utility, transit-inspired
- Character: Authoritative but not cold. Clear. Directional.

LAYOUT:
- Density: Rich but organized - like a station map
- Shapes: Sharp with intentional rounded exceptions (like train windows)
- Signature element: Strong horizontal bands that divide sections like train schedules

MOTION:
- Level: Subtle but precise
- Signature animation: Elements slide in from the side like arriving trains - horizontal, smooth, with exact timing

WILDCARD:
- One element uses a fabric-like texture overlay - the haute couture collision
```

---

### Inspiration Starters (When Stuck on Q1)

**Spaces:**
Night market in Bangkok | Empty museum at closing | Airport lounge at 4am |
Vintage record store | Hospital waiting room | Casino floor |
Greenhouse in winter | Subway platform | Observatory dome |
Abandoned factory | Luxury yacht interior | 24-hour laundromat |
Library rare books room | Auto body shop | Space station module

**Objects:**
1980s synthesizer | Surgical instruments | Vintage luggage |
Racing motorcycle | Antique compass | Industrial loom |
Neon sign | Typewriter | Scientific glassware |
Leather-bound book | Circuit board | Porcelain dishware

**Eras/Movements:**
Soviet constructivism | Memphis design | Swiss international |
Art nouveau | Bauhaus | De Stijl |
Googie architecture | Streamline moderne | Brutalism |
Japanese metabolism | Scandinavian modernism | Italian futurism

---

### The Anti-Convergence Rules

1. **No hex code memory** - Generate colors fresh from the reference, don't recall "my usual blue"
2. **Font rotation required** - Cannot use the same display font in consecutive projects
3. **Collision must show** - If someone can't see BOTH influences from Q3, push harder
4. **Wildcard is mandatory** - Every vibe needs one element that doesn't "fit" but makes it unique
5. **Name it** - An unnamed vibe becomes generic. A named vibe has identity.

---

### Quick Context Questions (Minimal Version)

If the user just says "make me a landing page" with no context, ask:

1. "What's one place or object that captures this brand's energy?"
2. "What emotion should dominate?"
3. "What should this NEVER look like?"

Then synthesize a vibe from those three answers.

---

## The 50% Rule
**Spend 50% of your time on the hero section.** It's the cover image for social media, the first impression, the hook. Everything else flows from getting the hero right.

## Section Composition (Top to Bottom)

### 1. Hero Section (Primary Focus)
The make-or-break element. Must contain:
- **Headline**: Sharp, benefit-driven hook (reference H1 Gallery for inspiration)
- **Subheadline**: Supporting context, 1-2 sentences max
- **CTA Button(s)**: Primary action + optional secondary
- **Social Proof**: Logo marquee, testimonials, or trust badges
- **Visual Element**: Product shot, illustration, or animated background

**Hero Variations**:
- Split layout (text left, visual right)
- Centered with floating elements
- Full-bleed background with overlay text
- Asymmetric with decorative elements

### 2. Features/Benefits Section
Show what the product does. Options:
- **Bento Grid**: Cards in asymmetric layout (popularized by Apple)
- **Alternating Rows**: Image + text, flipping sides
- **Icon Grid**: Simple icons with short descriptions
- **Interactive Cards**: Hover states, micro-animations

### 3. Social Proof Section
Build trust through:
- Logo carousel (marquee animation)
- Testimonial cards with photos
- Stats/metrics with animated counters
- Case study snippets

### 4. How It Works Section
Step-by-step explanation:
- Numbered steps (01, 02, 03 pattern adds sophistication)
- Sticky scrolling with progressive reveal
- Timeline or flowchart visualization

### 5. Pricing Section (if applicable)
- 2-3 tier comparison
- Highlighted "recommended" tier
- Feature comparison table
- FAQ accordion below

### 6. CTA Section
Final conversion push:
- Repeat value proposition
- Strong headline
- Single focused action
- Urgency elements (if authentic)

### 7. Footer
- Navigation links
- Social icons
- Legal links
- Optional newsletter signup

## Anti-AI-Slop Principles

### Icons: Avoid Lucide (Overused)
Use instead:
- **Iconify Solar**: Multiple styles (outline, broken, duotone)
- **Heroicons**: When you need Apple-like simplicity
- **Phosphor**: Flexible weight system
- **Custom SVGs**: For brand differentiation

### Fonts: Kill Inter/Roboto
Distinctive alternatives:
- **Display**: Newsreader, Playfair Display, Space Grotesk, Clash Display
- **Body**: Outfit, Plus Jakarta Sans, Manrope, Satoshi
- **Mono**: JetBrains Mono, IBM Plex Mono, Fira Code

### Colors: No Purple Gradients
Bold alternatives:
- Deep navy + electric accent
- Warm neutrals + single pop color
- Monochromatic with tonal depth
- Dark mode with neon accents
- Earthy/organic palettes

### Layouts: Break the Grid
- Overlapping elements
- Diagonal sections
- Asymmetric spacing
- Container-breaking hero elements
- Negative space as design element

## Animation Vocabulary

### Entrance Animations
- `fade-in`: Simple opacity transition
- `blur-in`: Starts blurred, sharpens
- `slide-in`: Direction-based entrance
- `scale-in`: Grows from small to full size
- `stagger`: Sequential reveal of child elements

### Continuous Animations
- `marquee`: Infinite horizontal scroll (logos, testimonials)
- `beam`: Light traveling along a path/border
- `pulse`: Subtle scale/opacity breathing
- `float`: Gentle up/down movement
- `rotate`: Continuous spin (icons, decorations)

### Interactive Animations
- `hover-lift`: Subtle Y translation + shadow
- `hover-glow`: Border/shadow color change
- `hover-reveal`: Hidden element appears
- `click-ripple`: Material-style feedback

### Decorative Elements
- Vertical grid lines (container-size based)
- Noodles/curved connectors between elements
- Gradient orbs/blobs in background
- Grain/noise texture overlay
- Geometric shapes (circles, rectangles with rounded corners)

## Design Resources

### Hero Inspiration
- **Superhero** (superhero.design): Curated hero sections
- **Dribbble**: Search "hero section", "landing page"
- **Awwwards**: Award-winning designs

### Section Patterns
- **Mobin**: Real websites with section breakdowns
- **Bento Grids**: Card layout inspiration
- **CTA Gallery**: Call-to-action patterns

### Typography
- **Google Fonts**: Free, AI-accessible fonts
- **Fontshare**: Free quality fonts
- **H1 Gallery**: Headline inspiration

### Icons & Logos
- **Iconify**: Unified icon API (Solar, Heroicons, etc.)
- **Simple Icons**: Brand logos (SVG)
- **Heroicons**: Tailwind's icon set

## Implementation Workflow

### Phase 1: Research & Collect
1. Gather 5-10 hero screenshots as wireframes
2. Identify section patterns needed
3. Choose icon set and font pairing
4. Define color palette

### Phase 2: Hero Development
1. Generate hero from best reference screenshot
2. Iterate: change colors, fonts, layouts
3. Add animations (beam, fade-in, etc.)
4. Add decorative elements (noodles, grids, numbers)
5. Refine until distinctive

### Phase 3: Section Build-Out
1. Add sections one at a time (not all at once)
2. Reference specific components/screenshots per section
3. Maintain color/font consistency from hero
4. Add section-specific animations

### Phase 4: Polish
1. Fix responsive breakpoints (mobile, tablet, desktop)
2. Replace placeholder images with real/quality assets
3. Optimize animations for performance
4. Test all interactive elements

### Phase 5: Presentation
1. Create cover screenshot with infinity canvas layout
2. Show hero prominently
3. Include mobile and desktop views
4. Add subtle background (blurred gradient, pattern)

## Prompt Patterns

### Hero Generation
```
Create a hero section for [PRODUCT TYPE].
Change text, names, and numbers to fit [BRAND].
Use Iconify Solar icons (duotone style).
Use [FONT] for headlines.
Add vertical container-size grid lines.
Add 01, 02, 03 step indicators for sophistication.
Use [COLOR] as primary, dark mode.
```

### Section Addition
```
Adapt a new [SECTION TYPE] section.
Match the hero's color scheme and typography.
Use marquee animation for logos.
Add fade-in blur-in entrance animation.
Keep the hero exactly as is.
```

### Animation Enhancement
```
Add beam animation to the primary button border.
The beam should be 1px, continuously traveling around the pill shape.
Add a subtle hover-lift effect to feature cards.
```

### Negative Prompts (What NOT to change)
```
Don't change the hero section.
Keep the navbar exactly as is.
Don't modify the existing animations.
```

## Quality Checklist

### Visual Distinction
- [ ] No generic purple gradients
- [ ] Non-default icon set (not Lucide)
- [ ] Distinctive font pairing
- [ ] At least one "memorable" element
- [ ] Consistent color system via CSS variables

### Technical Quality
- [ ] Mobile responsive (no horizontal scroll)
- [ ] All images loading (no broken placeholders)
- [ ] Animations performant (no jank)
- [ ] Accessible color contrast
- [ ] Fast initial load

### Conversion Optimization
- [ ] Clear value proposition above fold
- [ ] Single primary CTA visible
- [ ] Social proof present
- [ ] Logical information hierarchy
- [ ] No friction to main action
