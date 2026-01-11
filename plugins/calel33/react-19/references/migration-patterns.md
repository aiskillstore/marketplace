# React 19 Migration Patterns

Comprehensive guide for migrating from React 18 to React 19, including breaking changes, codemods, and refactoring patterns.

---

## Breaking Changes

### 1. ReactDOM.render Removed

**Before (React 18):**
```javascript
import { render } from 'react-dom';

render(<App />, document.getElementById('root'));
```

**After (React 19):**
```javascript
import { createRoot } from 'react-dom/client';

const root = createRoot(document.getElementById('root'));
root.render(<App />);
```

**Codemod:**
```bash
npx codemod@latest react/19/replace-reactdom-render
```

---

### 2. forwardRef Deprecated

Refs are now regular props (no wrapping needed).

**Before (React 18):**
```javascript
import { forwardRef } from 'react';

const MyInput = forwardRef((props, ref) => {
  return <input ref={ref} {...props} />;
});
```

**After (React 19):**
```javascript
function MyInput({ ref, ...props }) {
  return <input ref={ref} {...props} />;
}
```

**Note:** `forwardRef` still works but is deprecated. Remove it for cleaner code.

---

### 3. PropTypes Removed

PropTypes are no longer bundled. Use TypeScript instead.

**Before (React 18):**
```javascript
import PropTypes from 'prop-types';

function Heading({ text, level }) {
  return <h1>{text}</h1>;
}

Heading.propTypes = {
  text: PropTypes.string,
  level: PropTypes.number
};

Heading.defaultProps = {
  text: 'Hello',
  level: 1
};
```

**After (React 19):**
```typescript
interface HeadingProps {
  text?: string;
  level?: number;
}

function Heading({ text = 'Hello', level = 1 }: HeadingProps) {
  return <h1>{text}</h1>;
}
```

**Codemod:**
```bash
npx codemod@latest react/prop-types-typescript
```

---

### 4. String Refs Removed

String refs are no longer supported.

**Before (React 18):**
```javascript
class MyComponent extends React.Component {
  componentDidMount() {
    this.refs.input.focus();
  }

  render() {
    return <input ref="input" />;
  }
}
```

**After (React 19):**
```javascript
class MyComponent extends React.Component {
  inputRef = null;

  componentDidMount() {
    this.inputRef?.focus();
  }

  render() {
    return <input ref={el => this.inputRef = el} />;
  }
}
```

**Or with createRef:**
```javascript
class MyComponent extends React.Component {
  inputRef = React.createRef();

  componentDidMount() {
    this.inputRef.current?.focus();
  }

  render() {
    return <input ref={this.inputRef} />;
  }
}
```

**Codemod:**
```bash
npx codemod@latest react/19/replace-string-ref
```

---

### 5. useRef Requires an Argument

**Before (React 18):**
```javascript
const ref = useRef(); // Allowed
```

**After (React 19):**
```javascript
const ref = useRef(null); // Required
// or
const ref = useRef<HTMLDivElement>(null);
```

TypeScript will error if you omit the argument.

---

### 6. Ref Callbacks Cannot Return Values

Implicit returns are now errors.

**Before (React 18):**
```javascript
<div ref={current => (instance = current)} /> // Implicit return
```

**After (React 19):**
```javascript
<div ref={current => {instance = current}} /> // Block statement
// or
<div ref={current => void (instance = current)} />
```

**Codemod:**
```bash
npx codemod@latest react/19/no-implicit-ref-callback-return
```

---

### 7. Context.Provider Simplified

You can now use Context directly instead of Context.Provider.

**Before (React 18):**
```javascript
<ThemeContext.Provider value={theme}>
  <App />
</ThemeContext.Provider>
```

**After (React 19):**
```javascript
<ThemeContext value={theme}>
  <App />
</ThemeContext>
```

**Note:** `Context.Provider` still works but is deprecated.

---

### 8. Modern JSX Transform Required

React 19 requires the modern JSX transform.

**tsconfig.json:**
```json
{
  "compilerOptions": {
    "jsx": "react-jsx"
  }
}
```

**Or .babelrc:**
```json
{
  "presets": [
    ["@babel/preset-react", {
      "runtime": "automatic"
    }]
  ]
}
```

Without this, you'll get: `"Your app is using an outdated JSX transform"`

---

## Common Pitfalls

### Pitfall 1: Actions Must Be Wrapped in Transitions

**❌ Wrong:**
```javascript
async function handleSubmit() {
  await updateData();
}
```

**✅ Correct:**
```javascript
const [isPending, startTransition] = useTransition();

async function handleSubmit() {
  startTransition(async () => {
    await updateData();
  });
}
```

**Or use useActionState (automatic transition):**
```javascript
const [state, formAction, isPending] = useActionState(
  async (prevState, formData) => {
    await updateData(formData);
  },
  {}
);
```

---

### Pitfall 2: Server Components Cannot Use Client Hooks

**❌ Wrong:**
```javascript
async function MyComponent() {
  const [state, setState] = useState(0); // Error!
  return <div>{state}</div>;
}
```

**✅ Correct:**
```javascript
'use client';
function MyComponent() {
  const [state, setState] = useState(0);
  return <div>{state}</div>;
}
```

**Rule:** If a component uses hooks (useState, useEffect, etc.), mark it with `'use client'`.

---

### Pitfall 3: Server Actions Need 'use server' Directive

**❌ Wrong:**
```javascript
// app/actions.js
export async function createPost(formData) {
  await db.posts.create({
    title: formData.get('title')
  });
}
```

**✅ Correct:**
```javascript
// app/actions.js
'use server';
export async function createPost(formData) {
  await db.posts.create({
    title: formData.get('title')
  });
}
```

---

### Pitfall 4: Secrets Must Be Read Inside Functions

**❌ Wrong (secret leaks to client):**
```javascript
'use server';
const API_KEY = process.env.API_KEY; // Bundled in client!

export async function fetchData() {
  return fetch('https://api.example.com', {
    headers: { 'Authorization': `Bearer ${API_KEY}` }
  });
}
```

**✅ Correct:**
```javascript
'use server';
export async function fetchData() {
  const API_KEY = process.env.API_KEY; // Read inside function
  
  return fetch('https://api.example.com', {
    headers: { 'Authorization': `Bearer ${API_KEY}` }
  });
}
```

---

### Pitfall 5: Client Components Cannot Import Server-Only Modules

**❌ Wrong:**
```javascript
'use client';
import { db } from '@/lib/database'; // Server-only!

function MyComponent() {
  const [data, setData] = useState([]);
  
  useEffect(() => {
    db.users.getAll().then(setData); // Fails - db doesn't exist in browser
  }, []);
  
  return <div>{data.map(...)}</div>;
}
```

**✅ Correct:**
```javascript
// app/actions.js
'use server';
import { db } from '@/lib/database';

export async function getUsers() {
  return await db.users.getAll();
}
```

```javascript
// app/users/page.js
'use client';
import { getUsers } from './actions';

function MyComponent() {
  const [data, setData] = useState([]);
  
  useEffect(() => {
    getUsers().then(setData); // Calls Server Action
  }, []);
  
  return <div>{data.map(...)}</div>;
}
```

---

## Step-by-Step Migration

### Step 1: Update to React 18.3 First

```bash
npm install react@18.3.0 react-dom@18.3.0
```

1. Run application
2. Fix all warnings in console (these become errors in React 19)
3. Ensure all tests pass

---

### Step 2: Update to React 19

```bash
npm install react@19.2.1 react-dom@19.2.1
npm install --save-dev @types/react@19.0.0 @types/react-dom@19.0.0
```

---

### Step 3: Run All Codemods

```bash
# Run entire migration recipe
npx codemod@latest react/19/migration-recipe
```

This runs:
- `replace-reactdom-render` - Updates ReactDOM.render to createRoot
- `replace-string-ref` - Converts string refs to callback refs
- `no-implicit-ref-callback-return` - Fixes ref callback returns
- `replace-act-import` - Updates test utilities

---

### Step 4: Fix TypeScript Issues

```bash
npx types-react-codemod@latest preset-19 ./src
```

Fixes:
- `useRef` requiring arguments
- Ref callback types
- Context types
- Event handler types

---

### Step 5: Manual Updates

#### Update Entry Point

**Before:**
```javascript
// index.js
import { render } from 'react-dom';
import App from './App';

render(<App />, document.getElementById('root'));
```

**After:**
```javascript
// index.js
import { createRoot } from 'react-dom/client';
import App from './App';

const root = createRoot(document.getElementById('root'));
root.render(<App />);
```

#### Enable Modern JSX Transform

**tsconfig.json:**
```json
{
  "compilerOptions": {
    "jsx": "react-jsx",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "target": "ES2020"
  }
}
```

#### Remove forwardRef

**Before:**
```javascript
const Input = forwardRef(({ label, ...props }, ref) => (
  <div>
    <label>{label}</label>
    <input ref={ref} {...props} />
  </div>
));
```

**After:**
```javascript
function Input({ label, ref, ...props }) {
  return (
    <div>
      <label>{label}</label>
      <input ref={ref} {...props} />
    </div>
  );
}
```

#### Convert PropTypes to TypeScript

**Before:**
```javascript
function Button({ onClick, children }) {
  return <button onClick={onClick}>{children}</button>;
}

Button.propTypes = {
  onClick: PropTypes.func.isRequired,
  children: PropTypes.node
};

Button.defaultProps = {
  children: 'Click me'
};
```

**After:**
```typescript
interface ButtonProps {
  onClick: () => void;
  children?: React.ReactNode;
}

function Button({ onClick, children = 'Click me' }: ButtonProps) {
  return <button onClick={onClick}>{children}</button>;
}
```

---

### Step 6: Test Thoroughly

```bash
# Run tests
npm test

# Build for production
npm run build

# Run application
npm start
```

**Test checklist:**
- [ ] All tests pass
- [ ] No console warnings
- [ ] Forms submit correctly
- [ ] Refs work (focus management, scroll, etc.)
- [ ] Context works correctly
- [ ] Production build succeeds
- [ ] Application runs without errors

---

## Framework-Specific Migrations

### Next.js

**Update to Next.js 15.5.7+:**
```bash
npm install next@latest
```

**next.config.js:**
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // React 19 requires modern JSX transform (default in Next 15+)
};

module.exports = nextConfig;
```

**App Router (Server Components):**
```javascript
// app/page.js (Server Component by default)
export default async function Home() {
  const data = await fetchData(); // Direct async/await
  return <div>{data}</div>;
}
```

**Client Components:**
```javascript
// app/counter.js
'use client';
import { useState } from 'react';

export function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

---

### Vite

**vite.config.js:**
```javascript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  esbuild: {
    jsxInject: `import React from 'react'`, // Optional
  }
});
```

**Update dependencies:**
```bash
npm install @vitejs/plugin-react@latest
```

---

### Create React App

**Note:** Create React App is no longer recommended. Migrate to:
- Next.js (recommended)
- Vite
- Remix

**Quick migration to Vite:**
```bash
# Create new Vite project
npm create vite@latest my-app -- --template react-ts

# Copy src/ and public/ folders
cp -r old-app/src new-app/src
cp -r old-app/public new-app/public

# Install dependencies
npm install
```

---

## TypeScript Migration

### Update tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "jsx": "react-jsx",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src"]
}
```

### Fix Common Type Errors

#### Error: "Expected 1 argument but saw none"

**Before:**
```typescript
const ref = useRef(); // Error
```

**After:**
```typescript
const ref = useRef<HTMLDivElement>(null);
```

#### Error: "Type 'string' is not assignable to type 'never'"

**Before:**
```typescript
const [value, setValue] = useState(); // Infers never
```

**After:**
```typescript
const [value, setValue] = useState<string>('');
```

#### Error: "Ref callback cannot return a value"

**Before:**
```typescript
<div ref={el => (ref.current = el)} /> // Implicit return
```

**After:**
```typescript
<div ref={el => void (ref.current = el)} />
// or
<div ref={el => {ref.current = el}} />
```

---

## Rollback Plan

If issues occur, revert to React 18:

```bash
# Revert React
npm install react@18.3.0 react-dom@18.3.0

# Revert code changes
git revert <commit-hash>

# Rebuild
npm run build
```

**Before rolling back:**
1. Document the error
2. Check GitHub issues for known problems
3. Test in isolated environment
4. Consider temporary fixes

---

## Migration Checklist

- [ ] **Pre-migration**
  - [ ] Update to React 18.3.0
  - [ ] Fix all React 18.3 warnings
  - [ ] All tests passing
  - [ ] Dependencies checked for React 19 support

- [ ] **Update packages**
  - [ ] React 19.2.1+
  - [ ] react-dom 19.2.1+
  - [ ] @types/react 19.0.0+
  - [ ] @types/react-dom 19.0.0+

- [ ] **Run codemods**
  - [ ] react/19/migration-recipe
  - [ ] types-react-codemod preset-19

- [ ] **Manual updates**
  - [ ] Modern JSX transform enabled
  - [ ] ReactDOM.render → createRoot
  - [ ] forwardRef removed (where possible)
  - [ ] PropTypes → TypeScript
  - [ ] String refs → callback refs
  - [ ] useRef() → useRef(null)

- [ ] **Testing**
  - [ ] All tests pass
  - [ ] No console warnings
  - [ ] Manual testing complete
  - [ ] Production build succeeds

- [ ] **Framework-specific**
  - [ ] Next.js 15.5.7+ (if using Next.js)
  - [ ] Server Components working
  - [ ] Server Actions working

---

## Troubleshooting

### "Your app is using an outdated JSX transform"

**Fix:** Enable modern JSX transform in `tsconfig.json`:
```json
{
  "compilerOptions": {
    "jsx": "react-jsx"
  }
}
```

---

### "Expected 1 argument but saw none" (useRef)

**Fix:** Add initial value:
```typescript
const ref = useRef<HTMLDivElement>(null);
```

---

### "Cannot find module 'react-dom/client'"

**Fix:** Update react-dom:
```bash
npm install react-dom@19.2.1
```

---

### Server Actions not working

**Fix:** Ensure you're using a framework with RSC support (Next.js 15+, Remix, etc.)

---

### Type errors after upgrade

**Fix:** Run TypeScript codemod:
```bash
npx types-react-codemod@latest preset-19 ./src
```

---

## Resources

- [Official React 19 Migration Guide](https://react.dev/blog/2024/12/05/react-19)
- [Codemod CLI](https://github.com/codemod-js/codemod)
- [TypeScript React Codemod](https://github.com/eps1lon/types-react-codemod)
- [Next.js 15 Upgrade Guide](https://nextjs.org/docs/app/building-your-application/upgrading/version-15)
