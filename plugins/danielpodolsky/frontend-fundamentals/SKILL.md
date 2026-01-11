---
name: Frontend Fundamentals
description: Auto-invoke when reviewing React, Vue, or frontend component code. Enforces component architecture, state management patterns, and UI best practices.
---

# Frontend Fundamentals Review

> "A component should do ONE thing well. If you're describing it with 'and', split it."

## When to Apply

Activate this skill when reviewing:
- React/Vue/Svelte components
- UI rendering logic
- State management code
- CSS/styling decisions
- Client-side routing

---

## Review Checklist

### Component Architecture

- [ ] **Single Responsibility**: Does each component do ONE job?
- [ ] **Size Check**: Is the component under 200 lines?
- [ ] **Props Count**: Are there fewer than 7 props?
- [ ] **Naming**: Can you describe the component without saying "and"?

### State Management

- [ ] **Colocation**: Is state as close as possible to where it's used?
- [ ] **Lifting**: Is state shared properly between siblings via parent?
- [ ] **Context vs Props**: Is prop drilling avoided (max 3 levels)?
- [ ] **Server State**: Is server data managed separately (React Query/SWR)?

### Performance

- [ ] **Memoization**: Are expensive computations wrapped in useMemo?
- [ ] **Callbacks**: Are event handlers wrapped in useCallback where needed?
- [ ] **Re-renders**: Will this cause unnecessary re-renders?
- [ ] **Lazy Loading**: Are heavy components code-split?

### Accessibility

- [ ] **Semantic HTML**: Are proper elements used (button vs div)?
- [ ] **ARIA**: Are interactive elements accessible?
- [ ] **Keyboard**: Can users navigate without a mouse?

---

## Common Mistakes (Anti-Patterns)

### 1. God Components
```
❌ UserDashboard.tsx (1000 lines)
   - fetches data, manages state, renders UI, handles routing

✅ Split into:
   - UserDashboardPage.tsx (container)
   - UserStats.tsx (presentation)
   - UserActivity.tsx (presentation)
   - useUserData.ts (hook)
```

### 2. Logic in Render
```
❌ return <div>{users.filter(u => u.active).map(u => ...)}</div>

✅ const activeUsers = useMemo(() => users.filter(u => u.active), [users]);
   return <div>{activeUsers.map(u => ...)}</div>
```

### 3. Prop Drilling
```
❌ <App user={user}>
     <Layout user={user}>
       <Main user={user}>
         <Widget user={user} />

✅ const user = useUser(); // in Widget.tsx
```

### 4. Boolean Prop Soup
```
❌ <Button primary secondary large small disabled loading />

✅ <Button variant="primary" size="large" state="loading" />
```

---

## Socratic Questions

Ask the junior these questions instead of giving answers:

1. **Architecture**: "What is the ONE job of this component?"
2. **Splitting**: "If I asked you to use just the header part elsewhere, could you?"
3. **State**: "Who needs this data? Should it live here or higher up?"
4. **Performance**: "What happens when the parent re-renders?"
5. **Complexity**: "Could a new developer understand this in 5 minutes?"

---

## Standards Reference

See detailed patterns in:
- `/standards/frontend/component-architecture.md`

---

## Red Flags to Call Out

| Flag | Question to Ask |
|------|-----------------|
| File > 200 lines | "Can we split this into smaller pieces?" |
| > 5 useState calls | "Should some of this state be lifted or combined?" |
| useEffect with [] deps but uses external values | "Are we missing dependencies?" |
| Direct DOM manipulation | "Is there a React way to do this?" |
| Inline styles everywhere | "Should we use a consistent styling approach?" |
