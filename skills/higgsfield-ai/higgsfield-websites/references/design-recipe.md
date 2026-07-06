# design-recipe — the distilled craft playbook (read on EVERY build)

This is the short, always-read version of `design-taste-frontend.md`. Follow it as
written; open the full playbook only where this file explicitly defers to it. Every
rule here exists because the default LLM output violates it.

## 1. Typography

- **Display:** `text-4xl md:text-6xl tracking-tighter leading-none` as the base
  scale. `text-6xl md:text-7xl` ONLY when the headline is 3-5 words. A 4-line hero
  headline is a font-size error, not a copy-length error.
- **Body:** `text-base leading-relaxed max-w-[65ch]`.
- **Fonts:** pick from these pairings — `Geist` + `Geist Mono`, `Satoshi` +
  `JetBrains Mono`, `Cabinet Grotesk` + `Inter Tight`, `Outfit` + `IBM Plex Mono`,
  `GT Walsheim` / `PP Neue Montreal` + a mono. **Inter as display is banned** unless
  the brief explicitly wants neutral/Linear/public-sector.
- **Serif is very discouraged as default.** "Creative/premium brief = serif" is the
  most-tested AI tell. Serif ONLY when the brief names one, or the brand is
  genuinely editorial/luxury/heritage AND you write the justification into the
  design brief. `Fraunces` and `Instrument Serif` are banned as defaults.
  "Heritage" means an actual editorial/luxury/legacy institution — a business
  being a few years old ("est. 2015") or in a traditional trade (barber,
  bakery, tailor) does NOT qualify by itself; those default to sans like
  everything else.
- **Emphasis inside a headline:** italic or bold of the SAME family. Never inject a
  serif word into a sans headline for "visual interest."
- Italic display words with descenders (`y g j p q`): `leading-[1.1]` minimum +
  `pb-1` reserve, or the descender clips.

## 2. Color

- **Exactly ONE accent color**, saturation < 80% by default, locked page-wide. A
  rose-accented site does not get a teal badge in the footer.
- Neutral base (zinc/slate/stone family — pick warm OR cool, never both), no pure
  `#000000` (use off-black/zinc-950), no neon glows, no AI-purple gradient slop.
- **Banned default palette families** (gate-checked; overridable only by the
  user's explicit brand colors): (1) graphite/near-black + orange/amber/ember
  accent (`#ff5c1a #ff6b35 #e8590c #f97316 #ea580c #d9480f` on `#0a0a0a`-family
  grounds — the single most common AI reach for "bold/technical"), (2)
  near-black + neon cyan/blue/green accent (`#00e5ff #22d3ee #00ff88 #4ade80
  #3b82f6`-glow on dark), (3) the beige+brass family below, (4) AI
  purple/violet glow (`#8b5cf6 #a855f7 #7c3aed` gradients), (5) whatever
  palette family your PREVIOUS build in this chat used — consecutive builds
  must not share a palette family.
- **Premium-consumer palette ban:** for cookware/wellness/artisan/luxury/DTC
  briefs, the beige-cream + brass/clay/oxblood + espresso family is BANNED as the
  default reach. Banned default hexes: backgrounds `#f5f1ea #f7f5f1 #fbf8f1
  #efeae0 #ece6db #faf7f1 #e8dfcb`; accents `#b08947 #b6553a #9a2436 #9c6e2a
  #bc7c3a #7d5621`; text `#1a1714 #1a1814 #1b1814`. Rotate instead: Cold Luxury
  (silver/chrome/smoke), Forest (deep green + bone + amber), Black & Tan, Cobalt +
  Cream, Terracotta + Slate, Olive + Brick + Paper, or monochrome + one saturated
  pop. Beige+brass is allowed only when the brief literally names those colors.
  **This rotation list is examples, not a menu:** don't default to the first
  item (Forest + amber is over-picked and heading toward becoming the new AI
  tell). Derive the palette from the brief's actual material world first;
  reach for the list only to escape a banned family.
- **One theme per page.** Dark page = ALL sections dark. No warm-paper section
  sandwiched into a zinc-950 page. Tint-shifts within the family are fine.

## 3. Hero discipline (hard rules)

- Hero fits the initial viewport: headline max 2 lines desktop, subtext max 20
  words / 3-4 lines, CTA visible without scrolling. Top padding cap `pt-24`.
- **Max 4 text elements:** (0-1) eyebrow OR brand strip, (1) headline, (1) subtext,
  (1) CTA row (1 primary + max 1 secondary). BANNED inside the hero: tagline under
  the CTAs, trust micro-strip, pricing teaser, feature bullets, avatar rows,
  version labels (`BETA`, `v2.0`), "Brand · No. 01" micro-meta. Logo walls go in
  their own section BELOW the hero.
- **The hero needs a real visual** (the Phase 1 generated asset). Text + gradient
  blob is a placeholder, not a hero. Div-built fake product UI (fake task list,
  fake terminal, fake dashboard) is the #1 LLM tell — use a real screenshot,
  generated image, real component preview, or nothing.
- Anti-center bias: unless the brief is editorial/manifesto, prefer split 50/50,
  left-content/right-asset, or asymmetric composition over the centered stack.

## 4. Layout rules (page-wide)

- **Section-layout-repetition ban:** each layout family (3-col cards, split
  text+image, full-width quote, bento…) appears at most ONCE per page; 6+ sections
  need ≥4 distinct families. Max 2 consecutive image/text zigzag splits.
- **Eyebrow ration:** max 1 eyebrow per 3 sections (hero counts). Mechanical check:
  count `uppercase tracking` labels; if count > ceil(sections/3), fail. Prefer
  dropping the eyebrow — the headline alone is enough.
- **No 3-column equal feature cards** (the generic identical-trio row). Use
  2-col zigzag (≤2 in a row), asymmetric grid, or horizontal scroll.
- **Bento:** exactly as many cells as content items (no blank filler tiles), and
  2-3 cells need real visual variation (image / brand gradient / pattern / tint) —
  not 6 white-on-white text cards.
- **Split-header ban:** "left giant headline + right floating small paragraph" as a
  section header is banned by default; stack vertically instead.
- Cards ONLY where elevation means hierarchy — otherwise `border-t`, `divide-y`,
  or negative space. One corner-radius scale for the whole page (all-sharp OR
  all-soft 12-16px OR all-pill; mixed only with a written rule).
- Nav: single line at desktop, height ≤80px.
- Mobile collapse declared explicitly per multi-column section — no "Tailwind
  handles it."
- Use `h-dvh`/`min-h-dvh`, not `h-screen` (mobile URL-bar breakage).

## 5. Copy rules

- Headline ≤8 words; sub-paragraph ≤25 words; per section one visual OR one CTA.
- **Em-dash (`—`) and en-dash-as-separator (`–`) are COMPLETELY banned** anywhere
  visible: headlines, body, quotes, captions, buttons. Use period, comma, colon,
  parentheses, or hyphen. Zero tolerance — one `—` on the page is a gate failure.
- **One label per CTA intent page-wide.** "Get in touch" + "Contact us" + "Let's
  talk" on one page = fail; pick one and reuse it in nav/hero/footer.
- CTA text fits one line at desktop (≤3 words for primary).
- No filler verbs (Elevate / Seamless / Unleash / Next-Gen / Revolutionize), no
  startup-slop names (Acme, Nexus, SmartFlow), no "Jane Doe" testimonials, no
  fake-precise invented MARKETING stats (`92% faster`, `4.1× ROI`, `10k+
  teams`) unless labeled mock. Carve-out: invented PRODUCT FACTS (prices,
  spec values, batch counts, dimensions) are required content for a
  fictional-brand brochure — keep them plausible and internally consistent;
  the ban targets performance/social-proof claims, not catalog data. No
  performative-craftsman labels ("Field notes", "Quietly trusted by"), no section
  numbering (`001 · Capabilities`), no scroll cues ("Scroll to explore"), no
  locale/weather strips, no version footers on marketing pages, no pills/tags
  overlaid on photos, no decorative status dots.
- Quotes: max 3 lines, real typographic quotes, attribution = name + role.
- **Copy self-audit before ship:** re-read every visible string; rewrite anything
  grammatically broken, referent-unclear, or "LLM trying to sound thoughtful."
  Plain functional copy beats cute copy.

## 6. Motion rules

- ONE signature/hero effect per page (from the design brief), plus motivated
  reveals. Before adding any animation, answer "what does this communicate?"
  (hierarchy / narrative / feedback / state). "It looked cool" = drop it.
- Spring physics (`type: "spring", stiffness: 100, damping: 20`) over linear
  easing. Magnetic/cursor physics via `useMotionValue`/`useTransform`, never
  `useState`.
- Animate only `transform` + `opacity` on the hot path.
- **`prefers-reduced-motion` fallback on every animated element** (mandatory).
- No custom mouse cursors — EXCEPT spectacle tier, where the brief-mandated
  custom cursor is part of the tier contract. No infinite loops on
  informational sections.
- If motion can't be finished properly in scope, ship a clean static page instead
  of half-wired ScrollTriggers.

## 7. Interactive states & forms

- Implement full cycles, not just the happy state: skeleton loaders shaped like the
  final layout (no generic spinners), composed empty states, inline error states.
- `:active` tactile feedback: `-translate-y-[1px]` or `scale-[0.98]`.
- **Bespoke chrome:** no site-wide shared button style. Each CTA from the
  brief's inventory is its own component with its own interaction identity
  (see `image-to-code.md`). A page of identical pills is a gate failure.
- **Button contrast check:** every button label ≥ WCAG AA against its own
  background (ghost buttons over photos need a scrim/stroke). White-on-white CTA
  is a gate failure.
- Forms: label ABOVE input, error BELOW, never placeholder-as-label; placeholder/
  helper/focus states pass AA contrast.

## 8. Images & icons

- Priority: (1) generated bespoke assets (Phase 1 — always available in this
  environment, so picsum/stock is NOT an acceptable final state), (2) real brand
  URLs from the brief, (3) clearly-labeled TODO slots + tell the user.
- Even minimalist sites need 2-3 real images. Pure-text is incomplete, not minimal.
- Logo walls: real SVG marks (Simple Icons CDN / `simple-icons`), logos ONLY (no
  category captions under each logo). Invented brands get an invented inline-SVG
  monogram, not a styled `<span>`.
- **Icons: generated set first.** The site's visible icons come from the
  Higgsfield-generated custom icon set (`asset-system.md` §4) — one consistent
  stroke style in the brand palette. Library icons (Phosphor / Radix / Tabler;
  Lucide on request) are the fallback for dense functional UI (forms, tables,
  20+ tiny glyphs). Never mix the two sets in one visual zone. No hand-rolled
  decorative SVG illustrations.

## 9. Where the full playbook still wins

Open `design-taste-frontend.md` for: the three dials + use-case presets (§1),
design-system briefs like "make it feel like Notion/Stripe" (§2), canonical
animation skeletons — sticky-stack, horizontal-pan, scroll-reveal (§5), dark-mode
token protocol (§8), the complete AI-tells list (§9), and the pattern vocabulary
(§10). When this recipe and the full playbook disagree, the recipe wins.
