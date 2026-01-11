---
name: pitfalls-react
description: React component patterns, forms, accessibility, and responsive design. Use when building React components, handling forms, or ensuring accessibility. Triggers on: React component, useEffect, form validation, a11y, responsive, Error Boundary.
---

# React Pitfalls

Common pitfalls and correct patterns for React development.

## When to Use

- Building React components
- Implementing form validation
- Adding error boundaries
- Ensuring accessibility (a11y)
- Creating responsive layouts
- Reviewing React code

## Workflow

### Step 1: Check Component Patterns

Verify loading/error states and data checks.

### Step 2: Verify Form Validation

Ensure Zod schemas and proper error display.

### Step 3: Check Accessibility

Verify ARIA labels and keyboard navigation.

---

## Component Patterns

```tsx
// ✅ Define helpers before use or as exports
function formatPrice(price: number) { ... }

export default function Component() {
  // ✅ Check data exists before accessing
  if (!data) return <Loading />;

  // ✅ useEffect for side effects only
  useEffect(() => {
    fetchData();
  }, []);

  // ✅ data-testid on interactive elements
  return <button data-testid="submit-btn">Submit</button>;
}

// ❌ WRONG: Defining function in render
return <button onClick={() => {
  function doSomething() { } // Don't define here
  doSomething();
}}>

// ✅ Navigation with router, not window
import { Link, useLocation } from 'wouter';
<Link to="/dashboard">Go</Link>
// ❌ window.location.href = '/dashboard'
```

## Error Boundary

```tsx
// ✅ Wrap major components in error boundaries
class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    logError({ error, componentStack: info.componentStack });
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback onRetry={() => this.setState({ hasError: false })} />;
    }
    return this.props.children;
  }
}

// ✅ Graceful degradation
function Dashboard() {
  const { data, error, isLoading } = useQuery(...);

  if (isLoading) return <Skeleton />;
  if (error) return <ErrorCard message="Unable to load" onRetry={refetch} />;
  if (!data) return <EmptyState />;

  return <DashboardContent data={data} />;
}
```

## Form Validation

```typescript
// ✅ Zod schemas for all forms
const createStrategySchema = z.object({
  name: z.string().min(1, 'Name required').max(100),
  type: z.enum(['cross-exchange', 'triangular']),
  minProfit: z.number().positive('Must be positive'),
});

// ✅ React Hook Form with Zod
const form = useForm<z.infer<typeof createStrategySchema>>({
  resolver: zodResolver(createStrategySchema),
});

// ✅ Show errors inline
{errors.name && <span className="text-red-500">{errors.name.message}</span>}

// ✅ Disable submit while validating/submitting
<button disabled={isSubmitting || !isValid}>Submit</button>
```

## Responsive Layout

```css
/* ✅ Mobile-first breakpoints */
.container { padding: 1rem; }

@media (min-width: 768px) {
  .container { padding: 2rem; }
}

/* ✅ Touch-friendly button sizes (min 44px) */
.btn { min-height: 44px; min-width: 44px; }

/* ✅ Horizontal scroll for data tables on mobile */
.table-container { overflow-x: auto; }
```

## Accessibility (a11y)

```tsx
// ✅ Semantic HTML
<nav>...</nav>
<main>...</main>
<button>Click me</button>  // Not <div onClick>

// ✅ ARIA labels
<button aria-label="Close dialog">×</button>

// ✅ Keyboard navigation
<button onKeyDown={(e) => e.key === 'Enter' && handleClick()}>

// ✅ Focus indicators
button:focus { outline: 2px solid blue; outline-offset: 2px; }
```

## Quick Checklist

- [ ] Loading/error states handled
- [ ] data-testid on interactive elements
- [ ] Using router Link, not window.location
- [ ] Helper functions defined before use
- [ ] Error boundaries on major components
- [ ] Touch targets ≥ 44px
- [ ] ARIA labels on icon buttons
