# app-layouts — the standard Higgsfield app layouts (`type: "app"` builds ONLY)

A `type: "app"` product must look and feel like a Higgsfield product. Instead of
inventing app chrome from scratch, START from one of the four reference layouts
below — each is a screenshot of a real Higgsfield app. There are NO prebuilt
layout scaffolds: you compose the screen yourself from Quanta components (Astryx
only for gaps). Pick the closest layout, then **actually VIEW its reference
image** (open the URL / fetch it) and read the real composition — spacing, where
the form/canvas/feed/composer sit, what the controls are — before you build it.
**If the user asks for a different shape, build what they ask for** — these four
are the defaults, not a cage (a custom layout is still Quanta + `q-` tokens; a
guided multi-step flow, for instance, has no reference image — build it custom).

## The four reference layouts

View the image for the one you pick — the description only tells you which to
open, the image tells you how to build it.

| Layout | Reference image (VIEW it) | Shape / when to use |
|---|---|---|
| **Simple app** | `https://static.higgsfield.ai/website-builder/layout-references/simple-app.png` | One-shot tool (Face Swap). Two-column hero: a form card LEFT (big uppercase headline + subtitle, one–three labelled upload/input cards, an optional Image/Video mode toggle, ONE full-width lime Generate CTA with the credit cost + a "N free generations left" helper line) and a large result/preview panel RIGHT (before/after where it fits). Optional "how it works in 3 steps" explainer row below the fold. Use for a single transform with a few inputs and one action. |
| **Preset app** | `https://static.higgsfield.ai/website-builder/layout-references/preset-app.png` | Pick-a-style-then-generate (Shorts Studio). A persistent LEFT creation rail (app title, the selected-preset card with a Change action, a source upload/dropzone with constraints, an output-ratio toggle, a big lime Generate CTA) beside a large responsive GRID of preset/template tiles (preview thumbnail + name label; selected tile has a lime border; a leading "Create a preset" tile), with top tabs (Presets / History / How it works) + a search box. Use when browsing a gallery of styles/templates is the main surface. |
| **Complex app** | `https://static.higgsfield.ai/website-builder/layout-references/complex-app.png` | Single-asset editor with many controls (Relight). A dominant work canvas CENTER (empty state = a titled upload card in a big dark stage; then the asset/result) beside a dense RIGHT controls sidebar (quick-select button grid, a drag pad / sliders / toggles / color field, and the costed lime Generate pinned at the bottom). Use for enhance/edit tools with rich parameters on one asset. |
| **Studio app** | `https://static.higgsfield.ai/website-builder/layout-references/studio-app.png` | Full creative workspace (Cinema Studio). A projects-first LEFT nav sidebar (product switcher + nav rows with colored icon tiles + a Projects section with New project and a project list) and a MAIN area with a hero/home state, a prompt composer (Image/Video mode toggle, prompt input, a settings-chips row — model / aspect / resolution / duration / batch / audio — and a lime GENERATE button with the credit cost), and a generations/projects feed below. The richest layout, for multi-project generation tools. |

## Invariants (every layout, incl. custom)

- **No app header/top bar** — apps render INSIDE Higgsfield, whose chrome
  provides the global header, credits/balance, and account controls. Never add
  a brand/logo row, top nav bar, or sign-out/credits UI. In-app navigation is a
  Quanta `Sidebar` (studio) or inline controls (tabs, segmented mode toggles);
  a page title is just a heading inside the content area.
- **Permanently DARK** — `data-theme="default-dark"` is pinned on `<html>` in
  the template. No theme toggle, no light mode, no `dark:` variants.
- **Container width** — `mx-auto w-full max-w-7xl` on the shell (the body
  background fills the viewport). The exception is the studio layout — a
  full-bleed workspace (sidebar + edge-to-edge feed under the composer).
- **Buttons** — the GENERATE action is always Quanta `variant="marketingPrimary"`
  (the 3D lime CTA) with the credit cost INSIDE the button as
  `{label} {sparkles icon} {credits}` — the sparkle is the branded asset
  `@/assets/icon-sparkles-soft.svg?react` at 14px, and the credits number
  inherits the button label's font (never smaller/other). Quanta variant colors
  do NOT follow the names: `primary` = flat LIME, `secondary` = solid WHITE,
  `tertiary` = dark white/10 glass. Ordinary/nav actions use the dark
  `tertiary`/`ghost`; `secondary` (white) only where the real product shows a
  white button.
- **Quanta first** — `Button`, `Input`, `Textarea`, `Dropdown`, `Select`,
  `Modal`, `Tabs`, `Sidebar`, `Avatar`, `Badge`, `Tooltip`, `sonner` toasts,
  `Loader`, `Media`, `Grid`. Spacing = native Tailwind (`p-4`, `gap-3`);
  semantics = `q-` utilities (`bg-q-background-primary`,
  `text-q-body-md-regular`). Astryx only for components Quanta lacks
  (`references/astryx-fallback.md`).
- **Real end-to-end app** — Higgsfield auth (`references/auth.md`), server-side
  generation submit + poll, and the app's own product state in D1
  (saved/favorited, collections, presets, history). The signed-out state, auth
  guards, `/api/user`, cost preview, submit/poll routes, and D1 persistence are
  MANDATORY — see the checklist in `references/fnf-sdk.md`.

## Building the moving parts (studio / preset composer, feeds, results)

These recur across the layouts; build them from Quanta:

- **Prompt composer** (studio, and any prompt surface): a glass card —
  `bg-q-background-glass` + `backdrop-blur-2xl` + `rounded-[1.25rem]` — with an
  attachment-thumbnail strip on top (40px `rounded-lg` thumbs, quanta
  `CloseButton` to remove); an inner surface `bg-q-transparent-dark-30
  rounded-[1.125rem]` holding an auto-growing transparent textarea (Enter
  submits, never empty; real placeholders: image "Describe what you want to
  create...", video "Describe your scene - use @ to add characters &
  locations") over a settings-chips row (quanta `Chip` size="xs"
  color="neutral" — model / aspect / resolution / duration / batch, not
  full-width selects); and the tall GENERATE button filling the right edge
  (marketingPrimary, uppercase `text-q-accent-xs-bold` label stacked over the
  sparkle + credit cost). The studio's Image/Video mode switcher is a small
  separate glass rail card (stacked icon-over-caption buttons, selected mode on
  a white/10 fill), docked left of the composer.
- **Generation feed**: build from quanta pieces (CSS-columns masonry or `Grid`
  `cols="auto-fit"`, resize `minColWidth` rather than breakpoint ladders):
  image cards plus hover-play video cards (poster swaps to a muted looping
  video on hover), real empty-state copy, in-flight status cards (Loader +
  "In queue" / "In progress" Badge) while polling, failure cards with retry.
- **Results**: designed cards composed from quanta `Media` inside `Card` (or
  your feed cell) with a model/time meta strip — never a bare `<img>`. The
  helpers in `app/src/lib/higgsfield-generation-results.ts` map a Generation to
  its preview URL with the right precedence.
- **Polish** per `references/quanta-design.md` Layer 1: real empty/loading/error
  states, keyboard focus states, responsive down to mobile.
