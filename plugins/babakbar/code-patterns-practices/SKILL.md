---
name: Code Patterns & Practices
description: React Native coding patterns, best practices, and common solutions for mobile development. Use when implementing features or refactoring code.
allowed-tools: Read, Write, Edit
---

# Code Patterns & Practices

Common patterns and best practices for React Native development.

## When to Use

- Implementing new features
- Refactoring existing code
- Choosing architecture patterns
- Solving common problems
- Improving code quality

## Component Patterns

### Custom Hooks

```typescript
// Extract reusable logic
function useToggle(initial = false) {
  const [value, setValue] = useState(initial);
  const toggle = useCallback(() => setValue(v => !v), []);
  return [value, toggle] as const;
}

// Usage
const [isOpen, toggleOpen] = useToggle();
```

### Compound Components

```typescript
// Create flexible component APIs
interface TabsProps {
  children: React.ReactNode;
  defaultValue?: string;
}

function Tabs({ children, defaultValue }: TabsProps) {
  const [active, setActive] = useState(defaultValue);

  return (
    <TabsContext.Provider value={{ active, setActive }}>
      {children}
    </TabsContext.Provider>
  );
}

Tabs.List = TabsList;
Tabs.Trigger = TabsTrigger;
Tabs.Content = TabsContent;

// Usage
<Tabs defaultValue="home">
  <Tabs.List>
    <Tabs.Trigger value="home">Home</Tabs.Trigger>
    <Tabs.Trigger value="profile">Profile</Tabs.Trigger>
  </Tabs.List>
  <Tabs.Content value="home">Home Content</Tabs.Content>
  <Tabs.Content value="profile">Profile Content</Tabs.Content>
</Tabs>
```

### Render Props

```typescript
// Share component logic
interface DataLoaderProps<T> {
  loadData: () => Promise<T>;
  children: (data: T | null, loading: boolean, error: Error | null) => React.ReactNode;
}

function DataLoader<T>({ loadData, children }: DataLoaderProps<T>) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    loadData()
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [loadData]);

  return <>{children(data, loading, error)}</>;
}

// Usage
<DataLoader loadData={fetchUser}>
  {(user, loading, error) => {
    if (loading) return <Loading />;
    if (error) return <Error error={error} />;
    return <UserProfile user={user} />;
  }}
</DataLoader>
```

## State Management Patterns

### Local State

```typescript
// Keep it simple when possible
function Counter() {
  const [count, setCount] = useState(0);
  return <Button onPress={() => setCount(c => c + 1)}>Count: {count}</Button>;
}
```

### Shared State (Context)

```typescript
// For cross-cutting concerns
const ThemeContext = createContext<ThemeContextValue>(null!);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used within ThemeProvider');
  return context;
}
```

### Global State (Zustand)

```typescript
// For app-wide state
import { create } from 'zustand';

interface UserState {
  user: User | null;
  setUser: (user: User) => void;
  logout: () => void;
}

export const useUserStore = create<UserState>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
  logout: () => set({ user: null }),
}));
```

## Data Fetching Patterns

### With Async/Await

```typescript
function useUserData(userId: string) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchData() {
      try {
        const response = await fetch(`/api/users/${userId}`);
        const result = await response.json();
        if (!cancelled) {
          setData(result);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchData();

    return () => {
      cancelled = true;
    };
  }, [userId]);

  return { data, loading, error };
}
```

## Performance Patterns

### Memoization

```typescript
// Expensive calculations
const expensiveValue = useMemo(() => {
  return calculateExpensiveValue(data);
}, [data]);

// Stable callbacks
const handlePress = useCallback(() => {
  doSomething(value);
}, [value]);

// Component memoization
const MemoizedChild = memo(function Child({ data }: ChildProps) {
  return <View>{data}</View>;
});
```

### Lazy Loading

```typescript
import { lazy, Suspense } from 'react';

const HeavyComponent = lazy(() => import('./HeavyComponent'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <HeavyComponent />
    </Suspense>
  );
}
```

## Error Handling Patterns

### Error Boundaries

```typescript
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error: Error | null }
> {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error('Error caught:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return <ErrorScreen error={this.state.error} />;
    }
    return this.props.children;
  }
}
```

### Try-Catch Pattern

```typescript
async function saveData() {
  try {
    await api.save(data);
    showSuccess('Saved!');
  } catch (error) {
    if (error instanceof NetworkError) {
      showError('Network error. Check connection.');
    } else if (error instanceof ValidationError) {
      showError(error.message);
    } else {
      showError('Something went wrong.');
    }
  }
}
```

## Mobile-Specific Patterns

### Safe Area Handling

```typescript
import { useSafeAreaInsets } from 'react-native-safe-area-context';

function Screen() {
  const insets = useSafeAreaInsets();

  return (
    <View style={{ paddingTop: insets.top, paddingBottom: insets.bottom }}>
      {/* Content */}
    </View>
  );
}
```

### Keyboard Avoiding

```typescript
import { KeyboardAvoidingView, Platform } from 'react-native';

<KeyboardAvoidingView
  behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
  style={{ flex: 1 }}
>
  {/* Input form */}
</KeyboardAvoidingView>
```

## Best Practices

1. **Keep Components Small**: Single responsibility, easy to test
2. **Extract Custom Hooks**: Reuse logic across components
3. **Use TypeScript**: Catch errors early
4. **Handle Loading & Error States**: Better user experience
5. **Clean Up Side Effects**: Prevent memory leaks
6. **Optimize Wisely**: Profile before optimizing
7. **Test Behavior**: Focus on user interactions

## Anti-Patterns to Avoid

- ❌ Massive components (>300 lines)
- ❌ Prop drilling (use context/store instead)
- ❌ Missing cleanup in useEffect
- ❌ Inline function definitions in render
- ❌ Mutating state directly
- ❌ Over-optimization without measuring

## Resources

- [React Patterns](https://reactpatterns.com/)
- [React Native Best Practices](https://reactnative.dev/docs/performance)
