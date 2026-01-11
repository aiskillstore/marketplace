# Advanced App Router Patterns

## 1. Server Actions

Server Actions allow calling server-side functions directly from client components.

```typescript
// app/actions/tasks.ts
'use server';

import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';

export async function createTask(formData: FormData) {
  const title = formData.get('title') as string;

  await db.insert(tasks).values({ title });
  revalidatePath('/tasks');
  redirect('/tasks');
}

// Usage in client component
'use client';
import { createTask } from '@/app/actions/tasks';

export function CreateTaskForm() {
  return (
    <form action={createTask}>
      <input name="title" />
      <button type="submit">Create</button>
    </form>
  );
}
```

## 2. Route Groups with Auth

Organize routes without affecting URL structure.

```
app/
  (auth)/
    layout.tsx          # Auth-specific layout
    login/page.tsx       # /login
    register/page.tsx    # /register
  (dashboard)/
    layout.tsx          # Dashboard layout
    page.tsx            # /dashboard
    settings/page.tsx    # /settings
```

## 3. Intercepting Routes

Show a modal while preserving original URL.

```typescript
// app/photos/[id]/page.tsx - Original page
export default async function PhotoPage({ params }: Props) {
  const photo = await getPhoto(params.id);
  return <PhotoDetail photo={photo} />;
}

// app/photos/[id]/@modal/page.tsx - Intercept
export default async function PhotoModal({ params }: Props) {
  const photo = await getPhoto(params.id);
  return <PhotoModal photo={photo} />;
}
```

## 4. Parallel Routes with Slots

Render multiple pages simultaneously.

```
app/
  dashboard/
    layout.tsx           # <div>{children} <slot /></div>
    page.tsx             # Left panel
    @analytics/
      page.tsx           # Right panel - analytics
    @activity/
      page.tsx           # Right panel - activity
```

```typescript
// app/dashboard/layout.tsx
export default function DashboardLayout({
  children,
  analytics,
  activity,
}: {
  children: React.ReactNode;
  analytics?: React.ReactNode;
  activity?: React.ReactNode;
}) {
  return (
    <div className="grid grid-cols-3 gap-4">
      <div className="col-span-2">{children}</div>
      <div>
        {analytics}
        {activity}
      </div>
    </div>
  );
}
```

## 5. Middleware for Route Protection

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const protectedRoutes = ['/dashboard', '/settings'];

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token')?.value;

  if (protectedRoutes.some(route => request.nextUrl.pathname.startsWith(route))) {
    if (!token) {
      return NextResponse.redirect(new URL('/login', request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
```

## 6. Streaming with Suspense

Stream data progressively for better perceived performance.

```typescript
// app/dashboard/page.tsx
import { Suspense } from 'react';

export default async function Dashboard() {
  return (
    <main>
      <Suspense fallback={<StatsSkeleton />}>
        <Stats />
      </Suspense>
      <Suspense fallback={<TasksSkeleton />}>
        <Tasks />
      </Suspense>
    </main>
  );
}

async function Stats() {
  const stats = await getStats(); // Takes 200ms
  return <StatsView stats={stats} />;
}

async function Tasks() {
  const tasks = await getTasks(); // Takes 300ms
  return <TasksView tasks={tasks} />;
}
```

## 7. Prefetching

Preload routes in background.

```typescript
'use client';
import { useRouter } from 'next/navigation';

export function TaskList() {
  const router = useRouter();

  return (
    <ul>
      {tasks.map(task => (
        <li key={task.id}>
          <Link
            href={`/tasks/${task.id}`}
            onMouseEnter={() => router.prefetch(`/tasks/${task.id}`)}
          >
            {task.title}
          </Link>
        </li>
      ))}
    </ul>
  );
}
```

## 8. Dynamic Metadata Generation

```typescript
// app/products/[id]/page.tsx
import type { Metadata } from 'next';

type Props = Promise<{ id: string }>;

export async function generateMetadata({ params }: { params: Props }): Promise<Metadata> {
  const { id } = await params;
  const product = await getProduct(id);

  return {
    title: product.name,
    description: product.description,
    openGraph: {
      title: product.name,
      images: [product.image],
    },
  };
}
```

## 9. Static Generation with Revalidation

```typescript
// app/blog/[slug]/page.tsx
export const revalidate = 3600; // Revalidate every hour

export default async function BlogPost({ params }: Props) {
  const post = await getPost(params.slug);
  return <PostContent post={post} />;
}
```

## 10. Image Optimization

```typescript
import Image from 'next/image';

export default function Avatar({ src, name }: { src: string; name: string }) {
  return (
    <Image
      src={src}
      alt={name}
      width={40}
      height={40}
      className="rounded-full"
      priority={false} // Set true for above-fold images
    />
  );
}
```
