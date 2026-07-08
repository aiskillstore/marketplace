# app-layouts — the standard Higgsfield app layouts (`type: "app"` builds ONLY)

A `type: "app"` product must look and feel like a Higgsfield product, so you do
NOT invent app chrome. The template ships the standard layouts and the UI they
are built from as **real code** — you build by copying/composing those, not by
reproducing a screenshot.

Two hard rules, no exceptions:

1. **Start from one of the three shipped layouts — Studio, Preset, or App
   detail.** Match the app to whichever is closest (`app/src/layouts/studio.tsx`,
   `preset.tsx`, or `app-detail.tsx`) and adapt it; an unusual request still maps
   to the nearest one — adapt within it, never invent a different app shell. A
   fully custom layout is fine only when the user asks for something none covers.
2. **Read the code, then build.** After `higgsfield website repo-access` + clone, read
   `app/src/layouts/AGENTS.md` (the scaffold catalog — anatomy + rules for each)
   and open the layout/component files you'll use. They are the source of truth
   for structure; build from them, not from memory.

Everything is code in the repo — there are no external reference images to open.

## The three layouts (`app/src/layouts/`)

The template ships **three** ready-made layout screens as real code —
**prefer one of them**. Copy the closest one into your route (or compose it from
a route file) and adapt freely. See `app/src/layouts/AGENTS.md` for each one's
anatomy.

| Layout | When to pick |
|---|---|
| `studio.tsx` (`StudioTemplate`) | A full creative workspace: projects-first `Sidebar` + hero + a floating prompt dock (`@/components/prompt-box` — mode toggle, inline setting pills, lime GENERATE) over an edge-to-edge generations feed. The richest shell — for multi-project generation tools. |
| `preset.tsx` (`PresetTemplate`) | A **preset app**: a persistent left creation rail (`@/components/composer` + `@/components/setting-trigger` rows + costed Generate) beside a browsable preset gallery (Presets/History/How-it-works tabs + search + media grid). |
| `app-detail.tsx` (`AppDetailTemplate`) | A single app's **public landing page**: a centered `max-w-7xl` scroll page with a two-column generator hero (`@/components/dropzone` inputs on the left, a large `Media` preview on the right, costed Generate) and a "how it works in 3 steps" explainer. For a marketing/detail page around one tool, not a full workspace. |

Map any request to the closest of the three; only build a fully custom shell
when the user asks for something none covers.

## Reusable UI components (`app/src/components/`)

Build the moving parts from these instead of hand-rolling them (they compose
Quanta and match the product):

- `prompt-box/` — the studio prompt dock (caption, textarea, inline setting
  pills that open as `Select` dropdowns, a tall marketing-primary Generate).
- `composer/` — a simpler prompt-input pane (caption + borderless textarea +
  footer action pills) for form-style builders.
- `setting-trigger/` — a compact labelled picker row (label + current value +
  chevron) for builder panels; compose with Modal/Vault/Dropdown/Select.
- `generation-card/` — a single generation-result tile (`ready` shows the
  cover; `generating` shows a pulsing brand-glow placeholder + status pill).
- `history-grid.tsx` — a generation feed/grid of `generation-card`s.
- `media-card/` — a framed gallery/cover tile (bordered frame + bottom title +
  optional glass action chip).
- `asset-library.tsx` — the assets modal (folder tree + tabbed media grid) for
  attach/reference flows.
- `generation-detail.tsx` — the full-view lightbox for a single generation
  (stage + info panel + actions).
- `template-picker.tsx` — the full-screen template/preset picker modal.
- `template-modal/` — a compact modal for picking a template/preset option.
- `dropzone/` — a file-drop upload area (`Dropzone`) + its selected-file
  preview (`DropzonePreview`), for the app-detail input hero.

Anything these don't cover, build your own component from Quanta primitives
(`references/quanta-design.md` rule 5) — never a third-party UI library.

## Invariants (every layout)

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
  `Loader`, `Media`, `Grid`, plus the app components above. Spacing = native
  Tailwind (`p-4`, `gap-3`); semantics = `q-` utilities
  (`bg-q-background-primary`, `text-q-body-md-regular`). For anything Quanta
  lacks, build your own component from Quanta primitives — never a third-party
  UI library.
- **Real end-to-end app** — Higgsfield auth (`references/auth.md`), server-side
  generation submit + poll, and the app's own product state in D1
  (saved/favorited, collections, presets, history). The signed-out state, auth
  guards, `/api/user`, cost preview, submit/poll routes, and D1 persistence are
  MANDATORY — see the checklist in `references/fnf-sdk.md`.
