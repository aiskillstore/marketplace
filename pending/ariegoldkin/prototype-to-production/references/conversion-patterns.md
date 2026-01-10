# HTML to React Conversion Patterns

Reference guide for converting HTML prototype patterns to production React/TypeScript components.

## Attribute Conversions

### Basic Attributes

| HTML | React |
|------|-------|
| `class="..."` | `className="..."` |
| `for="..."` | `htmlFor="..."` |
| `tabindex="0"` | `tabIndex={0}` |
| `readonly` | `readOnly` |
| `maxlength="100"` | `maxLength={100}` |
| `colspan="2"` | `colSpan={2}` |

### Event Handlers

| HTML | React |
|------|-------|
| `onclick="..."` | `onClick={handler}` |
| `onchange="..."` | `onChange={handler}` |
| `onsubmit="..."` | `onSubmit={handler}` |
| `onkeydown="..."` | `onKeyDown={handler}` |
| `onfocus="..."` | `onFocus={handler}` |
| `onblur="..."` | `onBlur={handler}` |

### Boolean Attributes

```tsx
// HTML
<input disabled>
<button hidden>

// React
<input disabled={true} />
<button hidden={true}>
```

## Style Conversions

### Inline Styles to Objects

```tsx
// HTML
<div style="background-color: blue; font-size: 16px; margin-top: 10px;">

// React
<div style={{ backgroundColor: 'blue', fontSize: '16px', marginTop: '10px' }}>
```

### Inline Styles to Tailwind

```tsx
// HTML
<div style="display: flex; justify-content: center; padding: 16px; background: #3b82f6;">

// React + Tailwind
<div className="flex justify-center p-4 bg-blue-500">
```

### Common Style Mappings

| CSS Property | Tailwind Class Pattern |
|--------------|----------------------|
| `display: flex` | `flex` |
| `justify-content: center` | `justify-center` |
| `align-items: center` | `items-center` |
| `padding: 16px` | `p-4` |
| `margin: 8px` | `m-2` |
| `background-color: #...` | `bg-{color}-{shade}` |
| `color: #...` | `text-{color}-{shade}` |
| `border-radius: 8px` | `rounded-lg` |
| `font-weight: 600` | `font-semibold` |
| `font-size: 14px` | `text-sm` |

## Form Elements

### Uncontrolled to Controlled Input

```tsx
// HTML (uncontrolled)
<input type="text" value="default">

// React (controlled)
const [value, setValue] = useState('default');

<input
  type="text"
  value={value}
  onChange={(e) => setValue(e.target.value)}
/>
```

### Select Element

```tsx
// HTML
<select>
  <option value="a">Option A</option>
  <option value="b" selected>Option B</option>
</select>

// React
const [selected, setSelected] = useState('b');

<select value={selected} onChange={(e) => setSelected(e.target.value)}>
  <option value="a">Option A</option>
  <option value="b">Option B</option>
</select>
```

### Checkbox

```tsx
// HTML
<input type="checkbox" checked>

// React
const [checked, setChecked] = useState(true);

<input
  type="checkbox"
  checked={checked}
  onChange={(e) => setChecked(e.target.checked)}
/>
```

### Form Submission

```tsx
// HTML
<form action="/submit" method="POST">

// React
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  // Handle submission
};

<form onSubmit={handleSubmit}>
```

## Interactive Elements

### Clickable Div to Button

```tsx
// HTML (anti-pattern)
<div onclick="handleClick()" class="button">Click me</div>

// React (accessible)
<button type="button" onClick={handleClick} className="button">
  Click me
</button>
```

### Link Button

```tsx
// HTML
<a href="#" onclick="doSomething()">Action</a>

// React (if navigation)
<Link href="/path">Action</Link>

// React (if action)
<button type="button" onClick={doSomething}>Action</button>
```

### Modal/Dialog

```tsx
// HTML
<div class="modal" style="display: none;">
  <div class="modal-content">...</div>
</div>

// React
const [isOpen, setIsOpen] = useState(false);

{isOpen && (
  <div
    className="modal"
    role="dialog"
    aria-modal="true"
    aria-labelledby="modal-title"
  >
    <div className="modal-content">
      <h2 id="modal-title">Title</h2>
      ...
    </div>
  </div>
)}
```

## Lists and Iteration

### Static List to Dynamic

```tsx
// HTML
<ul>
  <li>Item 1</li>
  <li>Item 2</li>
  <li>Item 3</li>
</ul>

// React
const items = ['Item 1', 'Item 2', 'Item 3'];

<ul>
  {items.map((item, index) => (
    <li key={index}>{item}</li>
  ))}
</ul>
```

### With Unique IDs (Preferred)

```tsx
interface Item {
  id: string;
  label: string;
}

const items: Item[] = [
  { id: '1', label: 'Item 1' },
  { id: '2', label: 'Item 2' },
];

<ul>
  {items.map((item) => (
    <li key={item.id}>{item.label}</li>
  ))}
</ul>
```

## Conditional Rendering

### Display Toggle

```tsx
// HTML
<div style="display: none;">Hidden content</div>

// React (unmount when hidden)
{isVisible && <div>Hidden content</div>}

// React (CSS hidden)
<div className={isVisible ? '' : 'hidden'}>Hidden content</div>
```

### Conditional Classes

```tsx
// HTML
<div class="card active">

// React with cn utility
<div className={cn('card', isActive && 'active')}>

// React with template literal
<div className={`card ${isActive ? 'active' : ''}`}>
```

## Image Handling

### Static Images

```tsx
// HTML
<img src="/images/logo.png" alt="Logo">

// React (with import)
import logo from './assets/logo.png';
<img src={logo} alt="Logo" />

// React (public folder)
<img src="/images/logo.png" alt="Logo" />
```

### Responsive Images

```tsx
// HTML
<img src="small.jpg" srcset="large.jpg 2x">

// React
<img
  src="/images/small.jpg"
  srcSet="/images/large.jpg 2x"
  alt="Description"
/>
```

## SVG Icons

### Inline SVG

```tsx
// HTML
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
  <path d="..." />
</svg>

// React Component
export const IconName = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    className={className}
    aria-hidden="true"
  >
    <path d="..." />
  </svg>
);
```

## Accessibility Additions

### Adding ARIA Labels

```tsx
// HTML (missing accessibility)
<button><svg>...</svg></button>

// React (accessible)
<button aria-label="Close menu" type="button">
  <svg aria-hidden="true">...</svg>
</button>
```

### Skip Link

```tsx
// Add to top of page
<a
  href="#main-content"
  className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4"
>
  Skip to main content
</a>

// Target
<main id="main-content" tabIndex={-1}>
```

### Focus Management

```tsx
// For modals, trap focus
import { FocusTrap } from '@headlessui/react';

<FocusTrap>
  <div className="modal">
    {/* Modal content */}
  </div>
</FocusTrap>
```

## Framework-Specific Patterns

### Next.js

```tsx
// Links
import Link from 'next/link';
<Link href="/about">About</Link>

// Images
import Image from 'next/image';
<Image src="/logo.png" alt="Logo" width={100} height={50} />

// Head/Metadata
import Head from 'next/head';
<Head>
  <title>Page Title</title>
</Head>
```

### React Router

```tsx
// Links
import { Link } from 'react-router-dom';
<Link to="/about">About</Link>

// Navigation
import { useNavigate } from 'react-router-dom';
const navigate = useNavigate();
navigate('/dashboard');
```
