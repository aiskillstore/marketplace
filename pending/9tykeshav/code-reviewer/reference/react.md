# React Code Review - Claude Skill
React 19.x | Dec 2025

## 1. Component Anti-Patterns

| Issue | BAD | GOOD |
|-------|-----|------|
| Prop drilling | `<A u={u}><B u={u}><C u={u}/></B></A>` | Context/composition |
| God components | 500+ lines, 50 useEffects | Split by responsibility |
| Spread props | `<Avatar {...props} />` | Explicit props |
| Impure | `let x=0; function C(){x++}` | Pure functions |

## 2. Hooks Anti-Patterns

| Issue | BAD | GOOD |
|-------|-----|------|
| Stale closures | `useEffect(() => setInterval(() => console.log(count), 1000), [])` | Updater: `setCount(c => c)` |
| Race conditions | `fetch().then(setResults)` | `let ignore=false; if(!ignore)setResults(); return()=>ignore=true` |
| Missing cleanup | No return in useEffect | `return () => conn.disconnect()` |
| Conditional hooks | `if(x){useState('')}` | ERROR - hooks at top level always |
| Effects for data | `useEffect(() => setFullName(first+last), [first,last])` | `const fullName = first+last` |
| Effect chains | Multiple useEffects triggering each other | Handle in event handler |

### Infinite Loop Causes
| Dependency | Fix |
|------------|-----|
| `[object]` `[array]` | `useMemo` or primitives |
| `[function]` | `useCallback` |
| State setter depends on state | Remove from deps |

## 3. State Management

| State Type | Tool |
|------------|------|
| Server data | React Query, SWR |
| URL state | URL params |
| UI state | Local useState |
| Form state | React Hook Form |
| Global | Context API |

| Issue | Fix |
|-------|-----|
| Derived state | `const total = items.reduce(...)` not useState+useEffect |
| Context with frequent changes | Split by update frequency |
| Deep nested updates | Immer: `updateState(draft => draft.user.name = n)` |

## 4. Performance

### useMemo/useCallback Rules
**Only when:** Calc >1ms, prevents expensive child re-renders, stabilizes refs, profiling shows improvement

| Issue | Fix |
|-------|-----|
| Objects/arrays break memo | `useMemo(() => ({ name, role }), [name])` or pass primitives |
| useCallback without memo child | Useless - need both |
| Long lists (10k+) | react-window `<FixedSizeList>` |
| Code splitting | `lazy(() => import('./Dashboard'))` + `<Suspense>` |

## 5. Security

| Vulnerability | BAD | GOOD |
|--------------|-----|------|
| XSS | `dangerouslySetInnerHTML={{__html: userInput}}` | `{userInput}` or DOMPurify |
| API keys | Client-side | Proxy through backend |
| Open redirects | `location.href = params.get('redirect')` | Whitelist or `startsWith('/')` |
| Auth tokens | localStorage | httpOnly cookies: `res.cookie('token', t, {httpOnly:true, secure:true, sameSite:'strict'})` |

## 6. Testing

**Query Priority:** 1.`getByRole` 2.`getByLabelText` 3.`getByText` 4.`getByTestId`

```jsx
// MSW
import { rest } from 'msw';
import { setupServer } from 'msw/node';
const server = setupServer(rest.get('/api/users/:id', (req, res, ctx) => res(ctx.json({id: 1}))));
beforeAll(() => server.listen()); afterEach(() => server.resetHandlers()); afterAll(() => server.close());

// A11y
import { axe, toHaveNoViolations } from 'jest-axe';
expect(await axe(container)).toHaveNoViolations();
```

## 7. Forms

```jsx
import { useForm } from 'react-hook-form';
const { register, handleSubmit, formState: { errors } } = useForm();
<input {...register('email', { required: true, pattern: /^\S+@\S+$/ })} />
```

## 8. API Integration

```jsx
import { useQuery } from '@tanstack/react-query';
const { data, isLoading, error } = useQuery({ queryKey: ['products'], queryFn: () => fetch('/api/products').then(r => r.json()) });
```

**Error Boundaries:**
```jsx
class ErrorBoundary extends Component {
  state = { hasError: false };
  static getDerivedStateFromError() { return { hasError: true }; }
  componentDidCatch(error, info) { logError(error, info); }
  render() { return this.state.hasError ? <ErrorFallback /> : this.props.children; }
}
```

## 9. Accessibility

| Issue | BAD | GOOD |
|-------|-----|------|
| No labels | `<input />` | `<label>Email<input /></label>` |
| Div buttons | `<div onClick={}>` | `<button>` |
| No alt | `<img src=""/>` | `<img alt="Desc"/>` |
| No ARIA | `<div>Modal</div>` | `<div role="dialog" aria-modal="true">` |
| Poor contrast | `#ccc on #ddd` | 4.5:1 ratio min |
| No focus | `outline: none` | `:focus { outline: 2px solid }` |

**Custom interactive:** `<div role="button" tabIndex={0} onClick={handler} onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handler(); } }}>`

## 10. TypeScript

```tsx
interface UserProps { name: string; age?: number; onUpdate: (user: User) => void; }
interface ListProps<T> { items: T[]; renderItem: (item: T) => ReactNode; }
const [user, setUser] = useState<User | null>(null);
const ref = useRef<HTMLInputElement>(null);
const handleChange = (e: ChangeEvent<HTMLInputElement>) => {};
const handleSubmit = (e: FormEvent<HTMLFormElement>) => {};
```

## 11. Production Bugs

| Issue | BAD | GOOD |
|-------|-----|------|
| Key warnings | `key={i}` (index) → reordering bugs | `key={item.id}` (stable unique ID) |
| Memory leaks | Missing cleanup, listeners, subscriptions, timers | Return cleanup in useEffect |
| Hydration mismatch | `<div>{new Date().toISOString()}</div>` | `const [time, setTime] = useState(null); useEffect(() => setTime(new Date().toISOString()), []);` |

## Code Review Checklist

**Components**
- [ ] <200 lines, single responsibility
- [ ] Pure (no side effects during render)
- [ ] Hooks at top level
- [ ] Proper keys (not index)

**Performance**
- [ ] memo/useMemo/useCallback used appropriately (not overused)
- [ ] No new objects/arrays breaking memo
- [ ] Virtualization for long lists
- [ ] Code splitting for routes

**State**
- [ ] No derived state
- [ ] Context not overused
- [ ] Appropriate management (local vs global)

**Effects**
- [ ] All dependencies included
- [ ] Cleanup for subscriptions/listeners
- [ ] No infinite loops
- [ ] Race conditions handled
- [ ] No data transformations in effects

**Security**
- [ ] No dangerouslySetInnerHTML with user input
- [ ] No API keys in client
- [ ] Redirects validated
- [ ] httpOnly cookies for auth

**Testing**
- [ ] Tests behavior not implementation
- [ ] Error/loading/empty states tested
- [ ] Accessibility tested (jest-axe)
- [ ] APIs mocked (MSW)

**Accessibility**
- [ ] Semantic HTML
- [ ] Labels for inputs
- [ ] Alt text for images
- [ ] Keyboard accessible
- [ ] ARIA where needed
