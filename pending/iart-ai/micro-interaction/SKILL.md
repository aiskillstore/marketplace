---
name: micro-interaction
description: This skill should be used when the user asks to "add a hover/press effect", "animate a toggle or switch", "build an animated like button", "make a toast/snackbar slide in", "animate a drawer or modal", "animate list reordering or add/remove", "do a shared-element layout transition", or "polish UI feedback". Covers UI motion with Framer Motion (motion/react) and modern CSS.
version: 0.1.0
---

# Micro-interactions (UI Motion)

Small, functional motion that makes an interface feel responsive and alive: hover/press/focus feedback, toggles, toasts, drawers, and list/layout animation. The goal is feedback and continuity, not decoration.

## When to use

- Hover/press/focus feedback; toggles, checkboxes, like/heart buttons
- Toasts/snackbars, drawers, modals, tooltips, accordions (enter/exit)
- List add/remove/reorder; shared-element ("magic move") layout transitions
- Loading → success → error state transitions

## Principles (apply to all of it)

- Duration: UI micro-interactions live in **100–250ms**. Anything over ~400ms feels laggy for a click response.
- Animate `transform` and `opacity` only — they are GPU-composited (no layout/paint). Avoid animating `width/height/top/left`; use `scale` or layout animation instead.
- Give **instant** press feedback: `scale: 0.96` on tap with a fast spring.
- Asymmetric timing: enter slightly slower (ease-out), exit faster (ease-in). Things should arrive gracefully and leave promptly.
- Respect `prefers-reduced-motion`: gate non-essential motion; keep opacity changes, drop large movement.
- Easing defaults: ease-out for entrances `cubic-bezier(0.16, 1, 0.3, 1)`; a tasteful overshoot is `cubic-bezier(0.34, 1.56, 0.64, 1)`; standard move `cubic-bezier(0.4, 0, 0.2, 1)`.

## Framer Motion (motion/react) essentials

As of v11+, the package is imported as `motion/react` (the `framer-motion` name still works).

### Gestures and springs

```jsx
import { motion } from "motion/react";

<motion.button
  whileHover={{ scale: 1.03 }}
  whileTap={{ scale: 0.96 }}
  whileFocus={{ boxShadow: "0 0 0 3px rgba(59,130,246,.5)" }}
  transition={{ type: "spring", stiffness: 400, damping: 30 }}
/>
```

Spring intuition: higher `stiffness` = faster; higher `damping` = less bounce. `stiffness: 400, damping: 30` is a snappy UI default. For visible bounce, lower damping (e.g. `damping: 12`).

### Enter / exit with AnimatePresence

Exit animations require `AnimatePresence` wrapping conditionally-rendered children, each with a stable `key`.

```jsx
import { AnimatePresence, motion } from "motion/react";

<AnimatePresence>
  {open && (
    <motion.div
      key="panel"
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 8 }}
      transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
    />
  )}
</AnimatePresence>
```

For toasts/lists, use `mode="popLayout"` so removed items don't hold space while exiting.

### Layout animation (the superpower)

`layout` automatically animates any layout change (position/size) using transforms — perfect for reordering, expanding cards, and grid<->list.

```jsx
<motion.li layout transition={{ type: "spring", stiffness: 500, damping: 40 }} />
```

Shared-element transition across components: give two elements the same `layoutId` and Framer Motion animates between them as one mounts and the other unmounts.

```jsx
{!open && <motion.div layoutId="card" onClick={() => setOpen(true)} />}
<AnimatePresence>
  {open && <motion.div layoutId="card" />} {/* "magic moves" from the source */}
</AnimatePresence>
```

Gotcha: a plain `layout` element distorts `border-radius` and text during scale. Add `layout` to direct children that should counter-scale, and prefer `borderRadius`/`boxShadow` as motion values, or use `layout="position"` to animate position only.

## Pure CSS path (no JS, including discrete properties)

Modern CSS can animate enter/exit and even `display` toggles without a library.

```css
.toast {
  transition: opacity 0.2s ease, transform 0.2s ease;
  /* allow animating to/from display:none and from initial render */
  transition-behavior: allow-discrete;
}
.toast[hidden] { display: none; }

/* animate FROM these values on first render / when entering */
@starting-style {
  .toast { opacity: 0; transform: translateY(8px); }
}
```

`@starting-style` defines the "before-open" values so an element animates in on first appearance; `transition-behavior: allow-discrete` lets `display` (and `overlay` for popovers/dialogs) participate so exit animations run before the element is removed. Baseline in Chrome/Edge/Safari; provide a no-animation fallback for older browsers.

Always include a reduced-motion guard:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

## State, not just decoration

Loading → success → error should be one continuous motion (e.g. a button morphs spinner → checkmark), not a jump cut. Keep the element mounted and animate between states so the eye tracks the same object.

## Deliver & verify (standalone HTML)

> **Packaged helper** (`scripts/`): `scripts/seek-shot.sh anim.html 0 1.5 3` freezes the `?t=N` harness and screenshots each moment; `scripts/contact-sheet.sh sheet.png frame-*.png` tiles them for one-glance review. See `scripts/README.md`.

For a self-contained interaction demo (toggle, like button, toast, drawer) the deliverable is **one HTML file that opens directly in a browser**. Pure-CSS interactions ship as-is; for a Framer Motion demo, load React + `motion` from CDN (`esm.sh`) into one inline module — no build step. One file is the right tier; don't reach for a bundler.

**Output contract:**
- One `.html` file: your markup plus either CSS transitions/`@starting-style` or an inline `<script type="module">` importing `motion` from CDN.
- A way to land on the **resolved end state** for a screenshot — interactions are state-driven, not time-driven, so freeze the state rather than a clock.

**Seek harness — pin a deterministic state.** A micro-interaction's "frames" are its states (idle / hover / pressed / open). `?state=open` applies the target state on load so a screenshot captures it settled:

```html
<script>
  const s = new URLSearchParams(location.search).get("state");
  if (s) document.documentElement.dataset.state = s;   // CSS keys off [data-state="open"]
  // Framer Motion: set the controlled prop from `s` (e.g. const [open]=useState(s==="open"))
  // For a CSS @keyframes loop instead, freeze it: el.style.animationDelay=(-N)+"s"; el.style.animationPlayState="paused";
  window.__ready = true;
</script>
```

**Verify loop — render → set state → screenshot → check:** open each meaningful state (`?state=idle`, `?state=hover`, `?state=open`), screenshot, and check **fidelity** (press feedback reads instant, exit runs before unmount) plus **artifacts** (`layout` distorting `border-radius`/text, toast holding space after exit, FOUC, jank). Any headless tool works:

```bash
npx playwright screenshot --wait-for-timeout=400 "file://$PWD/demo.html?state=open" open.png
```

**Before you finish:**
1. Opens standalone — no console errors, CDN React/`motion` (if used) resolves.
2. The `?state=` (or controlled-prop) freeze lands a deterministic, settled state.
3. Screenshotted across states — idle / active / open — matches the brief, no artifacts.
4. `prefers-reduced-motion` honored — large movement dropped, opacity/feedback kept.
5. Easing is intentional — enter ease-out, exit ease-in, durations in the 100–250ms band.

## Quick reference

| Need | Approach |
|------|----------|
| Press feedback | `whileTap={{ scale: 0.96 }}` spring 400/30 |
| Enter/exit | `AnimatePresence` + `initial/animate/exit` |
| Reorder / resize | `layout` prop (spring) |
| Magic move | shared `layoutId` |
| Toast stack | `AnimatePresence mode="popLayout"` |
| No-JS enter | `@starting-style` + transition |
| Animate to display:none | `transition-behavior: allow-discrete` |
| Accessibility | `prefers-reduced-motion` guard always |

## Reference files

- `references/framer-motion-recipes.md` — variants + stagger, `AnimatePresence` modes, `layout`/`layoutId` magic move, `Reorder` drag-to-sort, drag constraints, gesture composition, and `useReducedMotion`.
- `references/css-recipes.md` — `@starting-style`, `transition-behavior: allow-discrete`, popover/dialog exit animation, keyframe spinners/toggles, `@property` for animatable custom properties, and `prefers-reduced-motion` patterns.
