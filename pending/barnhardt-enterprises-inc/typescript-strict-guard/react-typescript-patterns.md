# React TypeScript Patterns

**Official Documentation:**
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)
- [React 19 TypeScript Documentation](https://react.dev/learn/typescript)
- [React Types Reference](https://github.com/DefinitelyTyped/DefinitelyTyped/tree/master/types/react)

Complete reference for typing React components, hooks, and patterns.

---

## 1. Functional Component Props

**Basic Props:**

```typescript
// ❌ DON'T: No prop types
function Button({ label, onClick }) {
  return <button onClick={onClick}>{label}</button>
}

// ✅ DO: Explicit interface
interface ButtonProps {
  label: string
  onClick: () => void
}

function Button({ label, onClick }: ButtonProps) {
  return <button onClick={onClick}>{label}</button>
}

// ✅ DO: Type alias (alternative)
type ButtonProps = {
  label: string
  onClick: () => void
}

// ✅ DO: React.FC (includes children automatically)
const Button: React.FC<ButtonProps> = ({ label, onClick }) => {
  return <button onClick={onClick}>{label}</button>
}

// Note: React.FC is less common now, prefer explicit typing
```

**Optional Props:**

```typescript
interface ButtonProps {
  label: string
  onClick: () => void
  disabled?: boolean        // Optional
  variant?: 'primary' | 'secondary'  // Optional with union
  className?: string        // Optional
}

function Button({
  label,
  onClick,
  disabled = false,         // Default value
  variant = 'primary',      // Default value
  className
}: ButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`btn btn-${variant} ${className ?? ''}`}
    >
      {label}
    </button>
  )
}
```

**Props with Children:**

```typescript
// ✅ DO: ReactNode for flexible children
interface CardProps {
  title: string
  children: React.ReactNode  // Can be anything renderable
}

function Card({ title, children }: CardProps) {
  return (
    <div className="card">
      <h2>{title}</h2>
      {children}
    </div>
  )
}

// ✅ DO: ReactElement for specific component type
interface WrapperProps {
  children: React.ReactElement<ButtonProps>  // Must be Button component
}

function Wrapper({ children }: WrapperProps) {
  return <div className="wrapper">{children}</div>
}

// Usage
<Wrapper>
  <Button label="Click" onClick={() => {}} />
</Wrapper>

// ✅ DO: Multiple children with specific types
interface LayoutProps {
  header: React.ReactNode
  sidebar: React.ReactNode
  content: React.ReactNode
  footer?: React.ReactNode
}

function Layout({ header, sidebar, content, footer }: LayoutProps) {
  return (
    <div>
      <header>{header}</header>
      <aside>{sidebar}</aside>
      <main>{content}</main>
      {footer && <footer>{footer}</footer>}
    </div>
  )
}
```

---

## 2. Event Handler Typing

**All Event Types:**

```typescript
function EventDemo() {
  // Click events
  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    console.log('Clicked at', e.clientX, e.clientY)
    e.currentTarget.disabled = true  // Type-safe element access
  }

  // Input change events
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log('Input value:', e.target.value)
    console.log('Input type:', e.target.type)  // Type-safe
  }

  // Textarea change events
  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    console.log('Textarea value:', e.target.value)
  }

  // Select change events
  const handleSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    console.log('Selected value:', e.target.value)
  }

  // Form submit events
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const email = formData.get('email')
  }

  // Keyboard events
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      console.log('Enter pressed')
    }
    console.log('Key:', e.key, 'Code:', e.code)
  }

  // Focus events
  const handleFocus = (e: React.FocusEvent<HTMLInputElement>) => {
    console.log('Input focused')
    e.target.select()  // Type-safe
  }

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    console.log('Input blurred')
  }

  // Mouse events
  const handleMouseEnter = (e: React.MouseEvent<HTMLDivElement>) => {
    console.log('Mouse entered')
  }

  const handleMouseLeave = (e: React.MouseEvent<HTMLDivElement>) => {
    console.log('Mouse left')
  }

  // Drag events
  const handleDragStart = (e: React.DragEvent<HTMLDivElement>) => {
    e.dataTransfer.setData('text/plain', 'dragged')
  }

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    const data = e.dataTransfer.getData('text/plain')
  }

  // Scroll events
  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const target = e.currentTarget
    console.log('Scroll position:', target.scrollTop)
  }

  // Touch events
  const handleTouchStart = (e: React.TouchEvent<HTMLDivElement>) => {
    const touch = e.touches[0]
    console.log('Touch at', touch.clientX, touch.clientY)
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        onFocus={handleFocus}
        onBlur={handleBlur}
      />
      <button onClick={handleClick}>Submit</button>
    </form>
  )
}
```

**Generic Event Handler:**

```typescript
// ✅ DO: Reusable event handler type
type EventHandler<T extends HTMLElement, E extends React.SyntheticEvent> =
  (event: E) => void

interface FormProps {
  onSubmit: EventHandler<HTMLFormElement, React.FormEvent<HTMLFormElement>>
  onChange: EventHandler<HTMLInputElement, React.ChangeEvent<HTMLInputElement>>
}

// ✅ DO: Event handler with custom parameters
type ClickHandler = (id: string, event: React.MouseEvent<HTMLButtonElement>) => void

interface ItemProps {
  id: string
  onClick: ClickHandler
}

function Item({ id, onClick }: ItemProps) {
  return (
    <button onClick={(e) => onClick(id, e)}>
      Click me
    </button>
  )
}
```

---

## 3. useState Hook Typing

**Basic State:**

```typescript
// ✅ DO: Type inference (simple types)
const [count, setCount] = useState(0)  // Inferred as number
const [name, setName] = useState('')   // Inferred as string
const [isOpen, setIsOpen] = useState(false)  // Inferred as boolean

// ✅ DO: Explicit type (complex types)
interface User {
  id: string
  name: string
  email: string
}

const [user, setUser] = useState<User | null>(null)

// ✅ DO: Array state
const [items, setItems] = useState<string[]>([])
const [users, setUsers] = useState<User[]>([])

// ✅ DO: Object state
interface FormState {
  email: string
  password: string
  remember: boolean
}

const [form, setForm] = useState<FormState>({
  email: '',
  password: '',
  remember: false
})

// ✅ DO: Update object state
const updateForm = (field: keyof FormState, value: string | boolean) => {
  setForm(prev => ({ ...prev, [field]: value }))
}

// ✅ BETTER: Type-safe field updater
type FormField = keyof FormState
type FormValue<K extends FormField> = FormState[K]

function updateFormField<K extends FormField>(
  field: K,
  value: FormValue<K>
): void {
  setForm(prev => ({ ...prev, [field]: value }))
}

updateFormField('email', 'test@example.com')  // OK
updateFormField('remember', true)  // OK
// updateFormField('email', true)  // Error: wrong type
```

**Lazy Initialization:**

```typescript
// ✅ DO: Lazy initial state
const [user, setUser] = useState<User>(() => {
  const saved = localStorage.getItem('user')
  return saved ? JSON.parse(saved) : null
})

// ✅ DO: Complex initialization
interface AppState {
  theme: 'light' | 'dark'
  language: string
  notifications: boolean
}

const [state, setState] = useState<AppState>(() => {
  const defaults: AppState = {
    theme: 'light',
    language: 'en',
    notifications: true
  }

  try {
    const saved = localStorage.getItem('appState')
    return saved ? { ...defaults, ...JSON.parse(saved) } : defaults
  } catch {
    return defaults
  }
})
```

---

## 4. useRef Hook Typing

**DOM Element Refs:**

```typescript
// ✅ DO: HTML element refs
function TextInput() {
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    // Must check for null
    if (inputRef.current) {
      inputRef.current.focus()
    }
  }, [])

  return <input ref={inputRef} type="text" />
}

// ✅ DO: All common element types
const buttonRef = useRef<HTMLButtonElement>(null)
const divRef = useRef<HTMLDivElement>(null)
const formRef = useRef<HTMLFormElement>(null)
const textareaRef = useRef<HTMLTextAreaElement>(null)
const selectRef = useRef<HTMLSelectElement>(null)
const canvasRef = useRef<HTMLCanvasElement>(null)
const videoRef = useRef<HTMLVideoElement>(null)
const audioRef = useRef<HTMLAudioElement>(null)

// ✅ DO: Type-safe ref operations
function VideoPlayer() {
  const videoRef = useRef<HTMLVideoElement>(null)

  const play = () => {
    videoRef.current?.play()
  }

  const pause = () => {
    videoRef.current?.pause()
  }

  const seek = (time: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = time
    }
  }

  return (
    <div>
      <video ref={videoRef} src="/video.mp4" />
      <button onClick={play}>Play</button>
      <button onClick={pause}>Pause</button>
    </div>
  )
}
```

**Mutable Value Refs:**

```typescript
// ✅ DO: Mutable value (not DOM element)
function Timer() {
  const intervalRef = useRef<number | null>(null)

  useEffect(() => {
    intervalRef.current = window.setInterval(() => {
      console.log('Tick')
    }, 1000)

    return () => {
      if (intervalRef.current !== null) {
        clearInterval(intervalRef.current)
      }
    }
  }, [])

  return <div>Timer running</div>
}

// ✅ DO: Previous value tracking
function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T>()

  useEffect(() => {
    ref.current = value
  }, [value])

  return ref.current
}

// Usage
const [count, setCount] = useState(0)
const previousCount = usePrevious(count)

// ✅ DO: Callback ref for complex scenarios
function CallbackRefExample() {
  const [height, setHeight] = useState(0)

  const measuredRef = useCallback((node: HTMLDivElement | null) => {
    if (node !== null) {
      setHeight(node.getBoundingClientRect().height)
    }
  }, [])

  return <div ref={measuredRef}>Height: {height}px</div>
}
```

---

## 5. useEffect and useLayoutEffect

```typescript
// ✅ DO: Basic effect
useEffect(() => {
  console.log('Component mounted')

  // Cleanup function
  return () => {
    console.log('Component unmounted')
  }
}, [])

// ✅ DO: Effect with dependencies
useEffect(() => {
  const fetchData = async () => {
    const response = await fetch(`/api/users/${userId}`)
    const data: User = await response.json()
    setUser(data)
  }

  fetchData()
}, [userId])

// ✅ DO: Cleanup with abort controller
useEffect(() => {
  const controller = new AbortController()

  const fetchData = async () => {
    try {
      const response = await fetch(`/api/users/${userId}`, {
        signal: controller.signal
      })
      const data: User = await response.json()
      setUser(data)
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('Fetch aborted')
      }
    }
  }

  fetchData()

  return () => {
    controller.abort()
  }
}, [userId])

// ✅ DO: useLayoutEffect for DOM measurements
useLayoutEffect(() => {
  if (divRef.current) {
    const rect = divRef.current.getBoundingClientRect()
    setDimensions({ width: rect.width, height: rect.height })
  }
}, [])
```

---

## 6. useContext Hook

```typescript
// ✅ DO: Create typed context
interface AuthContextType {
  user: User | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

// ✅ DO: Provider component
interface AuthProviderProps {
  children: React.ReactNode
}

function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const login = async (email: string, password: string) => {
    setIsLoading(true)
    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        body: JSON.stringify({ email, password })
      })
      const user: User = await response.json()
      setUser(user)
    } finally {
      setIsLoading(false)
    }
  }

  const logout = () => {
    setUser(null)
  }

  const value: AuthContextType = {
    user,
    login,
    logout,
    isLoading
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// ✅ DO: Custom hook with type guard
function useAuth(): AuthContextType {
  const context = useContext(AuthContext)

  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider')
  }

  return context
}

// Usage
function ProfilePage() {
  const { user, logout } = useAuth()

  if (!user) {
    return <div>Not logged in</div>
  }

  return (
    <div>
      <h1>{user.name}</h1>
      <button onClick={logout}>Logout</button>
    </div>
  )
}
```

---

## 7. Custom Hooks

**Basic Custom Hook:**

```typescript
// ✅ DO: Explicit return type
function useCounter(initialValue: number = 0): {
  count: number
  increment: () => void
  decrement: () => void
  reset: () => void
} {
  const [count, setCount] = useState(initialValue)

  const increment = () => setCount(c => c + 1)
  const decrement = () => setCount(c => c - 1)
  const reset = () => setCount(initialValue)

  return { count, increment, decrement, reset }
}

// ✅ BETTER: Type alias for return type
type UseCounterReturn = {
  count: number
  increment: () => void
  decrement: () => void
  reset: () => void
}

function useCounter(initialValue: number = 0): UseCounterReturn {
  // ... implementation
}
```

**Generic Custom Hook:**

```typescript
// ✅ DO: Generic async data fetching hook
type AsyncState<T> =
  | { status: 'idle'; data: null; error: null }
  | { status: 'loading'; data: null; error: null }
  | { status: 'success'; data: T; error: null }
  | { status: 'error'; data: null; error: Error }

function useAsync<T>(
  asyncFunction: () => Promise<T>,
  deps: React.DependencyList = []
): AsyncState<T> {
  const [state, setState] = useState<AsyncState<T>>({
    status: 'idle',
    data: null,
    error: null
  })

  useEffect(() => {
    setState({ status: 'loading', data: null, error: null })

    asyncFunction()
      .then(data => {
        setState({ status: 'success', data, error: null })
      })
      .catch(error => {
        setState({
          status: 'error',
          data: null,
          error: error instanceof Error ? error : new Error('Unknown error')
        })
      })
  }, deps)

  return state
}

// Usage
function UserProfile({ userId }: { userId: string }) {
  const state = useAsync(
    () => fetch(`/api/users/${userId}`).then(r => r.json()),
    [userId]
  )

  if (state.status === 'loading') return <div>Loading...</div>
  if (state.status === 'error') return <div>Error: {state.error.message}</div>
  if (state.status === 'success') return <div>{state.data.name}</div>

  return null
}
```

**Local Storage Hook:**

```typescript
// ✅ DO: Generic localStorage hook
function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((prev: T) => T)) => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key)
      return item ? JSON.parse(item) : initialValue
    } catch (error) {
      console.error(error)
      return initialValue
    }
  })

  const setValue = (value: T | ((prev: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value
      setStoredValue(valueToStore)
      window.localStorage.setItem(key, JSON.stringify(valueToStore))
    } catch (error) {
      console.error(error)
    }
  }

  return [storedValue, setValue]
}

// Usage
const [theme, setTheme] = useLocalStorage<'light' | 'dark'>('theme', 'light')
```

---

## 8. forwardRef

```typescript
// ✅ DO: forwardRef with generic component
interface InputProps {
  label: string
  error?: string
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error }, ref) => {
    return (
      <div>
        <label>{label}</label>
        <input ref={ref} />
        {error && <span>{error}</span>}
      </div>
    )
  }
)

Input.displayName = 'Input'

// Usage
function Form() {
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  return <Input ref={inputRef} label="Email" />
}

// ✅ DO: forwardRef with multiple types
type ButtonProps = {
  variant: 'primary' | 'secondary'
  children: React.ReactNode
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant, children, ...props }, ref) => {
    return (
      <button ref={ref} className={`btn-${variant}`} {...props}>
        {children}
      </button>
    )
  }
)
```

---

## 9. Higher-Order Components (HOC)

```typescript
// ✅ DO: HOC with proper typing
interface WithLoadingProps {
  isLoading: boolean
}

function withLoading<P extends object>(
  Component: React.ComponentType<P>
): React.FC<P & WithLoadingProps> {
  return ({ isLoading, ...props }: WithLoadingProps & P) => {
    if (isLoading) {
      return <div>Loading...</div>
    }
    return <Component {...(props as P)} />
  }
}

// Usage
interface UserListProps {
  users: User[]
}

const UserList: React.FC<UserListProps> = ({ users }) => {
  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  )
}

const UserListWithLoading = withLoading(UserList)

// Use it
<UserListWithLoading users={users} isLoading={loading} />
```

---

## 10. Render Props

```typescript
// ✅ DO: Render prop pattern
interface MousePosition {
  x: number
  y: number
}

interface MouseTrackerProps {
  render: (position: MousePosition) => React.ReactNode
}

function MouseTracker({ render }: MouseTrackerProps) {
  const [position, setPosition] = useState<MousePosition>({ x: 0, y: 0 })

  const handleMouseMove = (event: React.MouseEvent<HTMLDivElement>) => {
    setPosition({ x: event.clientX, y: event.clientY })
  }

  return <div onMouseMove={handleMouseMove}>{render(position)}</div>
}

// Usage
<MouseTracker
  render={({ x, y }) => (
    <div>
      Mouse position: {x}, {y}
    </div>
  )}
/>

// ✅ DO: Children as function
interface DataProviderProps<T> {
  data: T
  children: (data: T) => React.ReactNode
}

function DataProvider<T>({ data, children }: DataProviderProps<T>) {
  return <>{children(data)}</>
}

// Usage
<DataProvider data={user}>
  {user => <div>{user.name}</div>}
</DataProvider>
```

---

## 11. Component Composition

```typescript
// ✅ DO: Compound components pattern
interface TabsContextType {
  activeTab: string
  setActiveTab: (id: string) => void
}

const TabsContext = createContext<TabsContextType | undefined>(undefined)

interface TabsProps {
  defaultTab: string
  children: React.ReactNode
}

function Tabs({ defaultTab, children }: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultTab)

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      {children}
    </TabsContext.Provider>
  )
}

interface TabListProps {
  children: React.ReactNode
}

function TabList({ children }: TabListProps) {
  return <div className="tab-list">{children}</div>
}

interface TabProps {
  id: string
  children: React.ReactNode
}

function Tab({ id, children }: TabProps) {
  const context = useContext(TabsContext)
  if (!context) throw new Error('Tab must be used within Tabs')

  const { activeTab, setActiveTab } = context

  return (
    <button
      className={activeTab === id ? 'active' : ''}
      onClick={() => setActiveTab(id)}
    >
      {children}
    </button>
  )
}

interface TabPanelProps {
  id: string
  children: React.ReactNode
}

function TabPanel({ id, children }: TabPanelProps) {
  const context = useContext(TabsContext)
  if (!context) throw new Error('TabPanel must be used within Tabs')

  if (context.activeTab !== id) return null

  return <div className="tab-panel">{children}</div>
}

// Attach components
Tabs.List = TabList
Tabs.Tab = Tab
Tabs.Panel = TabPanel

// Usage
<Tabs defaultTab="home">
  <Tabs.List>
    <Tabs.Tab id="home">Home</Tabs.Tab>
    <Tabs.Tab id="profile">Profile</Tabs.Tab>
  </Tabs.List>

  <Tabs.Panel id="home">Home content</Tabs.Panel>
  <Tabs.Panel id="profile">Profile content</Tabs.Panel>
</Tabs>
```

---

## 12. Form Handling

```typescript
// ✅ DO: Controlled form with type-safe state
interface FormData {
  email: string
  password: string
  remember: boolean
}

function LoginForm() {
  const [formData, setFormData] = useState<FormData>({
    email: '',
    password: '',
    remember: false
  })

  const [errors, setErrors] = useState<Partial<Record<keyof FormData, string>>>({})

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const { name, value, type, checked } = e.target

    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()

    // Validation
    const newErrors: Partial<Record<keyof FormData, string>> = {}

    if (!formData.email.includes('@')) {
      newErrors.email = 'Invalid email'
    }

    if (formData.password.length < 8) {
      newErrors.password = 'Password too short'
    }

    setErrors(newErrors)

    if (Object.keys(newErrors).length === 0) {
      // Submit form
      console.log('Form data:', formData)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        name="email"
        type="email"
        value={formData.email}
        onChange={handleChange}
      />
      {errors.email && <span>{errors.email}</span>}

      <input
        name="password"
        type="password"
        value={formData.password}
        onChange={handleChange}
      />
      {errors.password && <span>{errors.password}</span>}

      <label>
        <input
          name="remember"
          type="checkbox"
          checked={formData.remember}
          onChange={handleChange}
        />
        Remember me
      </label>

      <button type="submit">Login</button>
    </form>
  )
}
```

---

## 13. Server Components (Next.js 15)

```typescript
// ✅ DO: Server Component with async data
interface User {
  id: string
  name: string
  email: string
}

async function getUser(id: string): Promise<User> {
  const response = await fetch(`https://api.example.com/users/${id}`)
  if (!response.ok) {
    throw new Error('Failed to fetch user')
  }
  return response.json()
}

// Server Component (no 'use client')
async function UserProfile({ userId }: { userId: string }) {
  const user = await getUser(userId)

  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  )
}

// ✅ DO: Mix Server and Client Components
// app/page.tsx (Server Component)
import { ClientButton } from './ClientButton'

async function Page() {
  const data = await fetchServerData()

  return (
    <div>
      <h1>Server Data: {data.title}</h1>
      <ClientButton />
    </div>
  )
}

// ClientButton.tsx (Client Component)
'use client'

export function ClientButton() {
  const [count, setCount] = useState(0)

  return (
    <button onClick={() => setCount(c => c + 1)}>
      Clicked {count} times
    </button>
  )
}
```

---

## Test Requirements

**Every pattern must be tested:**

```typescript
// Component props
describe('Button', () => {
  it('should render with correct props', () => {
    const onClick = vi.fn()
    render(<Button label="Click me" onClick={onClick} />)

    const button = screen.getByRole('button', { name: 'Click me' })
    fireEvent.click(button)

    expect(onClick).toHaveBeenCalledOnce()
  })
})

// Event handlers
describe('Form', () => {
  it('should handle input change', () => {
    render(<Form />)

    const input = screen.getByRole('textbox')
    fireEvent.change(input, { target: { value: 'test' } })

    expect(input).toHaveValue('test')
  })
})

// Custom hooks
describe('useCounter', () => {
  it('should increment count', () => {
    const { result } = renderHook(() => useCounter(0))

    act(() => {
      result.current.increment()
    })

    expect(result.current.count).toBe(1)
  })
})
```

---

## Quick Reference

| Pattern | Type | Example |
|---------|------|---------|
| Props | `interface Props` | `{ label: string }` |
| Children | `React.ReactNode` | Any renderable content |
| Events | `React.XEvent<HTMLElement>` | `React.ChangeEvent<HTMLInputElement>` |
| Ref (DOM) | `useRef<HTMLElement>(null)` | `useRef<HTMLInputElement>(null)` |
| Ref (value) | `useRef<Type>()` | `useRef<number>()` |
| State | `useState<Type>()` | `useState<User \| null>(null)` |
| Context | `createContext<Type>()` | `createContext<AuthContext>()` |
| Custom Hook | Return type | `function useHook(): ReturnType` |
| forwardRef | `forwardRef<El, Props>` | `forwardRef<HTMLInputElement, Props>` |
