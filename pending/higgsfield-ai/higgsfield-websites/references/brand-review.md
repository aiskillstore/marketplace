# Brand review — the Higgs taste rubric (design self-review)

Designer-authored rubric for judging whether a design LOOKS like Higgsfield —
taste and judgment (focus, composition, visual voice, imagery, coherence, copy
tone, finish), not token conformance (tokens/components are covered by
`references/quanta-design.md`). Designer-authored (translated from the
Higgsfield design team's Russian original).

When building a `type: "app"` product, run this rubric as
a self-review against your rendered screens (screenshots) BEFORE delivering —
the "Site/product" channel column is the one that applies. Fix
what the rubric flags with confidence; note "watch" observations without
blocking on them.

# Higgs · Brand Review Skill

The skill runs a design through a single set of Higgs brand criteria and returns
structured feedback. Two jobs: (a) self-review for junior designers
(catches what the art director fixes on the first pass); (b) cross-channel
consistency (site/product, SMM, video, marketing — one engine).

## What the skill does NOT check (Figma's zone)

Technical conformance is covered by Figma (`check design`): tokens (color,
typography, grid/spacing) and DS components. The skill does NOT duplicate that — it judges
TASTE and brand principles. Important: tokens only protect the product/site; in SMM, video,
and marketing there are no tokens, graphics are assembled in other tools — that's where the brand
"drifts," and that's where the skill carries the main load.

## How to run a review (procedure)

1. **Determine the channel** — site/product, SMM, video, or marketing. It determines
   the emphases (see the matrix) and the scope of rules (product vs marketing vs Canvas).
2. **Run through ALL 7 criteria** — for each one, answer the check question,
   relying on "Brand specifics" below (rules, reference examples, anti-examples). Do not skip a single
   criterion, including **7. Finish** (it's easy to forget because it's
   cross-cutting — always check it: are there any leftover/vestigial elements, and does
   the layout look unfinished?).
3. **In your answer, list all 7 criteria by name**, each with a status — even if
   "On brand (matches)". Do not collapse or skip criteria that have no remarks; "Finish"
   must be present in every review. Status — one of three (see "Output format"),
   always with a specific explanation of "what exactly and why".
4. **Per-factor verdict** — do not write off the whole layout over one detail.
   For example: the scene/image may be on brand while the text/styling is not. Keep
   the good parts, flag only what's problematic.
5. **Confidence threshold** — flag as "off brand" only when confidence is above
   ~70%. Keep weak signals as "watch" (a soft observation), not as a hard flag.

## Rubric: 7 criteria

1. **Focus and hierarchy** — is it immediately clear where to look, and is the main thing the most
   noticeable? (You can assemble everything from correct tokens and still drown the main CTA.)
2. **Composition and space** — balanced, has whitespace, everything aligned,
   density comfortable?
3. **Visual voice (tone and character)** — does it feel like Higgs? This also covers
   the *application* of color/typography (not "is it from the palette" — that's Figma, but is it used
   in our character: proportions, accents, restraint).
4. **Imagery: photos and illustrations** — are the images in our style, treatment, unified
   language?
5. **Coherence: brand + channel** — from the same universe as everything else, and
   appropriate to the channel format? (stories ≠ key visual ≠ product screen).
6. **Copy tone (copywriting)** — do the words sound like the brand voice? (Matters for SMM and
   marketing.)
7. **Finish** — the design is taken all the way to done: nothing extra and nothing unfinished?
   A cut across all the others. Two types: (a) **extra/vestigial elements** —
   hanging around with no function (a stepper connector after the last step, a duplicate divider,
   a forgotten placeholder); (b) **unfinishedness** — a raw layout that at once lacks
   an accent, visual voice, clear composition, and coherence (a cumulative
   "not taken to done" signal, often = several of criteria 1–5 sagging at the same time).

For **video**: the criteria apply to the storyboard, key frames, titles,
cover, overall visual tone. Motion/timing/editing the skill does NOT evaluate.

## Emphases by channel

The criteria are the same everywhere, but the skill looks first at different things (●● — main focus,
● — important, · — background):

| Criterion | Site/product | SMM | Video | Marketing |
|----------|:---:|:---:|:---:|:---:|
| 1. Focus and hierarchy | ●● | ● | ● | ●● |
| 2. Composition and space | ●● | ● | ● | ● |
| 3. Visual voice | ● | ●● | ●● | ● |
| 4. Imagery | · | ●● | ●● | ● |
| 5. Coherence: brand + channel | ● | ●● | ● | ● |
| 6. Copy tone (copywriting) | ● | ●● | ● | ●● |
| 7. Finish | ●● | ● | ● | ●● |

## Output format: feedback statuses

For each criterion (and overall) — one of three statuses, always with a specific
explanation:

| Status | Meaning | What to do |
|--------|----------|------------|
| **On brand (matches)** | Matches Higgs principles | No need to touch |
| **Needs adjustment (adjust)** | Close, but one thing is off | Fix it, with an explanation of what exactly |
| **Off brand (flag)** | Clearly not our vibe | Redo, with an explanation of what and why |

**Answer structure (mandatory):** a brief overall verdict → then a **checklist of
all 7 criteria in order**, each with its own status (even "On brand (matches)") and
a short reason → separately "what's on brand" (held) from what we flag. Do not
skip criteria that have no remarks — write "On brand (matches)". **Always include criterion 7
"Finish"**: check for extra/vestigial elements and the overall
unfinishedness signal. The explanation is always specific, so a junior understands the fix.

Checklist template:
```
1. Focus and hierarchy — [status]: …
2. Composition and space — [status]: …
3. Visual voice — [status]: …
4. Imagery — [status]: …
5. Coherence — [status]: …
6. Copy tone — [status]: …
7. Finish — [status]: …
```

## Boundaries

The skill is a first-pass filter, not a replacement for art direction (~70% of a junior's
fixes: mechanics + obvious taste violations). Statics (site, banners, posts, presentations,
key frames) — good. Video — partially (frames yes, editing no). The quality of the skill
= the quality of the principles and examples put into it.

---

# Brand specifics (rules, reference examples, anti-examples)

Below is the working core: brand rules for each criterion, with reference examples,
anti-examples, scope (product/marketing/Canvas), exceptions, and confidence
scales. Check the design under review against these rules.


This is where we collect concrete "yes / no" markers that fill out the criteria. Each marker
is tagged with a scope: where the skill actually checks it (on the product, Figma guards a lot of it).

> **Brand colors:**
> - brand accent `#D1FE17` (lime) — the canonical Higgs accent, works across all channels;
> - `#828282` — secondary gray for secondary icons/elements (softly, ≈80/20);
> - **supporting colors: red (marketing) and blue (paired with lime).** Lime remains
>   the universal accent, red/blue do not replace it (see Criterion 3).
>   - red/crimson — marketing OK (incl. aggressive); in the product — not ours (anti-example:
>     the red "TOP" badge in the Features/Models modal). Refines the earlier "pink/magenta ≈20%".
>   - blue — OK as support IN A PAIR with brand lime, incl. in the product (e.g. collab cursors
>     on Canvas); we do not make blue a standalone accent.

### Criterion 1 — Focus and hierarchy
- **One section / component — at most one accent button.** (Confirmed.)
  There is one main action → so there is one accent button. Secondary actions are neutral/ghost,
  not a second filled accent.
  Scope: judgment call, all channels. Figma does NOT catch this — both buttons can be valid components.
  Off-brand tell: two filled accent buttons in one section competing for attention
  (anti-example: an orange + a lime button in the same steps card).
  Reference example of "one accent": the Supercomputer prompt box — the only accent is the lime send
  button, while "Smart mode" and "Ask before generation" are left as neutral secondary controls.
- **The accent must not get lost: one main focus must read.** (Anti-pattern.)
  If a screen has many elements of similar weight (role chips, tabs, buttons of equal prominence),
  the accent gets diluted and components fight for attention. You need to build a hierarchy: one main
  accent (lime), everything else quieter.
  Scope: judgment call, all channels.
  Off-brand tell: no single focus, components compete (anti-example: the share modal —
  Owner/Collaborator role chips, tabs, and Copy link at similar weight, the lime accent gets lost).
- **An element's visual weight = its importance; the secondary does not shout.** (Anti-pattern.)
  Utility/secondary icons and elements must not stand out more than they deserve —
  neither in brightness nor in saturated color. Ties into Criterion 3 (restraint of color).
  Scope: judgment call, all channels.
  Off-brand tell: an overly bright/saturated color on a utility icon that pulls attention
  (anti-example: a screaming-red PDF icon that has no reason to dominate the screen).
- **A utilitarian toolbar/panel — restrained background, no accent overload or glows.** (Anti-pattern.)
  A low-level toolbar modal (tools, controls) must not have an overly accented/
  glowing background — that's too much for its role. The background is quiet, the accent only on the active tool.
  Scope: judgment call, product.
  Off-brand tell: an overly accented toolbar background with glows (anti-examples: the bottom toolbar
  in Realtime Draw — the background is too "loud" for the panel's level; the background of the "DAM — New
  uploading" toolbar modal — accented, with glows, too much for a utility toolbar). We save glow/accented
  backgrounds for hero/highlighted blocks, not for utilitarian panels.
- **Observation (low confidence ≈50/50): two "heavy" blocks can conflict in weight.**
  When a screen has two weighty elements (e.g. a floating bottom toolbar + a right info sidebar),
  they can visually fight for weight even if each one is on brand on its own. The skill does NOT flag
  hard — it flags it as a possible reason to rebalance the hierarchy. Confidence is low for now.
  Observation example: the viewer screen — the bottom toolbar (Overview/Color Grading/…) is on-brand in style,
  but in weight it competes with the sidebar.

### Criterion 2 — Composition and space
- **An ad inside the hero is our device.** (Confirmed.)
  An ad/promo block embedded in the hero section (banner-in-hero) is a valid composition device.
  Scope: marketing, website, hero sections.
  Reference example: the "Make games with Higgsfield" ad banner in the hero (lime background + dots + game characters).
- **A lime background as the hero is our device.** (Confirmed.)
  A bright solid brand-lime `#D1FE17` (with dots) as the hero/banner background is in the brand's spirit; text on it
  is black, the button is white (contrast, see Criterion 5). Reference example: the "Make games with Higgsfield" banner.
- **Three-zone layout — our product skeleton.** (Confirmed on reference examples.)
  The structure of product screens: left sidebar (navigation) + central content (body) +
  right sidebar/panel (context: gallery, ToC, team board, canvas). Zones may nest
  (e.g. an additional folders sidebar inside the left zone). This is a recognizable structural skeleton, not
  "content sprawled across the full screen."
  Scope: judgment call, product/web.
  Reference examples: Supercomputer (task view: nav sidebar + chat + right gallery/ToC); Cinema Studio,
  the Cully Boys project (nav sidebar + folders sidebar + generations grid + right team/canvas board).
- **Balanced composition + filled space — a general marker of "ours."**
  (Confirmed on all reference examples.)
  In everything marked "good example / reference example" the composition is well balanced, and the space
  is filled intelligently: neither empty nor overloaded. This is the baseline sign of on-brand composition —
  the skill checks it first under this criterion.
  Higgs is NOT a minimalist "airy" brand: an excess of empty space reads as
  non-Higgs, even if everything else follows the rules.
  Scope: judgment call, all channels.
  Reference examples: all "good examples / reference examples" (Supercomputer, AI Marketplace, and others).
  Off-brand tell: too much whitespace / empty space, a sparse composition
  (anti-examples: the "HIGGSFIELD EARN" section — the H2 heading follows the rule, but there is excess emptiness, ≈50%
  on-brand; the "The ultimate AI-powered camera control" footer — lime background and black text per
  the rules, but too much whitespace; the voice-change panel — too much emptiness; the
  "Select Avatar" modal — a lot of empty space, sparse composition; the asset-picker modal
  (Uploads/Elements) — too much whitespace while the previews are too small; the "Share Cully
  boys" share modals — large empty gaps between rows); and the opposite —
  overly tight spacing, too little whitespace between elements (anti-example: the cramped margin between
  the graphic and the heading in the Cinema page hero — whitespace needs to be added). Balance: neither empty nor cramped.
- **We separate sections with whitespace/padding, not divider lines.** (Confirmed.)
  Content is segmented via space and padding, not horizontal/vertical divider
  lines. Divider lines read as foreign/"cheap" UI; with us, structure is held by the rhythm
  of spacing.
  Scope: judgment call, product/web.
  Off-brand tell: sections/tabs/rows separated by divider lines instead of padding
  (anti-example: the asset-picker modal (Uploads/Elements) — dividers instead of whitespace).
- **Previews/tiles are of a readable size, not tiny.** (Confirmed.)
  Preview cards in grids must be large enough for the content to be readable; overly
  small previews + lots of whitespace around them = sparse and unclear. Same for list rows: the row size
  is balanced — neither large nor small (reference example: the projects list in the Cinema Studio sidebar).
  Scope: judgment call, product.
  Off-brand tell: small previews amid an excess of empty space (anti-example: the asset-picker grid —
  previews are too small).
- **Spacing discipline: inner padding is even, components don't stick to the container edges.** (Confirmed.)
  Between the content and the edge of a modal/container there is even inner padding (elements are not pressed
  against the edges). Cell/card padding is uniform, without "crookedness" or floating offsets.
  Scope: judgment call, product/web.
  Off-brand tell: a component pressed against the container edge (anti-example: the search bar almost flush
  with the edges of the search modal); uneven/"crooked" cell padding (anti-example: the cells of that same modal).
- **Clean background: bright or dark solid, components built cleanly.** (Confirmed.)
  No muddy semi-transparent gray layers over a busy/variegated background — at the junction of
  figure and ground you get mush. A component must read against a clear background. Cards/components
  are built cleanly and "premium," without a cheap look (limp shadows, murky layers, gaudiness = cheap).
  Scope: judgment call, all channels.
  Off-brand tell: a murky semi-transparent background over a photo/texture; a muddy blend of
  gray with green; a green-tinted semi-transparent section background (muddy); a muddy/murky
  green-olive gradient background; a component "drowning" in the background (anti-examples: the Uploads panel over
  variegated photos; the green transparent background of the Credits section in the dropdown; the muddy green gradient
  in the "Supercomputer for Creative Work" banner).
  Important distinction: a CLEAN brand-lime gradient is ours (Supercomputer reference example); a MUDDY murky
  green-olive gradient is not ours. The difference is in cleanliness, not in the mere fact of a gradient.
  Additional anti-example (confirmed): a muddy green gradient on a black background (murky, not lime) —
  not ours; and a muddy gray blur (murky grayish frosted) — not ours (see the clean-blur rule below).
- **Clean blur (frosted) on cards is OK; it is NOT "muddy semi-transparent."** (Confirmed.)
  Frosted cards on a clean/dark background are our device (intentional, clean). Distinguish from the anti-
  pattern above: a muddy semi-transparent layer over variegated/busy content.
  For prompt boxes / cards, clean blur is the expected device; its absence reads as unfinished work.
  Reference example: the UGC Creator / Marketing / Production cards in the Supercomputer banner.
  Reference example of a clean component on a dark background (no blur, on solid dark): the Supercomputer
  prompt box — the container and controls are assembled cleanly, the text hierarchy is clear (see the mixed example below).
  Reference example of frosted blur over a busy background: the model-selection modal (a frosted panel over a photo
  with a grid) — the background recedes readably, the component stays clean.
  **A blurred backdrop in the image viewer is our device (it distinguishes us from similar services).**
  When viewing an image, the background fills with a blurred version of that same image — this is a recognizable
  brand device of the viewer, not a flat gray/black backdrop. Scope: product (viewer/media viewing).
  Reference example: the image-viewing screen (portrait on a blurred backdrop).
  **Nuance about noise/grain:** "clean" does NOT mean "zero noise." Light grain/noise in frosted surfaces and in
  the backgrounds of cards/surfaces is acceptable and even organic, as long as it is MODERATE (the nuance concerns
  not only blur but backgrounds in general). The line: moderate noise = OK; heavy/muddy noise
  that turns the layer into mush = anti-pattern. Reference examples of moderate noise: the model-selection modal;
  the top-up pricing cards.
  Off-brand tell: a prompt box without blur, and moreover "muddy" on a muddy gradient (anti-example:
  the "Make a talking head video" prompt box on a muddy green gradient, without blur); a large
  modal/menu rendered flat on dark without frosted where blur is expected (anti-examples:
  the Features/Models modal — a large panel with no blur at all; the "Select Avatar" modal — a flat
  dark panel without blur; the asset-picker modal (Uploads/Elements) — without blur); a muddy gray blur —
  murky grayish frosted instead of clean (confirmed: muddy gray blur = not ours).
  **Important:** the anti is specifically the version WITHOUT blur. That same Features/Models mega-menu WITH frosted blur over
  images, neutral gray feature icons, two-tone text and inline badges (NEW lime /
  TOP magenta next to the text, and NOT on the corners of the icons) — is on-brand (reference example).
- **Side panels / info sidebars are wrapped in a card, not "hanging" in a void.** (Confirmed.)
  An info panel, sidebar, or set of metadata is enclosed in a card container — this holds the structure
  and the brand's presence. We do not leave controls and text lying "bare" on the background.
  Scope: judgment call, product; useful on all channels.
  Reference example: the right info sidebar of the viewing screen (Author / Prompt / Information), wrapped in a card.
- **Banner: a balance of whitespace and density.** (Confirmed on the reference example.)
  For a banner we maintain a combination of whitespace and density — neither empty nor mush.
  Composition reference example: the Supercomputer banner.
- **A gray banner background is questionable, more likely not Higgs.** (Softly negative, ≈20/80.)
  A flat gray banner background is most likely not ours: brand banners carry the brand's presence
  (lime gradient, perspective grid, etc.). The skill may gently express doubt, but not flag it hard.
  Questionable example: the gray gradient of the Photodump banner.

### Criterion 3 — Visual voice / application of typography and color
- **Headings H1–H3: visually all caps + the Space Grotesk typeface.** (Confirmed.)
  A rule about *visual* application: however the source text is typed, in the output the heading
  is displayed in all caps and in the Space Grotesk typeface.
  Scope: the skill knows this rule and checks it on all channels. On the site/in the product Figma
  redundantly guards it (token), but the skill still flags visible violations.
  Off-brand tell: a heading not in all caps, or set in a different typeface (system sans, etc.)
  (anti-examples: the section heading "Introducing Higgsfield Games" — not all caps and not Space Grotesk,
  even though it is H2/H3 level; the "COMPARE PLANS" page — the heading is all caps but NOT Space Grotesk, and
  the "Starter" / "Plus" / "Ultra" / "Video" columns/sections are neither all caps nor Space Grotesk).
  - **The heading color adapts to the background; the form (all caps + Space Grotesk) is invariant.**
    Section-heading reference example: brand lime `#D1FE17` + all caps + Space Grotesk ("HIGGSFIELD VIRAL
    PRESETS"). Valid heading colors: on a dark background — white or lime; on lime — black
    (reference examples: Supercomputer — white, AI Marketplace — black, Viral Presets — lime).
    **Red/crimson is NOT a heading color.** Red lives as a marketing accent (badges/CTA/
    graphics), but we do not paint the main title with it — only white/lime/black. Anti-example: the red
    "SHOTS" title — red text is not Higgs.
    A heading is in ONE color, not two at once, and WITHOUT a gradient on the text (let alone a muddy one).
    We avoid a two-color heading (at best questionable, ≈50/50 — pick one color).
    **Exception — marketing-material covers:** coloring a title in parts (e.g. a white word +
    a lime word) looks sketchy in regular UI, BUT on video/marketing covers it is acceptable
    (cover reference examples: "MICRO BEASTS PACK", "FACE SWAP", "SKIN ENHANCER", "URBAN CUTS" — white +
    lime). In product/web we keep one color.
    A muddy gradient on heading text is an anti-pattern (in any case).
    Questionable example: the Cinema heading "CREATE YOUR FIRST PROJECT. / GENERATE THE IMPOSSIBLE."
    in two colors. Anti-example: "Introducing Higgsfield Games" — two colors + a muddy gradient
    on the text (on top of not being all caps and not Space Grotesk).
  - **Boundary: the rule applies only to H1–H3. H4/H5 and below do NOT get the heading treatment.**
    A cell title, a card heading (that is H4/H5 level), a title inside a component — these are NOT H1–H3,
    and must not get Space Grotesk + all caps.
    Anti-patterns: a cell title set in Space Grotesk all caps as if it were H1 (the "PLACE IT" example
    in an element card); an H4/H5 card heading in Space Grotesk all caps (the "HIGGSFIELD
    PLUGIN FOR DAVINCI RESOLVE" example in a site section card).
    The skill needs to distinguish the heading level from the text's role in context.
- **All caps — only Space Grotesk.** (Confirmed.)
  If text is set in ALL CAPS — the typeface must be Space Grotesk. All caps in a foreign/system typeface is not ours.
  Scope: judgment call, all channels; especially video/marketing covers (no tokens there).
  Off-brand tell: all-caps text not in Space Grotesk (anti-examples: all-caps titles in foreign typefaces
  on video covers — "CLICK TO AD", "FACE SWAP", "URBAN CUTS", etc.; "SHOTS", "INPAINT" —
  all caps not in Space Grotesk).
- **Slanting text for no reason is not Higgs.** (Anti-pattern.)
  Italic/oblique without a reason is not welcome. Italic is justified only in the badge spec (NEW = bold
  italic); in headings/titles an arbitrary slant is not ours.
  Scope: judgment call, all channels; especially video/marketing covers.
  Off-brand tell: a slanted title without grounds (anti-examples: italic "VIRAL APPS",
  "PRO" in "4K NANO BANANA PRO").
- **Air between letters (wide tracking) is not Higgs.** (Anti-pattern.)
  Letterspacing/wide inter-letter spacing in headings/labels is not our device; we keep tight/
  normal tracking.
  Scope: judgment call, all channels; especially video/marketing covers.
  Off-brand tell: widely spaced all-caps labels (anti-examples: "U N L I M I T E D",
  "O P E N A I", "I N T R O D U C I N G", a letterspaced "HIGGSFIELD" on covers).
- **Text is in the recognizable brand style, not random typefaces.** (Anti-pattern.)
  We keep labels/titles in our typography (Space Grotesk for all caps, our character), not in
  random "showy" typefaces (chrome/metal, handwritten script, default sans). A random/
  unrecognizable text style reads as a foreign/generic service.
  Scope: judgment call, all channels; especially video/marketing covers.
  Off-brand tell: an unrecognizable text style (anti-examples: script-italic "AI Stylist";
  chrome/metal "ZEPHYR"; a jumble of typefaces on covers — "looks more like a default AI service").
- **Text is not tiny: titles/labels are readable and noticeable.** (Anti-pattern.)
  Key text (a cover title, an offer) must not be small — scale matches importance and layout
  (ties to Criterion 1). Small text gets lost and cheapens.
  Scope: judgment call, all channels; especially covers/banners.
  Off-brand tell: labels that are too small in covers/compositions.
- **The accent is always brand lime `#D1FE17`.** (Confirmed.)
  The accent preference is always our lime. Competing accent colors (orange, etc.)
  in the primary-button role are not our brand.
  **The accent's role is to direct attention to the MAIN feature, in moderate quantity.** Lime works,
  when there is little of it and it points at the key thing (feature, action, state), rather than being smeared across the screen.
  Reference examples: the lime brush/highlight on "Draw to Video" — lime pulls focus onto the feature itself; lime
  highlight strokes in the cinema videos — moderate and purposeful.
  Scope: judgment call, all channels.
  Off-brand tell: the primary action is colored something other than #D1FE17; several different accent colors
  on one screen; lime smeared everywhere without pointing at the main thing.
- **There is exactly one green on the site — brand lime `#D1FE17`. Any other green is off-brand.** (Confirmed.)
  The brand's only green shade is lime `#D1FE17`. Generic green (the iOS-style toggle,
  "ordinary" green in graphics, olive, etc.) is not ours: we replace it with lime. This tightens
  the earlier observation about "generic green" (the One Canvas banner).
  Scope: judgment call, all channels (especially the website).
  Off-brand tell: a green shade different from `#D1FE17` (anti-examples: the generic-green
  "Annual 30% OFF" toggle on the Compare Plans page — should be brand lime; green graphic objects
  in One Canvas — generic green instead of lime; the green "That's cool!" chat bubble and green
  cursor on the canvas — generic green, should be lime; the green "Quick Start" label text —
  not brand lime). Reminder: when recoloring to lime, text on top of lime is black (contrast).
- **Avatars/initial circles — not in random bright colors.** (Confirmed.)
  Colored initial avatars (purple/pink/green etc. "rainbow" circles) fall outside the
  brand palette. Keep them restrained/neutral, without random fills (a green fill
  additionally violates the single-green rule).
  Scope: judgment call, all channels (product).
  Off-brand tell: a set of multicolored initial avatars (anti-example: purple/pink/green
  participant avatars in the share modal).
- **Secondary icons — secondary gray `#828282`, not multicolored. BUT: colored nav/folder icons as a system — OK.** (Clarified.)
  We distinguish two cases:
  - **Off-brand:** RANDOM multicolored utility icons (e.g. section-header icons in different
    colors) — they break up the accent; we push those into secondary gray `#828282`. Linked to Criterion 1.
  - **On-brand:** a CONSISTENT color system for sidebar/navigation icons (branded gradient
    tiles) and color coding of folders — moderate, "doesn't shout, but isn't boring either," gives a bit of
    life. This is a deliberate system, not random scatter. (Confirmed by the user.)
    Reference example: Cinema Studio nav icons (Home / My Generations / …) + colored folder icons
    (Costumes/MISHA/SAMIR/ASSETS …).
  Boundary: icon color is OK if it is a consistent system and it is moderate; not OK if random
  scatter breaks the single accent. Reminder about green: within the system we use brand lime, not
  generic green (Criterion 3, single green).
  **Anti: flat gray generic nav.** A menu of flat gray outline icons + text with no brand
  character looks "like everyone else's" — for Higgs that's an anti-pattern (recognizability is lost). Nav is better
  with branded colored icons (see the Cinema Studio reference example). Anti-example: the Supercomputer sidebar —
  flat gray icons, 100% like the competitors.
  **Icon color signals state:** an ACTIVE / selected icon — brand lime `#D1FE17`;
  inactive / secondary — secondary gray `#828282`. (Confirmed: the active Seedance icon
  in the toolbar — lime; in the model-selection modal the selected row carries a lime checkmark
  and a lime "G" icon, while unselected rows have the same "G" icon in gray; the selected "Elf" card
  in the avatar grid — lime border + lime checkmark; the active/current stepper step — lime,
  the remaining steps neutral.)
  **Lime = highlight for the selected/recommended.** A highlighted card/option is styled with
  a lime border + lime ribbon header (black text, icon), or with a lime gradient
  glow on the block. Reference example: the "RECOMMENDED" card on top-up pricing (lime border +
  lime header ribbon); the "Most Popular" row with a lime gradient glow.
  **On the highlighted block — a primary lime 3D button.** Since the block is highlighted as the main choice,
  its CTA must be the strongest accent — a lime 3D primary, not white/flat.
  Off-brand tell: a white flat button sitting on a brand-gradient-highlighted row instead of
  a lime 3D one (anti-example: the white "Purchase" on the highlighted "Most Popular" row — the highlight
  is there, but the CTA accent is weaker than it should be).
  **States in functional UI:** progress and success — lime (progress ring, "success" checkmark);
  error/Failed and neutral/cancelled — GRAY, NOT red (for us red is marketing; in the product
  an error is neutral). Reference example: the downloads modal — lime progress ring and check, gray cloud-x on
  Failed, gray eye-off on "Cancelled. Restricted content".
  Scope: judgment call, all channels.
  Off-brand tell: multicolored small icons (anti-example: the teal / amber / green
  section-header icons for Gender / Ethnicity / Skin Color on one screen).
- **Text — a combination of white (primary) and gray (secondary).** (Reference example confirmed.)
  Two-tone text hierarchy: white — primary, gray — secondary/captions. Clear separation
  by importance, without extra colors in text.
  Scope: judgment call, all channels (on a dark background). On a lime background the primary text is black
  (see the heading-color/contrast rule above).
  Reference example: the text in the Create Video prompt box.
- **Text without a black outline/border (stroke).** (Anti-pattern.)
  We do not outline text with a black contour. It reads as cheap and not our style; we maintain readability
  through contrast (white/lime/black depending on the background), not with a black stroke around the letters. Especially — captions/
  subtitles on video.
  Scope: judgment call, all channels; primarily video and text over an image.
  Off-brand tell: text with a black outline (anti-example: the video captions "THE LIFESTYLE SHOTS AND"
  / "MANUALLY EXPORT FROM ONE" / "WILLINGNESS TO LEARN THESE" — letters in a black outline).
- **Discounted price: mute the old price (gray), highlight the new one with the brand.** (Clarified.)
  A struck-through old price is secondary information → gray, muted. Red/crimson on
  the old price pulls the weight to the wrong place (the old mattering more than the new — a hierarchy mistake). The current
  discounted price gets highlighted with brand lime `#D1FE17`, so the accent lands on the savings.
  Scope: judgment call, all channels (especially pricing/promo). Linked to Criterion 1 (weight = importance).
  Off-brand tell: the struck-through old price set in bright red/crimson (too accented),
  the current price in neutral white with no highlight (anti-example: top-up pricing — old prices
  in crimson, new ones in white; better: old in gray, new in lime).
- **Restrained typographic hierarchy: a limited set of sizes and weights.** (Confirmed.)
  We don't multiply many different accent sizes and text weights. A clear small system (heading /
  body / secondary), not a dozen competing "accent" styles — otherwise the screen gets noisy
  and the hierarchy is lost. Linked to Criterion 1 (weight = importance).
  Scope: judgment call, all channels.
  Off-brand tell: too many accent sizes/weights on one screen (anti-example:
  the asset-picker modal — an overload of accent text sizes and weights).
- **Icons — outline by default. Filled — rarely and only small (12–14px).**
  (Confirmed.)
  Filled icons are used rarely and only at a very small size (~12–14px). NOT on
  large icons and certainly not in core components (cells, buttons).
  Scope: judgment call, all channels.
  Off-brand tell: a large filled icon; a filled icon in a cell/button/core component
  (anti-example: the large filled lime icons for "Top-up credits" / "Boost speed" in the profile
  dropdown).
- **Shape / corner rounding: moderate radius. Neither 100% pill/circle, nor excessively large radii.** (Confirmed.)
  The rule is general for all components, not just buttons and avatars: 100% corner rounding
  (a full pill or circle) is not Higgs. And the opposite boundary: an overly LARGE corner radius
  (inflated "soft" corners on modals/cards/tiles) is not ours either. The brand has its own MODERATE rounding
  shape — not a full circle/pill and not an exaggeratedly large radius (cf. the NEW badge —
  a rounded rectangle with a moderate radius).
  **Holds in marketing too (for buttons/components):** the marketing exception gives freedom in
  COLOR (Criterion 5), but NOT in shape — a pill button remains off-brand in marketing as well.
  Narrow exception: on marketing LANDING PAGES, round (pill) LABELS/tags are allowed — for noise
  control (see Criterion 5). This does not extend to buttons.
  **Shape consistency on a screen:** buttons on one screen share a shape. A lime pill next
  to moderately rounded buttons = both a shape violation and a mismatch.
  **Exception — the Canvas product:** in Canvas, the toolbar with 100% round buttons is the signature
  style of Canvas SPECIFICALLY (confirmed: "хороший toolbar ui" ["good toolbar ui"]). Only here are round buttons on-brand;
  on any other surfaces the "no 100% rounding" rule holds. The scope of the exception is strictly
  the Canvas product (toolbar/tools).
  Scope: judgment call, all channels. In the product, shape is guarded by the DS.
  Off-brand tell: a round avatar; a button/tab/container with fully rounded ends
  (anti-examples: the round "AI Influencer" avatar, the "Try in chat" pill button, the "Claude"
  pill tab in the switcher; the round (100%) send button in the prompt box — additionally flat,
  not 3D; the lime "Buy boost credits" pill on the pricing page — the color is OK, but it's a 100% pill and
  inconsistent with the moderately rounded white "Purchase" buttons on the same screen); as well as
  an excessively large corner radius on a modal/cards (anti-example: the "Select Avatar" modal —
  inflated rounding, softer than our moderate shape); a pill search bar (anti-example: an overly
  rounded search bar in the search modal — should be a moderate radius).
- **No skeuomorphism in the interface.** (Anti-pattern.)
  For us, 3D is only for buttons, icons, and decorative graphics. The interface itself stays clean
  and flat: no physical knobs/dials, faux-LCD displays, or realistic "hardware"
  controls. Excessive skeuomorphism/3D on the UI is off-brand (an important boundary: 3D ≠ skeuomorphic UI).
  Scope: judgment call, all channels.
  Off-brand tell: skeuomorphic controls (anti-example: the voice-change panel with a physical
  rotary dial and an LCD display).
- **Marketing colors — red (marketing) and blue (paired with lime).** (Clarified + reference example.)
  A supporting palette beyond the accent. The accent is always `#D1FE17`; red/blue do not replace it.
  **What counts as a marketing surface:** banners, promos, and also pricing/promo pages
  on the site — that's marketing (an aggressive palette is acceptable there). The internal working UI of the product —
  no.
  - **Red / crimson (aggressive)** — OK in marketing, including brightly aggressive (headings,
    promo badges, CTAs). In the product — off-brand. Reference example: the pricing page (crimson banner,
    heading, "SPECIAL 30% OFF" badge, pink "Upgrade Plan" button).
  - **Blue — OK when PAIRED with brand lime, including at scale as a background/element (clarified).** Blue is acceptable
    as support next to lime, not as a standalone accent. It works both in the product (e.g.
    the collab cursor/name tag on Canvas next to a lime button) and in marketing (the blue "Explore
    Plans" + lime badges). Saturated blue is OK even IN LARGE QUANTITY — as a banner background or an element
    of a video (reference example: the blue "Animated Infographics" banner with the lime "Try" button). The key point —
    the accent/CTA stays lime; blue does not become the accent.
  Scope: red — marketing (in the product we flag it); blue — OK paired with lime (incl. the product).
  Off-brand tell: red in the product UI (anti-examples: the red "TOP" badge in the
  Features/Models modal; the garishly red PDF icon, Criterion 1); blue as a standalone accent without
  brand lime. An additional frequent problem: such a colored button is also flat — in the product that's against
  the 3D spec (Criterion 5); in MARKETING a flat colored CTA is acceptable.
- **Colored 1px borders (hairline outlines) on icons/tiles — not our device.** (Anti-pattern.)
  A thin colored frame around an icon/tile (especially in the badge's color — pink-red, lime)
  does not belong to the brand. Icon tiles are built clean, without colored hairline outlines.
  Scope: judgment call, all channels.
  Off-brand tell: 1px colored borders on icon tiles (anti-example: the pink-red and lime
  icon outlines on the TOP / NEW items in the Features/Models modal).
- **Dots on the background — part of the identity (website + Canvas).** (Confirmed.)
  The dotted background pattern is a recognizable identity motif; confirmed on the website and on Canvas.
  Scope: website and Canvas (for other channels — an optional motif, not a requirement).
- **Background brand motifs: a clean lime gradient and a perspective grid.** (Reference example confirmed.)
  The brand can express itself through a clean lime gradient (glow) and grid lines in perspective
  (a metaphor of space/canvas). The key is clean, without mud.
  Scope: judgment call; stronger in marketing/banners and on the website.
  Reference example: the Supercomputer banner.
- **Logo as a texture / watermark on a banner — our motif.** (Reference example confirmed.)
  A large Higgs logo set into the background (semi-transparent/tonal, like a texture) is a recognizable
  device for styling a marketing banner. Not to be confused with a faceless section without the brand: here the brand
  is in fact present through the logo texture.
  Scope: marketing, banners, promo pages.
  Reference example: the logo texture in the crimson banner of the pricing page.
- **Black text on a lime background — contrasty and readable (our device).** (Confirmed.)
  On brand lime `#D1FE17`, black text gives strong contrast — this is valid, do not flag.
  Reference example: the texts in the AI Marketplace banner.

### Criterion 4 — Imagery: photos and illustrations
- **The brand's imagery is alive and vivid; cartoonish, 3D, and cinematic are ours too.** (Confirmed.)
  The imagery palette is wide: editorial photo, cartoonish/illustrative, 3D, cinematic
  (cinema/film-grade) shots — all on-brand, AS LONG AS it is alive, vivid, and energetic (the main criterion is
  no dullness/passivity, see below).
  Scope: judgment call; SMM, video, marketing, product.
  Reference examples: game/anime characters, 3D graphics/icons, vivid fashion shots, cartoonish covers
  (e.g. "MICRO BEASTS PACK"), cinematic shots (Cinema Studio / Seedance / Angles covers).
  Boundary: within a single library the style stays uniform (see the avatar-style rule — that is exactly where
  we do NOT mix generic-3D/cartoon into the editorial line).
- **Avatar/character style — conceptual editorial photography (differentiates us from competitors).** (Reference example confirmed.)
  The avatar library in the signature style: surreal editorial portraits (human
  bodies + animal/creature heads), a uniform neutral backdrop, uniform waist-up framing,
  fashion styling (blazers, jackets). Bold concept + a "real" camera look = recognizably ours,
  not generic-3D and not cartoonish. This is precisely the differentiator from competitors.
  Scope: judgment call; product (avatar/character libraries), SMM, marketing.
  Reference example: the avatar-styles grid (Human / Ant / Octopus / Elf …) — uniform style and treatment.
  Off-brand tell: a jumble of styles within one library, generic-3D/cartoonishness, cheap stock,
  inconsistent treatment/framing.
- **Brand photography: editorial fashion photography with character.** (Reference example confirmed.)
  On-brand tells:
  - shot with a real camera, editorial/fashion grade (not generic stock, not flat pictures);
  - a dynamic, unconventional angle and pronounced perspective (low angle, top-down shot,
    foreshortening);
  - bright, saturated, bold color (e.g. deep red, saturated pink/glitter);
  - fashionable, stylish, with character;
  - sharp focus, a clear hero in the frame.
  Scope: judgment call; strongest in SMM, video, marketing (see matrix 3a).
  Off-brand tell (confirmed): dull/unvivid photos, limp ungraded color (example: the dull
  photo content in the Photodump banner); washed-out flat generic stock, boring frontal
  angles, unclear focus, absence of style; overly gray, passive, unnoticeable hero graphics
  that carry no energy (anti-example: the gray collage of project cards in the Collab ad modal — the graphics
  are dull and passive; a bright/energetic visual is needed); a dark/muted promo banner that carries
  no energy next to bright ones (soft, ≈30/70: the dark "MCP & CLI" banner does not "shout" against the
  teal/magenta banners — a promo banner is better off with energy/brightness).
- **Perspective / distortion — our device (in graphics AND in text/logos).** (Confirmed.)
  Tilted cards, a collage in perspective, warping of space — in the Higgs spirit
  (cf. the perspective grid, Criterion 3). **The device extends to text/logos:** perspective-
  distorted ("warp") product logos are a signature effect. Important: the device itself is ours, but the photo
  content must still be bright (see the rule above).
  Scope: judgment call; marketing, video covers, hero.
  Reference examples: the perspective collage in the Photodump banner; the perspective-warp "CINEMA STUDIO" logos (2.5 /
  3.5 / 2), "SEEDANCE 2.0", "ANGLES" on video covers.
- **The curve / squiggle as a graphic element-symbol — our motif.** (Confirmed.)
  The signature curve (squiggle, the same motif as the logo "S") is used as a decorative
  graphic element/symbol in covers and graphics.
  Scope: judgment call; marketing, video, graphics.
  Reference example: the curve-symbol in the Cinema Studio covers.
- **3D icons as decorative graphics — our device.** (Reference example confirmed.)
  Glossy volumetric 3D icons are used as graphic/hero elements. This is NOT the same as
  functional UI icons: the rule "outline / gray #828282 / filled only when small" (Criterion 3)
  applies to UI icons in the interface, not to decorative 3D graphics.
  Scope: judgment call; marketing, banners, hero sections.
  Reference examples: the row of 3D icons in the Supercomputer and AI Marketplace banners (incl. with a motion effect —
  movement/animation of 3D icons is our device too).
  Off-brand tell (soft): graphics/cards without 3D depth where volume is expected (anti-examples:
  the flat tilted video cards in the hero of the Cinema page — not quite 3D; the hero collage in the Collab ad
  modal — flat and gray, without a 3D element that would add energy).
- **Illustrated characters in anime/game style — our device.** (Reference example confirmed.)
  Stylized characters (anime, game) support the brand's 3D/game theme and are appropriate as graphics.
  Reference example: the characters in the "Make games with Higgsfield" ad banner.

### Criterion 5 — Consistency / fidelity of brand assets
- **Small brand symbol — the lime "S"/squiggle mark.** (Canon, keep.)
  The compact Higgs logo symbol (the lime "S"/swirled mark) is the canonical small branded symbol
  for sidebar headers, compact placements, favicons. Color — brand lime `#D1FE17`, not gray/
  muted (cf. the brand-presence rule).
  Scope: product, web.
  Reference example: the symbol in the "Cinema Studio" header.
- **Themed logo styling — OK for supporting a theme (game tie-in).** (Confirmed.)
  The logo/symbol may be styled to match the content's theme (e.g. a pixelated "Minecraft" style for
  a game tie-in) — this is a deliberate theme-support device, not a brand violation. It echoes
  the pixel motif and the game/anime line (Criterion 4).
  Scope: game/themed content, collabs. NOT the default product/primary logo.
  Reference example: "HIGGSFIELD IN MINECRAFT" — pixelated logos and text in the Minecraft style.
- **Pixel-styled Higgs logo/symbol — our device.** (Reference example confirmed.)
  The logo/symbol in a pixelated rendering is on-brand (continues the pixel/dots motif, cf. the brand
  spinner). Reference examples: the pixelated "Higgsfield Recraft 4.1" logo; the pixelated "Higgsie" avatar;
  pixel-styled graphics and text for Supercomputer/CLI ("HIGGSFIELD CLI + INTEGRATED SKILLS").
  Scope: product, marketing, video; the pixel style is especially appropriate for Supercomputer/CLI.
- **Collab lockup with other brands — OK.** (Confirmed.)
  Co-branding in the "Higgsfield × Partner" format (Higgs logo + "×" separator + partner logo) is a
  valid pattern for collabs. The Higgs logo stays recognizable (brand color/clean presentation).
  Scope: marketing, collabs, video.
  Reference examples: "Higgsfield × Grok Imagine"; "Higgsfield Recraft 4.1".
- **Product name in marketing — a crafted graphic logo/lockup, not just text.** (Confirmed.)
  A product name in marketing materials is presented as a deliberately crafted graphic logo (lockup/
  emblem), not default typography. "Just bold text" in the role of a logo is an anti-pattern (looks
  off-brand).
  Scope: marketing, video, promo.
  Reference example (OK): "MARKETING STUDIO" as an oval emblem lockup (a distinct graphic logo);
  the lime/white perspective-warp logos "CINEMA STUDIO" (2 / 2.5 / 3.5), "SEEDANCE 2.0",
  "ANGLES" on video covers — bright accent logos with the signature warp.
  Off-brand tell: the name set in plain bold text without logo treatment (anti-example:
  "MARKETING STUDIO" in flat bold text — reads as just text, not in the Higgs style).
- **Brand spinner / loader — the pixel/halftone-animated Higgs logo.** (Reference example confirmed, canon.)
  The canonical loading asset: the Higgs logo in a pixelated/dotted (halftone) animation on a dark
  background + a minimal horizontal progress bar. It continues the identity's dots/pixel motif.
  Scope: product, web (any loading states).
  Reference example: the loading screen with the pixel-animated logo + progress bar.
  Off-brand tell: a generic spinner (a system ring/spinner) instead of the signature pixel logo.
- **Credits progress as dots (lime filled + gray empty) — a brand element.** (Confirmed.)
  The credits indicator as a row of dots: filled ones — brand lime, empty ones — gray. A signature
  component (formerly a "candidate", now confirmed).
  Scope: product (profile dropdown, billing).
  Reference example: "Credits 2,482 left" with lime dots in the profile dropdown.
- **Stepper (numbered steps) — specification.** (Confirmed.)
  - **The active/current step is accented (lime)**, the rest neutral/gray. A stepper without an accent
    (all steps equally gray) does not show progress — that is an anti (ties to active=lime, Criterion 3).
  - **The connector lines between steps have weight and a light inner glow**, not hairline-thin.
    A line that is too thin reads weak/cheap.
  - **There is NO connector after the last step** — the line ends at the last step; a "dangling"
    tail after the final step is superfluous.
  Scope: judgment call, product (onboarding/setup modals, multistep flows).
  Off-brand tell (anti-example: the stepper in the "Connect your Okta" modal — steps without an active
  lime state; lines that are too thin; a superfluous connector after the 3rd step).
- **Large / primary accent buttons — the 3D button.** (Confirmed + reference examples obtained.)
  Reference-example tells: a volumetric (raised, "pressable") look — the bottom edge/shadow gives depth;
  shape — a rounded rectangle with a moderate radius (NOT a pill); black text and icon;
  may carry an icon (star/play) and a counter.
  **This also extends to icon-only accent buttons** (lime sparkle/generate buttons) — they too
  must be 3D, not flat.
  Fill variants:
  - lime `#D1FE17` with a light gradient (brighter on top → more saturated at the bottom) — the primary brand accent;
  - white — an alternative variant of the 3D button (same volume, black text).
  Reference examples: "Generate Influencer ✦ 2" (lime), "GENERATE ✦ 56" (lime), "Try now" (white),
  "Turn to video" (lime, full-width, with a video icon — in the info sidebar of the viewing screen),
  "Go to Cinema Studio" (lime, full-width — in the Collab ad modal).
  Scope: judgment call + channels without tokens. In product — the component from the DS.
  Off-brand tell: a flat primary button without volume; a pill button (anti-example: the flat
  lime "Play" pill — a double violation: shape + absence of 3D); flat white buttons
  where a 3D primary is needed (anti-examples: "Try Canvas", "Try Photodump" in banners); a flat
  lime "Generate ✦ 2" — color and shape correct, but no 3D volume; the "Generate ✦ 1" button
  in the voice-change panel — not to the 3D primary spec; the round (100%) flat lime send
  button in the Supercomputer prompt box — a double violation (shape + absence of 3D), even though the
  lime color and the "single accent" role are correct; fixed by switching to 3D + moderate rounding;
  the flat dark-gray "Apple-style" "Downgrade/Upgrade Plan" buttons on the Compare Plans page —
  neither lime, nor white, nor 3D, they read as a foreign (Apple) UI kit, not Higgs; flat lime
  icon-only accent buttons (sparkle/generate) — they must be 3D (anti-examples: the lime sparkle
  button on the Higgsfield Games card; the lime sparkle generate button on Canvas).
  Secondary actions nearby stay neutral (the single-accent-button rule, Criterion 1).
- **Secondary/ghost buttons — without a heavy border.** (Confirmed.)
  On secondary/ghost buttons (Copy, Paste, etc.) we do not use a thick 2px border — it adds unnecessary
  weight and competes for attention. Variants: a 1px border, or no background (pure ghost), or a filled
  neutral-gray background without a border. We keep secondary weight quiet.
  Scope: judgment call, product.
  Off-brand tell: a 2px border on a secondary button (anti-example: the "Copy" buttons in the
  "Connect your Okta" modal — 2px border, unnecessary weight; fixed with 1px / no background / filled gray).
- **Button color — only brand lime `#D1FE17` or white. We have NO black buttons.** (Confirmed.)
  IN PRODUCT there are exactly two button fill variants: lime and white. A black button is not our case.
  **Exception — marketing:** on marketing surfaces the CTA may be in the aggressive
  marketing palette (crimson — OK; blue — ≈50/50) and flat. Reference example: the pink "Upgrade Plan"
  and the blue "Explore Plans" on the pricing page. This does NOT extend to product.
  Scope: product — only lime/white 3D; marketing — a colored flat CTA is allowed.
  **Choosing lime vs white — by contrast with the background.** On a lime background the button is white (lime-on-lime
  does not contrast); on a dark one — lime or white.
  Off-brand tell: a black button (anti-examples: the black "Browse more" in the AI Marketplace banner;
  the black "Create game" in the Make games ad banner on a lime background — confirmed, fix: white);
  a colored (red/blue) button in product UI.
- **CTA button size — to the scale of the layout.** (Confirmed.)
  On a large banner the main button must not be small: the CTA's scale matches the size of the
  layout and the importance of the action (ties to Criterion 1, focus/hierarchy).
  Off-brand tell: a small CTA on a large banner (anti-example: the tiny "Browse more").
- **Status labels (NEW, UNLIMITED, etc.) — a fixed badge look (see reference):**
  - shape: a rounded rectangle with a slight tilt (dynamic, not strictly straight);
  - fill: brand lime `#D1FE17`;
  - text: all caps, black, bold italic, tight;
  - tight paddings, the badge sits inline to the right of the heading, vertically centered.
  **Shape — the angular tilted badge by default. Exception — marketing landings:** there,
  round (pill) labels are allowed. The reason is noise control: if EVERY label is made an accented
  angular badge, the landing ends up with too much noise. So on marketing landings
  some labels may be calm pills (reference examples: "$1 = 21 credits", "−45%", "Best Value",
  "Most Popular" on the top-up pricing). Important: the exception is about LABEL SHAPE, not buttons —
  pill buttons remain off-brand (Criterion 3, shape).
  **Do not make all labels accented.** An accented (lime, noticeable) label is for the main thing;
  functional/informational labels are kept quieter (a neutral pill), otherwise the screen shouts.
  The spec is uniform for the whole family of status labels, not only "NEW" (confirmed: "NEW" and
  "UNLIMITED" in the model-selection modal are styled identically to this spec).
  **Placement — inline next to the heading, not on the icon/tile.** The badge sits by the heading
  text, not in the corner of the icon. Placement must be consistent across the whole list.
  **Fill color — lime by default.** In product, badges are lime only; red/pink ones
  (e.g. "TOP") in product are not ours. **Exception — marketing:** promo/status labels may
  be in the aggressive crimson fill (reference examples: "SPECIAL 30% OFF", "25% OFF", "MOST POPULAR" on the
  pricing page), while functional badges there stay lime ("FULL ACCESS",
  "UNLIMITED", "70% CHEAPER"). Blue badges (BEST VALUE / SEEDANCE) — marketing ≈50/50.
  Scope: channels without tokens (SMM, video, marketing). In product — the component from the DS.
  Reference example: the "NEW" / "UNLIMITED" badges in the model-selection modal.
  Off-brand tell: a different fill shade, a straight (untilted) or heavily rounded
  pill-shaped badge, non-italic/non-all-caps text, light text on lime; badge on the corner of an icon
  instead of inline next to the heading; inconsistent badges within one list (anti-example: the
  Features/Models modal WITHOUT blur — TOP/NEW badges on icon tiles rather than next to the text). Clarification: the problem
  was the PLACEMENT (on the icon corner) and the missing blur, not the NEW/TOP badges themselves — inline next to the text,
  NEW (lime) and TOP (magenta, like the promo highlight in discovery) consistently = ok (reference example: mega-menu
  with blur).
  a label with a dark-olive fill and lime text, not all caps/not italic, pill-shaped (anti-example:
  "New" next to the "Games" item in the Supercomputer sidebar — misses the spec on fill, text, and shape).
- **Labels / categories — always a tag with a background, never bare text.** (Rule + positive reference example.)
  Any label/category is styled as a tag, not as a caption/"title" placed over the content.
  Positive fill (reference example "PHOTODUMP"): background — brand lime `#D1FE17`, solid and clean;
  text — all caps, black, bold, dense; shape — rounded rectangle with a slight tilt.
  In essence a category tag = the same device as the NEW badge.
  Prohibitions: the background is NOT semi-transparent (transparent = muddy/unprofessional); the color is NOT orange;
  no generic green in the text (only brand lime, see the single-green rule, Criterion 3).
  Scope: judgment call, all channels.
  Reference examples: "PHOTODUMP" in the banner; "NEW" / "EXCLUSIVE" in the menu — solid lime fill, angled
  tilt, black bold italic all caps, inline next to the heading (exemplary form of the brand label).
  Off-brand tell: a category as bare text (anti-examples: "UGC" / "UGC Virtual Try On" on
  video cards; "NEW FEATURE" in the One Canvas banner); a tag with orange text on a
  semi-transparent background (anti-example: "GENERATIVE MEDIA" in a site section); a label with a TRANSPARENT background
  and rounded (pill) edges, green text — does not match the other labels (anti-example:
  the "Quick Start" tab/label — transparent background + pill + generic-green text; fixed with a solid
  fill and brand lime).
- **Brand presence: Higgs must be readable in the section/visual.** (Anti-pattern of absence.)
  If a visual sits in a site section (or on a brand surface) but there is no Higgs brand in it —
  the section is faceless, this is an anti-pattern.
  Minimum: the Higgs logo colored in the brand color `#D1FE17` (not gray/muted).
  Scope: judgment call, all channels.
  Off-brand tell: a section without a recognizable brand presence; a gray/muted Higgs logo
  instead of the brand color (anti-example: the ROSEFIELD visual in a section with a gray logo in the bottom-right corner);
  a component/modal that is entirely monochrome gray, without a single lime accent or brand element
  (anti-example: the "Higgsie" assistant modal — no lime even on the send button, brand presence
  is absent). Minimum presence: lime at least on the main action/accent/state.
- **Recognizability > generic: the interface must not look "like everyone else's."** (Anti-pattern.)
  If a screen/component is indistinguishable from competitors (flat gray generic, default UI kit without
  brand character) — that is an anti-pattern, even if everything is formally "clean." The brand must read through.
  Scope: judgment call, product/web.
  Off-brand tell: an overly simple generic UI, 100% like similar services (anti-example:
  the Supercomputer sidebar — a flat gray menu without brand character; cf. the Cinema Studio reference example
  with its signature colored nav icons).
- **Global header — only the CURRENT one.** (Confirmed.)
  Mockups use the current version of the global navigation, not an outdated one. An old header
  (different items/order) = out of sync with production, not ours.
  The current header (reference): Higgs logo (lime mark) → `Image · Video · Audio |
  Supercomputer [NEW] · MCP & CLI [NEW] · Plugins [NEW] · Collab · Marketing Studio · Cinema Studio ·
  AI Influencer · Canvas · Apps`; on the right — Search (⌘K), Pricing / Buy Credits, Assets (lime),
  avatar. NEW badges are lime.
  Scope: judgment call, product/web (any screen with the global header).
  Off-brand tell: an outdated header (anti-example: Realtime Draw — the old set of items
  Explore/Edit/Character/Sora 2 Trends/Assist/Popcorn… instead of the current one).

### Criterion 7 — Finish

The "was it carried through to the end" lens. Does not duplicate 1–6; instead it catches two "not finished" states.

- **Extraneous / vestigial elements — remove.** (Confirmed.)
  Elements left "hanging" with no function: a connector/line leading nowhere; a duplicate divider;
  a forgotten placeholder; a control with no purpose. Every element must have a reason to be on the screen.
  Scope: judgment call, all channels.
  Off-brand tell: a dangling tail/line with no continuation (anti-example: the connector progress line
  AFTER the last (3rd) step of a stepper — there is no 4th step, the line is extraneous); a duplicate divider; a forgotten
  placeholder in a final mockup; a divider not finished off neatly (anti-examples: the vertical
  line between two panels in Realtime Draw runs into the header — looks unfinished; the line
  between two previews in the "DAM — New uploading" modal stretches the full height and cuts into the header).
  If a divider between panels/previews is needed — it is a contained divider, SHORTER in height than
  the panels, not edge-to-edge and not "jammed" into the header.
- **Unfinishedness — the aggregate "raw" signal.** (Confirmed.)
  A design looks unfinished when several basic things sag at once: no accent,
  no visual voice, no clear composition or alignment with the brand. This is not one
  specific violation but their sum → the status "unfinished" (rather than a set of separate small fixes).
  How to score it: if on criteria 1–5 it is simultaneously "nothing" (not aggressively off, just
  nothing there — no focus, no voice, no composition) — that is exactly "unfinished," flag it as a whole.
  Scope: judgment call, all channels.
  Off-brand tell: a mockup with no accent + no brand voice + no coherent composition — assembled, but
  "not carried through"; reads as a draft/half-product, not a final.

### Reference example: Supercomputer banner (positive, across several criteria)

A comprehensive gold-standard Higgs banner. What makes it "ours":
1. the brand as a **clean lime gradient** (glow along the edges) — Criterion 3;
2. **perspective grid lines** in the background as space/canvas — Criterion 3 (background motif);
3. the **3D white button** "Try Supercomputer" — Criterion 5 (the 3D-button variant);
4. **clean cards with blur** (frosted) — Criterion 2 (clean blur, not a muddy layer);
5. **3D icons as graphics** (a row of glossy icons) — Criterion 4 (decorative graphics, not UI);
6. the **composition** itself — Criterion 2;
7. the **balance of whitespace and density** for a banner — Criterion 2;
8. the **H1 Space Grotesk all-caps** headline ("SUPERCOMPUTER") — Criterion 3.

### Reference example: model-selection modal (positive, across several criteria)

Gold standard for a product modal. What makes it "ours":
1. **clean frosted blur** over a busy background (photo + grid) — Criterion 2; noise/grain
   is moderate — within norm, not muddy;
2. **NEW / UNLIMITED status labels** strictly per the badge spec (lime, black bold italic all caps,
   tilted rounded rectangle) — Criterion 5;
3. **state via lime:** the selected row carries a lime checkmark and a lime "G" icon,
   unselected ones — gray — Criterion 3;
4. **two-tone text** (white heading + gray caption) — Criterion 3;
5. the **shape** of preview icons and row highlight — rounded rectangles of moderate radius,
   not circles — Criterion 3;
6. **sparing accent:** lime only on states and badges, everything else neutral — Criterion 1.

### Reference example: image-viewing screen (positive, with one watch note)

Predominantly on brand. What makes it "ours":
1. **blurred backdrop** — the background is a blurred version of the same image (a recognizable viewer device,
   distinguishes it from similar services) — Criterion 2;
2. **info sidebar wrapped in cards** — Details/Comments tabs (active — white pill); INFORMATION cards
   (Status/Type/Size/Uploaded/Last used/Author) and UPLOADED IN (author/project/folder chips) —
   Criterion 2;
3. **3D brand button** "Turn to video" (lime, full-width, video icon) — Criterion 5;
4. secondary actions (Publish / Recreate / Reference / Download) are neutral — a single accent —
   Criterion 1.
- **Watch (low confidence):** the bottom toolbar (Overview/Color Grading/Upscale/…) is ours in style,
  but in visual weight it competes with the sidebar — a possible reason to rebalance, not a hard flag.

### Reference example: pricing page (marketing on the website, across several criteria)

Gold standard for a MARKETING surface (pricing/promo on the website is marketing, not product).
What makes it "ours":
1. **aggressive crimson/red** in the banner, heading, promo badges, and CTA — Criterion 3
   (marketing color, in the spirit);
2. **the logo as a texture** in the banner background — Criterion 3 (brand motif);
3. **labels in style:** promo badges are crimson, functional ones (FULL ACCESS / UNLIMITED /
   70% CHEAPER) — lime — Criterion 5;
4. clear offer hierarchy and a dense but not overloaded layout — Criterion 1, 2.
- **Watch (blue ≈50/50):** the blue "Explore Plans" button and blue badges (BEST VALUE / SEEDANCE)
  — in marketing they seem ok paired with the palette; confidence is low, do not carry into product.

### REFERENCE BASE: canonical modal template (the basis for ALL modals)

The default anatomy of a Higgs modal — the baseline against which we check any modal. All types (selection, form,
asset picker, search, confirmation) are built on the same skeleton.
1. **Shell** — frosted blur over content/imagery; moderate radius (NOT a pill, NOT bloated);
   even inner paddings, content does not stick to the edges — Criterion 2 / 3.
2. **Header** — {title} heading at top left; close (X) — a neutral circle at top right.
   Variant with tabs: the active tab is a white pill (Sketch to Video / Uploads / All / Models / Pinned …);
   inactive ones — neutral — Criterion 1 / 5.
3. **Body** — clean; a search bar of moderate radius; Filter / View — neutral controls; content
   in a grid, in two columns or with a sidebar; skeleton placeholders — gray tiles of moderate radius —
   Criterion 2 / 3.
4. **Bottom (action bar)** — {caption} on the left; buttons on the right: one white primary + one neutral
   secondary (Cancel/Save, Cancel/Move, Create, Link, Call to action). Exactly one accent — Criterion 1 / 5.
5. **Consistency** — one skeleton for all modals; the content changes, not the language.
Off-brand tell (typical deviations from the base): no blur; a bloated/pill radius; components
at the edges; several competing accents; the active tab is not a white pill; dividers instead of paddings.

### Reference example: functional modals (upload progress, across several criteria)

Gold standard for functional/status modals (upload toasts, Uploading/Uploaded/
Failed states). What makes them "ours":
1. a **clean dark panel**, moderate radius (not a pill, not bloated) — Criterion 3;
2. **lime only on the state** — the progress ring and the "success" checkmark are lime, everything else
   neutral — Criterion 1 / 3;
3. **error/Failed = gray (cloud-x), NOT red**; "Cancelled. Restricted content" — a gray
   eye-off (red for us is marketing; in product, an error is neutral) — Criterion 3;
4. **white neutral action buttons** (Cancel / Retry / Retry all) of moderate radius —
   secondary, do not fight the lime accent — Criterion 1, 5;
5. **two-tone text** (white file / gray status) — Criterion 3;
6. **grouping of sections with whitespace** + a destination link ("Uploading to New folder") — Criterion 2;
7. collapse/close controls are neutral.

### Reference example: full Assets screen / media library (holistic, across all criteria)

Gold standard for an entire product screen — "everything about Higgs." Useful as a reference for "a correct
screen as a whole," not an individual component.
1. **three-zone layout** — nav sidebar (workspace/projects) + media sidebar (All/Image/Video/…) +
   content grid — Criterion 2;
2. **lime sparingly and purposefully** — the active "Assets," NEW badges in the navbar, the usage progress bar,
   the Share button, the lime "S" workspace symbol; everything else neutral — Criterion 1 / 3;
3. **white secondary (Upload) + lime primary (Share)** — Criterion 5;
4. **cinematic fashion imagery** in the grid — Criterion 4;
5. **clean cards** of moderate radius, neutral file-type icons (MD/TXT/PDF/Figma/Notion)
   without colored noise — Criterion 2 / 3;
6. **two-tone text** (white titles / gray sizes/counters) — Criterion 3;
7. **grouping by dates** ("Yesterday"), even paddings/grids — Criterion 2.
Confirmed states of the same screen (also on brand):
- **grid and list/table views** are both ours (File name/Uploaded/Type/Size/Author/Date columns — clean);
- **multi-select** — lime checkmarks on selected items (the "selected" state = lime, Criterion 3);
- **contextual action bar at the bottom** (Download / Publish all / Move to / Copy to / ♡ / Remove) —
  neutral actions, no competing accent (Criterion 1);
- **nested folders** (S1 › Street; Misha › Tobbin / Dmity) — recognizable structure (Criterion 2).

### Mixed example (≈50% on brand): One Canvas banner

Partially on brand — useful as a "partial presence" case: the skill gives a per-factor verdict,
not a "yes/no".
- **ON brand:** the photos of the girl (bubblegum bubble, fashion shots) align with the Higgs style
  (Criterion 4); the H1 headline in Space Grotesk, all caps.
- **NOT on brand / could be better:**
  - the "NEW FEATURE" label as bare text — tag anti-pattern (Criterion 5);
  - the white "Try Canvas" button is flat — could have been a 3D primary (Criterion 5);
  - the green objects in the graphics — could have been brand lime `#D1FE17` instead of generic green
    (Criterion 3);
  - the blue background — acceptable in marketing, but questionable in product (Criterion 3).

### Anti-example: Features / Models modal — the version WITHOUT blur (across several criteria)

This is the anti-version of a specific modal (WITHOUT blur, with badges on the icon corners). The same modal WITH blur
and inline badges is on brand (see the mega-menu reference example). Useful as a comprehensive anti-reference:
1. **no blur** — a large panel rendered flat on dark where frosted is expected — Criterion 2;
2. **colored 1px borders on the icon tiles** (pink-red on TOP, lime on NEW) — Criterion 3;
3. **badges on the icon corner + colored outlines** — placement and outlines off-spec — Criterion 5;
4. **labels misplaced and inconsistent** — badges on the icon corner instead of inline next to the title —
   Criterion 5. (The NEW/TOP badges themselves are not the problem — the problem is the placement/outlines/missing blur.)

### Anti-example: Compare Plans page (across several criteria)

A pricing comparison that goes off-brand on several criteria:
1. **headings not in Space Grotesk** — "COMPARE PLANS" in all caps but a foreign font; "Starter/Plus/
   Ultra/Video" neither all caps nor Space Grotesk — Criterion 3;
2. **"Apple-style" buttons** — flat dark-gray "Downgrade/Upgrade Plan", neither lime/white nor
   3D — they read as a foreign UI kit, not Higgs — Criterion 5;
3. **generic green** — the "Annual 30% OFF" toggle is filled with plain green, not brand lime;
   on the site there must be exactly one green — `#D1FE17` — Criterion 3.

### Anti-example: "Select Avatar" modal (across several criteria)

An avatar-selection modal that goes off-brand on several criteria:
1. **too much empty space** — sparse layout, excess whitespace (Higgs is not an "airy"
   brand) — Criterion 2;
2. **corner radii too large** — bloated radius on the modal/cards, softer than our moderate
   shape — Criterion 3;
3. **no blur** — a flat dark panel without frosted where blur is expected — Criterion 2.
(The avatar photos themselves are fashion-grade, on brand per Criterion 4; we flag the shell, not the content.)

### Anti-example: share modal (across several criteria)

A project-sharing modal that goes off-brand on several criteria:
1. **too much empty space** — large gaps between the participant rows — Criterion 2;
2. **colored initial avatars** (purple/pink/green) — outside the brand palette; the green one
   also breaks the single-green rule — Criterion 3;
3. **the accent gets lost** — role chips, tabs, and Copy link at similar weight, components fighting for
   attention, no single focus — Criterion 1.

### Mixed example: covers where "the scene is fine — the styling isn't" (per-factor breakdown)

A frequent case in marketing: the photo/scene is on brand, but the text and graphics are not. The skill gives a split
verdict (imagery vs styling), not "the whole cover is bad".
- **ON brand (imagery):** cinematic, characterful scenes — Criterion 4 (reference examples: watermelon+samurai
  "Nano Banana 2"; girl with a Chupa Chups "Zephyr").
- **NOT on brand (styling):** unrecognizable text styles (script/chrome/default) — Criterion 3;
  tiny text — Criterion 3; cheap-looking cards — Criterion 2; unfortunate text compositions —
  Criterion 1/2; overall look of a "default AI service", not recognizably Higgs — Criterion 5.

### Mixed example: Supercomputer prompt box

A clean component almost entirely on brand — exactly one detail breaks. Useful as a
"per-factor verdict" case: we keep everything else and flag only the button.
- **ON brand:** the container is a rounded rectangle of moderate radius (not a pill, Criterion 3);
  the component is built cleanly on a solid dark background (Criterion 2); the text hierarchy is clear — gray
  placeholder and gray disclaimer (Criterion 3); "Smart mode" and "Ask before generation" are kept
  as neutral secondary, the sole accent is the lime send button (Criterion 1).
- **NOT on brand:** the send button — a double violation: 100% round (Criterion 3, shape)
  and flat, not 3D (Criterion 5). The color (lime) and the role of sole accent are correct — fix only
  the shape and depth: make it 3D + moderate rounding, keeping the lime.

### Mixed example: Collab / Cinema Studio ad modal

The modal shell is on brand, the graphics fall short — a "strong shell, weak visual" case.
- **ON brand:** the lime 3D button "Go to Cinema Studio" (Criterion 5); the headline "COLLAB NOW
  LIVES IN CINEMA STUDIO" — Space Grotesk in all caps (Criterion 3); two-tone text (Criterion 3).
- **NOT on brand / weak:** the hero graphic (a collage of project cards) is too gray, passive,
  without a 3D element, unnoticeable — Criterion 4 (dull imagery) + missing 3D depth where it
  would have added energy. It needs a bright, energetic visual with a 3D accent.

### Mixed example: asset-picker modal (Uploads / Elements) — ≈70% on brand

Close to our modal in style (≈70%), but falls short on a number of details. An "almost ours,
finish the job" case.
- **ON brand:** the tabbed structure (active tab is a white pill), the folder sidebar, the element grid,
  lime state markers on the cards — the overall language is ours.
- **NOT on brand / to fix:** no blur on the modal (Criterion 2); sections separated by dividers
  instead of padding/whitespace (Criterion 2); previews too small given the excess whitespace (Criterion 2);
  too many accent text sizes/weights (Criterion 3).

### Mixed example: search modal / command palette — ≈70% on brand

Almost ours in language, finish the details.
- **ON brand:** the modal has blur (Criterion 2); NEW badges (lime) / TRENDING; filter pills
  and the list structure — the overall language is ours.
- **NOT on brand / to fix:** the search bar is too rounded (pill) — needs a moderate radius
  (Criterion 3); the search bar sticks to the modal edges — needs inner padding (Criterion 2);
  "crooked" padding on cells (Criterion 2); the dark "MCP & CLI" banner doesn't shout against the bright ones —
  a promo banner is better off with energy (Criterion 4, softly).

### Identity candidates (low confidence — the skill does NOT flag these yet)

Signals that may become brand, but confidence is low. The skill does NOT use them for
"off-brand" flags — we keep them in view until confidence grows (guideline: below ~70% we don't flag).

- **Hero composition: headline + photo-graphics cluster.** Confidence ≈50/50.
  A hero with a headline and an organic rounded cluster of images (as in the marketing-tool
  modal "Pick the format that hits"). A possible signature device, still in question.
  (The all-caps H1 headline and the bright photos inside it already follow the rules; what's in question is the cluster device itself.)
- (also here by meaning — dark blue (not approved, see Criterion 3) and the dots background; blue is softer, dots
  are confirmed for the website.)

---

## Decision log

- The skill focuses on **judgment calls**, not technique — tokens/components stay with Figma.
- A DS git repository as a foundation is **not required**.
- The skill's foundation is **brand principles + reference examples**, not DS code.
- The output format is three statuses with a mandatory explanation.
- The rubric is **7 criteria** (focus, composition, visual voice, imagery, consistency,
  copywriting, finish).
- **Finish (Criterion 7)** was added: it catches (a) leftover/vestigial elements (a tail line
  with no continuation, a duplicate, a placeholder) and (b) unfinishedness as an aggregate signal (no accent +
  no voice + no composition = "raw", status "unfinished").
- **Copywriting is included** in the skill (important for SMM/marketing), but NOT yet filled with specifics (no examples).
- The criteria set is **unified**, but with **per-channel emphases** (see matrix 3a).
- **The brand accent is fixed: `#D1FE17` (lime).** Secondary gray `#828282`.
- **There is exactly one green on the site — `#D1FE17`.** Any other green (generic/iOS toggle,
  olive, etc.) is not ours; replace it with lime.
- **Supporting colors: red/crimson (marketing) and blue (paired with lime).** The accent is
  always lime. Red/crimson — marketing (banners, promos, pricing pages); in product we
  flag it. Blue is OK as SUPPORT paired with brand lime, including in product (e.g. collab cursors
  on Canvas); we never make blue a standalone accent. (The earlier "pink/magenta ≈20%" = the red
  marketing color.) In marketing a flat colored CTA and crimson promo badges are acceptable.
- Judgment-call rules (as opposed to technical ones): one accent button per section; a clean background
  (bright/dark), components are built cleanly; badges are lime only and inline next to the title; icons
  without colored 1px outlines. This is the core of the skill's zone — Figma can't catch this.
- **Label noise control:** not all labels are accents. On marketing LANDING PAGES, round
  (pill) labels are allowed (an exception to "no pills", for labels only, not buttons).
- **Selection highlight:** the selected/recommended block carries a lime highlight (border/gradient)
  AND a primary lime 3D button (not a white flat one).
- **Discounted price:** the old (struck-through) price — in gray/muted; the current one — highlighted
  in brand lime. Red on the old price = too much accent.
- **Canvas exception:** 100% round toolbar buttons are a signature style of the Canvas product ONLY;
  on all other surfaces the "no 100% rounding" rule holds.
- **States in product:** progress/success — lime; error/Failed and cancelled — gray, NOT red.
- **Brand spinner:** pixel/halftone-animated logo + a minimal progress bar (canon).
- **Typography (video/covers):** all caps — only in Space Grotesk; arbitrary slant — not ours;
  wide tracking (whitespace between letters) — not ours; a two-color/partially-tinted title is OK
  ONLY on marketing covers; in product, one color.
- **Imagery:** lively/bright/cartoonish/3D — on brand; the main enemy is dullness/passivity.
- **Brand assets:** the product name in marketing = a graphic logo/lockup (not just text);
  themed logo styling (game tie-in) is OK; the small mark is the lime "S"/squiggle.
- **Canonical modal template:** there is a single base modal (blur, moderate radius, {title}+X,
  active tab as a white pill, bottom: {caption} + white primary/neutral secondary). All modals are
  checked against it; the typical deviations (no blur, flush to edges, competing accents) = not ours.
