# Framer Motion Recipes

Import from `motion/react` (v11+). All examples are React + Framer Motion.

```jsx
import { motion, AnimatePresence, Reorder, useReducedMotion, useDragControls } from "motion/react";
```

## Variants and staggered children

Variants are named animation states a parent can propagate to children, enabling orchestration like staggering without per-child timing math.

```jsx
const list = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.06, delayChildren: 0.1 },
  },
};
const item = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 500, damping: 30 } },
};

<motion.ul variants={list} initial="hidden" animate="show">
  {items.map((t) => (
    <motion.li key={t.id} variants={item}>{t.label}</motion.li>
  ))}
</motion.ul>
```

`staggerDirection: -1` staggers from last to first. `when: "beforeChildren"` / `"afterChildren"` sequences parent vs children.

## AnimatePresence modes

```jsx
<AnimatePresence mode="wait">   {/* outgoing finishes before incoming starts (route/tab switches) */}
  <motion.div key={tab} initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}} />
</AnimatePresence>
```

Modes:
- default (`"sync"`) — incoming and outgoing animate simultaneously.
- `"wait"` — finish exit before enter (single-element swaps like tabs/pages).
- `"popLayout"` — exiting items are popped from layout flow so siblings re-flow immediately (toast stacks, removing list items). Children must be capable of `layout`.

Require a unique, stable `key` on each child. To run exit on initial mount too, that is not needed; to suppress enter animation on first render set `<AnimatePresence initial={false}>`.

## Toast stack (popLayout + layout)

```jsx
function Toasts({ toasts }) {
  return (
    <div className="toast-region">
      <AnimatePresence mode="popLayout">
        {toasts.map((t) => (
          <motion.div
            key={t.id}
            layout
            initial={{ opacity: 0, y: 24, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9, transition: { duration: 0.15 } }}
            transition={{ type: "spring", stiffness: 500, damping: 40 }}
          >
            {t.message}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
```

`layout` makes remaining toasts slide up smoothly when one is dismissed.

## Magic-move / shared-element layout

```jsx
function Gallery() {
  const [active, setActive] = useState(null);
  return (
    <>
      <div className="grid">
        {photos.map((p) => (
          <motion.img key={p.id} layoutId={`photo-${p.id}`} src={p.thumb}
            onClick={() => setActive(p)} />
        ))}
      </div>
      <AnimatePresence>
        {active && (
          <motion.div className="backdrop" onClick={() => setActive(null)}
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <motion.img layoutId={`photo-${active.id}`} src={active.full} />
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
```

Matching `layoutId` makes the thumbnail visually fly to the lightbox and back.

## Drag-to-reorder list

`Reorder` handles pointer drag, axis locking, and live reordering with layout animation built in.

```jsx
function SortableList({ items, setItems }) {
  return (
    <Reorder.Group axis="y" values={items} onReorder={setItems}>
      {items.map((item) => (
        <Reorder.Item key={item} value={item}
          whileDrag={{ scale: 1.03, boxShadow: "0 8px 24px rgba(0,0,0,.18)" }}>
          {item}
        </Reorder.Item>
      ))}
    </Reorder.Group>
  );
}
```

For a dedicated drag handle, use `useDragControls`:

```jsx
const controls = useDragControls();
<Reorder.Item value={item} dragListener={false} dragControls={controls}>
  <span className="handle" onPointerDown={(e) => controls.start(e)}>⠿</span>
  {item.label}
</Reorder.Item>
```

## Drag with constraints and elastic

```jsx
const ref = useRef(null);
<div ref={ref} className="bounds">
  <motion.div drag dragConstraints={ref} dragElastic={0.2}
    dragTransition={{ bounceStiffness: 600, bounceDamping: 20 }} />
</div>
```

`dragElastic` (0–1) controls how far past constraints it can be pulled; `dragSnapToOrigin` returns it on release.

## Gesture composition (like button)

```jsx
function Like() {
  const [liked, setLiked] = useState(false);
  return (
    <motion.button onClick={() => setLiked((v) => !v)} whileTap={{ scale: 0.85 }}>
      <motion.span
        animate={liked ? { scale: [1, 1.4, 1], color: "#ef4444" } : { scale: 1, color: "#9ca3af" }}
        transition={{ duration: 0.35, ease: "easeOut" }}
      >♥</motion.span>
    </motion.button>
  );
}
```

Arrays of values (`scale: [1, 1.4, 1]`) are keyframes; control their spacing with `times: [0, 0.6, 1]`.

## Respecting reduced motion

```jsx
function Panel() {
  const reduce = useReducedMotion();
  return (
    <motion.div
      initial={reduce ? false : { opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
    />
  );
}
```

Wrap an app in `<MotionConfig reducedMotion="user">` to globally strip transform/layout animations for users who prefer reduced motion while keeping opacity.

## Performance notes

- Prefer `transform`/`opacity`; Framer Motion already uses transforms for `x/y/scale/rotate`.
- For frequently-updated values (cursor follow, scroll), use `useMotionValue` + `useSpring` instead of React state to avoid re-renders.
- `layout` is powerful but measure-heavy; avoid putting it on hundreds of simultaneously-animating nodes.

---
Tune the timing and easing and a micro-interaction feels effortless. Built by **[iart.ai](https://iart.ai/?utm_source=github&utm_medium=readme&utm_campaign=web-animation-skills&utm_content=skill_footer&utm_term=micro-interaction)** — the AI motion agent for editable, on-brand motion graphics.
