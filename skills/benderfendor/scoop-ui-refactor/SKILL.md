---
name: scoop-ui-refactor
description: Project-specific UI refactor workflow for the Scoop news platform in /home/bender/classwork/Thesis. Use when updating Scoop frontend layouts, globe UX, research workspace, and brand docs while preserving all features and enforcing a no-emoji policy across UI, logs, and docs.
---

# Scoop UI Refactor

## Scope
- Project root: `/home/bender/classwork/Thesis`
- Frontend: `frontend/app` and `frontend/components`

## Required outcomes
- Preserve all existing features (view modes, filters, research, modals).
- Increase density and reduce empty vertical space.
- Make globe selection flow clear and usable.
- Have grid view have snap scroll.
- Keep feed snap-scroll while preserving global header visibility.
- Remove emojis from UI, logs, and docs.

## Workflow

1) Review primary surfaces
- `frontend/app/page.tsx` (home layout)
- `frontend/components/globe-view.tsx` and `frontend/components/interactive-globe.tsx`
- `frontend/app/search/page.tsx` (research UI)
- `frontend/app/globals.css` (theme tokens)

2) Home layout refactor
- Compress the lead story into title + summary + action row.
- Move big narrative blocks into a compact summary card.
- Convert long "Contact" sections into short action rows.
- Keep view mode controls and filters visible and separated.

3) Globe view UX
- Add a clear country focus header.
- Show source count and top sources for the selected country.
- Keep a clear "reset" action visible.
- Remove all country flag emojis and any emoji usage.

4) Research workspace
- Use a top query bar.
- Add Brief and Flow modes (Flow shows reasoning steps in sequence).
- Move history or chat list into a sidebar.
- Ensure research visuals are distinct from the main feed styling.

5) No-emoji enforcement
- Use ripgrep to find emoji usage and remove it.
- Replace emoji with icons or labels.
- Apply to UI strings, logs, and docs.

6) Feed view snap-scroll (TikTok style)
- Use full-viewport sections (`h-screen`, `snap-start`) within a scroll container that has `snap-y snap-mandatory scroll-smooth`.
- Keep the global header visible by only calling `event.preventDefault()` on wheel/touch when a snap transition actually occurs; allow default scrolling when at the first/last item.
- Track `activeIndex` and an `isAnimating` guard; call `scrollIntoView` for the next/previous section and clear the guard after a short timeout.
- Support wheel, touch (deltaY threshold), and arrow keys; debounce small deltas to avoid accidental snaps.
- Retain modals, bookmarks, likes, and favorites behavior; do not regress existing feed actions.

## Checks
- Confirm view modes still switch correctly.
- Confirm modals and source filters still work.
- Confirm research results still render with embedded sources.
- Confirm feed snap-scroll still works on wheel, touch, and arrow keys, and that the header remains accessible at top-level scroll.

## Recent context
- Snap-scroll feed clips lower content if sections are fixed to `h-screen` without accounting for surrounding layout; prefer a flex parent (`flex-1 h-full min-h-0`) and per-section `h-full min-h-full snap-start` inside the scroll container so each article uses the available viewport height without hiding titles.
- Lint currently fails with pre-existing warnings/errors across the frontend (unused vars, hook ordering, explicit `any`); fixes are pending and not related to snap-scroll layout.
