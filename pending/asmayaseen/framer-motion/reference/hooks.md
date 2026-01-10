# Animation Hooks Reference

Framer Motion provides hooks for advanced animation control.

## useAnimation

Programmatic control over animations.

```tsx
import { motion, useAnimation } from "framer-motion";

function Component() {
  const controls = useAnimation();

  async function sequence() {
    await controls.start({ x: 100 });
    await controls.start({ y: 100 });
    await controls.start({ x: 0, y: 0 });
  }

  return (
    <>
      <button onClick={sequence}>Start sequence</button>
      <motion.div animate={controls}>
        Controlled animation
      </motion.div>
    </>
  );
}
```

### Control Methods

```tsx
const controls = useAnimation();

// Start animation
controls.start({ opacity: 1, x: 100 });

// Start with variant
controls.start("visible");

// Start with transition
controls.start({ x: 100 }, { duration: 0.5 });

// Stop animation
controls.stop();

// Set values immediately (no animation)
controls.set({ x: 0, opacity: 0 });
```

### Orchestrating Multiple Elements

```tsx
function Component() {
  const boxControls = useAnimation();
  const circleControls = useAnimation();

  async function playSequence() {
    await boxControls.start({ x: 100 });
    await circleControls.start({ scale: 1.5 });
    await Promise.all([
      boxControls.start({ x: 0 }),
      circleControls.start({ scale: 1 }),
    ]);
  }

  return (
    <>
      <motion.div animate={boxControls}>Box</motion.div>
      <motion.div animate={circleControls}>Circle</motion.div>
      <button onClick={playSequence}>Play</button>
    </>
  );
}
```

## useMotionValue

Create reactive values for animations.

```tsx
import { motion, useMotionValue } from "framer-motion";

function Component() {
  const x = useMotionValue(0);

  return (
    <motion.div
      style={{ x }}
      drag="x"
      onDrag={(event, info) => {
        console.log(x.get()); // Get current value
      }}
    >
      Drag me
    </motion.div>
  );
}
```

### MotionValue Methods

```tsx
const x = useMotionValue(0);

// Get current value
const current = x.get();

// Set value (no animation)
x.set(100);

// Subscribe to changes
const unsubscribe = x.on("change", (latest) => {
  console.log("x changed to", latest);
});

// Jump to value (skips animation)
x.jump(100);

// Check if animating
const isAnimating = x.isAnimating();

// Get velocity
const velocity = x.getVelocity();
```

## useTransform

Transform one motion value into another.

```tsx
import { motion, useMotionValue, useTransform } from "framer-motion";

function Component() {
  const x = useMotionValue(0);

  // Transform x (0-200) to opacity (1-0)
  const opacity = useTransform(x, [0, 200], [1, 0]);

  // Transform x to rotation
  const rotate = useTransform(x, [0, 200], [0, 180]);

  // Transform x to scale
  const scale = useTransform(x, [-100, 0, 100], [0.5, 1, 1.5]);

  return (
    <motion.div
      drag="x"
      style={{ x, opacity, rotate, scale }}
    >
      Drag me
    </motion.div>
  );
}
```

### Chained Transforms

```tsx
const x = useMotionValue(0);
const xRange = useTransform(x, [0, 100], [0, 1]);
const opacity = useTransform(xRange, [0, 0.5, 1], [0, 1, 0]);
```

### Custom Transform Function

```tsx
const x = useMotionValue(0);

const background = useTransform(x, (value) => {
  return value > 0 ? "#22c55e" : "#ef4444";
});
```

## useSpring

Create spring-animated motion values.

```tsx
import { motion, useSpring, useMotionValue } from "framer-motion";

function Component() {
  const x = useMotionValue(0);
  const springX = useSpring(x, { stiffness: 300, damping: 30 });

  return (
    <motion.div
      style={{ x: springX }}
      onMouseMove={(e) => x.set(e.clientX)}
    >
      Follows cursor with spring
    </motion.div>
  );
}
```

### Spring Options

```tsx
const springValue = useSpring(motionValue, {
  stiffness: 300,  // Higher = snappier
  damping: 30,     // Higher = less bounce
  mass: 1,         // Higher = more momentum
  velocity: 0,     // Initial velocity
  restSpeed: 0.01, // Minimum speed to consider "at rest"
  restDelta: 0.01, // Minimum distance to consider "at rest"
});
```

## useScroll

Track scroll progress.

```tsx
import { motion, useScroll, useTransform } from "framer-motion";

function ScrollProgress() {
  const { scrollYProgress } = useScroll();

  return (
    <motion.div
      style={{ scaleX: scrollYProgress }}
      className="fixed top-0 left-0 right-0 h-1 bg-primary origin-left"
    />
  );
}
```

### Scroll Container

```tsx
function Component() {
  const containerRef = useRef(null);
  const { scrollYProgress } = useScroll({
    container: containerRef,
  });

  return (
    <div ref={containerRef} className="h-[400px] overflow-y-scroll">
      <motion.div style={{ opacity: scrollYProgress }}>
        Fades in as you scroll
      </motion.div>
    </div>
  );
}
```

### Scroll Target Element

```tsx
function Component() {
  const targetRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: targetRef,
    offset: ["start end", "end start"], // When to start/end tracking
  });

  return (
    <motion.div
      ref={targetRef}
      style={{ opacity: scrollYProgress }}
    >
      Animates as it passes through viewport
    </motion.div>
  );
}
```

### Scroll Offset Options

```tsx
const { scrollYProgress } = useScroll({
  target: ref,
  offset: [
    "start end",    // When target's start reaches viewport's end
    "end start",    // When target's end reaches viewport's start
  ],
});

// Other offset values:
// "start", "center", "end" - element positions
// Numbers: pixels (100) or percentages (0.5)
```

## useVelocity

Get velocity of a motion value.

```tsx
import { useMotionValue, useVelocity } from "framer-motion";

function Component() {
  const x = useMotionValue(0);
  const xVelocity = useVelocity(x);

  return (
    <motion.div
      drag="x"
      style={{ x }}
      onDragEnd={() => {
        console.log("Release velocity:", xVelocity.get());
      }}
    >
      Drag me
    </motion.div>
  );
}
```

## useInView

Detect when element enters viewport.

```tsx
import { useInView } from "framer-motion";

function Component() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 50 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.5 }}
    >
      Animates when scrolled into view
    </motion.div>
  );
}
```

### InView Options

```tsx
const isInView = useInView(ref, {
  once: true,           // Only trigger once
  amount: 0.5,          // Trigger when 50% visible
  margin: "-100px",     // Adjust trigger point
  root: scrollContainerRef,  // Custom scroll container
});
```

## useReducedMotion

Detect reduced motion preference.

```tsx
import { useReducedMotion } from "framer-motion";

function Component() {
  const prefersReducedMotion = useReducedMotion();

  return (
    <motion.div
      animate={{ x: 100 }}
      transition={{
        duration: prefersReducedMotion ? 0 : 0.5,
      }}
    >
      Respects motion preference
    </motion.div>
  );
}
```

## useDragControls

Create custom drag handles.

```tsx
import { motion, useDragControls } from "framer-motion";

function DraggableCard() {
  const dragControls = useDragControls();

  return (
    <motion.div
      drag
      dragControls={dragControls}
      dragListener={false}  // Disable drag on whole element
    >
      <div
        onPointerDown={(e) => dragControls.start(e)}
        className="cursor-grab"
      >
        Drag Handle
      </div>
      <div>Card Content (not draggable)</div>
    </motion.div>
  );
}
```

## useAnimationFrame

Run code every animation frame.

```tsx
import { useAnimationFrame } from "framer-motion";

function Component() {
  const ref = useRef(null);

  useAnimationFrame((time, delta) => {
    // time: total time elapsed (ms)
    // delta: time since last frame (ms)

    if (ref.current) {
      ref.current.style.transform = `rotate(${time / 10}deg)`;
    }
  });

  return <div ref={ref}>Spinning</div>;
}
```

## Combining Hooks

```tsx
function ParallaxSection() {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  });

  const y = useTransform(scrollYProgress, [0, 1], [100, -100]);
  const opacity = useTransform(scrollYProgress, [0, 0.5, 1], [0, 1, 0]);

  return (
    <motion.section
      ref={ref}
      style={{ y, opacity }}
      className="h-screen"
    >
      Parallax content
    </motion.section>
  );
}
```
