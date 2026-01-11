# Zustand Reference

## Basic Store

```typescript
import { create } from 'zustand';

interface CounterStore {
  count: number;
  increment: () => void;
  decrement: () => void;
  reset: () => void;
}

export const useCounterStore = create<CounterStore>((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 })),
  reset: () => set({ count: 0 }),
}));
```

## With Immer (for nested updates)

```typescript
import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';

interface TodoStore {
  todos: Todo[];
  addTodo: (text: string) => void;
  toggleTodo: (id: string) => void;
}

export const useTodoStore = create<TodoStore>()(
  immer((set) => ({
    todos: [],
    addTodo: (text) =>
      set((state) => {
        state.todos.push({ id: crypto.randomUUID(), text, done: false });
      }),
    toggleTodo: (id) =>
      set((state) => {
        const todo = state.todos.find((t) => t.id === id);
        if (todo) todo.done = !todo.done;
      }),
  }))
);
```

## With Persist

```typescript
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

interface AuthStore {
  token: string | null;
  setToken: (token: string) => void;
  clearToken: () => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      token: null,
      setToken: (token) => set({ token }),
      clearToken: () => set({ token: null }),
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({ token: state.token }),
    }
  )
);
```

## Slices Pattern (for large stores)

```typescript
// slices/user-slice.ts
export interface UserSlice {
  user: User | null;
  setUser: (user: User) => void;
}

export const createUserSlice: StateCreator<UserSlice> = (set) => ({
  user: null,
  setUser: (user) => set({ user }),
});

// slices/ui-slice.ts
export interface UISlice {
  theme: 'light' | 'dark';
  setTheme: (theme: 'light' | 'dark') => void;
}

export const createUISlice: StateCreator<UISlice> = (set) => ({
  theme: 'light',
  setTheme: (theme) => set({ theme }),
});

// store.ts
import { create } from 'zustand';

type Store = UserSlice & UISlice;

export const useStore = create<Store>()((...a) => ({
  ...createUserSlice(...a),
  ...createUISlice(...a),
}));
```

## Selectors for Performance

```typescript
// Create memoized selectors
const selectUser = (state: Store) => state.user;
const selectIsAdmin = (state: Store) => state.user?.role === 'admin';

// Use in component - only re-renders when selected value changes
function UserBadge() {
  const isAdmin = useStore(selectIsAdmin);
  return isAdmin ? <AdminBadge /> : null;
}
```

## Outside React

```typescript
// Access store outside React
const { getState, setState, subscribe } = useStore;

// Get current state
const currentUser = useStore.getState().user;

// Update state
useStore.setState({ theme: 'dark' });

// Subscribe to changes
const unsubscribe = useStore.subscribe(
  (state) => console.log('State changed:', state)
);
```
