# React 19 Hooks API Reference

Complete documentation for React 19's new hooks with detailed examples and use cases.

---

## useActionState

Form state management hook with automatic pending states, error handling, and form resets.

### Signature

```typescript
function useActionState<State>(
  action: (prevState: State, formData: FormData) => Promise<State>,
  initialState: State,
  permalink?: string
): [state: State, formAction: (formData: FormData) => void, isPending: boolean]
```

### Parameters

- **action**: Async function that receives previous state and form data, returns new state
- **initialState**: Initial state value (returned on first render)
- **permalink** (optional): URL to navigate to if form is submitted before JS loads (progressive enhancement)

### Returns

Array with three elements:
1. **state**: Current state (starts as `initialState`, becomes return value of action after submission)
2. **formAction**: Function to pass to form's `action` prop
3. **isPending**: Boolean indicating if action is in flight

### Basic Example

```javascript
'use client';
import { useActionState } from 'react';

function SignupForm() {
  const [state, formAction, isPending] = useActionState(
    async (previousState, formData) => {
      const email = formData.get('email');
      const password = formData.get('password');
      
      // Validate
      if (!email || !password) {
        return { error: 'Email and password required' };
      }
      
      // Create user
      const error = await createUser(email, password);
      
      if (error) {
        return { error };
      }
      
      // Redirect on success
      redirect('/dashboard');
      return null;
    },
    { error: null } // initial state
  );

  return (
    <form action={formAction}>
      <input type="email" name="email" required />
      <input type="password" name="password" required />
      <button type="submit" disabled={isPending}>
        {isPending ? 'Signing up...' : 'Sign Up'}
      </button>
      {state.error && <p className="error">{state.error}</p>}
    </form>
  );
}
```

### With Server Actions

```javascript
// app/actions.js
'use server';
import { z } from 'zod';

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
});

export async function signup(prevState, formData) {
  const result = schema.safeParse({
    email: formData.get('email'),
    password: formData.get('password')
  });
  
  if (!result.success) {
    return { 
      error: result.error.flatten().fieldErrors 
    };
  }
  
  const user = await db.users.create(result.data);
  await setSession(user.id);
  redirect('/dashboard');
}
```

```javascript
// app/signup/page.js
'use client';
import { useActionState } from 'react';
import { signup } from './actions';

export default function SignupPage() {
  const [state, formAction, isPending] = useActionState(signup, {});
  
  return (
    <form action={formAction}>
      <input name="email" type="email" />
      {state.error?.email && <span>{state.error.email}</span>}
      
      <input name="password" type="password" />
      {state.error?.password && <span>{state.error.password}</span>}
      
      <button disabled={isPending}>
        {isPending ? 'Submitting...' : 'Sign Up'}
      </button>
    </form>
  );
}
```

### Progressive Enhancement

```javascript
const [state, formAction, isPending] = useActionState(
  signup,
  {},
  '/signup/fallback' // Works without JS
);
```

When JavaScript is disabled, form submits to `/signup/fallback`.

### Key Behaviors

- Form automatically resets on successful submission (no manual reset needed)
- `isPending` is `true` during action execution
- Action runs in a transition (non-blocking)
- State persists across renders until next submission

---

## useOptimistic

Optimistic UI updates that automatically revert on error.

### Signature

```typescript
function useOptimistic<State>(
  passthrough: State,
  reducerFn: (currentState: State, optimisticValue: any) => State
): [optimisticState: State, addOptimistic: (value: any) => void]
```

### Parameters

- **passthrough**: Base state (usually from props or server state)
- **reducerFn**: Function that computes optimistic state from current state and optimistic value

### Returns

Array with two elements:
1. **optimisticState**: State to render (either real or optimistic)
2. **addOptimistic**: Function to add optimistic update

### Basic Example

```javascript
'use client';
import { useOptimistic } from 'react';

function LikeButton({ likes, postId, onLike }) {
  const [optimisticLikes, addOptimisticLike] = useOptimistic(
    likes,
    (currentLikes, amount) => currentLikes + amount
  );

  async function handleLike() {
    addOptimisticLike(1); // UI updates immediately
    await onLike(postId); // Send to server
  }

  return (
    <button onClick={handleLike}>
      ❤️ {optimisticLikes}
    </button>
  );
}
```

### Comment System Example

```javascript
'use client';
import { useOptimistic } from 'react';

function CommentList({ comments, addComment }) {
  const [optimisticComments, addOptimisticComment] = useOptimistic(
    comments,
    (currentComments, newComment) => [
      ...currentComments,
      { ...newComment, pending: true }
    ]
  );

  async function submitComment(formData) {
    const newComment = {
      id: Date.now(),
      text: formData.get('comment'),
      author: 'You',
      timestamp: new Date().toISOString()
    };
    
    // Show immediately
    addOptimisticComment(newComment);
    
    // Send to server
    await addComment(newComment);
  }

  return (
    <div>
      {optimisticComments.map(comment => (
        <div 
          key={comment.id} 
          className={comment.pending ? 'opacity-50' : ''}
        >
          <strong>{comment.author}</strong>: {comment.text}
          {comment.pending && <span> (Sending...)</span>}
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

### Todo List with Optimistic Toggle

```javascript
'use client';
import { useOptimistic } from 'react';

function TodoList({ todos, toggleTodo }) {
  const [optimisticTodos, toggleOptimistic] = useOptimistic(
    todos,
    (state, todoId) => state.map(todo =>
      todo.id === todoId 
        ? { ...todo, completed: !todo.completed, pending: true }
        : todo
    )
  );

  async function handleToggle(todoId) {
    toggleOptimistic(todoId);
    await toggleTodo(todoId);
  }

  return (
    <ul>
      {optimisticTodos.map(todo => (
        <li key={todo.id} style={{ opacity: todo.pending ? 0.6 : 1 }}>
          <input
            type="checkbox"
            checked={todo.completed}
            onChange={() => handleToggle(todo.id)}
          />
          {todo.text}
        </li>
      ))}
    </ul>
  );
}
```

### With Error Handling

```javascript
'use client';
import { useOptimistic, useState } from 'react';

function LikeButton({ postId, initialLikes }) {
  const [likes, setLikes] = useState(initialLikes);
  const [error, setError] = useState(null);
  const [optimisticLikes, addOptimistic] = useOptimistic(likes);

  async function handleLike() {
    setError(null);
    addOptimistic(likes + 1);
    
    try {
      const newLikes = await likePost(postId);
      setLikes(newLikes); // Update real state
    } catch (err) {
      setError('Failed to like post');
      // Optimistic state automatically reverts
    }
  }

  return (
    <div>
      <button onClick={handleLike}>❤️ {optimisticLikes}</button>
      {error && <p className="error">{error}</p>}
    </div>
  );
}
```

### Key Behaviors

- Optimistic state automatically reverts when `passthrough` changes
- Updates are immediate (no waiting for server)
- Great for perceived performance
- Should be paired with real state updates

---

## use()

Read promises or context conditionally (breaks hook rules).

### Signature

```typescript
function use<T>(resource: Promise<T> | Context<T>): T
```

### Parameters

- **resource**: Promise or Context to read

### Returns

- Resolved value of promise, or current context value

### Reading Promises

```javascript
import { use, Suspense } from 'react';

function UserProfile({ userPromise }) {
  // Can be called conditionally!
  const user = use(userPromise);
  
  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.bio}</p>
    </div>
  );
}

function App({ userId }) {
  // Create promise outside render
  const userPromise = fetchUser(userId);
  
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <UserProfile userPromise={userPromise} />
    </Suspense>
  );
}
```

### Conditional Promise Reading

```javascript
import { use } from 'react';

function Message({ messagePromise, isPreview }) {
  // ✅ Can use conditionally (unlike hooks!)
  if (!isPreview) {
    const message = use(messagePromise);
    return <div>{message.text}</div>;
  }
  
  return <div>Preview mode</div>;
}
```

### Reading Context

```javascript
import { use } from 'react';

function Button({ children }) {
  // ✅ Can call after early return (unlike useContext!)
  if (children === null) {
    return null;
  }
  
  const theme = use(ThemeContext);
  
  return (
    <button style={{ color: theme.color }}>
      {children}
    </button>
  );
}
```

### In Loops

```javascript
import { use } from 'react';

function UserList({ userPromises }) {
  return (
    <ul>
      {userPromises.map((promise, index) => {
        // ✅ Can call in loops (unlike hooks!)
        const user = use(promise);
        return <li key={index}>{user.name}</li>;
      })}
    </ul>
  );
}
```

### With Parallel Fetching

```javascript
import { use, Suspense } from 'react';

function Dashboard() {
  // Start all fetches in parallel
  const revenuePromise = fetchRevenue();
  const usersPromise = fetchUsers();
  const ordersPromise = fetchOrders();
  
  return (
    <div className="dashboard">
      <Suspense fallback={<Skeleton />}>
        <RevenueCard promise={revenuePromise} />
      </Suspense>
      
      <Suspense fallback={<Skeleton />}>
        <UsersCard promise={usersPromise} />
      </Suspense>
      
      <Suspense fallback={<Skeleton />}>
        <OrdersCard promise={ordersPromise} />
      </Suspense>
    </div>
  );
}

function RevenueCard({ promise }) {
  const revenue = use(promise);
  return <div>Revenue: ${revenue}</div>;
}
```

### Key Behaviors

- **NOT a hook** - Can be called conditionally, in loops, after returns
- Suspends component until promise resolves
- Must be wrapped in Suspense boundary
- Promise should be created outside render (not inside component)

---

## useTransition

Mark state updates as non-urgent.

### Signature

```typescript
function useTransition(): [isPending: boolean, startTransition: (callback: () => void) => void]
```

### Returns

Array with two elements:
1. **isPending**: Boolean indicating if transition is pending
2. **startTransition**: Function to wrap state updates

### Basic Example

```javascript
import { useState, useTransition } from 'react';

function SearchResults() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isPending, startTransition] = useTransition();

  function handleSearch(value) {
    setQuery(value); // Urgent: update input
    
    startTransition(() => {
      // Non-urgent: update results
      setResults(filterResults(value));
    });
  }

  return (
    <div>
      <input 
        value={query} 
        onChange={e => handleSearch(e.target.value)}
        placeholder="Search..."
      />
      {isPending && <Spinner />}
      <ResultsList results={results} />
    </div>
  );
}
```

### With Actions

```javascript
import { useTransition } from 'react';

function UpdateButton({ updateData }) {
  const [isPending, startTransition] = useTransition();

  function handleClick() {
    startTransition(async () => {
      await updateData(); // Async action
    });
  }

  return (
    <button onClick={handleClick} disabled={isPending}>
      {isPending ? 'Updating...' : 'Update'}
    </button>
  );
}
```

### Tab Switching

```javascript
import { useState, useTransition } from 'react';

function TabContainer() {
  const [activeTab, setActiveTab] = useState('home');
  const [isPending, startTransition] = useTransition();

  function selectTab(tab) {
    startTransition(() => {
      setActiveTab(tab);
    });
  }

  return (
    <div>
      <TabButton 
        isActive={activeTab === 'home'} 
        onClick={() => selectTab('home')}
      >
        Home
      </TabButton>
      <TabButton 
        isActive={activeTab === 'posts'} 
        onClick={() => selectTab('posts')}
      >
        Posts {isPending && '⏳'}
      </TabButton>
      
      <hr />
      
      {activeTab === 'home' && <HomePage />}
      {activeTab === 'posts' && <PostsPage />}
    </div>
  );
}
```

### Key Behaviors

- State updates inside `startTransition` are non-blocking
- UI remains responsive during transition
- Can be interrupted by urgent updates
- Automatically used by `useActionState`

---

## Comparison Table

| Hook | Purpose | Async Support | Form Integration | Pending State |
|------|---------|---------------|------------------|---------------|
| `useActionState` | Form state + submissions | ✅ Built-in | ✅ Native | ✅ Automatic |
| `useOptimistic` | Optimistic UI updates | ✅ With manual state | ❌ Manual | ❌ Manual |
| `use()` | Read promises/context | ✅ Built-in | ❌ | ❌ (use Suspense) |
| `useTransition` | Non-urgent updates | ✅ Built-in | ❌ Manual | ✅ Automatic |

---

## Best Practices

### useActionState
- ✅ Use for all forms with async submissions
- ✅ Return error objects for validation feedback
- ✅ Use `redirect()` for success navigation
- ❌ Don't nest actions (use Server Actions instead)

### useOptimistic
- ✅ Use for instant feedback (likes, toggles, comments)
- ✅ Always pair with real state updates
- ✅ Show visual difference (opacity, pending indicator)
- ❌ Don't use for critical data (payments, deletions)

### use()
- ✅ Create promises outside render
- ✅ Wrap in Suspense boundary
- ✅ Use for conditional data loading
- ❌ Don't create promises inside component

### useTransition
- ✅ Use for non-urgent updates (filtering, tab switching)
- ✅ Show pending state during transitions
- ✅ Keep urgent updates outside `startTransition`
- ❌ Don't wrap all state updates (only slow ones)

---

## When to Use What

| Scenario | Use This |
|----------|----------|
| Form submission | `useActionState` |
| Like button | `useOptimistic` |
| Comment posting | `useOptimistic` + `useActionState` |
| Data fetching | `use()` + Suspense |
| Tab switching | `useTransition` |
| Search filtering | `useTransition` |
| Server mutation | `useActionState` + Server Actions |
| Real-time updates | `useOptimistic` |
