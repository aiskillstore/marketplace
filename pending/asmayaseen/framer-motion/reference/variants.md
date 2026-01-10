# Variants Reference

Variants are predefined animation states that simplify complex animations.

## Basic Variants

```tsx
const variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
};

<motion.div
  variants={variants}
  initial="hidden"
  animate="visible"
>
  Fades in
</motion.div>
```

## Multiple Properties

```tsx
const variants = {
  hidden: {
    opacity: 0,
    y: 20,
    scale: 0.95,
  },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
  },
};

<motion.div variants={variants} initial="hidden" animate="visible">
  Fades in, slides up, and scales
</motion.div>
```

## Transitions in Variants

```tsx
const variants = {
  hidden: {
    opacity: 0,
    y: 20,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
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

## Parent-Child Orchestration

Children automatically inherit variants from parents:

```tsx
const container = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      when: "beforeChildren",  // Animate parent first
      staggerChildren: 0.1,    // Delay between children
      delayChildren: 0.3,      // Delay before first child
    },
  },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

<motion.ul variants={container} initial="hidden" animate="visible">
  <motion.li variants={item}>Item 1</motion.li>
  <motion.li variants={item}>Item 2</motion.li>
  <motion.li variants={item}>Item 3</motion.li>
</motion.ul>
```

## Stagger Options

```tsx
const container = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      staggerDirection: 1,  // 1 = forward, -1 = reverse
      delayChildren: 0.2,
    },
  },
  exit: {
    opacity: 0,
    transition: {
      staggerChildren: 0.05,
      staggerDirection: -1,  // Reverse stagger on exit
      when: "afterChildren", // Wait for children to exit
    },
  },
};
```

## When Property

```tsx
const variants = {
  visible: {
    opacity: 1,
    transition: {
      when: "beforeChildren",  // Parent animates first
      // or
      when: "afterChildren",   // Children animate first
    },
  },
};
```

## Dynamic Variants

Pass custom values to variants:

```tsx
const variants = {
  hidden: { opacity: 0 },
  visible: (custom: number) => ({
    opacity: 1,
    transition: { delay: custom * 0.1 },
  }),
};

<motion.ul initial="hidden" animate="visible">
  {items.map((item, i) => (
    <motion.li
      key={item.id}
      variants={variants}
      custom={i}  // Pass index to variant
    >
      {item.name}
    </motion.li>
  ))}
</motion.ul>
```

## Hover/Tap Variants

```tsx
const buttonVariants = {
  initial: {
    scale: 1,
    backgroundColor: "#3b82f6",
  },
  hover: {
    scale: 1.05,
    backgroundColor: "#2563eb",
  },
  tap: {
    scale: 0.95,
  },
};

<motion.button
  variants={buttonVariants}
  initial="initial"
  whileHover="hover"
  whileTap="tap"
>
  Click me
</motion.button>
```

## Complex Card Example

```tsx
const cardVariants = {
  hidden: {
    opacity: 0,
    y: 20,
    scale: 0.95,
  },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.4,
      ease: "easeOut",
      when: "beforeChildren",
      staggerChildren: 0.1,
    },
  },
  hover: {
    y: -5,
    boxShadow: "0 10px 30px -10px rgba(0,0,0,0.2)",
    transition: {
      duration: 0.2,
    },
  },
};

const contentVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
};

<motion.div
  variants={cardVariants}
  initial="hidden"
  animate="visible"
  whileHover="hover"
>
  <motion.h3 variants={contentVariants}>Title</motion.h3>
  <motion.p variants={contentVariants}>Description</motion.p>
  <motion.button variants={contentVariants}>Action</motion.button>
</motion.div>
```

## List Animation

```tsx
const listVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.07,
      delayChildren: 0.2,
    },
  },
  exit: {
    opacity: 0,
    transition: {
      staggerChildren: 0.05,
      staggerDirection: -1,
    },
  },
};

const itemVariants = {
  hidden: {
    y: 20,
    opacity: 0,
  },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      type: "spring",
      stiffness: 300,
      damping: 24,
    },
  },
  exit: {
    y: -20,
    opacity: 0,
  },
};

<AnimatePresence mode="popLayout">
  <motion.ul
    variants={listVariants}
    initial="hidden"
    animate="visible"
    exit="exit"
  >
    {items.map((item) => (
      <motion.li
        key={item.id}
        variants={itemVariants}
        layout
      >
        {item.name}
      </motion.li>
    ))}
  </motion.ul>
</AnimatePresence>
```

## Page Transition Variants

```tsx
const pageVariants = {
  initial: {
    opacity: 0,
    x: -20,
  },
  enter: {
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.4,
      ease: "easeOut",
    },
  },
  exit: {
    opacity: 0,
    x: 20,
    transition: {
      duration: 0.3,
      ease: "easeIn",
    },
  },
};

// In your page component
<motion.div
  variants={pageVariants}
  initial="initial"
  animate="enter"
  exit="exit"
>
  Page content
</motion.div>
```

## Sidebar Variants

```tsx
const sidebarVariants = {
  open: {
    x: 0,
    transition: {
      type: "spring",
      stiffness: 300,
      damping: 30,
      when: "beforeChildren",
      staggerChildren: 0.05,
    },
  },
  closed: {
    x: "-100%",
    transition: {
      type: "spring",
      stiffness: 400,
      damping: 40,
      when: "afterChildren",
      staggerChildren: 0.05,
      staggerDirection: -1,
    },
  },
};

const linkVariants = {
  open: {
    opacity: 1,
    x: 0,
  },
  closed: {
    opacity: 0,
    x: -20,
  },
};

<motion.aside
  variants={sidebarVariants}
  initial="closed"
  animate={isOpen ? "open" : "closed"}
>
  <nav>
    {links.map((link) => (
      <motion.a key={link.href} href={link.href} variants={linkVariants}>
        {link.label}
      </motion.a>
    ))}
  </nav>
</motion.aside>
```

## Best Practices

1. **Use semantic variant names**: `hidden`/`visible`, `open`/`closed`, `enter`/`exit`
2. **Define transitions in variants**: Keeps animation logic together
3. **Orchestrate with parent**: Use `staggerChildren`, `delayChildren`, `when`
4. **Children inherit variant names**: No need to set `initial`/`animate` on children
5. **Use `custom` for dynamic values**: Index-based delays, direction, etc.
