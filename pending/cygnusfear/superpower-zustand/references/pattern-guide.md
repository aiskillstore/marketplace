# Zustand StoreBuilder Pattern Guide

## Overview

The StoreBuilder pattern provides a standardized way to create Zustand stores with:
- Type-safe state management
- Optional persistence using Zustand's persist middleware
- Immer middleware for immutable state updates
- Separation of actions from state using the factory pattern
- Exposed non-reactive `get`/`set` for use outside React components

## Core API

```typescript
const { get, set, useStore, subscribe, createFactory } = StoreBuilder(initialState, persistConfig?)
```

### Returns

- **`useStore`**: React hook for reactive state access in components
- **`get`**: Non-reactive function to get current state
- **`set`**: Function to update state (works with immer)
- **`subscribe`**: Subscribe to state changes
- **`createFactory`**: Create a factory function that combines state with custom actions

## Basic Usage (Without Persistence)

```typescript
import { StoreBuilder } from './storebuilder';

type CounterState = {
  count: number;
  increment: () => void;
  decrement: () => void;
};

const { get, set, useStore, createFactory } = StoreBuilder<Omit<CounterState, 'increment' | 'decrement'>>({
  count: 0,
});

// Create factory with actions separated from state
const useCounterStore = createFactory({
  increment: () => set((state) => { state.count += 1; }),
  decrement: () => set((state) => { state.count -= 1; }),
});

// Usage in React components
function Counter() {
  const { count, increment, decrement } = useCounterStore();

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={increment}>+</button>
      <button onClick={decrement}>-</button>
    </div>
  );
}
```

## With Persistence

```typescript
import { StoreBuilder } from './storebuilder';

type UserPreferences = {
  theme: 'light' | 'dark';
  language: string;
  setTheme: (theme: 'light' | 'dark') => void;
  setLanguage: (language: string) => void;
};

const { get, set, useStore, createFactory } = StoreBuilder<Omit<UserPreferences, 'setTheme' | 'setLanguage'>>(
  {
    theme: 'light',
    language: 'en',
  },
  {
    name: 'user-preferences', // localStorage key
    version: 1,
    // Optional: only persist specific fields
    partialize: (state) => ({ theme: state.theme, language: state.language }),
  }
);

const useUserPreferences = createFactory({
  setTheme: (theme: 'light' | 'dark') => set((state) => { state.theme = theme; }),
  setLanguage: (language: string) => set((state) => { state.language = language; }),
});

// Usage
function Settings() {
  const { theme, language, setTheme, setLanguage } = useUserPreferences();

  return (
    <div>
      <select value={theme} onChange={(e) => setTheme(e.target.value as 'light' | 'dark')}>
        <option value="light">Light</option>
        <option value="dark">Dark</option>
      </select>
      <input value={language} onChange={(e) => setLanguage(e.target.value)} />
    </div>
  );
}
```

## Complex Example with Async Actions

```typescript
import { StoreBuilder } from './storebuilder';

type TodoState = {
  todos: Array<{ id: string; text: string; completed: boolean }>;
  loading: boolean;
  error: string | null;
};

type TodoActions = {
  addTodo: (text: string) => void;
  toggleTodo: (id: string) => void;
  deleteTodo: (id: string) => void;
  fetchTodos: () => Promise<void>;
};

const { get, set, useStore, createFactory } = StoreBuilder<TodoState>({
  todos: [],
  loading: false,
  error: null,
});

const useTodoStore = createFactory<TodoActions>({
  addTodo: (text: string) => {
    const id = Math.random().toString(36);
    set((state) => {
      state.todos.push({ id, text, completed: false });
    });
  },

  toggleTodo: (id: string) => {
    set((state) => {
      const todo = state.todos.find(t => t.id === id);
      if (todo) {
        todo.completed = !todo.completed;
      }
    });
  },

  deleteTodo: (id: string) => {
    set((state) => {
      state.todos = state.todos.filter(t => t.id !== id);
    });
  },

  fetchTodos: async () => {
    set((state) => { state.loading = true; state.error = null; });
    try {
      const response = await fetch('/api/todos');
      const todos = await response.json();
      set((state) => {
        state.todos = todos;
        state.loading = false;
      });
    } catch (error) {
      set((state) => {
        state.error = error instanceof Error ? error.message : 'Unknown error';
        state.loading = false;
      });
    }
  },
});

// Usage
function TodoList() {
  const { todos, loading, error, addTodo, toggleTodo, deleteTodo } = useTodoStore();

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      {todos.map(todo => (
        <div key={todo.id}>
          <input
            type="checkbox"
            checked={todo.completed}
            onChange={() => toggleTodo(todo.id)}
          />
          <span>{todo.text}</span>
          <button onClick={() => deleteTodo(todo.id)}>Delete</button>
        </div>
      ))}
    </div>
  );
}
```

## Using `get` and `set` Outside React Components

```typescript
// Get current state outside React
const currentCount = get().count;

// Update state outside React
set((state) => { state.count = 10; });

// Subscribe to changes outside React
const unsubscribe = subscribe((state) => {
  console.log('State changed:', state);
});

// Later: unsubscribe()
```

## Pattern Benefits

1. **Type Safety**: Full TypeScript support with type inference
2. **Immer Integration**: Write mutations that are automatically converted to immutable updates
3. **Separation of Concerns**: State definition separate from actions via `createFactory`
4. **Persistence**: Optional localStorage/sessionStorage persistence with fine-grained control
5. **Flexibility**: Works in React components (via hook) and outside React (via get/set)
6. **Non-Reactive Access**: Use `get()` and `set()` for non-reactive state access when needed

## Key Patterns

### State vs Actions Separation

Always separate state types from action types using `Omit`:

```typescript
type FullState = {
  // State
  value: number;
  // Actions
  setValue: (v: number) => void;
};

// Pass only state to StoreBuilder
const { createFactory } = StoreBuilder<Omit<FullState, 'setValue'>>({
  value: 0,
});

// Add actions in createFactory
const useMyStore = createFactory({
  setValue: (v: number) => set((state) => { state.value = v; }),
});
```

### Immer Draft Mutations

With immer middleware, update state by mutating the draft:

```typescript
// ✅ Correct: Mutate the draft
set((state) => {
  state.count += 1;
  state.items.push(newItem);
});

// ❌ Incorrect: Don't return new state
set((state) => {
  return { ...state, count: state.count + 1 };
});
```

### Factory Return Type

The factory combines state, actions, and store methods:

```typescript
const useMyStore = createFactory({ ...actions });

// Returns: State & Actions & { set, subscribe }
const storeValue = useMyStore();
// Access: storeValue.count, storeValue.increment, storeValue.set, storeValue.subscribe
```
