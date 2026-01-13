# React 19 Upgrade Checklist

## Phase 1: Pre-Upgrade (React 18.3 First)

### Step 1: Update to React 18.3

```bash
npm install react@18.3.0 react-dom@18.3.0
```

- [ ] Update React to 18.3.0
- [ ] Update react-dom to 18.3.0
- [ ] Clear node_modules and reinstall if needed

### Step 2: Fix React 18.3 Warnings

- [ ] Run application in development mode
- [ ] Open browser console
- [ ] Fix all React warnings (these will be errors in React 19)
- [ ] Common warnings to look for:
  - Deprecated lifecycle methods
  - String refs usage
  - Legacy Context API usage
  - Deprecated findDOMNode calls

### Step 3: Run Test Suite

- [ ] Run full test suite: `npm test`
- [ ] Ensure all tests pass on React 18.3
- [ ] Fix any broken tests
- [ ] Add tests for critical user flows

### Step 4: Check Dependencies

- [ ] List all dependencies: `npm list --depth=0`
- [ ] Check each major dependency for React 19 support
- [ ] Update incompatible dependencies
- [ ] Create issue list for dependencies without React 19 support

---

## Phase 2: Upgrade to React 19

### Step 1: Update React Packages

```bash
# Update React
npm install react@19.2.1 react-dom@19.2.1

# Update TypeScript types
npm install --save-dev @types/react@19.0.0 @types/react-dom@19.0.0
```

- [ ] Update React to 19.2.1 (includes security patches)
- [ ] Update react-dom to 19.2.1
- [ ] Update TypeScript types
- [ ] Clear package-lock.json and reinstall

### Step 2: Verify JSX Transform

- [ ] Check `tsconfig.json` has `"jsx": "react-jsx"`
  ```json
  {
    "compilerOptions": {
      "jsx": "react-jsx"
    }
  }
  ```

- [ ] Or check `.babelrc` has `@babel/preset-react`
  ```json
  {
    "presets": [
      ["@babel/preset-react", {
        "runtime": "automatic"
      }]
    ]
  }
  ```

---

## Phase 3: Run Codemods

### Step 1: Run All React 19 Codemods

```bash
npx codemod@latest react/19/migration-recipe
```

- [ ] Run migration recipe
- [ ] Review all proposed changes
- [ ] Test after applying changes

### Step 2: Fix TypeScript Issues

```bash
npx types-react-codemod@latest preset-19 ./src
```

- [ ] Run TypeScript codemod
- [ ] Fix remaining type errors
- [ ] Update custom type definitions

### Step 3: Individual Codemods (if needed)

```bash
# PropTypes to TypeScript
npx codemod@latest react/prop-types-typescript

# String refs
npx codemod@latest react/19/replace-string-ref

# ReactDOM.render
npx codemod@latest react/19/replace-reactdom-render

# Ref callback returns
npx codemod@latest react/19/no-implicit-ref-callback-return
```

- [ ] Run individual codemods as needed
- [ ] Test each change incrementally

### Step 4: Review Codemod Changes

- [ ] **Don't blindly accept all changes**
- [ ] Review each file changed by codemods
- [ ] Understand what changed and why
- [ ] Test affected components

---

## Phase 4: Manual Code Updates

### Update 1: Replace ReactDOM.render

**Before:**
```javascript
import { render } from 'react-dom';
render(<App />, document.getElementById('root'));
```

**After:**
```javascript
import { createRoot } from 'react-dom/client';
const root = createRoot(document.getElementById('root'));
root.render(<App />);
```

- [ ] Find all `ReactDOM.render` calls
- [ ] Replace with `createRoot`
- [ ] Update error handling if needed

### Update 2: Remove forwardRef

**Before:**
```javascript
const MyInput = forwardRef((props, ref) => {
  return <input ref={ref} {...props} />;
});
```

**After:**
```javascript
function MyInput({ ref, ...props }) {
  return <input ref={ref} {...props} />;
}
```

- [ ] Identify all `forwardRef` usage
- [ ] Replace with `ref` as prop where possible
- [ ] Keep `forwardRef` if component needs it for compatibility

### Update 3: Replace propTypes

**Before:**
```javascript
function Heading({ text }) {
  return <h1>{text}</h1>;
}
Heading.propTypes = {
  text: PropTypes.string,
};
Heading.defaultProps = {
  text: 'Hello, world!',
};
```

**After:**
```javascript
interface Props {
  text?: string;
}
function Heading({ text = 'Hello, world!' }: Props) {
  return <h1>{text}</h1>;
}
```

- [ ] Find all `propTypes` usage
- [ ] Convert to TypeScript interfaces
- [ ] Move default values to function parameters

### Update 4: Update useRef() Calls

**Before:**
```javascript
const ref = useRef();
```

**After:**
```javascript
const ref = useRef(null);
// or
const ref = useRef<HTMLDivElement>(null);
```

- [ ] Find all `useRef()` without arguments
- [ ] Add initial value (`null` or `undefined`)

### Update 5: Fix String Refs

**Before:**
```javascript
class MyComponent extends React.Component {
  componentDidMount() {
    this.refs.input.focus();
  }
  render() {
    return <input ref='input' />;
  }
}
```

**After:**
```javascript
class MyComponent extends React.Component {
  inputRef = null;
  
  componentDidMount() {
    this.inputRef.focus();
  }
  render() {
    return <input ref={el => this.inputRef = el} />;
  }
}
```

- [ ] Find all string refs (`ref="myRef"`)
- [ ] Convert to callback refs
- [ ] Test component functionality

### Update 6: Update Context Providers

**Before:**
```javascript
<ThemeContext.Provider value={theme}>
  <App />
</ThemeContext.Provider>
```

**After:**
```javascript
<ThemeContext value={theme}>
  <App />
</ThemeContext>
```

- [ ] Find all `<Context.Provider>` usage
- [ ] Replace with `<Context>` directly
- [ ] `<Context.Provider>` still works but deprecated

---

## Phase 5: Testing

### Step 1: Run Full Test Suite

```bash
npm test
```

- [ ] Run all unit tests
- [ ] Run integration tests
- [ ] Run end-to-end tests
- [ ] Fix any failing tests

### Step 2: Manual Browser Testing

- [ ] Test critical user flows manually
- [ ] Test on multiple browsers (Chrome, Firefox, Safari, Edge)
- [ ] Test on mobile devices
- [ ] Test with slow network (throttle to 3G)

### Step 3: Check Console

- [ ] Open browser console
- [ ] Verify no React warnings
- [ ] Verify no React errors
- [ ] Check for deprecation warnings

### Step 4: Test Forms

- [ ] Test all form submissions
- [ ] Verify Actions work correctly
- [ ] Check pending states display properly
- [ ] Verify error handling works

### Step 5: Test Suspense

- [ ] Test all loading states
- [ ] Verify Suspense boundaries work
- [ ] Check skeleton loaders display correctly
- [ ] Test error boundaries

---

## Phase 6: Framework-Specific (Next.js)

### Update Next.js

```bash
npm install next@latest
```

- [ ] Update Next.js to 15.5.7+ (includes security patches)
- [ ] Update next.config.js if needed
- [ ] Test App Router features
- [ ] Test Pages Router (if using legacy pages)

### Test Server Components

- [ ] Test all async Server Components
- [ ] Verify data fetching works
- [ ] Test Server Actions
- [ ] Check revalidation works (`revalidatePath`, `revalidateTag`)

### Test Middleware

- [ ] Test middleware functions
- [ ] Verify routing works correctly
- [ ] Check authentication middleware
- [ ] Test redirects and rewrites

### Verify Deployment

- [ ] Build for production: `npm run build`
- [ ] Check build output for errors
- [ ] Test in staging environment
- [ ] Verify environment variables work

---

## Phase 7: Production Deployment

### Pre-Deployment

- [ ] Create detailed deployment plan
- [ ] Have rollback plan ready
- [ ] Schedule deployment during low-traffic period
- [ ] Notify team of deployment

### Deploy to Staging

- [ ] Deploy to staging environment
- [ ] Run full regression tests
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Load test if possible

### Deploy to Production

- [ ] Deploy to production
- [ ] Monitor error tracking (Sentry, Datadog, etc.)
- [ ] Watch Core Web Vitals
- [ ] Monitor user reports
- [ ] Check server logs

### Post-Deployment

- [ ] Monitor for 24-48 hours
- [ ] Check error rates haven't spiked
- [ ] Verify performance is stable or improved
- [ ] Gather user feedback
- [ ] Document any issues found

---

## Common Issues & Solutions

### Issue 1: "Your app is using an outdated JSX transform"

**Solution:** Enable modern JSX transform in `tsconfig.json`:
```json
{
  "compilerOptions": {
    "jsx": "react-jsx"
  }
}
```

### Issue 2: "Expected 1 argument but saw none" for useRef

**Solution:** Add initial value to useRef:
```javascript
const ref = useRef(null);
```

### Issue 3: Server Actions not working

**Solution:** Ensure you're using a framework that supports RSC (Next.js 15+, Remix, etc.)

### Issue 4: Type errors after upgrade

**Solution:** Run TypeScript codemod and update types:
```bash
npx types-react-codemod@latest preset-19 ./src
npm install --save-dev @types/react@19.0.0 @types/react-dom@19.0.0
```

### Issue 5: Tests failing with "createRoot is not a function"

**Solution:** Update test setup to use `createRoot`:
```javascript
import { createRoot } from 'react-dom/client';

const root = createRoot(container);
root.render(<App />);
```

---

## Rollback Plan

### If Critical Issues Occur

1. **Revert to previous version**
   ```bash
   npm install react@18.3.0 react-dom@18.3.0
   ```

2. **Revert code changes**
   ```bash
   git revert <commit-hash>
   ```

3. **Redeploy previous version**

4. **Investigate issues offline**

5. **Fix issues before attempting upgrade again**

---

## Timeline Estimate

| Phase | Estimated Time |
|-------|----------------|
| Pre-upgrade (React 18.3) | 1-2 days |
| Upgrade to React 19 | 1 day |
| Run codemods | 2-4 hours |
| Manual code updates | 2-5 days |
| Testing | 2-3 days |
| Framework-specific | 1-2 days |
| Production deployment | 1 day |
| **Total** | **7-14 days** |

**Note:** Timeline varies based on:
- Codebase size
- Test coverage
- Team size
- Complexity of application

---

## Success Criteria

- [ ] All tests passing
- [ ] No React warnings in console
- [ ] All critical user flows working
- [ ] Performance metrics stable or improved
- [ ] Error rates not increased
- [ ] Security audit passing
- [ ] Team confident in changes
