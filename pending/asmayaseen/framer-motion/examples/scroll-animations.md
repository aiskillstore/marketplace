# Scroll Animation Examples

Scroll-triggered animations and parallax effects.

## Basic Scroll Reveal

```tsx
"use client";

import { motion } from "framer-motion";

export function ScrollReveal({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-100px" }}
      transition={{ duration: 0.5, ease: "easeOut" }}
    >
      {children}
    </motion.div>
  );
}

// Usage
<ScrollReveal>
  <Card>Content appears when scrolled into view</Card>
</ScrollReveal>
```

## Staggered Scroll Reveal

```tsx
"use client";

import { motion } from "framer-motion";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5 },
  },
};

export function StaggeredReveal({ items }: { items: any[] }) {
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-50px" }}
      className="grid grid-cols-3 gap-6"
    >
      {items.map((item) => (
        <motion.div key={item.id} variants={itemVariants}>
          {item.content}
        </motion.div>
      ))}
    </motion.div>
  );
}
```

## Scroll Progress Indicator

```tsx
"use client";

import { motion, useScroll, useSpring } from "framer-motion";

export function ScrollProgressBar() {
  const { scrollYProgress } = useScroll();
  const scaleX = useSpring(scrollYProgress, {
    stiffness: 100,
    damping: 30,
    restDelta: 0.001,
  });

  return (
    <motion.div
      style={{ scaleX }}
      className="fixed top-0 left-0 right-0 h-1 bg-primary origin-left z-50"
    />
  );
}
```

## Parallax Section

```tsx
"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";

export function ParallaxSection() {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  });

  const y = useTransform(scrollYProgress, [0, 1], [100, -100]);
  const opacity = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [0, 1, 1, 0]);

  return (
    <section ref={ref} className="h-screen relative overflow-hidden">
      <motion.div
        style={{ y, opacity }}
        className="absolute inset-0 flex items-center justify-center"
      >
        <h2 className="text-6xl font-bold">Parallax Text</h2>
      </motion.div>
    </section>
  );
}
```

## Parallax Background

```tsx
"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";

export function ParallaxHero() {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end start"],
  });

  const backgroundY = useTransform(scrollYProgress, [0, 1], ["0%", "50%"]);
  const textY = useTransform(scrollYProgress, [0, 1], ["0%", "100%"]);
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);

  return (
    <div ref={ref} className="relative h-screen overflow-hidden">
      {/* Background image with parallax */}
      <motion.div
        style={{ y: backgroundY }}
        className="absolute inset-0 bg-cover bg-center"
        style={{
          backgroundImage: "url(/hero-bg.jpg)",
          y: backgroundY,
        }}
      />

      {/* Content */}
      <motion.div
        style={{ y: textY, opacity }}
        className="relative z-10 flex h-full items-center justify-center"
      >
        <h1 className="text-6xl font-bold text-white">Hero Title</h1>
      </motion.div>
    </div>
  );
}
```

## Scroll-Linked Animation

```tsx
"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";

export function ScrollLinkedCard() {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "center center"],
  });

  const scale = useTransform(scrollYProgress, [0, 1], [0.8, 1]);
  const opacity = useTransform(scrollYProgress, [0, 1], [0.3, 1]);
  const rotateX = useTransform(scrollYProgress, [0, 1], [20, 0]);

  return (
    <motion.div
      ref={ref}
      style={{ scale, opacity, rotateX, transformPerspective: 1000 }}
      className="p-8 bg-card rounded-xl border"
    >
      Card that scales and rotates as you scroll
    </motion.div>
  );
}
```

## Horizontal Scroll Section

```tsx
"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";

export function HorizontalScrollSection() {
  const targetRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: targetRef,
  });

  const x = useTransform(scrollYProgress, [0, 1], ["0%", "-75%"]);

  return (
    <section ref={targetRef} className="relative h-[300vh]">
      <div className="sticky top-0 h-screen flex items-center overflow-hidden">
        <motion.div style={{ x }} className="flex gap-8">
          {[1, 2, 3, 4].map((item) => (
            <div
              key={item}
              className="w-[80vw] h-[60vh] shrink-0 bg-card rounded-xl border flex items-center justify-center"
            >
              <span className="text-4xl font-bold">Slide {item}</span>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
```

## Reveal on Scroll with Different Directions

```tsx
"use client";

import { motion } from "framer-motion";

type Direction = "up" | "down" | "left" | "right";

const directionVariants = {
  up: { y: 50 },
  down: { y: -50 },
  left: { x: 50 },
  right: { x: -50 },
};

export function DirectionalReveal({
  children,
  direction = "up",
}: {
  children: React.ReactNode;
  direction?: Direction;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, ...directionVariants[direction] }}
      whileInView={{ opacity: 1, x: 0, y: 0 }}
      viewport={{ once: true, margin: "-100px" }}
      transition={{ duration: 0.6, ease: "easeOut" }}
    >
      {children}
    </motion.div>
  );
}

// Usage
<DirectionalReveal direction="left">
  <Card>Slides in from the left</Card>
</DirectionalReveal>
```

## Number Counter on Scroll

```tsx
"use client";

import { useRef, useEffect, useState } from "react";
import { motion, useInView, animate } from "framer-motion";

export function CountUp({
  target,
  duration = 2,
}: {
  target: number;
  duration?: number;
}) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (isInView) {
      const controls = animate(0, target, {
        duration,
        onUpdate: (value) => setCount(Math.floor(value)),
      });
      return () => controls.stop();
    }
  }, [isInView, target, duration]);

  return (
    <motion.span
      ref={ref}
      initial={{ opacity: 0 }}
      animate={isInView ? { opacity: 1 } : {}}
      className="text-5xl font-bold"
    >
      {count.toLocaleString()}
    </motion.span>
  );
}
```

## Scroll Snap with Animations

```tsx
"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";

const sections = [
  { id: 1, title: "Section One", color: "bg-blue-500" },
  { id: 2, title: "Section Two", color: "bg-green-500" },
  { id: 3, title: "Section Three", color: "bg-purple-500" },
];

export function ScrollSnapSections() {
  return (
    <div className="h-screen overflow-y-scroll snap-y snap-mandatory">
      {sections.map((section) => (
        <ScrollSnapSection key={section.id} {...section} />
      ))}
    </div>
  );
}

function ScrollSnapSection({
  title,
  color,
}: {
  title: string;
  color: string;
}) {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  });

  const scale = useTransform(scrollYProgress, [0, 0.5, 1], [0.8, 1, 0.8]);
  const opacity = useTransform(scrollYProgress, [0, 0.5, 1], [0.3, 1, 0.3]);

  return (
    <section
      ref={ref}
      className={`h-screen snap-start flex items-center justify-center ${color}`}
    >
      <motion.h2 style={{ scale, opacity }} className="text-6xl font-bold text-white">
        {title}
      </motion.h2>
    </section>
  );
}
```

## Scroll-Triggered Path Animation

```tsx
"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";

export function ScrollPathAnimation() {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  });

  const pathLength = useTransform(scrollYProgress, [0, 0.5], [0, 1]);

  return (
    <div ref={ref} className="h-[200vh] flex items-center justify-center">
      <svg width="200" height="200" viewBox="0 0 100 100" className="stroke-primary">
        <motion.circle
          cx="50"
          cy="50"
          r="40"
          fill="none"
          strokeWidth="4"
          style={{ pathLength }}
        />
      </svg>
    </div>
  );
}
```

## Best Practices

1. **Use `viewport={{ once: true }}`**: Prevents re-triggering on scroll back
2. **Add margin to viewport**: Trigger slightly before element is visible
3. **Use `useSpring` for progress**: Smoother progress bar animations
4. **Keep parallax subtle**: Small movements (50-100px) feel more natural
5. **Test performance**: Heavy scroll animations can impact mobile performance
6. **Consider reduced motion**: Disable parallax for `prefers-reduced-motion`
