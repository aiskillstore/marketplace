---
name: shadcn-framer
description: ShadCN UI + Framer Motion patterns.
---

# ShadCN + Framer Motion

## ShadCN Setup

```bash
pnpm dlx shadcn@latest init
pnpm dlx shadcn@latest add button card dialog
```

## Component Usage

```typescript
import { Button } from '@/components/ui/button';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from '@/components/ui/card';

export function UserCard({ user }: { user: User }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{user.name}</CardTitle>
        <CardDescription>{user.email}</CardDescription>
      </CardHeader>
      <CardContent>
        <p>{user.bio}</p>
      </CardContent>
      <CardFooter>
        <Button>View Profile</Button>
      </CardFooter>
    </Card>
  );
}
```

## Framer Motion Basics

```typescript
'use client';

import { motion } from 'framer-motion';

export function FadeIn({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {children}
    </motion.div>
  );
}
```

## Animated List

```typescript
'use client';

import { motion, AnimatePresence } from 'framer-motion';

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
};

const item = {
  hidden: { opacity: 0, x: -20 },
  show: { opacity: 1, x: 0 },
};

export function AnimatedList({ items }: { items: Item[] }) {
  return (
    <motion.ul variants={container} initial="hidden" animate="show">
      <AnimatePresence>
        {items.map((i) => (
          <motion.li
            key={i.id}
            variants={item}
            exit={{ opacity: 0, x: 20 }}
            layout
          >
            {i.name}
          </motion.li>
        ))}
      </AnimatePresence>
    </motion.ul>
  );
}
```

## Page Transitions

```typescript
// components/page-transition.tsx
'use client';

import { motion } from 'framer-motion';

export function PageTransition({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.2 }}
    >
      {children}
    </motion.div>
  );
}
```

## Animated Dialog

```typescript
'use client';

import { motion, AnimatePresence } from 'framer-motion';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

export function AnimatedDialog({
  open,
  onOpenChange,
  children,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  children: React.ReactNode;
}) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <AnimatePresence>
        {open && (
          <DialogContent asChild>
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.15 }}
            >
              {children}
            </motion.div>
          </DialogContent>
        )}
      </AnimatePresence>
    </Dialog>
  );
}
```

## Hover Effects

```typescript
'use client';

import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';

export function HoverCard({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -4 }}
      whileTap={{ scale: 0.98 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
    >
      <Card className="cursor-pointer">{children}</Card>
    </motion.div>
  );
}
```

## Loading Skeleton with Pulse

```typescript
'use client';

import { motion } from 'framer-motion';

export function Skeleton({ className }: { className?: string }) {
  return (
    <motion.div
      className={`bg-muted rounded ${className}`}
      animate={{ opacity: [0.5, 1, 0.5] }}
      transition={{ duration: 1.5, repeat: Infinity }}
    />
  );
}
```
