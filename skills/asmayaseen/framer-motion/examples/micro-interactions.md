# Micro-interaction Examples

Small, delightful animations that enhance UI interactions.

## Button Interactions

### Basic Button

```tsx
<motion.button
  whileHover={{ scale: 1.02 }}
  whileTap={{ scale: 0.98 }}
  transition={{ type: "spring", stiffness: 400, damping: 17 }}
  className="px-6 py-3 bg-primary text-primary-foreground rounded-lg"
>
  Click me
</motion.button>
```

### Button with Icon Animation

```tsx
"use client";

import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";

export function ButtonWithArrow() {
  return (
    <motion.button
      whileHover="hover"
      className="group flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-lg"
    >
      <span>Continue</span>
      <motion.span
        variants={{
          hover: { x: 5 },
        }}
        transition={{ type: "spring", stiffness: 400, damping: 17 }}
      >
        <ArrowRight className="h-4 w-4" />
      </motion.span>
    </motion.button>
  );
}
```

### Loading Button

```tsx
"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Loader2, Check } from "lucide-react";

type ButtonState = "idle" | "loading" | "success";

export function LoadingButton({
  state,
  onClick,
}: {
  state: ButtonState;
  onClick: () => void;
}) {
  return (
    <motion.button
      onClick={onClick}
      disabled={state !== "idle"}
      whileHover={state === "idle" ? { scale: 1.02 } : {}}
      whileTap={state === "idle" ? { scale: 0.98 } : {}}
      className="relative px-6 py-3 bg-primary text-primary-foreground rounded-lg overflow-hidden min-w-[120px]"
    >
      <AnimatePresence mode="wait">
        {state === "idle" && (
          <motion.span
            key="idle"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            Submit
          </motion.span>
        )}
        {state === "loading" && (
          <motion.span
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex items-center justify-center"
          >
            <Loader2 className="h-5 w-5 animate-spin" />
          </motion.span>
        )}
        {state === "success" && (
          <motion.span
            key="success"
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex items-center justify-center"
          >
            <Check className="h-5 w-5" />
          </motion.span>
        )}
      </AnimatePresence>
    </motion.button>
  );
}
```

## Card Interactions

### Hover Lift Card

```tsx
<motion.div
  whileHover={{
    y: -5,
    boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)",
  }}
  transition={{ type: "spring", stiffness: 300, damping: 20 }}
  className="p-6 bg-card rounded-xl border"
>
  Card content
</motion.div>
```

### Card with Glow Effect

```tsx
"use client";

import { motion, useMotionTemplate, useMotionValue } from "framer-motion";

export function GlowCard({ children }: { children: React.ReactNode }) {
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  function handleMouseMove(e: React.MouseEvent) {
    const { left, top } = e.currentTarget.getBoundingClientRect();
    mouseX.set(e.clientX - left);
    mouseY.set(e.clientY - top);
  }

  const background = useMotionTemplate`radial-gradient(
    200px circle at ${mouseX}px ${mouseY}px,
    rgba(59, 130, 246, 0.15),
    transparent 80%
  )`;

  return (
    <motion.div
      onMouseMove={handleMouseMove}
      style={{ background }}
      whileHover={{ scale: 1.02 }}
      className="relative p-6 bg-card rounded-xl border overflow-hidden"
    >
      {children}
    </motion.div>
  );
}
```

### Expandable Card

```tsx
"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown } from "lucide-react";

export function ExpandableCard({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="border rounded-xl overflow-hidden">
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-4 text-left"
        whileHover={{ backgroundColor: "rgba(0,0,0,0.02)" }}
      >
        <span className="font-medium">{title}</span>
        <motion.span animate={{ rotate: isOpen ? 180 : 0 }}>
          <ChevronDown className="h-5 w-5" />
        </motion.span>
      </motion.button>
      <AnimatePresence initial={false}>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="overflow-hidden"
          >
            <div className="p-4 pt-0 border-t">{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
```

## Input Interactions

### Floating Label Input

```tsx
"use client";

import { useState } from "react";
import { motion } from "framer-motion";

export function FloatingLabelInput({ label }: { label: string }) {
  const [isFocused, setIsFocused] = useState(false);
  const [value, setValue] = useState("");

  const isActive = isFocused || value.length > 0;

  return (
    <div className="relative">
      <motion.label
        initial={false}
        animate={{
          y: isActive ? -24 : 0,
          scale: isActive ? 0.85 : 1,
          color: isFocused ? "hsl(var(--primary))" : "hsl(var(--muted-foreground))",
        }}
        className="absolute left-3 top-3 origin-left pointer-events-none"
      >
        {label}
      </motion.label>
      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        className="w-full px-3 py-3 border rounded-lg focus:ring-2 focus:ring-primary outline-none"
      />
    </div>
  );
}
```

### Search Input with Icon

```tsx
"use client";

import { motion } from "framer-motion";
import { Search, X } from "lucide-react";

export function SearchInput({
  value,
  onChange,
  onClear,
}: {
  value: string;
  onChange: (value: string) => void;
  onClear: () => void;
}) {
  return (
    <div className="relative">
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Search..."
        className="w-full pl-10 pr-10 py-2 border rounded-lg focus:ring-2 focus:ring-primary outline-none"
      />
      <AnimatePresence>
        {value && (
          <motion.button
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            onClick={onClear}
            className="absolute right-3 top-1/2 -translate-y-1/2"
          >
            <X className="h-4 w-4 text-muted-foreground" />
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  );
}
```

## Toggle & Switch

### Animated Toggle

```tsx
"use client";

import { motion } from "framer-motion";

export function AnimatedToggle({
  isOn,
  onToggle,
}: {
  isOn: boolean;
  onToggle: () => void;
}) {
  return (
    <motion.button
      onClick={onToggle}
      animate={{ backgroundColor: isOn ? "hsl(var(--primary))" : "hsl(var(--muted))" }}
      className="w-14 h-8 rounded-full p-1"
    >
      <motion.div
        animate={{ x: isOn ? 24 : 0 }}
        transition={{ type: "spring", stiffness: 500, damping: 30 }}
        className="w-6 h-6 bg-white rounded-full shadow-md"
      />
    </motion.button>
  );
}
```

## Modal Interactions

### Modal with Backdrop

```tsx
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { X } from "lucide-react";

export function AnimatedModal({
  isOpen,
  onClose,
  children,
}: {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
}) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 z-40"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-md bg-background rounded-xl p-6 shadow-xl"
          >
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={onClose}
              className="absolute top-4 right-4"
            >
              <X className="h-5 w-5" />
            </motion.button>
            {children}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
```

## Notification Toast

```tsx
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { CheckCircle, X } from "lucide-react";

export function AnimatedToast({
  isVisible,
  message,
  onClose,
}: {
  isVisible: boolean;
  message: string;
  onClose: () => void;
}) {
  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: 50, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 20, scale: 0.9 }}
          transition={{ type: "spring", damping: 25, stiffness: 300 }}
          className="fixed bottom-4 right-4 flex items-center gap-3 px-4 py-3 bg-green-500 text-white rounded-lg shadow-lg"
        >
          <CheckCircle className="h-5 w-5" />
          <span>{message}</span>
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={onClose}
          >
            <X className="h-4 w-4" />
          </motion.button>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
```

## Loading Spinner

```tsx
"use client";

import { motion } from "framer-motion";

export function LoadingSpinner() {
  return (
    <motion.div
      animate={{ rotate: 360 }}
      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
      className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full"
    />
  );
}

// Pulsing dots
export function LoadingDots() {
  return (
    <div className="flex gap-1">
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          animate={{ scale: [1, 1.2, 1] }}
          transition={{
            duration: 0.6,
            repeat: Infinity,
            delay: i * 0.2,
          }}
          className="w-2 h-2 bg-primary rounded-full"
        />
      ))}
    </div>
  );
}
```

## Checkbox Animation

```tsx
"use client";

import { motion } from "framer-motion";
import { Check } from "lucide-react";

export function AnimatedCheckbox({
  checked,
  onChange,
}: {
  checked: boolean;
  onChange: (checked: boolean) => void;
}) {
  return (
    <motion.button
      onClick={() => onChange(!checked)}
      animate={{
        backgroundColor: checked ? "hsl(var(--primary))" : "transparent",
        borderColor: checked ? "hsl(var(--primary))" : "hsl(var(--border))",
      }}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      className="w-5 h-5 border-2 rounded flex items-center justify-center"
    >
      <motion.span
        initial={false}
        animate={{ scale: checked ? 1 : 0 }}
        transition={{ type: "spring", stiffness: 500, damping: 30 }}
      >
        <Check className="h-3 w-3 text-primary-foreground" />
      </motion.span>
    </motion.button>
  );
}
```

## Best Practices

1. **Keep it subtle**: Micro-interactions should enhance, not distract
2. **Use springs for responsiveness**: They feel more natural than tweens
3. **Short durations**: 100-300ms for most micro-interactions
4. **Consistent timing**: Use the same spring settings throughout your app
5. **Purpose over decoration**: Every animation should have a reason
6. **Test without animations**: UI should work without motion
