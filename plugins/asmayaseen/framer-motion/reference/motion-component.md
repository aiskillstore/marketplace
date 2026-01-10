# Motion Component Reference

The `motion` component is the core building block of Framer Motion.

## Basic Usage

```tsx
import { motion } from "framer-motion";

// Any HTML element can be animated
<motion.div />
<motion.span />
<motion.button />
<motion.ul />
<motion.li />
<motion.svg />
<motion.path />
<motion.img />
```

## Animation Props

### initial

The initial state before animation begins.

```tsx
<motion.div initial={{ opacity: 0, scale: 0.5 }}>
  Starts invisible and small
</motion.div>

// Can be false to disable initial animation
<motion.div initial={false} animate={{ x: 100 }}>
  Animates immediately without initial state
</motion.div>

// Can reference a variant
<motion.div initial="hidden" animate="visible" variants={variants}>
```

### animate

The target state to animate to.

```tsx
<motion.div animate={{ opacity: 1, x: 100 }}>
  Animates to these values
</motion.div>

// Can be a variant name
<motion.div animate="visible" variants={variants}>

// Can be controlled by state
<motion.div animate={{ x: isActive ? 100 : 0 }}>
```

### exit

The state to animate to when removed (requires `AnimatePresence`).

```tsx
import { AnimatePresence, motion } from "framer-motion";

<AnimatePresence>
  {isVisible && (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      I animate out when removed
    </motion.div>
  )}
</AnimatePresence>
```

### transition

Controls how the animation behaves.

```tsx
<motion.div
  animate={{ x: 100 }}
  transition={{
    duration: 0.5,       // Seconds
    delay: 0.2,          // Seconds
    ease: "easeInOut",   // Easing function
    repeat: Infinity,    // Number of repeats
    repeatType: "reverse", // "loop" | "reverse" | "mirror"
    repeatDelay: 0.5,    // Delay between repeats
  }}
>

// Spring animation
<motion.div
  animate={{ x: 100 }}
  transition={{
    type: "spring",
    stiffness: 300,      // Higher = snappier
    damping: 20,         // Higher = less bounce
    mass: 1,             // Higher = more momentum
  }}
>

// Spring with bounce
<motion.div
  animate={{ x: 100 }}
  transition={{
    type: "spring",
    bounce: 0.25,        // 0 = no bounce, 1 = max bounce
    duration: 0.6,       // Target duration
  }}
>
```

## Gesture Props

### whileHover

Animate while hovering.

```tsx
<motion.button
  whileHover={{ scale: 1.1, backgroundColor: "#f00" }}
>
  Hover me
</motion.button>

// With transition
<motion.button
  whileHover={{ scale: 1.1 }}
  transition={{ type: "spring", stiffness: 400 }}
>
```

### whileTap

Animate while pressing/clicking.

```tsx
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
>
  Click me
</motion.button>
```

### whileFocus

Animate while focused.

```tsx
<motion.input
  whileFocus={{ scale: 1.02, borderColor: "#3b82f6" }}
/>
```

### whileInView

Animate when element enters viewport.

```tsx
<motion.div
  initial={{ opacity: 0, y: 50 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true }}
>
  Animates when scrolled into view
</motion.div>
```

### whileDrag

Animate while dragging.

```tsx
<motion.div
  drag
  whileDrag={{ scale: 1.1, cursor: "grabbing" }}
>
  Drag me
</motion.div>
```

## Drag Props

### drag

Enable dragging.

```tsx
// Drag in any direction
<motion.div drag>Drag me</motion.div>

// Drag only on x-axis
<motion.div drag="x">Horizontal only</motion.div>

// Drag only on y-axis
<motion.div drag="y">Vertical only</motion.div>
```

### dragConstraints

Limit drag area.

```tsx
// Pixel constraints
<motion.div
  drag
  dragConstraints={{ top: -50, left: -50, right: 50, bottom: 50 }}
>

// Reference another element
const constraintsRef = useRef(null);

<div ref={constraintsRef} className="w-[500px] h-[500px]">
  <motion.div
    drag
    dragConstraints={constraintsRef}
  >
    Constrained within parent
  </motion.div>
</div>
```

### dragElastic

How far element can be dragged past constraints (0-1).

```tsx
<motion.div
  drag
  dragConstraints={{ left: 0, right: 0 }}
  dragElastic={0.1}
>
  Slightly elastic
</motion.div>
```

### dragSnapToOrigin

Return to original position when released.

```tsx
<motion.div drag dragSnapToOrigin>
  Snaps back when released
</motion.div>
```

## Layout Props

### layout

Enable layout animations.

```tsx
// Animate when layout changes
<motion.div layout>
  Content that may change size
</motion.div>

// Only animate position
<motion.div layout="position">

// Only animate size
<motion.div layout="size">
```

### layoutId

Enable shared element transitions.

```tsx
// In list view
<motion.div layoutId={`card-${id}`}>
  Card thumbnail
</motion.div>

// In detail view (same layoutId = smooth transition)
<motion.div layoutId={`card-${id}`}>
  Card expanded
</motion.div>
```

## Style Props

Transform properties are GPU-accelerated:

```tsx
<motion.div
  animate={{
    // Transform (GPU accelerated)
    x: 100,          // translateX
    y: 100,          // translateY
    z: 100,          // translateZ
    rotate: 45,      // rotate (degrees)
    rotateX: 45,     // rotate3d X
    rotateY: 45,     // rotate3d Y
    rotateZ: 45,     // rotate3d Z
    scale: 1.5,      // scale
    scaleX: 1.5,     // scaleX
    scaleY: 1.5,     // scaleY
    skew: 10,        // skew (degrees)
    skewX: 10,       // skewX
    skewY: 10,       // skewY

    // Opacity
    opacity: 0.5,

    // Colors
    backgroundColor: "#ff0000",
    color: "#ffffff",
    borderColor: "#000000",

    // Size (not GPU accelerated)
    width: 100,
    height: 100,

    // Other CSS properties
    borderRadius: 10,
    boxShadow: "0 10px 20px rgba(0,0,0,0.2)",
  }}
>
```

## Event Callbacks

```tsx
<motion.div
  // Animation events
  onAnimationStart={() => console.log("Animation started")}
  onAnimationComplete={() => console.log("Animation complete")}

  // Hover events
  onHoverStart={() => console.log("Hover start")}
  onHoverEnd={() => console.log("Hover end")}

  // Tap events
  onTap={() => console.log("Tapped")}
  onTapStart={() => console.log("Tap start")}
  onTapCancel={() => console.log("Tap cancelled")}

  // Drag events
  onDrag={(event, info) => console.log(info.point.x, info.point.y)}
  onDragStart={(event, info) => console.log("Drag started")}
  onDragEnd={(event, info) => console.log("Drag ended")}

  // Pan events
  onPan={(event, info) => console.log(info.delta.x)}
  onPanStart={(event, info) => console.log("Pan started")}
  onPanEnd={(event, info) => console.log("Pan ended")}

  // Viewport events
  onViewportEnter={() => console.log("Entered viewport")}
  onViewportLeave={() => console.log("Left viewport")}
>
```

## Viewport Options

```tsx
<motion.div
  whileInView={{ opacity: 1 }}
  viewport={{
    once: true,           // Only animate once
    amount: 0.5,          // Trigger when 50% visible (0-1)
    margin: "-100px",     // Adjust trigger point
    root: scrollRef,      // Custom scroll container
  }}
>
```

## Custom Components

```tsx
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";

// Create motion version of custom component
const MotionButton = motion(Button);

<MotionButton
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
>
  Animated Button
</MotionButton>
```

## SVG Animation

```tsx
<motion.svg viewBox="0 0 100 100">
  <motion.circle
    cx="50"
    cy="50"
    r="40"
    initial={{ pathLength: 0 }}
    animate={{ pathLength: 1 }}
    transition={{ duration: 2, ease: "easeInOut" }}
  />

  <motion.path
    d="M10 10 L90 90"
    initial={{ pathLength: 0 }}
    animate={{ pathLength: 1 }}
    transition={{ duration: 1 }}
  />
</motion.svg>
```
