---
name: state-management
description: Implement state management patterns for frontend applications. Use when managing global state, handling complex data flows, or coordinating state across components. Handles React Context, Redux, Zustand, Recoil, and state management best practices.
metadata:
  tags: state-management, React, Redux, Context, Zustand, Recoil, global-state
  platforms: Claude, ChatGPT, Gemini
---


# State Management


## When to use this skill

- **Global State Required**: Multiple components share the same data
- **Props Drilling Problem**: Passing props through 5+ levels
- **Complex State Logic**: Authentication, shopping cart, themes, etc.
- **State Synchronization**: Sync server data with client state

## Instructions

### Step 1: Determine State Scope

Distinguish between local and global state.

**Decision Criteria**:
- **Local State**: Used only within a single component
  - Form input values, toggle states, dropdown open/close
  - Use `useState`, `useReducer`

- **Global State**: Shared across multiple components
  - User authentication, shopping cart, theme, language settings
  - Use Context API, Redux, Zustand

**Example**:
```tsx
// ✅ Local state (single component)
function SearchBox() {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => setIsOpen(true)}
      />
      {isOpen && <SearchResults query={query} />}
    </div>
  );
}

// ✅ Global state (multiple components)
// User authentication info is used in Header, Profile, Settings, etc.
const { user, logout } = useAuth();  // Context or Zustand
```

### Step 2: React Context API (Simple Global State)

Suitable for lightweight global state management.

**Example** (Authentication Context):
```tsx
// contexts/AuthContext.tsx
import { createContext, useContext, useState, ReactNode } from 'react';

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const login = async (email: string, password: string) => {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    const data = await response.json();
    setUser(data.user);
    localStorage.setItem('token', data.token);
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('token');
  };

  return (
    <AuthContext.Provider value={{
      user,
      login,
      logout,
      isAuthenticated: !!user
    }}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

**Usage**:
```tsx
// App.tsx
function App() {
  return (
    <AuthProvider>
      <Router>
        <Header />
        <Routes />
      </Router>
    </AuthProvider>
  );
}

// Header.tsx
function Header() {
  const { user, logout, isAuthenticated } = useAuth();

  return (
    <header>
      {isAuthenticated ? (
        <>
          <span>Welcome, {user!.name}</span>
          <button onClick={logout}>Logout</button>
        </>
      ) : (
        <Link to="/login">Login</Link>
      )}
    </header>
  );
}
```

### Step 3: Zustand (Modern and Concise State Management)

Simpler than Redux with less boilerplate.

**Installation**:
```bash
npm install zustand
```

**Example** (Shopping Cart):
```tsx
// stores/cartStore.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
}

interface CartStore {
  items: CartItem[];
  addItem: (item: Omit<CartItem, 'quantity'>) => void;
  removeItem: (id: string) => void;
  updateQuantity: (id: string, quantity: number) => void;
  clearCart: () => void;
  total: () => number;
}

export const useCartStore = create<CartStore>()(
  devtools(
    persist(
      (set, get) => ({
        items: [],

        addItem: (item) => set((state) => {
          const existing = state.items.find(i => i.id === item.id);
          if (existing) {
            return {
              items: state.items.map(i =>
                i.id === item.id
                  ? { ...i, quantity: i.quantity + 1 }
                  : i
              )
            };
          }
          return { items: [...state.items, { ...item, quantity: 1 }] };
        }),

        removeItem: (id) => set((state) => ({
          items: state.items.filter(item => item.id !== id)
        })),

        updateQuantity: (id, quantity) => set((state) => ({
          items: state.items.map(item =>
            item.id === id ? { ...item, quantity } : item
          )
        })),

        clearCart: () => set({ items: [] }),

        total: () => {
          const { items } = get();
          return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
        }
      }),
      { name: 'cart-storage' }  // localStorage key
    )
  )
);
```

**Usage**:
```tsx
// components/ProductCard.tsx
function ProductCard({ product }) {
  const addItem = useCartStore(state => state.addItem);

  return (
    <div>
      <h3>{product.name}</h3>
      <p>${product.price}</p>
      <button onClick={() => addItem(product)}>
        Add to Cart
      </button>
    </div>
  );
}

// components/Cart.tsx
function Cart() {
  const items = useCartStore(state => state.items);
  const total = useCartStore(state => state.total());
  const removeItem = useCartStore(state => state.removeItem);

  return (
    <div>
      <h2>Cart</h2>
      {items.map(item => (
        <div key={item.id}>
          <span>{item.name} x {item.quantity}</span>
          <span>${item.price * item.quantity}</span>
          <button onClick={() => removeItem(item.id)}>Remove</button>
        </div>
      ))}
      <p>Total: ${total.toFixed(2)}</p>
    </div>
  );
}
```

### Step 4: Redux Toolkit (Large-Scale Apps)

Use when complex state logic and middleware are required.

**Installation**:
```bash
npm install @reduxjs/toolkit react-redux
```

**Example** (Todo):
```tsx
// store/todosSlice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';

interface Todo {
  id: string;
  text: string;
  completed: boolean;
}

interface TodosState {
  items: Todo[];
  status: 'idle' | 'loading' | 'failed';
}

const initialState: TodosState = {
  items: [],
  status: 'idle'
};

// Async action
export const fetchTodos = createAsyncThunk('todos/fetch', async () => {
  const response = await fetch('/api/todos');
  return response.json();
});

const todosSlice = createSlice({
  name: 'todos',
  initialState,
  reducers: {
    addTodo: (state, action: PayloadAction<string>) => {
      state.items.push({
        id: Date.now().toString(),
        text: action.payload,
        completed: false
      });
    },
    toggleTodo: (state, action: PayloadAction<string>) => {
      const todo = state.items.find(t => t.id === action.payload);
      if (todo) {
        todo.completed = !todo.completed;
      }
    },
    removeTodo: (state, action: PayloadAction<string>) => {
      state.items = state.items.filter(t => t.id !== action.payload);
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchTodos.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchTodos.fulfilled, (state, action) => {
        state.status = 'idle';
        state.items = action.payload;
      })
      .addCase(fetchTodos.rejected, (state) => {
        state.status = 'failed';
      });
  }
});

export const { addTodo, toggleTodo, removeTodo } = todosSlice.actions;
export default todosSlice.reducer;

// store/index.ts
import { configureStore } from '@reduxjs/toolkit';
import todosReducer from './todosSlice';

export const store = configureStore({
  reducer: {
    todos: todosReducer
  }
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

**Usage**:
```tsx
// App.tsx
import { Provider } from 'react-redux';
import { store } from './store';

function App() {
  return (
    <Provider store={store}>
      <TodoApp />
    </Provider>
  );
}

// components/TodoList.tsx
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../store';
import { toggleTodo, removeTodo } from '../store/todosSlice';

function TodoList() {
  const todos = useSelector((state: RootState) => state.todos.items);
  const dispatch = useDispatch();

  return (
    <ul>
      {todos.map(todo => (
        <li key={todo.id}>
          <input
            type="checkbox"
            checked={todo.completed}
            onChange={() => dispatch(toggleTodo(todo.id))}
          />
          <span style={{ textDecoration: todo.completed ? 'line-through' : 'none' }}>
            {todo.text}
          </span>
          <button onClick={() => dispatch(removeTodo(todo.id))}>Delete</button>
        </li>
      ))}
    </ul>
  );
}
```

### Step 5: Server State Management (React Query / TanStack Query)

Specialized for API data fetching and caching.

```tsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

function UserProfile({ userId }: { userId: string }) {
  const queryClient = useQueryClient();

  // GET: Fetch user info
  const { data: user, isLoading, error } = useQuery({
    queryKey: ['user', userId],
    queryFn: async () => {
      const res = await fetch(`/api/users/${userId}`);
      return res.json();
    },
    staleTime: 5 * 60 * 1000,  // Cache for 5 minutes
  });

  // POST: Update user info
  const mutation = useMutation({
    mutationFn: async (updatedUser: Partial<User>) => {
      const res = await fetch(`/api/users/${userId}`, {
        method: 'PATCH',
        body: JSON.stringify(updatedUser)
      });
      return res.json();
    },
    onSuccess: () => {
      // Invalidate cache and refetch
      queryClient.invalidateQueries({ queryKey: ['user', userId] });
    }
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <h2>{user.name}</h2>
      <p>{user.email}</p>
      <button onClick={() => mutation.mutate({ name: 'New Name' })}>
        Update Name
      </button>
    </div>
  );
}
```

## Output format

### State Management Tool Selection Guide

```
Recommended tools by scenario:

1. Simple global state (theme, language)
   → React Context API

2. Medium complexity (shopping cart, user settings)
   → Zustand

3. Large-scale apps, complex logic, middleware required
   → Redux Toolkit

4. Server data fetching/caching
   → React Query (TanStack Query)

5. Form state
   → React Hook Form + Zod
```

## Constraints

### Required Rules (MUST)

1. **State Immutability**: Never mutate state directly
   ```tsx
   // ❌ Bad example
   state.items.push(newItem);

   // ✅ Good example
   setState({ items: [...state.items, newItem] });
   ```

2. **Minimal State Principle**: Do not store derivable values in state
   ```tsx
   // ❌ Bad example
   const [items, setItems] = useState([]);
   const [count, setCount] = useState(0);  // Can be calculated as items.length

   // ✅ Good example
   const [items, setItems] = useState([]);
   const count = items.length;  // Derived value
   ```

3. **Single Source of Truth**: Do not duplicate the same data in multiple places

### Prohibited Rules (MUST NOT)

1. **Excessive Props Drilling**: Prohibited when passing props through 5+ levels
   - Use Context or a state management library

2. **Avoid Making Everything Global State**: Prefer local state when sufficient

## Best practices

1. **Selective Subscription**: Subscribe only to the state you need
   ```tsx
   // ✅ Good: only what you need
   const items = useCartStore(state => state.items);

   // ❌ Bad: subscribing to everything
   const { items, addItem, removeItem, updateQuantity, clearCart } = useCartStore();
   ```

2. **Clear Action Names**: `update` → `updateUserProfile`

3. **Use TypeScript**: Ensure type safety

## References

- [Zustand](https://zustand-demo.pmnd.rs/)
- [Redux Toolkit](https://redux-toolkit.js.org/)
- [React Query](https://tanstack.com/query/latest)
- [Jotai](https://jotai.org/)
- [Recoil](https://recoiljs.org/)

## Metadata

### Version
- **Current Version**: 1.0.0
- **Last Updated**: 2025-01-01
- **Compatible Platforms**: Claude, ChatGPT, Gemini

### Related Skills
- [ui-component-patterns](../ui-component-patterns/SKILL.md): Component and state integration
- [backend-testing](../../backend/backend-testing/SKILL.md): Testing state logic

### Tags
`#state-management` `#React` `#Redux` `#Zustand` `#Context` `#global-state` `#frontend`

## Examples

### Example 1: Basic usage
<!-- Add example content here -->

### Example 2: Advanced usage
<!-- Add advanced example content here -->
