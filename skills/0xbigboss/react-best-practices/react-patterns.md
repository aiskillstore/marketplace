# React Patterns Reference

Code examples for patterns summarized in `SKILL.md`. Load this file when you need to see or produce a concrete implementation.

## Effect Anti-Patterns

### Derived State (Calculate During Render)

```tsx
// BAD: Effect for derived state
const [firstName, setFirstName] = useState('Taylor');
const [lastName, setLastName] = useState('Swift');
const [fullName, setFullName] = useState('');
useEffect(() => {
  setFullName(firstName + ' ' + lastName);
}, [firstName, lastName]);

// GOOD: Calculate during render
const [firstName, setFirstName] = useState('Taylor');
const [lastName, setLastName] = useState('Swift');
const fullName = firstName + ' ' + lastName;
```

### Expensive Calculations (Use useMemo)

```tsx
// BAD: Effect for caching
const [visibleTodos, setVisibleTodos] = useState([]);
useEffect(() => {
  setVisibleTodos(getFilteredTodos(todos, filter));
}, [todos, filter]);

// GOOD: useMemo for expensive calculations
const visibleTodos = useMemo(
  () => getFilteredTodos(todos, filter),
  [todos, filter]
);
```

### Resetting State on Prop Change (Use key)

```tsx
// BAD: Effect to reset state
function ProfilePage({ userId }) {
  const [comment, setComment] = useState('');
  useEffect(() => {
    setComment('');
  }, [userId]);
}

// GOOD: Use key to reset component state
function ProfilePage({ userId }) {
  return <Profile userId={userId} key={userId} />;
}

function Profile({ userId }) {
  const [comment, setComment] = useState(''); // Resets automatically when key changes
}
```

### User Event Handling (Use Event Handlers)

```tsx
// BAD: Event-specific logic in Effect
function ProductPage({ product, addToCart }) {
  useEffect(() => {
    if (product.isInCart) {
      showNotification(`Added ${product.name} to cart`);
    }
  }, [product]);
}

// GOOD: Logic in event handler
function ProductPage({ product, addToCart }) {
  function buyProduct() {
    addToCart(product);
    showNotification(`Added ${product.name} to cart`);
  }
}
```

### Notifying Parent of State Changes

```tsx
// BAD: Effect to notify parent
function Toggle({ onChange }) {
  const [isOn, setIsOn] = useState(false);
  useEffect(() => {
    onChange(isOn);
  }, [isOn, onChange]);
}

// GOOD: Update both in event handler
function Toggle({ onChange }) {
  const [isOn, setIsOn] = useState(false);
  function updateToggle(nextIsOn) {
    setIsOn(nextIsOn);
    onChange(nextIsOn);
  }
}

// BEST: Fully controlled component
function Toggle({ isOn, onChange }) {
  function handleClick() {
    onChange(!isOn);
  }
}
```

### Chains of Effects

```tsx
// BAD: Effect chain — each effect re-renders before the next fires
useEffect(() => {
  if (card !== null && card.gold) {
    setGoldCardCount(c => c + 1);
  }
}, [card]);

useEffect(() => {
  if (goldCardCount > 3) {
    setRound(r => r + 1);
    setGoldCardCount(0);
  }
}, [goldCardCount]);

// GOOD: Calculate derived state, update everything in one event handler
const isGameOver = round > 5;

function handlePlaceCard(nextCard) {
  setCard(nextCard);
  if (nextCard.gold) {
    if (goldCardCount < 3) {
      setGoldCardCount(goldCardCount + 1);
    } else {
      setGoldCardCount(0);
      setRound(round + 1);
    }
  }
}
```

## Effect Dependencies

### Never Suppress the Linter

```tsx
// BAD: Suppressing linter hides bugs
useEffect(() => {
  const id = setInterval(() => {
    setCount(count + increment);
  }, 1000);
  return () => clearInterval(id);
  // eslint-disable-next-line react-hooks/exhaustive-deps
}, []);

// GOOD: Fix the code, not the linter
useEffect(() => {
  const id = setInterval(() => {
    setCount(c => c + increment);
  }, 1000);
  return () => clearInterval(id);
}, [increment]);
```

### Use Updater Functions to Remove State Dependencies

```tsx
// BAD: messages in dependencies causes reconnection on every message
useEffect(() => {
  connection.on('message', (msg) => {
    setMessages([...messages, msg]);
  });
}, [messages]); // Reconnects on every message!

// GOOD: Updater function removes the dependency
useEffect(() => {
  connection.on('message', (msg) => {
    setMessages(msgs => [...msgs, msg]);
  });
}, []); // No messages dependency needed
```

### Move Objects/Functions Inside Effects

```tsx
// BAD: Object created each render triggers Effect
function ChatRoom({ roomId }) {
  const options = { serverUrl, roomId }; // New object each render
  useEffect(() => {
    const connection = createConnection(options);
    connection.connect();
    return () => connection.disconnect();
  }, [options]); // Reconnects every render!
}

// GOOD: Create object inside Effect
function ChatRoom({ roomId }) {
  useEffect(() => {
    const options = { serverUrl, roomId };
    const connection = createConnection(options);
    connection.connect();
    return () => connection.disconnect();
  }, [roomId, serverUrl]); // Only reconnects when values change
}
```

### useEffectEvent for Non-Reactive Logic

```tsx
// BAD: theme change reconnects chat
function ChatRoom({ roomId, theme }) {
  useEffect(() => {
    const connection = createConnection(serverUrl, roomId);
    connection.on('connected', () => {
      showNotification('Connected!', theme);
    });
    connection.connect();
    return () => connection.disconnect();
  }, [roomId, theme]); // Reconnects on theme change!
}

// GOOD: useEffectEvent for non-reactive logic
function ChatRoom({ roomId, theme }) {
  const onConnected = useEffectEvent(() => {
    showNotification('Connected!', theme);
  });

  useEffect(() => {
    const connection = createConnection(serverUrl, roomId);
    connection.on('connected', () => {
      onConnected();
    });
    connection.connect();
    return () => connection.disconnect();
  }, [roomId]); // theme no longer causes reconnection
}
```

### Wrap Callback Props with useEffectEvent

```tsx
// BAD: Callback prop in dependencies reconnects if parent re-renders
function ChatRoom({ roomId, onReceiveMessage }) {
  useEffect(() => {
    connection.on('message', onReceiveMessage);
  }, [roomId, onReceiveMessage]);
}

// GOOD: Wrap callback in useEffectEvent
function ChatRoom({ roomId, onReceiveMessage }) {
  const onMessage = useEffectEvent(onReceiveMessage);

  useEffect(() => {
    connection.on('message', onMessage);
  }, [roomId]); // Stable dependency list
}
```

## Effect Cleanup

### Always Clean Up Subscriptions

```tsx
useEffect(() => {
  const connection = createConnection(serverUrl, roomId);
  connection.connect();
  return () => connection.disconnect(); // REQUIRED
}, [roomId]);

useEffect(() => {
  function handleScroll(e) {
    console.log(window.scrollY);
  }
  window.addEventListener('scroll', handleScroll);
  return () => window.removeEventListener('scroll', handleScroll); // REQUIRED
}, []);
```

### Data Fetching with Ignore Flag

```tsx
useEffect(() => {
  let ignore = false;

  async function fetchData() {
    const result = await fetchTodos(userId);
    if (!ignore) {
      setTodos(result);
    }
  }

  fetchData();

  return () => {
    ignore = true; // Prevents stale data from superseded requests
  };
}, [userId]);
```

### Development Double-Fire Is Intentional

React remounts components in development to verify cleanup works. If effects fire twice, fix the cleanup — don't suppress the double-fire:

```tsx
// BAD: Hiding the symptom
const didInit = useRef(false);
useEffect(() => {
  if (didInit.current) return;
  didInit.current = true;
  // ...
}, []);

// GOOD: Fix the cleanup so remounting is safe
useEffect(() => {
  const connection = createConnection();
  connection.connect();
  return () => connection.disconnect();
}, []);
```

## Ref Patterns

### Use Refs for Values That Don't Affect Rendering

```tsx
// GOOD: Ref for timeout ID (doesn't affect UI)
const timeoutRef = useRef(null);

function handleClick() {
  clearTimeout(timeoutRef.current);
  timeoutRef.current = setTimeout(() => {
    // ...
  }, 1000);
}

// BAD: Using ref for displayed value — UI won't update
const countRef = useRef(0);
countRef.current++;
```

### Never Read/Write ref.current During Render

```tsx
// BAD: Reading/writing ref during render
function MyComponent() {
  const ref = useRef(0);
  ref.current++; // Mutating during render!
  return <div>{ref.current}</div>; // Reading during render!
}

// GOOD: Read/write refs in event handlers and effects
function MyComponent() {
  const ref = useRef(0);

  function handleClick() {
    ref.current++; // OK in event handler
  }

  useEffect(() => {
    ref.current = someValue; // OK in effect
  }, [someValue]);
}
```

### Ref Callbacks for Dynamic Lists

```tsx
// BAD: Can't call useRef in a loop
{items.map((item) => {
  const ref = useRef(null); // Rules of Hooks violation!
  return <li ref={ref} />;
})}

// GOOD: Ref callback with Map
const itemsRef = useRef(new Map());

{items.map((item) => (
  <li
    key={item.id}
    ref={(node) => {
      if (node) {
        itemsRef.current.set(item.id, node);
      } else {
        itemsRef.current.delete(item.id);
      }
    }}
  />
))}
```

### useImperativeHandle for Controlled Exposure

```tsx
// Limit what parent can access through a ref — expose only the API surface you intend
function MyInput({ ref }) {
  const realInputRef = useRef(null);

  useImperativeHandle(ref, () => ({
    focus() {
      realInputRef.current.focus();
    },
    // Parent can ONLY call focus(), not access the full DOM node
  }));

  return <input ref={realInputRef} />;
}
```

## Custom Hook Patterns

### Hooks Share Logic, Not State

```tsx
// Each call gets independent state — these are two separate online status subscriptions
function StatusBar() {
  const isOnline = useOnlineStatus();
}

function SaveButton() {
  const isOnline = useOnlineStatus();
}
```

### Name Hooks useXxx Only If They Use Hooks

```tsx
// BAD: useXxx prefix but doesn't call any hooks
function useSorted(items) {
  return items.slice().sort();
}

// GOOD: Regular function
function getSorted(items) {
  return items.slice().sort();
}

// GOOD: Uses hooks, so prefix with use
function useAuth() {
  return useContext(AuthContext);
}
```

### Avoid "Lifecycle" Hooks

```tsx
// BAD: Custom lifecycle hooks prevent linter from catching missing dependencies
function useMount(fn) {
  useEffect(() => {
    fn();
  }, []); // fn is missing from dependencies — linter can't catch it
}

// GOOD: Use useEffect directly
useEffect(() => {
  doSomething();
}, [doSomething]);
```

## Component Patterns

### Controlled vs Uncontrolled

```tsx
// Uncontrolled: component owns state
function SearchInput() {
  const [query, setQuery] = useState('');
  return <input value={query} onChange={e => setQuery(e.target.value)} />;
}

// Controlled: parent owns state — more composable, easier to test
function SearchInput({ query, onQueryChange }) {
  return <input value={query} onChange={e => onQueryChange(e.target.value)} />;
}
```

### Prefer Composition Over Prop Drilling

```tsx
// BAD: Prop drilling through intermediate components that don't use the value
<App user={user}>
  <Layout user={user}>
    <Header user={user}>
      <Avatar user={user} />
    </Header>
  </Layout>
</App>

// GOOD: Pass the rendered element, not raw data
<App>
  <Layout>
    <Header avatar={<Avatar user={user} />} />
  </Layout>
</App>

// GOOD: Context for truly global state (auth, theme, locale)
<UserContext.Provider value={user}>
  <App />
</UserContext.Provider>
```

### flushSync for Synchronous DOM Updates

```tsx
// When you need to read the DOM immediately after a state update
// (e.g., scroll to a newly added list item before the next paint)
import { flushSync } from 'react-dom';

function handleAdd() {
  flushSync(() => {
    setTodos([...todos, newTodo]);
  });
  // DOM is now updated synchronously — safe to read layout
  listRef.current.lastChild.scrollIntoView();
}
```
