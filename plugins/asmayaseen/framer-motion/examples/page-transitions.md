# Page Transition Examples

Smooth transitions between pages and routes.

## Basic Page Transition (Next.js App Router)

### Page Wrapper Component

```tsx
// components/page-transition.tsx
"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";

const pageVariants = {
  initial: {
    opacity: 0,
  },
  enter: {
    opacity: 1,
    transition: {
      duration: 0.3,
      ease: "easeOut",
    },
  },
  exit: {
    opacity: 0,
    transition: {
      duration: 0.2,
      ease: "easeIn",
    },
  },
};

interface PageTransitionProps {
  children: ReactNode;
}

export function PageTransition({ children }: PageTransitionProps) {
  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="enter"
      exit="exit"
    >
      {children}
    </motion.div>
  );
}

// Usage in page
// app/about/page.tsx
import { PageTransition } from "@/components/page-transition";

export default function AboutPage() {
  return (
    <PageTransition>
      <h1>About</h1>
      <p>Page content here...</p>
    </PageTransition>
  );
}
```

## Slide Transitions

### Slide from Right

```tsx
const slideRightVariants = {
  initial: {
    opacity: 0,
    x: 20,
  },
  enter: {
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.4,
      ease: [0.25, 0.1, 0.25, 1], // Custom cubic-bezier
    },
  },
  exit: {
    opacity: 0,
    x: -20,
    transition: {
      duration: 0.3,
    },
  },
};
```

### Slide from Bottom

```tsx
const slideUpVariants = {
  initial: {
    opacity: 0,
    y: 30,
  },
  enter: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.4,
      ease: "easeOut",
    },
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: {
      duration: 0.3,
    },
  },
};
```

### Slide with Scale

```tsx
const slideScaleVariants = {
  initial: {
    opacity: 0,
    y: 20,
    scale: 0.98,
  },
  enter: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.4,
      ease: [0.25, 0.1, 0.25, 1],
    },
  },
  exit: {
    opacity: 0,
    scale: 0.98,
    transition: {
      duration: 0.3,
    },
  },
};
```

## Staggered Page Content

```tsx
const pageVariants = {
  initial: {
    opacity: 0,
  },
  enter: {
    opacity: 1,
    transition: {
      duration: 0.3,
      when: "beforeChildren",
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  initial: {
    opacity: 0,
    y: 20,
  },
  enter: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.4,
    },
  },
};

export function StaggeredPage({ children }) {
  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="enter"
    >
      <motion.h1 variants={itemVariants}>Page Title</motion.h1>
      <motion.p variants={itemVariants}>Description</motion.p>
      <motion.div variants={itemVariants}>{children}</motion.div>
    </motion.div>
  );
}
```

## AnimatePresence for Route Changes

### Template Component (App Router)

```tsx
// app/template.tsx
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { usePathname } from "next/navigation";

export default function Template({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={pathname}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3 }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}
```

### Mode Options

```tsx
// mode="wait" - Wait for exit animation before entering
<AnimatePresence mode="wait">
  {/* Only one child visible at a time */}
</AnimatePresence>

// mode="sync" - Enter and exit simultaneously (default)
<AnimatePresence mode="sync">
  {/* Both visible during transition */}
</AnimatePresence>

// mode="popLayout" - For layout animations
<AnimatePresence mode="popLayout">
  {/* Maintains layout during exit */}
</AnimatePresence>
```

## Shared Element Transitions

```tsx
// components/card.tsx
"use client";

import { motion } from "framer-motion";
import Link from "next/link";

interface CardProps {
  id: string;
  title: string;
  image: string;
}

export function Card({ id, title, image }: CardProps) {
  return (
    <Link href={`/posts/${id}`}>
      <motion.div
        layoutId={`card-container-${id}`}
        className="rounded-xl overflow-hidden"
      >
        <motion.img
          layoutId={`card-image-${id}`}
          src={image}
          alt={title}
          className="w-full h-48 object-cover"
        />
        <motion.div layoutId={`card-content-${id}`} className="p-4">
          <motion.h3 layoutId={`card-title-${id}`} className="font-bold">
            {title}
          </motion.h3>
        </motion.div>
      </motion.div>
    </Link>
  );
}

// app/posts/[id]/page.tsx
"use client";

import { motion } from "framer-motion";

export default function PostPage({ params }: { params: { id: string } }) {
  const { id } = params;

  return (
    <article>
      <motion.div
        layoutId={`card-container-${id}`}
        className="max-w-3xl mx-auto"
      >
        <motion.img
          layoutId={`card-image-${id}`}
          src={`/images/${id}.jpg`}
          alt="Post image"
          className="w-full h-96 object-cover rounded-xl"
        />
        <motion.div layoutId={`card-content-${id}`} className="p-6">
          <motion.h1 layoutId={`card-title-${id}`} className="text-3xl font-bold">
            Post Title
          </motion.h1>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            Post content that fades in...
          </motion.p>
        </motion.div>
      </motion.div>
    </article>
  );
}
```

## Full Page Slide Transition

```tsx
const fullPageVariants = {
  initial: (direction: number) => ({
    x: direction > 0 ? "100%" : "-100%",
    opacity: 0,
  }),
  enter: {
    x: 0,
    opacity: 1,
    transition: {
      duration: 0.4,
      ease: [0.25, 0.1, 0.25, 1],
    },
  },
  exit: (direction: number) => ({
    x: direction > 0 ? "-100%" : "100%",
    opacity: 0,
    transition: {
      duration: 0.4,
      ease: [0.25, 0.1, 0.25, 1],
    },
  }),
};

export function FullPageTransition({ children, direction = 1 }) {
  return (
    <motion.div
      custom={direction}
      variants={fullPageVariants}
      initial="initial"
      animate="enter"
      exit="exit"
      className="fixed inset-0"
    >
      {children}
    </motion.div>
  );
}
```

## Overlay Page Transition

```tsx
const overlayVariants = {
  initial: {
    y: "100%",
    borderRadius: "100% 100% 0 0",
  },
  enter: {
    y: 0,
    borderRadius: "0% 0% 0 0",
    transition: {
      duration: 0.5,
      ease: [0.76, 0, 0.24, 1],
    },
  },
  exit: {
    y: "100%",
    borderRadius: "100% 100% 0 0",
    transition: {
      duration: 0.5,
      ease: [0.76, 0, 0.24, 1],
    },
  },
};

export function OverlayTransition({ children }) {
  return (
    <motion.div
      variants={overlayVariants}
      initial="initial"
      animate="enter"
      exit="exit"
      className="fixed inset-0 bg-background"
    >
      {children}
    </motion.div>
  );
}
```

## Page Transition with Loading

```tsx
"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import { usePathname } from "next/navigation";

export function PageWithLoader({ children }) {
  const [isLoading, setIsLoading] = useState(true);
  const pathname = usePathname();

  useEffect(() => {
    setIsLoading(true);
    const timer = setTimeout(() => setIsLoading(false), 500);
    return () => clearTimeout(timer);
  }, [pathname]);

  return (
    <AnimatePresence mode="wait">
      {isLoading ? (
        <motion.div
          key="loader"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 flex items-center justify-center"
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full"
          />
        </motion.div>
      ) : (
        <motion.div
          key={pathname}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
        >
          {children}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
```

## Best Practices

1. **Keep transitions short**: 300-500ms max for page transitions
2. **Use `mode="wait"`**: For cleaner transitions between pages
3. **Match enter/exit**: Exit should feel like reverse of enter
4. **Avoid layout shifts**: Use `position: fixed` during transitions
5. **Stagger content**: Animate child elements for richer feel
6. **Test on mobile**: Ensure smooth performance on lower-end devices
7. **Respect reduced motion**: Disable or simplify for `prefers-reduced-motion`
