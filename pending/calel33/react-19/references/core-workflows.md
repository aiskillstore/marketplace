# React 19 Core Workflows

Complete examples for the 5 essential React 19 patterns.

## 1. Form Handling with useActionState

**Use for:** Forms with async submissions, automatic pending states, error handling

```javascript
'use client';
import { useActionState } from 'react';

function SignupForm() {
  const [state, formAction, isPending] = useActionState(
    async (previousState, formData) => {
      const email = formData.get('email');
      const error = await createUser(email);
      return error ? { error } : null;
    },
    { error: null }
  );

  return (
    <form action={formAction}>
      <input type="email" name="email" required />
      <button type="submit" disabled={isPending}>
        {isPending ? 'Signing up...' : 'Sign Up'}
      </button>
      {state.error && <p className="error">{state.error}</p>}
    </form>
  );
}
```

**Benefits:**
- Automatic pending state tracking
- Form reset on success
- Progressive enhancement
- Built-in error handling

---

## 2. Optimistic Updates with useOptimistic

**Use for:** Instant UI feedback (likes, comments, toggles)

```javascript
'use client';
import { useOptimistic } from 'react';

function CommentList({ comments, addComment }) {
  const [optimisticComments, addOptimisticComment] = useOptimistic(
    comments,
    (current, newComment) => [...current, { ...newComment, pending: true }]
  );

  async function submitComment(formData) {
    const newComment = { id: Date.now(), text: formData.get('comment') };
    addOptimisticComment(newComment);
    await addComment(newComment);
  }

  return (
    <div>
      {optimisticComments.map(comment => (
        <div key={comment.id} className={comment.pending ? 'opacity-50' : ''}>
          {comment.text}
        </div>
      ))}
      <form action={submitComment}>
        <input name="comment" placeholder="Add a comment..." />
        <button type="submit">Post</button>
      </form>
    </div>
  );
}
```

**Benefits:**
- UI updates immediately
- Automatically reverts on error
- Better perceived performance
- No manual rollback needed

---

## 3. Server Components + Server Actions

**Use for:** SEO-critical content, direct database access, reducing JS bundle

### Server Action

```javascript
// app/actions.js
'use server';
import { revalidatePath } from 'next/cache';
import { db } from '@/lib/db';

export async function createPost(formData) {
  const title = formData.get('title');
  
  if (!title || title.length < 3) {
    return { error: 'Title must be at least 3 characters' };
  }
  
  await db.posts.create({ title, authorId: await getCurrentUserId() });
  revalidatePath('/posts');
}
```

### Client Component

```javascript
// app/new-post/page.js
'use client';
import { useActionState } from 'react';
import { createPost } from './actions';

export default function NewPostForm() {
  const [state, formAction, isPending] = useActionState(createPost, {});
  
  return (
    <form action={formAction}>
      <input name="title" placeholder="Post title" />
      <button type="submit" disabled={isPending}>
        {isPending ? 'Publishing...' : 'Publish'}
      </button>
      {state.error && <p className="error">{state.error}</p>}
    </form>
  );
}
```

**Benefits:**
- No API routes needed
- Direct database access
- Type-safe
- Automatic serialization
- Built-in CSRF protection

---

## 4. Streaming with Suspense

**Use for:** Dashboards, pages with multiple data sources, progressive rendering

```javascript
import { Suspense } from 'react';

export default function DashboardPage() {
  return (
    <div className="dashboard">
      <h1>Analytics Dashboard</h1>
      <div className="grid">
        <Suspense fallback={<CardSkeleton />}>
          <RevenueCard />
        </Suspense>
        <Suspense fallback={<CardSkeleton />}>
          <UsersCard />
        </Suspense>
        <Suspense fallback={<CardSkeleton />}>
          <ActivityCard />
        </Suspense>
      </div>
    </div>
  );
}

async function RevenueCard() {
  const revenue = await db.analytics.getRevenue();
  return <div className="card">{revenue}</div>;
}

async function UsersCard() {
  const users = await db.analytics.getActiveUsers();
  return <div className="card">{users}</div>;
}

async function ActivityCard() {
  const activity = await db.analytics.getRecentActivity();
  return <div className="card">{activity.length} events</div>;
}

function CardSkeleton() {
  return <div className="card skeleton" />;
}
```

**Benefits:**
- Fast content displays first
- Sections load independently
- No waterfalls
- Better perceived performance
- SEO-friendly

---

## 5. Conditional Resource Loading with use()

**Use for:** Conditional data loading, reading context after early returns

```javascript
import { use } from 'react';

function UserProfile({ userPromise }) {
  const user = use(userPromise); // Can be called conditionally!
  if (!user) return null;
  
  const theme = use(ThemeContext);
  return <div style={{ color: theme.color }}>{user.name}</div>;
}

function App() {
  const userPromise = fetchUser(userId);
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <UserProfile userPromise={userPromise} />
    </Suspense>
  );
}
```

**Advanced example with conditional loading:**

```javascript
import { use } from 'react';

function ConditionalDataLoader({ shouldLoad, dataPromise }) {
  // Can call use() conditionally - not possible with hooks!
  if (!shouldLoad) {
    return <div>No data to display</div>;
  }
  
  const data = use(dataPromise);
  
  return (
    <div>
      {data.map(item => <div key={item.id}>{item.name}</div>)}
    </div>
  );
}
```

**Benefits:**
- Can be called conditionally
- Works in loops
- Can be called after early returns
- Replaces complex hook workarounds

---

## Common Pitfalls

### Actions Must Be Wrapped in Transitions

```javascript
// ✅ Use useActionState (automatic transition)
const [state, formAction, isPending] = useActionState(updateData, {});

// ✅ Or use useTransition
const [isPending, startTransition] = useTransition();
startTransition(async () => { await updateData(); });

// ❌ Wrong - no transition wrapper
async function handleClick() {
  await updateData(); // Error!
}
```

### Server Components Cannot Use Client Hooks

```javascript
// ❌ Wrong
async function MyComponent() {
  const [state, setState] = useState(0); // Error!
}

// ✅ Correct - Mark as Client Component
'use client';
function MyComponent() {
  const [state, setState] = useState(0);
}
```

### useRef Requires an Argument

```javascript
// ❌ Wrong
const ref = useRef();

// ✅ Correct
const ref = useRef(null);
const ref = useRef<HTMLDivElement>(null); // TypeScript
```

### Don't Mix Server and Client Boundaries Incorrectly

```javascript
// ❌ Wrong - Server Component importing Client Component with server-only code
import ClientComponent from './ClientComponent'; // Has 'use client'

export default async function ServerComponent() {
  const data = await db.query(); // Server-only
  return <ClientComponent data={data} />; // data must be serializable!
}

// ✅ Correct - Keep server logic in server
export default async function ServerComponent() {
  const data = await db.query();
  return <ClientComponent initialData={JSON.parse(JSON.stringify(data))} />;
}
```

---

## Key Primitives

1. **Actions** - Async functions in transitions with automatic pending/error handling
2. **Server Components (RSC)** - Zero-JS server-rendered components
3. **Server Actions** - Server-side mutations callable from client
4. **Suspense Boundaries** - Async rendering boundaries
5. **Transitions** - Non-urgent state updates

## Convention Over Configuration

- `"use server"` directive = Server Action
- `"use client"` directive = Client Component
- No directive in RSC environment = Server Component
- `async` component = Suspends automatically
