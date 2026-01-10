/**
 * Page Transition Template
 *
 * A reusable page transition wrapper for Next.js App Router.
 * Provides smooth enter/exit animations between routes.
 *
 * Usage:
 * 1. Use in individual pages:
 *    ```tsx
 *    // app/about/page.tsx
 *    import { PageTransition } from "@/components/page-transition";
 *
 *    export default function AboutPage() {
 *      return (
 *        <PageTransition>
 *          <h1>About</h1>
 *          <p>Page content...</p>
 *        </PageTransition>
 *      );
 *    }
 *    ```
 *
 * 2. Or use in template.tsx for app-wide transitions:
 *    ```tsx
 *    // app/template.tsx
 *    import { PageTransitionProvider } from "@/components/page-transition";
 *
 *    export default function Template({ children }: { children: React.ReactNode }) {
 *      return <PageTransitionProvider>{children}</PageTransitionProvider>;
 *    }
 *    ```
 */

"use client";

import { ReactNode } from "react";
import { AnimatePresence, motion, Variants } from "framer-motion";
import { usePathname } from "next/navigation";

// ============================================================================
// Transition Variants - Choose or customize
// ============================================================================

/**
 * Fade transition - Simple opacity change
 */
export const fadeVariants: Variants = {
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

/**
 * Slide up transition - Content slides up while fading
 */
export const slideUpVariants: Variants = {
  initial: {
    opacity: 0,
    y: 20,
  },
  enter: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.4,
      ease: [0.25, 0.1, 0.25, 1],
    },
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: {
      duration: 0.3,
      ease: [0.25, 0.1, 0.25, 1],
    },
  },
};

/**
 * Scale transition - Content scales while fading
 */
export const scaleVariants: Variants = {
  initial: {
    opacity: 0,
    scale: 0.98,
  },
  enter: {
    opacity: 1,
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

/**
 * Slide with scale - Combined slide and scale effect
 */
export const slideScaleVariants: Variants = {
  initial: {
    opacity: 0,
    y: 30,
    scale: 0.98,
  },
  enter: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: [0.25, 0.1, 0.25, 1],
    },
  },
  exit: {
    opacity: 0,
    y: -20,
    scale: 0.98,
    transition: {
      duration: 0.3,
    },
  },
};

// ============================================================================
// Page Transition Component
// ============================================================================

interface PageTransitionProps {
  children: ReactNode;
  /**
   * Choose a preset variant or provide custom variants
   * @default "slideUp"
   */
  variant?: "fade" | "slideUp" | "scale" | "slideScale" | Variants;
  /**
   * Additional CSS classes for the motion wrapper
   */
  className?: string;
}

const variantMap = {
  fade: fadeVariants,
  slideUp: slideUpVariants,
  scale: scaleVariants,
  slideScale: slideScaleVariants,
};

/**
 * PageTransition - Wrap your page content for enter animations
 *
 * Note: This only animates enter. For exit animations with route changes,
 * use PageTransitionProvider in template.tsx
 */
export function PageTransition({
  children,
  variant = "slideUp",
  className,
}: PageTransitionProps) {
  const variants = typeof variant === "string" ? variantMap[variant] : variant;

  return (
    <motion.div
      variants={variants}
      initial="initial"
      animate="enter"
      exit="exit"
      className={className}
    >
      {children}
    </motion.div>
  );
}

// ============================================================================
// Page Transition Provider (for template.tsx)
// ============================================================================

interface PageTransitionProviderProps {
  children: ReactNode;
  /**
   * Choose a preset variant or provide custom variants
   * @default "slideUp"
   */
  variant?: "fade" | "slideUp" | "scale" | "slideScale" | Variants;
  /**
   * AnimatePresence mode
   * - "wait": Wait for exit before enter (recommended)
   * - "sync": Enter and exit simultaneously
   * - "popLayout": Maintain layout during exit
   * @default "wait"
   */
  mode?: "wait" | "sync" | "popLayout";
  /**
   * Additional CSS classes for the motion wrapper
   */
  className?: string;
}

/**
 * PageTransitionProvider - Use in template.tsx for app-wide transitions
 *
 * Provides AnimatePresence wrapper that enables exit animations
 * when navigating between routes.
 */
export function PageTransitionProvider({
  children,
  variant = "slideUp",
  mode = "wait",
  className,
}: PageTransitionProviderProps) {
  const pathname = usePathname();
  const variants = typeof variant === "string" ? variantMap[variant] : variant;

  return (
    <AnimatePresence mode={mode}>
      <motion.div
        key={pathname}
        variants={variants}
        initial="initial"
        animate="enter"
        exit="exit"
        className={className}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}

// ============================================================================
// Staggered Page Content
// ============================================================================

const staggerContainerVariants: Variants = {
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
  exit: {
    opacity: 0,
    transition: {
      duration: 0.2,
    },
  },
};

const staggerItemVariants: Variants = {
  initial: {
    opacity: 0,
    y: 20,
  },
  enter: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.4,
      ease: [0.25, 0.1, 0.25, 1],
    },
  },
};

interface StaggeredPageProps {
  children: ReactNode;
  className?: string;
}

/**
 * StaggeredPage - Page wrapper that staggers child animations
 *
 * Use motion.div with variants={staggerItemVariants} for children
 * to get staggered entrance effect.
 *
 * @example
 * ```tsx
 * <StaggeredPage>
 *   <motion.h1 variants={staggerItemVariants}>Title</motion.h1>
 *   <motion.p variants={staggerItemVariants}>Content</motion.p>
 *   <motion.div variants={staggerItemVariants}>More content</motion.div>
 * </StaggeredPage>
 * ```
 */
export function StaggeredPage({ children, className }: StaggeredPageProps) {
  return (
    <motion.div
      variants={staggerContainerVariants}
      initial="initial"
      animate="enter"
      exit="exit"
      className={className}
    >
      {children}
    </motion.div>
  );
}

// Export the item variants for use in children
export { staggerItemVariants };
