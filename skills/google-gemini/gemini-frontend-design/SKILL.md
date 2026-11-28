---
name: gemini-frontend-design
description: Design and build polished websites and web apps tailored to the brief. Use when creating or redesigning web interfaces, covering layout, color, typography, custom imagery, and motion.
license: Apache-2.0
metadata:
  author: Google Gemini
  origin: gemini-original
  version: "1.0.0"
---

# Gemini Frontend Design

Strong web design commits to an unmistakable visual point of view, opens with a
first screen tailored to the page's true purpose, and lets **typography,
proportion, color, imagery, and motion** carry the entire experience rather than
decorative UI chrome. Establish a clear direction up front, sustain that exact
craft from top to bottom, and verify the rendered page visually before
finishing.

## 1. Commit to a Tailored Visual Direction

-   **Honor explicit style requests; otherwise derive the aesthetic from the
    subject**:
    -   When the user asks for a specific look, mood, era, or level of restraint
        (such as minimalist, brutalist, funky, or editorial), lean into it
        wholeheartedly.
    -   When the aesthetic is open, draw palette, contrast, and layout rhythm
        from the **subject's real materials, environment, and audience** rather
        than generic category reflexes.
    -   **Explore colors beyond beige**: Models often reach automatically for
        warm beige or cream paired with rust/terracotta (even when a prompt only
        mentions *"artisanal"*, *"craft"*, *"food"*, *"warm"*, or a vintage
        decade) or dark slate with neon purple glow. Unless the brief
        specifically calls for beige or dark neon, explore a wider color
        spectrum: bold chromatic color-blocking; deep roast, forest, ink, or
        marine darks; cool architectural stone or silver; sunlit pastels; or
        crisp gallery light.
-   **Navigation & purposeful color**:
    -   Keep desktop navigation on a single compact line, giving the **brand
        title, masthead, or wordmark** noticeably stronger visual presence
        (larger or bolder) than the menu links. On hero-led pages, let the hero
        surface, image, or gradient bleed seamlessly to the top edge (`y = 0`)
        behind a borderless header bar; if the header stays fixed on scroll,
        give it clean surface separation once scrolled so content never collides
        awkwardly behind nav links.
    -   In an existing codebase, respect its established framework and design
        tokens; when starting fresh, define clean theme tokens (`:root` CSS
        variables or Tailwind `@theme`) for page background, subtle secondary
        surface, primary text, muted text (meeting WCAG AA `4.5:1` contrast),
        and one deliberate accent. Reserve extra status colors for genuine
        interactive or semantic state.
-   **Typography with strict 3-size body discipline & above-the-fold freedom**:
    -   Use **at most 2 font families** across the project: either **1 versatile
        sans family across weights** or a purposeful **2-font pairing** loaded
        cleanly via `<link rel="preconnect">`, `@font-face`, or `next/font`. Do
        **not** add a 3rd monospace font for prices, timers, or counts - use
        `font-variant-numeric: tabular-nums` on your body font unless building a
        code, documentation, or terminal tool.
    -   **Intentional typeface selection**: Choose typefaces that fit the
        subject's character rather than defaulting every creative or consumer
        brief to a display serif paired with a generic sans; geometric,
        neo-grotesk, or expressive sans display faces can be the stronger
        primary choice.
    -   Lock **at most 3 font sizes across the body of the page** (e.g.,
        `--text-heading`, `--text-body`, `--text-sm`, or 3 consistent utility
        scale steps), differentiating subheadings (`<h3>`), buttons, and labels
        via **weight, font family, and text color** rather than inventing
        intermediate `20px-24px` steps (allow a 4th compact step only when the
        user explicitly requests a dense dashboard or multi-column data table).
        **Above-the-fold hero display type (or the page's primary `<h1>`) and
        the navbar brand wordmark do not count against this 3-size limit**, so
        give them bold, architectural scale, while **never placing tiny `< 13px`
        (`0.8125rem`) text above the fold**.
    -   **Keep body prose & lists at one consistent scale**: Render all body
        paragraphs and body bullet/numbered lists at the same body scale - do
        not split consecutive paragraphs into an oversized `.lead` paragraph
        above smaller paragraphs, or shrink body bullet lists down to caption
        size. Use **sentence case** for UI labels and table headers (avoid
        tracked-out `ALL CAPS` micro-labels), keep body prose `<= 65ch`, and
        tighten display tracking (`-0.02em` to `-0.05em`).

## 2. Match the Opening Screen to the Format (Bold Hero When Earned)

-   **Skip a hero banner when immediacy is the point**: Not every website
    belongs behind a full-screen hero. **News front pages, blogs, dashboards,
    analytics consoles, documentation, search or directory indexes, utility
    tools, and minimalist resumes/CVs** should open **directly into the live
    content, masthead + story grid, workspace, or typographic document sheet** -
    never push actual articles, controls, or data below a `100vh` marketing
    banner. Let bold masthead/title proportion, crisp grid tension, and lead
    imagery carry the opening viewport instead.
-   **When a page calls for a hero (brands, products, storefronts, events,
    portfolios, long-form stories), abandon the `50/50` split template**: Do
    **not** split the opening hero into a two-column `left-aligned H1 + long
    paragraph + button + underlined link + horizontal rule + 3-4 bottom stat
    columns` beside a right-hand media box. Trapping `<h1>` in a half-width
    column shrinks its presence and makes every site read like the same
    template - let the headline and lead visual command **the full width,
    center, or depth of the viewport**.
-   **Keep hero copy razor-sharp so scale can lead**: On hero-led pages, let
    oversized display type (`clamp(3.5rem, 7.5vw, 8rem)` with tight `0.9-1.0`
    line-height when word count allows) or full-bleed imagery do the heavy
    lifting. Pair the `<h1>` with **at most 1-2 short lines of supporting copy
    (`<= 25` words)** and one clear primary action (or an immediate interactive
    canvas) - **never** append a `3-4` item KPI/spec footer strip or horizontal
    divider row to the bottom of the hero.
-   **Sample hero spatial directions (adapt, combine, or invent freely - never
    assign mechanically by business type)**:
    -   *Centered monumental headline + wide interactive stage*: A wide centered
        display `<h1>` spanning `70%-92%` of the viewport (optionally setting a
        cutout portrait, live visual tile, or animated token **inline between
        words inside the `<h1>` line itself**), 1-2 concise centered lines + one
        button, rising above a wide (`80%-100%`) interactive workbench, tactile
        preview, or full-bleed lower stage visible above the fold.
    -   *Full-bleed photographic or living-canvas takeover*: Edge-to-edge
        (`width: 100%`, `min-height: 100dvh`) photography, portrait, or
        interactive fluid/shader canvas from `top: 0` behind a borderless
        header, with centered or horizon-anchored display type and CTA placed
        cleanly in a high-contrast clearing (such as the lower third or dead
        center).
    -   *Layered depth & foreground occlusion*: Ultra-wide or monumental display
        lettering spanning edge-to-edge *behind* a central cutout subject,
        sculptural product, or interactive object (`z-index` depth layering),
        with crisp title and primary action anchored along the lower horizon.
    -   *Wall-to-wall poster or corner-to-corner choreography*: Oversized
        tightly-stacked poster typography commanding most of the screen over
        bold chromatic color-blocking, top-edge painterly gradients, graphic
        shapes bleeding off the viewport edges, or diagonal corner-to-corner
        headline tension across open space.
-   **Expressive / kinetic hero typography**: Where it elevates a hero, use
    purposeful typographic motion - staggered line/word entrance, curved
    `<svg><textPath>` ribbons, subtle variable-weight or tracking response, or
    inline animated tokens - making sure the headline renders **visibly and
    legibly at rest** (never stuck at `opacity: 0`) and honors
    `prefers-reduced-motion`.
-   **Sustain the exact same ambition below the fold**: Carry the opening
    screen's color conviction, surface craft, and bespoke interactivity all the
    way to the footer, varying pacing across full-bleed stages, interactive
    tools, asymmetric editorial splits, and focused reading moments rather than
    dropping into generic three-column card rows after screen one.

## 3. Art-Directed Imagery & Calibrated Motion

-   **Custom visuals (`generate_image`)**:
    -   Skip decorative photos inside dense workspaces where they compete with
        controls. Where imagery earns its place and an image-generation tool
        (such as `generate_image`) is available, generate custom visuals saved
        inside the project with project-relative paths, using **one unique
        visual per item**. If no image-generation tool is available, craft
        bespoke inline SVGs, CSS/Canvas visuals, or user-supplied assets - never
        guess external image URLs or hardcode machine-local filesystem paths.
    -   Match the generated aspect ratio (`"16:9"`, `"4:5"`, `"3:2"`, `"1:1"`)
        to the CSS container, keep lighting and palette consistent across the
        set, and write **1-3 plain sentences** grounded in the subject's real
        domain. When staging full-bleed hero photography or cutout subjects,
        compose clean negative space or crisp figure-ground separation so
        overlaid or layered typography hits effortless WCAG AA contrast without
        muddy full-screen dark scrims.
-   **Scroll & UI motion**:
    -   Consider using **cohesive, content-driven scroll moments** where they
        elevate the story (such as a pinned stage stepping a live diagram or
        product view, or scroll-linked reveals via `animation-timeline` /
        `requestAnimationFrame`), sized cleanly for laptop and mobile screens. On
        utility tools, news feeds, recipes, data views, or sidebar navigation
        menus, keep scrolling native and immediate.
    -   Keep interactive transitions brisk (`140ms-240ms`, smooth ease-out like
        `cubic-bezier(0.22, 1, 0.36, 1)`, never `ease-in` or `transition: all`),
        animate `transform` / `opacity` / `clip-path`, avoid idle bobbing loops,
        and honor `@media (prefers-reduced-motion: reduce)`.

## 4. UI & Copy Patterns to Avoid

-   **No pre-heading eyebrows, decorative chips/badges, or hero spec strips**:
    Start sections **directly with the `<h1>` or `<h2>`** - do not perch
    `.eyebrow`/`.kicker` labels, `ALL CAPS` kickers, or `"Location · Batch ·
    Status"` lines above headings, do not attach decorative non-interactive
    badges, chips, or category tags of **any shape (rounded capsule or
    square/bordered box)** above headings, over images, or inside cards, and do
    not pad the bottom of a hero with a `3-4` column stat/metadata bar. Convey
    card and section metadata with plain typographic hierarchy instead,
    reserving bordered or capsule shapes for interactive controls (or genuine
    semantic status cells inside data tables and API references).
-   **No button walls or nested card cages**: Give marketing and content
    sections **at most one primary CTA button** (do not automatically pair every
    primary button with a second underlined link or ghost button unless the
    workflow genuinely requires two distinct actions). When visitors choose
    between modes, sizes, filters, or settings, use **non-button selection
    controls** - a connected segmented toggle, tabs, radios, switches,
    `<select>`, or direct canvas interaction - not clusters of separate bordered
    buttons. Group content with whitespace, `1px` dividers, or surface tint
    rather than bordered cards nested inside cards.
-   **No decorative numbering or fake telemetry**: Never prefix headings with
    `01`, `02`, `[ 01 / 04 ]`, or Roman numerals unless steps are a genuine
    sequence, and omit synthetic `"LIVE"` dots, `"SCROLL"` cues, or rotated edge
    text.
-   **Direct, customer-facing copy**: State clearly what the product does and
    how it helps - cut philosophical manifestos, filler (*"seamless"*,
    *"elevate"*, *"reimagined"*), stacked adjectives before every noun, and
    fourth-wall comments about your own design. Lead headings with benefits
    rather than raw specs (`"Lightweight shell"`, not `"2.6 kg Cabin Mass"`),
    keep headlines whole without `<br><em>` italic splits, and avoid em-dashes
    or spaced en-dashes in generated copy (always preserve user-supplied text
    verbatim).

## 5. Pre-Delivery Checklist & Full-Page Visual Critique

1.  **Audit your code and copy against every item before finishing**:
    -   [ ] **Opening format fit**: Content/workspace formats (news, blogs,
        docs, dashboards, tools, resumes) open directly into live content with
        zero marketing hero banner; hero-led pages use a bold non-split
        composition bleeding to `y = 0` with `<= 25` words of supporting copy,
        one primary action, and no bottom KPI/spec strip.
    -   [ ] **Typography discipline**: At most `2` font families (`tabular-nums`
        instead of a 3rd monospace font unless building a code, documentation,
        or terminal tool), at most `3` distinct body font-size steps below the
        hero (`4` only when a dense dashboard/table was requested; hero `<h1>`
        and navbar brand wordmark exempt), consistent body sizing across all
        paragraphs and lists, sentence-case UI labels, and zero `< 13px`
        (`0.8125rem`) text above the fold.
    -   [ ] **Zero decorative UI clutter**: Sections start directly with
        `<h1>`/`<h2>` (zero eyebrow kickers), zero decorative non-interactive
        chips, badges, or category tags of any shape (rounded or
        square/rectangular), zero decorative `01`/`02`/Roman heading prefixes or
        fake `"LIVE"`/`"SCROLL"` cues, at most one primary CTA button per
        content section (non-button controls for mode/filter/size choices), and
        zero nested card-in-card boxes.
    -   [ ] **Copy & transition hygiene**: Headings (`<h1>`-`<h3>`) lead with
        user benefits rather than raw numbers or specs (`"Instant local
        reasoning"`, not `"256 GB RAM Tier"`), headlines stay whole without
        `<br><em>` italic splits, generated copy in HTML and JS contains zero
        em-dashes or spaced en-dashes, CSS transitions name explicit properties
        (never `transition: all` / `transition-all`), and
        `@media (prefers-reduced-motion: reduce)` is honored.

2.  **Inspect the rendered site across sections and viewports**:
    -   When browser or screenshot tools are available, run the local dev or
        HTTP server so web fonts and project assets load, capture **both desktop
        (opening viewport AND scrolled below-the-fold sections at true desktop
        viewport height) and `390x844` mobile views**, and inspect the rendered
        screenshots directly.
    -   Verify single-line desktop navigation, clean scrolled header separation,
        zero text/visual collisions, sustained visual ambition and 3-size body
        hierarchy all the way to the footer, and zero horizontal overflow or
        clipped display words on desktop and mobile. Apply any fixes in a single
        focused pass.
