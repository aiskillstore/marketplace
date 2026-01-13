---
name: frontend-nextjs-app-router
description: |
  Use when working with Next.js App Router tasks - creating pages in /app/, setting up dynamic routes ([id]/page.tsx), implementing nested layouts/templates (layout.tsx), optimizing Server/Client components, or building ERP role-based pages (admin/teacher/student dashboards). Auto-use for all /app/ directory operations, dynamic routing, and App Router-specific features.
---

# Next.js App Router Expert

## Overview

Expert guidance for Next.js App Router development including page creation, dynamic routing, nested layouts, Server/Client component optimization, and ERP role-based dashboards.

## Core Capabilities

### 1. Page Creation (`/app/.../page.tsx`)

**Rules:**
- Use **Server Components** by default (no 'use client' directive)
- Async data fetching with `fetch()` or ORM queries directly
- No `useEffect` for initial data load
- Use `Suspense` boundaries for loading states
- SEO metadata via `generateMetadata()`

**Template:**
```typescript
// app/dashboard/page.tsx
import { Suspense } from 'react';
import { TaskList } from '@/components/TaskList';
import { TaskListSkeleton } from '@/components/TaskListSkeleton';

export const metadata = {
  title: 'Dashboard',
  description: 'Your task management dashboard',
};

export default async function DashboardPage() {
  const tasks = await fetchTasks();

  return (
    <main className="p-4">
      <h1>Dashboard</h1>
      <Suspense fallback={<TaskListSkeleton />}>
        <TaskList initialTasks={tasks} />
      </Suspense>
    </main>
  );
}
```

### 2. Dynamic Routes (`[slug]/page.tsx`)

**When to use:**
- Student profiles: `app/students/[studentId]/page.tsx`
- Task details: `app/tasks/[taskId]/page.tsx`
- Course pages: `app/courses/[courseId]/page.tsx`

**Rules:**
- Extract params from `params` prop (read-only)
- Use `generateMetadata()` for SEO
- Handle 404 with `not-found.tsx`

**Template:**
```typescript
// app/students/[studentId]/page.tsx
import { notFound } from 'next/navigation';

type Params = Promise<{ studentId: string }>;

export async function generateMetadata({ params }: { params: Params }) {
  const { studentId } = await params;
  const student = await getStudent(studentId);

  if (!student) return { title: 'Student Not Found' };

  return {
    title: `${student.name} - Student Profile`,
  };
}

export default async function StudentProfile({ params }: { params: Params }) {
  const { studentId } = await params;
  const student = await getStudent(studentId);

  if (!student) notFound();

  return <StudentProfileView student={student} />;
}
```

### 3. Parallel Routes (`@folder`)

**When to use:**
- Dashboard variants: `app/dashboard@(admin|teacher)/page.tsx`
- Split layouts: `app/settings@(user|organization)/layout.tsx`

**Template:**
```typescript
// app/dashboard/@admin/page.tsx - Admin dashboard
export default function AdminDashboard() {
  return <AdminPanel />;
}

// app/dashboard/@teacher/page.tsx - Teacher dashboard
export default function TeacherDashboard() {
  return <TeacherPanel />;
}
```

### 4. Layouts & Templates

**Root Layout (`app/layout.tsx`):**
```typescript
import { Providers } from '@/components/Providers';
import './globals.css';

export const metadata = {
  title: 'Todo Evolution',
  description: 'Task management for education',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

**Nested Layout (`app/dashboard/layout.tsx`):**
```typescript
import { DashboardNav } from '@/components/DashboardNav';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen">
      <DashboardNav />
      <main className="flex-1 p-6">{children}</main>
    </div>
  );
}
```

**Template (`app/tasks/template.tsx`):**
```typescript
// Re-executes on navigation, preserves form state
export default function TasksTemplate({ children }: { children: React.ReactNode }) {
  return (
    <div className="bg-gray-50 min-h-screen">
      <header className="bg-white shadow">
        <h1>Tasks</h1>
      </header>
      {children}
    </div>
  );
}
```

### 5. Server vs Client Components

**Use Server Components for:**
- Data fetching
- Direct database queries
- Static content
- Server-only operations

**Use Client Components (`'use client'`) for:**
- Browser APIs (`window`, `localStorage`)
- Event handlers (`onClick`, `onSubmit`)
- React hooks (`useState`, `useEffect`)
- State management (Zustand, Redux)
- Interactivity

```typescript
// Server Component (default)
export default async function TaskList() {
  const tasks = await fetchTasks(); // Direct DB query
  return <div>{tasks.map(/* ... */)}</div>;
}

// Client Component
'use client';
import { useTaskStore } from '@/store/tasks';

export function TaskFilter() {
  const { filter, setFilter } = useTaskStore();
  return <button onClick={() => setFilter('all')}>All Tasks</button>;
}
```

### 6. ERP Role-Based Pages

**Role Guards:**
```typescript
// app/admin/page.tsx
import { requireRole } from '@/lib/auth';
import { redirect } from 'next/navigation';

export default async function AdminPage() {
  const session = await getSession();

  if (session?.role !== 'admin') {
    redirect('/unauthorized');
  }

  return <AdminDashboard />;
}
```

**KPI Dashboard (Recharts):**
```typescript
'use client';
import { BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';

export function TaskKPIChart({ data }: { data: TaskStats[] }) {
  return (
    <BarChart width={600} height={300} data={data}>
      <XAxis dataKey="date" />
      <YAxis />
      <Tooltip />
      <Bar dataKey="completed" fill="#22c55e" />
    </BarChart>
  );
}
```

### 7. Error & Loading States

**Error Boundary (`error.tsx`):**
```typescript
'use client';
export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

**Loading State (`loading.tsx`):**
```typescript
export default function Loading() {
  return <div className="animate-pulse">Loading...</div>;
}

// Or with Suspense:
export default async function Page() {
  return (
    <Suspense fallback={<Loading />}>
      <Content />
    </Suspense>
  );
}
```

### 8. shadcn/ui Integration

**Installation:**
```bash
npx shadcn@latest add button card input dialog
```

**Usage in Server Components:**
```typescript
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader } from '@/components/ui/card';

export default async function TaskPage() {
  const tasks = await getTasks();

  return (
    <Card>
      <CardHeader>Tasks</CardHeader>
      <CardContent>
        {tasks.map(task => (
          <div key={task.id}>{task.title}</div>
        ))}
      </CardContent>
    </Card>
  );
}
```

## Workflow Decision Tree

**User Request** → **Analyze** → **Implementation Path**

1. **"Dashboard/Admin page banao"**
   → Server Component with `page.tsx`
   → Async data fetch
   → Add `layout.tsx` if navigation needed

2. **"Dynamic student profile"**
   → Create `[studentId]/page.tsx`
   → Extract params
   → Add `generateMetadata()`
   → Create `not-found.tsx` if needed

3. **"Shared layout add karo"**
   → Create `layout.tsx` in target folder
   → Wrap with providers if needed
   → Maintain children render

4. **"Form add karo"**
   → `'use client'` component
   → useState for form data
   → Server Action for submission OR API route

5. **"KPI charts/Analytics"**
   → `'use client'` for Recharts
   → Server Component parent with data fetch
   → Pass data as props

## Quality Checklist

Before marking task complete:

- [ ] TypeScript strict mode enabled
- [ ] Server Components used by default
- [ ] `'use client'` only when necessary
- [ ] `generateMetadata()` for SEO
- [ ] Suspense boundaries for async data
- [ ] Error boundaries (`error.tsx`) where needed
- [ ] No hydration mismatches
- [ ] Performance optimized (no blocking renders)
- [ ] Mobile-first responsive design
- [ ] Accessible (ARIA labels, keyboard nav)

## Common Patterns

**Pattern 1: Server Component + Client Component Mix**
```typescript
// Server Component
export default async function Page() {
  const tasks = await fetchTasks();
  return <TaskList tasks={tasks} />; // Client component for interactivity
}

'use client';
function TaskList({ tasks }: { tasks: Task[] }) {
  const [filter, setFilter] = useState('all');
  const filtered = tasks.filter(/* ... */);
  return <div>{filtered.map(/* ... */)}</div>;
}
```

**Pattern 2: Route Groups for Organization**
```
app/
  (marketing)/     # Group: no URL segment
    about/page.tsx
    contact/page.tsx
  (dashboard)/      # Group: no URL segment
    layout.tsx
    page.tsx
```

**Pattern 3: API Routes (Route Handlers)**
```typescript
// app/api/tasks/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  const tasks = await db.query.tasks.findMany();
  return NextResponse.json(tasks);
}

export async function POST(request: Request) {
  const body = await request.json();
  const task = await createTask(body);
  return NextResponse.json(task, { status: 201 });
}
```

## Trigger Examples

- "Dashboard page banao" → Generate `app/dashboard/page.tsx` with server component
- "Dynamic student profile route" → `app/students/[studentId]/page.tsx` with params and metadata
- "Shared layout add karo" → `app/dashboard/layout.tsx` with children
- "Admin panel with charts" → Server component + Client chart component
- "Login page banao" → `'use client'` form component + API route
- "404 page customize karo" → `app/not-found.tsx`
- "Error handle karo" → `app/dashboard/error.tsx`

## References

See `references/app-router-patterns.md` for advanced patterns and `references/api-routes.md` for route handler examples.
