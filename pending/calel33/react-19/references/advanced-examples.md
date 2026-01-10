# React 19 Advanced Examples

Production-ready examples demonstrating real-world React 19 patterns.

---

## Full-Stack Todo App

Complete todo application with Server Actions, useOptimistic, and database persistence.

### Server Actions (app/actions.js)

```javascript
'use server';
import { revalidatePath } from 'next/cache';
import { z } from 'zod';
import { db } from '@/lib/db';
import { getCurrentUser } from '@/lib/auth';

const todoSchema = z.object({
  text: z.string().min(1, 'Todo cannot be empty').max(200),
  priority: z.enum(['low', 'medium', 'high']).optional()
});

export async function createTodo(prevState, formData) {
  const user = await getCurrentUser();
  if (!user) {
    return { error: 'Unauthorized' };
  }

  const result = todoSchema.safeParse({
    text: formData.get('text'),
    priority: formData.get('priority') || 'medium'
  });

  if (!result.success) {
    return { 
      error: result.error.flatten().fieldErrors 
    };
  }

  try {
    await db.todos.create({
      userId: user.id,
      text: result.data.text,
      priority: result.data.priority,
      completed: false,
      createdAt: new Date()
    });

    revalidatePath('/todos');
    return { success: true };
  } catch (error) {
    return { error: 'Failed to create todo' };
  }
}

export async function toggleTodo(todoId) {
  const user = await getCurrentUser();
  if (!user) throw new Error('Unauthorized');

  const todo = await db.todos.findById(todoId);
  
  if (todo.userId !== user.id) {
    throw new Error('Forbidden');
  }

  await db.todos.update(todoId, {
    completed: !todo.completed
  });

  revalidatePath('/todos');
}

export async function deleteTodo(todoId) {
  const user = await getCurrentUser();
  if (!user) throw new Error('Unauthorized');

  const todo = await db.todos.findById(todoId);
  
  if (todo.userId !== user.id) {
    throw new Error('Forbidden');
  }

  await db.todos.delete(todoId);
  revalidatePath('/todos');
}
```

### Client Component (app/todos/page.js)

```javascript
'use client';
import { useActionState, useOptimistic, useState } from 'react';
import { createTodo, toggleTodo, deleteTodo } from './actions';

export function TodoList({ initialTodos }) {
  const [todos, setTodos] = useState(initialTodos);
  const [optimisticTodos, updateOptimistic] = useOptimistic(
    todos,
    (state, { action, todo, id }) => {
      switch (action) {
        case 'add':
          return [...state, { ...todo, pending: true }];
        case 'toggle':
          return state.map(t => 
            t.id === id ? { ...t, completed: !t.completed, pending: true } : t
          );
        case 'delete':
          return state.filter(t => t.id !== id);
        default:
          return state;
      }
    }
  );

  const [formState, formAction, isPending] = useActionState(
    async (prevState, formData) => {
      const newTodo = {
        id: Date.now(),
        text: formData.get('text'),
        priority: formData.get('priority'),
        completed: false
      };

      updateOptimistic({ action: 'add', todo: newTodo });
      
      const result = await createTodo(prevState, formData);
      
      if (result.success) {
        setTodos(prev => [...prev, newTodo]);
        return {};
      }
      
      return result;
    },
    {}
  );

  async function handleToggle(id) {
    updateOptimistic({ action: 'toggle', id });
    
    try {
      await toggleTodo(id);
      setTodos(prev => prev.map(t => 
        t.id === id ? { ...t, completed: !t.completed } : t
      ));
    } catch (error) {
      console.error('Failed to toggle:', error);
    }
  }

  async function handleDelete(id) {
    updateOptimistic({ action: 'delete', id });
    
    try {
      await deleteTodo(id);
      setTodos(prev => prev.filter(t => t.id !== id));
    } catch (error) {
      console.error('Failed to delete:', error);
    }
  }

  return (
    <div className="todo-app">
      <form action={formAction} className="add-todo">
        <input 
          name="text" 
          placeholder="What needs to be done?" 
          required 
        />
        <select name="priority" defaultValue="medium">
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
        <button type="submit" disabled={isPending}>
          {isPending ? 'Adding...' : 'Add'}
        </button>
        {formState.error && <p className="error">{formState.error}</p>}
      </form>

      <ul className="todo-list">
        {optimisticTodos.map(todo => (
          <li 
            key={todo.id} 
            className={`todo-item priority-${todo.priority} ${todo.pending ? 'pending' : ''}`}
          >
            <input
              type="checkbox"
              checked={todo.completed}
              onChange={() => handleToggle(todo.id)}
            />
            <span className={todo.completed ? 'completed' : ''}>
              {todo.text}
            </span>
            <button onClick={() => handleDelete(todo.id)}>
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### Server Component (app/todos/layout.js)

```javascript
import { db } from '@/lib/db';
import { getCurrentUser } from '@/lib/auth';
import { TodoList } from './page';

export default async function TodosPage() {
  const user = await getCurrentUser();
  
  if (!user) {
    redirect('/login');
  }

  const todos = await db.todos.findMany({
    where: { userId: user.id },
    orderBy: { createdAt: 'desc' }
  });

  return (
    <div>
      <h1>My Todos</h1>
      <TodoList initialTodos={todos} />
    </div>
  );
}
```

---

## Streaming Dashboard with Suspense

Progressive rendering dashboard with parallel data fetching.

### Server Components (app/dashboard/page.js)

```javascript
import { Suspense } from 'react';
import { 
  RevenueCard, 
  UsersCard, 
  OrdersCard, 
  ChartCard 
} from './components';

export default function DashboardPage() {
  return (
    <div className="dashboard">
      <h1>Analytics Dashboard</h1>
      
      {/* Each card loads independently */}
      <div className="grid">
        <Suspense fallback={<CardSkeleton title="Revenue" />}>
          <RevenueCard />
        </Suspense>
        
        <Suspense fallback={<CardSkeleton title="Users" />}>
          <UsersCard />
        </Suspense>
        
        <Suspense fallback={<CardSkeleton title="Orders" />}>
          <OrdersCard />
        </Suspense>
      </div>

      <Suspense fallback={<ChartSkeleton />}>
        <ChartCard />
      </Suspense>
    </div>
  );
}
```

### Async Components (app/dashboard/components.js)

```javascript
import { db } from '@/lib/db';

export async function RevenueCard() {
  // Simulated slow query
  const revenue = await db.analytics.getRevenue();
  
  return (
    <div className="card revenue">
      <h3>Revenue</h3>
      <p className="stat">${revenue.total.toLocaleString()}</p>
      <span className={revenue.change >= 0 ? 'positive' : 'negative'}>
        {revenue.change >= 0 ? '+' : ''}{revenue.change}% from last month
      </span>
    </div>
  );
}

export async function UsersCard() {
  const users = await db.analytics.getUsers();
  
  return (
    <div className="card users">
      <h3>Active Users</h3>
      <p className="stat">{users.active.toLocaleString()}</p>
      <span className="substat">
        {users.new} new this week
      </span>
    </div>
  );
}

export async function OrdersCard() {
  const orders = await db.analytics.getOrders();
  
  return (
    <div className="card orders">
      <h3>Orders</h3>
      <p className="stat">{orders.total.toLocaleString()}</p>
      <span className="substat">
        {orders.pending} pending
      </span>
    </div>
  );
}

export async function ChartCard() {
  // Very slow query
  await new Promise(resolve => setTimeout(resolve, 2000));
  const data = await db.analytics.getChartData();
  
  return (
    <div className="card chart">
      <h3>Sales Over Time</h3>
      <LineChart data={data} />
    </div>
  );
}
```

### Skeleton Components

```javascript
export function CardSkeleton({ title }) {
  return (
    <div className="card skeleton">
      <h3>{title}</h3>
      <div className="skeleton-stat" />
      <div className="skeleton-text" />
    </div>
  );
}

export function ChartSkeleton() {
  return (
    <div className="card skeleton chart">
      <h3>Sales Over Time</h3>
      <div className="skeleton-chart" />
    </div>
  );
}
```

---

## Advanced Form with File Upload

Multi-step form with file upload, validation, and progress tracking.

### Server Action (app/profile/actions.js)

```javascript
'use server';
import { z } from 'zod';
import { writeFile } from 'fs/promises';
import { join } from 'path';

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

const profileSchema = z.object({
  name: z.string().min(2, 'Name too short').max(50),
  email: z.string().email('Invalid email'),
  bio: z.string().max(500).optional(),
  avatar: z.instanceof(File).optional()
});

export async function updateProfile(prevState, formData) {
  const user = await getCurrentUser();
  if (!user) {
    return { error: 'Unauthorized' };
  }

  // Validate file size
  const avatar = formData.get('avatar');
  if (avatar && avatar.size > MAX_FILE_SIZE) {
    return { 
      error: 'File too large (max 5MB)' 
    };
  }

  // Validate data
  const result = profileSchema.safeParse({
    name: formData.get('name'),
    email: formData.get('email'),
    bio: formData.get('bio'),
    avatar
  });

  if (!result.success) {
    return { 
      errors: result.error.flatten().fieldErrors 
    };
  }

  try {
    let avatarPath = user.avatar;

    // Upload avatar if provided
    if (avatar && avatar.size > 0) {
      const bytes = await avatar.arrayBuffer();
      const buffer = Buffer.from(bytes);
      const filename = `${user.id}-${Date.now()}.${avatar.name.split('.').pop()}`;
      const path = join(process.cwd(), 'public/uploads', filename);
      
      await writeFile(path, buffer);
      avatarPath = `/uploads/${filename}`;
    }

    // Update database
    await db.users.update(user.id, {
      name: result.data.name,
      email: result.data.email,
      bio: result.data.bio,
      avatar: avatarPath
    });

    revalidatePath('/profile');
    return { success: true };
  } catch (error) {
    console.error(error);
    return { error: 'Failed to update profile' };
  }
}
```

### Client Component (app/profile/edit/page.js)

```javascript
'use client';
import { useActionState, useState } from 'react';
import { updateProfile } from '../actions';

export function ProfileEditForm({ user }) {
  const [preview, setPreview] = useState(user.avatar);
  const [state, formAction, isPending] = useActionState(updateProfile, {});

  function handleFileChange(e) {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => setPreview(reader.result);
      reader.readAsDataURL(file);
    }
  }

  return (
    <form action={formAction} className="profile-form">
      <div className="avatar-upload">
        <img 
          src={preview} 
          alt="Avatar preview" 
          className="avatar-preview"
        />
        <input 
          type="file" 
          name="avatar" 
          accept="image/*"
          onChange={handleFileChange}
        />
      </div>

      <div className="form-group">
        <label htmlFor="name">Name</label>
        <input 
          id="name"
          name="name" 
          defaultValue={user.name}
          required 
        />
        {state.errors?.name && (
          <span className="error">{state.errors.name}</span>
        )}
      </div>

      <div className="form-group">
        <label htmlFor="email">Email</label>
        <input 
          id="email"
          name="email" 
          type="email"
          defaultValue={user.email}
          required 
        />
        {state.errors?.email && (
          <span className="error">{state.errors.email}</span>
        )}
      </div>

      <div className="form-group">
        <label htmlFor="bio">Bio</label>
        <textarea 
          id="bio"
          name="bio" 
          rows={4}
          defaultValue={user.bio}
          maxLength={500}
        />
        {state.errors?.bio && (
          <span className="error">{state.errors.bio}</span>
        )}
      </div>

      <button type="submit" disabled={isPending}>
        {isPending ? 'Saving...' : 'Save Changes'}
      </button>

      {state.success && (
        <p className="success">Profile updated successfully!</p>
      )}
      {state.error && (
        <p className="error">{state.error}</p>
      )}
    </form>
  );
}
```

---

## Real-Time Collaborative Comments

Optimistic updates with conflict resolution for collaborative features.

### Server Actions (app/posts/[id]/actions.js)

```javascript
'use server';
import { revalidatePath } from 'next/cache';

export async function addComment(postId, prevState, formData) {
  const user = await getCurrentUser();
  if (!user) {
    return { error: 'Please log in to comment' };
  }

  const text = formData.get('comment');
  if (!text || text.trim().length === 0) {
    return { error: 'Comment cannot be empty' };
  }

  try {
    const comment = await db.comments.create({
      postId,
      userId: user.id,
      text: text.trim(),
      createdAt: new Date()
    });

    revalidatePath(`/posts/${postId}`);
    return { success: true, comment };
  } catch (error) {
    return { error: 'Failed to add comment' };
  }
}

export async function editComment(commentId, text) {
  const user = await getCurrentUser();
  if (!user) throw new Error('Unauthorized');

  const comment = await db.comments.findById(commentId);
  if (comment.userId !== user.id) {
    throw new Error('Forbidden');
  }

  const updated = await db.comments.update(commentId, {
    text,
    editedAt: new Date()
  });

  revalidatePath(`/posts/${comment.postId}`);
  return updated;
}

export async function deleteComment(commentId) {
  const user = await getCurrentUser();
  if (!user) throw new Error('Unauthorized');

  const comment = await db.comments.findById(commentId);
  if (comment.userId !== user.id && !user.isAdmin) {
    throw new Error('Forbidden');
  }

  await db.comments.delete(commentId);
  revalidatePath(`/posts/${comment.postId}`);
}
```

### Client Component

```javascript
'use client';
import { useActionState, useOptimistic, useState } from 'react';
import { addComment, editComment, deleteComment } from './actions';

export function CommentSection({ postId, initialComments, currentUser }) {
  const [comments, setComments] = useState(initialComments);
  const [editingId, setEditingId] = useState(null);

  const [optimisticComments, updateOptimistic] = useOptimistic(
    comments,
    (state, { type, comment, id, text }) => {
      switch (type) {
        case 'add':
          return [...state, { ...comment, pending: true }];
        case 'edit':
          return state.map(c => 
            c.id === id ? { ...c, text, pending: true } : c
          );
        case 'delete':
          return state.filter(c => c.id !== id);
        default:
          return state;
      }
    }
  );

  const [formState, formAction, isPending] = useActionState(
    async (prevState, formData) => {
      const newComment = {
        id: Date.now(),
        text: formData.get('comment'),
        userId: currentUser.id,
        userName: currentUser.name,
        userAvatar: currentUser.avatar,
        createdAt: new Date().toISOString()
      };

      updateOptimistic({ type: 'add', comment: newComment });
      
      const result = await addComment(postId, prevState, formData);
      
      if (result.success) {
        setComments(prev => [...prev, result.comment]);
        return {};
      }
      
      return result;
    },
    {}
  );

  async function handleEdit(id, text) {
    updateOptimistic({ type: 'edit', id, text });
    
    try {
      const updated = await editComment(id, text);
      setComments(prev => prev.map(c => c.id === id ? updated : c));
      setEditingId(null);
    } catch (error) {
      console.error('Failed to edit:', error);
    }
  }

  async function handleDelete(id) {
    if (!confirm('Delete this comment?')) return;
    
    updateOptimistic({ type: 'delete', id });
    
    try {
      await deleteComment(id);
      setComments(prev => prev.filter(c => c.id !== id));
    } catch (error) {
      console.error('Failed to delete:', error);
    }
  }

  return (
    <div className="comments">
      <h3>{optimisticComments.length} Comments</h3>

      <form action={formAction} className="comment-form">
        <textarea 
          name="comment"
          placeholder="Add a comment..."
          required
        />
        <button type="submit" disabled={isPending}>
          {isPending ? 'Posting...' : 'Post'}
        </button>
        {formState.error && (
          <p className="error">{formState.error}</p>
        )}
      </form>

      <div className="comment-list">
        {optimisticComments.map(comment => (
          <Comment
            key={comment.id}
            comment={comment}
            isOwner={comment.userId === currentUser?.id}
            isEditing={editingId === comment.id}
            onEdit={(text) => handleEdit(comment.id, text)}
            onDelete={() => handleDelete(comment.id)}
            onStartEdit={() => setEditingId(comment.id)}
            onCancelEdit={() => setEditingId(null)}
          />
        ))}
      </div>
    </div>
  );
}

function Comment({ 
  comment, 
  isOwner, 
  isEditing, 
  onEdit, 
  onDelete, 
  onStartEdit, 
  onCancelEdit 
}) {
  const [editText, setEditText] = useState(comment.text);

  if (isEditing) {
    return (
      <div className="comment editing">
        <textarea
          value={editText}
          onChange={(e) => setEditText(e.target.value)}
        />
        <button onClick={() => onEdit(editText)}>Save</button>
        <button onClick={onCancelEdit}>Cancel</button>
      </div>
    );
  }

  return (
    <div className={`comment ${comment.pending ? 'pending' : ''}`}>
      <img src={comment.userAvatar} alt="" className="avatar" />
      <div className="content">
        <strong>{comment.userName}</strong>
        <p>{comment.text}</p>
        <span className="timestamp">
          {new Date(comment.createdAt).toLocaleString()}
          {comment.editedAt && ' (edited)'}
        </span>
        {isOwner && (
          <div className="actions">
            <button onClick={onStartEdit}>Edit</button>
            <button onClick={onDelete}>Delete</button>
          </div>
        )}
      </div>
    </div>
  );
}
```

---

## Progressive Search with Debouncing

Search with instant results using transitions and debouncing.

```javascript
'use client';
import { useState, useTransition, useEffect } from 'react';
import { searchProducts } from './actions';

export function ProductSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isPending, startTransition] = useTransition();

  useEffect(() => {
    if (query.length === 0) {
      setResults([]);
      return;
    }

    const timer = setTimeout(() => {
      startTransition(async () => {
        const products = await searchProducts(query);
        setResults(products);
      });
    }, 300); // Debounce 300ms

    return () => clearTimeout(timer);
  }, [query]);

  return (
    <div className="search">
      <input
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search products..."
      />
      
      {isPending && <div className="loading">Searching...</div>}
      
      <div className="results">
        {results.length === 0 && query && !isPending && (
          <p>No results found</p>
        )}
        
        {results.map(product => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </div>
  );
}
```

---

## Resources

These examples demonstrate:
- ✅ Server Actions with authentication
- ✅ Optimistic updates with conflict resolution
- ✅ Streaming with Suspense boundaries
- ✅ File uploads with validation
- ✅ Real-time collaborative features
- ✅ Progressive search with debouncing

For more examples, see:
- [React 19 Docs](https://react.dev)
- [Next.js Examples](https://github.com/vercel/next.js/tree/canary/examples)
