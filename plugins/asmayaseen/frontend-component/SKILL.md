# Frontend Component Skill

**Purpose**: Guidance for creating Next.js components following server/client patterns and existing component structures.

## Overview

Next.js 16+ uses App Router with Server Components by default. Client Components are only used when interactivity is needed (hooks, event handlers, browser APIs).

## Server vs Client Components

### Server Components (Default)

**When to Use**:
- Pages and layouts
- Static content
- Data fetching from API (when possible)
- SEO-optimized content

**Pattern**:
```typescript
// No "use client" directive
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Page Title",
};

export default function PageComponent() {
  return <div>Static content</div>;
}
```

**Example**: `frontend/app/layout.tsx`, `frontend/app/page.tsx`

### Client Components (When Needed)

**When to Use**:
- Interactive elements (buttons, forms, inputs)
- Event handlers (onClick, onChange, etc.)
- React hooks (useState, useEffect, useRouter, etc.)
- Browser APIs (localStorage, window, document, etc.)
- Real-time updates
- Drag and drop functionality

**Pattern**:
```typescript
"use client"; // MUST be first line

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

interface ComponentProps {
  prop1: string;
  prop2?: number;
}

export default function ComponentName({ prop1, prop2 }: ComponentProps) {
  const router = useRouter();
  const [state, setState] = useState("");

  useEffect(() => {
    // Side effects
  }, []);

  return <div>{/* Component JSX */}</div>;
}
```

**Example**: `frontend/components/ProtectedRoute.tsx`, `frontend/app/signup/page.tsx`

## Component Structure Template

```typescript
"use client"; // Only if client component

/**
 * Component Name
 *
 * Brief description of what this component does
 */

import { useState, useEffect } from "react";
import { ComponentType } from "@/types";
import { cn } from "@/lib/utils";

interface ComponentProps {
  prop1: string;
  prop2?: number;
  className?: string;
}

export default function ComponentName({ prop1, prop2, className }: ComponentProps) {
  // State
  const [state, setState] = useState("");

  // Effects
  useEffect(() => {
    // Side effects
  }, []);

  // Handlers
  const handleClick = () => {
    // Handler logic
  };

  // Render
  return (
    <div className={cn("base-classes", className)}>
      {/* Component content */}
    </div>
  );
}
```

## Specific Component Patterns

### 1. ProtectedRoute Pattern

**From**: `frontend/components/ProtectedRoute.tsx`

```typescript
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { isAuthenticated } from "@/lib/auth";
import LoadingSpinner from "./LoadingSpinner";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const router = useRouter();
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    async function checkAuth() {
      try {
        const authenticated = await isAuthenticated();

        if (!authenticated) {
          const currentPath = window.location.pathname;
          if (currentPath !== "/signin") {
            sessionStorage.setItem("redirectAfterLogin", currentPath);
          }
          router.push("/signin");
        } else {
          setIsAuthorized(true);
        }
      } catch (error) {
        console.error("Auth check failed:", error);
        router.push("/signin");
      } finally {
        setIsChecking(false);
      }
    }

    checkAuth();
  }, [router]);

  if (isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (!isAuthorized) {
    return null;
  }

  return <>{children}</>;
}
```

**Pattern**:
- Check authentication on mount
- Show loading spinner during check
- Store intended destination in sessionStorage
- Redirect to `/signin` if not authenticated
- Only render children if authorized

### 2. LoadingSpinner Pattern

**From**: `frontend/components/LoadingSpinner.tsx`

```typescript
interface LoadingSpinnerProps {
  size?: "small" | "medium" | "large";
  color?: string;
  label?: string;
}

export default function LoadingSpinner({
  size = "medium",
  color = "blue",
  label = "Loading...",
}: LoadingSpinnerProps) {
  const sizeClasses = {
    small: "w-4 h-4 border-2",
    medium: "w-8 h-8 border-3",
    large: "w-12 h-12 border-4",
  };

  const colorClasses = {
    blue: "border-blue-600 border-t-transparent",
    gray: "border-gray-600 border-t-transparent",
    white: "border-white border-t-transparent",
  };

  const spinnerClass = `${sizeClasses[size]} ${
    colorClasses[color as keyof typeof colorClasses] || colorClasses.blue
  } rounded-full animate-spin`;

  return (
    <div
      className="flex items-center justify-center"
      role="status"
      aria-label={label}
      aria-live="polite"
    >
      <div className={spinnerClass}></div>
      <span className="sr-only">{label}</span>
    </div>
  );
}
```

**Pattern**:
- Multiple sizes (small, medium, large)
- Multiple colors (blue, gray, white)
- Accessibility labels (`role="status"`, `aria-label`, `aria-live`)
- Screen reader text with `sr-only` class

### 3. Form Handling Pattern

**From**: `frontend/app/signup/page.tsx`

```typescript
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { isValidEmail, getPasswordStrength } from "@/lib/utils";

export default function SignupPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState("");

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = "Name is required";
    }

    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!isValidEmail(formData.email)) {
      newErrors.email = "Please enter a valid email address";
    }

    // More validation...

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError("");

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      const response = await api.signup(formData);
      if (response.success) {
        router.push("/dashboard");
      } else {
        setApiError(response.message || "Signup failed");
      }
    } catch (error: any) {
      setApiError(error.message || "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
    </form>
  );
}
```

**Pattern**:
- Separate state for form data, errors, loading, API errors
- Validation function that returns boolean
- Clear errors on input change
- Loading state during submission
- Try-catch for error handling
- Redirect on success

### 4. ToastNotification Pattern

**From**: `frontend/components/ToastNotification.tsx`

```typescript
"use client";

import { useEffect, useState } from "react";
import { ToastMessage, ToastType } from "@/types";

export function useToast() {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const showToast = (type: ToastType, message: string, duration?: number) => {
    const id = `toast-${Date.now()}-${Math.random()}`;
    const newToast: ToastMessage = {
      id,
      type,
      message,
      duration,
    };
    setToasts((prev) => [...prev, newToast]);
  };

  const dismissToast = (id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  };

  return {
    toasts,
    showToast,
    dismissToast,
    success: (message: string, duration?: number) => showToast("success", message, duration),
    error: (message: string, duration?: number) => showToast("error", message, duration),
    // ...
  };
}
```

**Pattern**:
- Custom hook for toast management
- Auto-dismiss with duration
- Stack multiple toasts
- Helper methods (success, error, warning, info)

## Tailwind CSS Patterns

### 1. Utility Classes Only

```typescript
<div className="flex items-center justify-center gap-4 p-6 bg-white rounded-lg shadow-md">
```

**Pattern**: Use Tailwind utility classes, no inline styles

### 2. Conditional Classes with `cn()` Utility

```typescript
import { cn } from "@/lib/utils";

<div className={cn(
  "base-classes",
  condition && "conditional-classes",
  className // Allow prop override
)}>
```

**Pattern**: Use `cn()` from `@/lib/utils` for conditional classes

### 3. Dark Mode Support

```typescript
<div className="bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
```

**Pattern**: Use `dark:` prefix for dark mode styles

### 4. Responsive Design

```typescript
<div className="w-full sm:w-1/2 md:w-1/3 lg:w-1/4">
```

**Pattern**: Use breakpoint prefixes (`sm:`, `md:`, `lg:`, `xl:`)

## Accessibility Patterns (WCAG 2.1 AA)

### 1. ARIA Labels

```typescript
<button aria-label="Close dialog">×</button>
<div role="status" aria-live="polite" aria-label="Loading...">
```

**Pattern**: Always provide `aria-label` for icon-only buttons

### 2. Semantic HTML

```typescript
<nav>
  <ul>
    <li><a href="/">Home</a></li>
  </ul>
</nav>
```

**Pattern**: Use semantic HTML elements (`nav`, `main`, `section`, `article`, etc.)

### 3. Keyboard Navigation

```typescript
<button
  onClick={handleClick}
  onKeyDown={(e) => {
    if (e.key === "Enter" || e.key === " ") {
      handleClick();
    }
  }}
>
```

**Pattern**: Ensure keyboard accessibility for all interactive elements

### 4. Screen Reader Text

```typescript
<span className="sr-only">Loading content</span>
```

**Pattern**: Use `sr-only` class for screen reader-only text

### 5. Focus Management

```typescript
<input
  autoFocus
  className="focus:outline-none focus:ring-2 focus:ring-blue-500"
/>
```

**Pattern**: Always provide visible focus indicators

## File Naming Conventions

- **Pages**: kebab-case (e.g., `signup.tsx`, `signin.tsx`)
- **Components**: PascalCase (e.g., `TaskList.tsx`, `TaskItem.tsx`)
- **Layouts**: `layout.tsx`
- **Error Pages**: `error.tsx`, `not-found.tsx`

## Constitution Requirements

- **FR-033**: Next.js 16+ App Router structure ✅
- **FR-034**: Server components default, client when needed ✅
- **FR-035**: Error boundaries ✅
- **FR-036**: WCAG 2.1 AA compliance ✅
- **FR-037**: TypeScript strict mode ✅
- **FR-038**: Prettier formatting ✅
- **FR-039**: ESLint rules ✅

## References

- **Specification**: `specs/002-frontend-todo-app/spec.md` - Component specifications
- **Existing Components**: `frontend/components/*.tsx` - Component examples
- **Existing Pages**: `frontend/app/*.tsx` - Page examples

## Advanced Component Patterns

### 1. Drag and Drop Pattern (Phase 7 - T065)

**Library**: `@dnd-kit/core`

```typescript
"use client";

import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors } from "@dnd-kit/core";
import { SortableContext, sortableKeyboardCoordinates, useSortable, verticalListSortingStrategy } from "@dnd-kit/sortable";

export default function SortableTaskList({ tasks, onReorder }: Props) {
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (over && active.id !== over.id) {
      onReorder(active.id, over.id);
    }
  };

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <SortableContext items={tasks.map(t => t.id)} strategy={verticalListSortingStrategy}>
        {tasks.map(task => (
          <SortableTaskItem key={task.id} task={task} />
        ))}
      </SortableContext>
    </DndContext>
  );
}
```

**Pattern**: Use `@dnd-kit/core` for drag and drop, handle reorder on drag end

### 2. Undo/Redo Pattern (Phase 7 - T066)

```typescript
"use client";

import { useReducer } from "react";

interface HistoryState<T> {
  past: T[];
  present: T;
  future: T[];
}

function historyReducer<T>(state: HistoryState<T>, action: { type: string; newPresent?: T }): HistoryState<T> {
  const { past, present, future } = state;

  switch (action.type) {
    case "UNDO":
      if (past.length === 0) return state;
      return {
        past: past.slice(0, past.length - 1),
        present: past[past.length - 1],
        future: [present, ...future],
      };
    case "REDO":
      if (future.length === 0) return state;
      return {
        past: [...past, present],
        present: future[0],
        future: future.slice(1),
      };
    case "SET":
      if (action.newPresent === present) return state;
      return {
        past: [...past, present],
        present: action.newPresent!,
        future: [],
      };
    default:
      return state;
  }
}

export function useHistory<T>(initialPresent: T) {
  const [state, dispatch] = useReducer(historyReducer, {
    past: [],
    present: initialPresent,
    future: [],
  });

  const undo = () => dispatch({ type: "UNDO" });
  const redo = () => dispatch({ type: "REDO" });
  const set = (newPresent: T) => dispatch({ type: "SET", newPresent });

  return { state: state.present, set, undo, redo, canUndo: state.past.length > 0, canRedo: state.future.length > 0 };
}
```

**Pattern**: Use `useReducer` with history pattern for undo/redo functionality

### 3. Real-time Updates with Polling (Phase 7 - T067)

```typescript
"use client";

import { useEffect, useRef } from "react";

export function usePolling(callback: () => Promise<void>, interval: number = 5000) {
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const poll = async () => {
      try {
        await callback();
      } catch (error) {
        console.error("Polling error:", error);
      }
    };

    // Initial call
    poll();

    // Set up polling interval
    intervalRef.current = setInterval(poll, interval);

    // Cleanup
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [callback, interval]);
}
```

**Pattern**: Use `setInterval` for polling, cleanup on unmount, handle errors gracefully

### 4. Inline Editing Pattern (Phase 7 - T068)

```typescript
"use client";

import { useState } from "react";

export default function InlineEditable({ value, onSave }: Props) {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(value);

  const handleSave = () => {
    onSave(editValue);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditValue(value);
    setIsEditing(false);
  };

  if (isEditing) {
    return (
      <input
        value={editValue}
        onChange={(e) => setEditValue(e.target.value)}
        onBlur={handleSave}
        onKeyDown={(e) => {
          if (e.key === "Enter") handleSave();
          if (e.key === "Escape") handleCancel();
        }}
        autoFocus
      />
    );
  }

  return (
    <span onClick={() => setIsEditing(true)} className="cursor-pointer">
      {value}
    </span>
  );
}
```

**Pattern**: Toggle edit mode, save on blur/Enter, cancel on Escape

### 5. Performance Optimization Patterns (Phase 8 - T072)

#### Code Splitting with `next/dynamic`

```typescript
import dynamic from "next/dynamic";

// Lazy load heavy components
const TaskStatistics = dynamic(() => import("@/components/TaskStatistics"), {
  loading: () => <LoadingSpinner />,
  ssr: false, // Disable SSR if not needed
});

const TaskDetailModal = dynamic(() => import("@/components/TaskDetailModal"), {
  loading: () => <LoadingSpinner />,
});
```

**Pattern**: Use `next/dynamic` for code splitting, provide loading fallback

#### Image Optimization

```typescript
import Image from "next/image";

<Image
  src="/image.jpg"
  alt="Description"
  width={500}
  height={300}
  loading="lazy"
  placeholder="blur"
/>
```

**Pattern**: Use Next.js `Image` component for automatic optimization

### 6. Error Boundary Pattern (Phase 8 - T074)

```typescript
"use client";

import React, { Component, ErrorInfo, ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
    // Log to error tracking service
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div className="p-4 bg-red-50 border border-red-200 rounded">
            <h2 className="text-red-800 font-bold">Something went wrong</h2>
            <p className="text-red-600">{this.state.error?.message}</p>
            <button onClick={() => this.setState({ hasError: false })}>Try again</button>
          </div>
        )
      );
    }

    return this.props.children;
  }
}
```

**Pattern**: Class component, catch errors, provide fallback UI, log errors

### 7. PWA Patterns (Phase 8 - T069, T070, T071)

#### Service Worker Setup

```typescript
// public/sw.js or use next-pwa
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/sw.js")
      .then((registration) => {
        console.log("SW registered:", registration);
      })
      .catch((error) => {
        console.error("SW registration failed:", error);
      });
  });
}
```

**Pattern**: Register service worker on page load, handle registration errors

#### IndexedDB for Offline Storage

```typescript
import { openDB, DBSchema, IDBPDatabase } from "idb";

interface TaskDB extends DBSchema {
  tasks: {
    key: number;
    value: Task;
    indexes: { "by-user-id": string };
  };
}

export async function getDB(): Promise<IDBPDatabase<TaskDB>> {
  return openDB<TaskDB>("todo-db", 1, {
    upgrade(db) {
      const taskStore = db.createObjectStore("tasks", { keyPath: "id" });
      taskStore.createIndex("by-user-id", "user_id");
    },
  });
}

export async function saveTaskOffline(task: Task) {
  const db = await getDB();
  await db.put("tasks", task);
}

export async function getTasksOffline(userId: string): Promise<Task[]> {
  const db = await getDB();
  return db.getAllFromIndex("tasks", "by-user-id", userId);
}
```

**Pattern**: Use `idb` library for IndexedDB, create stores and indexes, handle offline data

#### Offline Sync Mechanism

```typescript
export async function syncOfflineChanges(userId: string) {
  const db = await getDB();
  const offlineTasks = await db.getAllFromIndex("tasks", "by-user-id", userId);

  for (const task of offlineTasks) {
    if (task.syncStatus === "pending") {
      try {
        await api.createTask(userId, task);
        await db.put("tasks", { ...task, syncStatus: "synced" });
      } catch (error) {
        console.error("Sync failed for task:", task.id, error);
      }
    }
  }
}

// Call on connection restore
window.addEventListener("online", () => {
  syncOfflineChanges(currentUserId);
});
```

**Pattern**: Track sync status, sync on connection restore, handle sync errors

### 8. Caching Strategies (Phase 8 - T073)

```typescript
// Cache API responses
const cache = new Map<string, { data: any; timestamp: number }>();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

export async function getCachedData<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
  const cached = cache.get(key);
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.data;
  }

  const data = await fetcher();
  cache.set(key, { data, timestamp: Date.now() });
  return data;
}
```

**Pattern**: Use Map for in-memory cache, check expiration, update cache on fetch

### 9. Error Logging and Tracking (Phase 8 - T075)

```typescript
export function logError(error: Error, context?: Record<string, any>) {
  console.error("Error:", error, context);

  // Send to error tracking service (e.g., Sentry)
  if (typeof window !== "undefined" && (window as any).Sentry) {
    (window as any).Sentry.captureException(error, {
      extra: context,
    });
  }

  // Or send to custom endpoint
  fetch("/api/log-error", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: error.message,
      stack: error.stack,
      context,
      timestamp: new Date().toISOString(),
    }),
  }).catch((err) => console.error("Failed to log error:", err));
}
```

**Pattern**: Log to console, send to error tracking service, include context

## Common Patterns Summary

1. ✅ Use Server Components by default
2. ✅ Add `"use client"` only when needed
3. ✅ Use TypeScript interfaces for props
4. ✅ Use `cn()` utility for conditional classes
5. ✅ Always include accessibility attributes
6. ✅ Use semantic HTML elements
7. ✅ Provide loading states
8. ✅ Handle errors gracefully
9. ✅ Use Tailwind utility classes
10. ✅ Support dark mode with `dark:` prefix
11. ✅ Use `@dnd-kit/core` for drag and drop
12. ✅ Use `useReducer` for undo/redo
13. ✅ Use `setInterval` for polling with cleanup
14. ✅ Use `next/dynamic` for code splitting
15. ✅ Use ErrorBoundary for error handling
16. ✅ Use IndexedDB for offline storage
17. ✅ Sync offline changes on connection restore
18. ✅ Cache API responses with expiration
19. ✅ Log errors to tracking service

