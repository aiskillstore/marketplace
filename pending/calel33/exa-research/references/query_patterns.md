# Effective Query Patterns for Exa Research

This guide provides proven query patterns for different research scenarios.

## Web Search Query Patterns

### Pattern 1: Technology Overview
```
"[Technology] overview features capabilities 2025"
"what is [Technology] and how does it work"
"[Technology] introduction guide for beginners"
```

**Examples:**
- "Next.js 15 overview features capabilities 2025"
- "what is Rust and how does it work"
- "FastAPI introduction guide for beginners"

### Pattern 2: Latest Updates
```
"[Technology] latest updates 2025"
"[Technology] what's new in [version]"
"[Technology] recent changes improvements"
```

**Examples:**
- "React latest updates 2025"
- "Python what's new in 3.12"
- "TypeScript recent changes improvements"

### Pattern 3: Comparisons
```
"[Solution A] vs [Solution B] comparison 2025"
"[Solution A] versus [Solution B] pros cons"
"choosing between [Solution A] and [Solution B]"
```

**Examples:**
- "Next.js vs Remix comparison 2025"
- "PostgreSQL versus MongoDB pros cons"
- "choosing between REST and GraphQL"

### Pattern 4: Best Practices
```
"[Technology] best practices 2025"
"[Technology] common mistakes to avoid"
"[Technology] production tips optimization"
```

**Examples:**
- "React best practices 2025"
- "Docker common mistakes to avoid"
- "Node.js production tips optimization"

### Pattern 5: Problem Solving
```
"how to fix [error] in [Technology]"
"[Technology] [problem] solutions"
"troubleshooting [Technology] [issue]"
```

**Examples:**
- "how to fix CORS errors in Next.js"
- "React hydration mismatch solutions"
- "troubleshooting PostgreSQL connection issues"

### Pattern 6: Use Cases
```
"when to use [Technology]"
"[Technology] use cases examples"
"is [Technology] good for [use case]"
```

**Examples:**
- "when to use Redis"
- "GraphQL use cases examples"
- "is Rust good for web development"

### Pattern 7: Tool Discovery
```
"best [category] tools 2025"
"top [category] libraries frameworks"
"latest [category] solutions"
```

**Examples:**
- "best AI coding tools 2025"
- "top React state management libraries"
- "latest authentication solutions"

### Pattern 8: Migration Guides
```
"migrating from [Old] to [New]"
"[Old] to [New] migration guide"
"how to switch from [Old] to [New]"
```

**Examples:**
- "migrating from JavaScript to TypeScript"
- "Next.js 14 to 15 migration guide"
- "how to switch from REST to GraphQL"

## Code Search Query Patterns

### Pattern 1: Getting Started
```
"[Technology] getting started tutorial"
"[Technology] hello world example"
"[Technology] basic setup configuration"
```

**Examples:**
- "FastAPI getting started tutorial"
- "React hooks hello world example"
- "Docker basic setup configuration"

### Pattern 2: Specific Features
```
"[Technology] [feature] implementation examples"
"how to use [Technology] [feature]"
"[Technology] [feature] code samples"
```

**Examples:**
- "Next.js server actions implementation examples"
- "how to use React useEffect hook"
- "PostgreSQL full-text search code samples"

### Pattern 3: Authentication/Authorization
```
"[Framework] authentication implementation"
"[Framework] [auth method] setup examples"
"[Framework] user authentication best practices"
```

**Examples:**
- "Next.js authentication implementation"
- "FastAPI JWT setup examples"
- "React user authentication best practices"

### Pattern 4: Database Integration
```
"[Framework] [database] integration examples"
"[Framework] database connection setup"
"[Framework] ORM implementation"
```

**Examples:**
- "Next.js PostgreSQL integration examples"
- "FastAPI database connection setup"
- "Django ORM implementation"

### Pattern 5: API Development
```
"[Framework] REST API examples"
"[Framework] API routes implementation"
"[Framework] GraphQL server setup"
```

**Examples:**
- "Express REST API examples"
- "Next.js API routes implementation"
- "Apollo GraphQL server setup"

### Pattern 6: State Management
```
"[Framework] state management examples"
"[Framework] [state library] implementation"
"[Framework] global state patterns"
```

**Examples:**
- "React state management examples"
- "Next.js Zustand implementation"
- "Vue global state patterns"

### Pattern 7: Testing
```
"[Framework] testing examples"
"[Framework] unit test setup"
"[Framework] integration testing patterns"
```

**Examples:**
- "React testing library examples"
- "FastAPI pytest setup"
- "Next.js integration testing patterns"

### Pattern 8: Deployment
```
"[Framework] deployment configuration"
"[Framework] production setup"
"[Framework] [platform] deployment guide"
```

**Examples:**
- "Next.js deployment configuration"
- "FastAPI production setup"
- "React Vercel deployment guide"

### Pattern 9: Performance Optimization
```
"[Framework] performance optimization"
"[Framework] caching implementation"
"[Framework] lazy loading examples"
```

**Examples:**
- "React performance optimization"
- "Next.js caching implementation"
- "Vue lazy loading examples"

### Pattern 10: Real-World Patterns
```
"[Framework] real-world examples"
"[Framework] production code patterns"
"[Framework] enterprise architecture"
```

**Examples:**
- "Next.js real-world examples"
- "FastAPI production code patterns"
- "React enterprise architecture"

## Combined Research Patterns

### Pattern 1: Full Technology Research
```python
# Web: Overview
overview = await exa_web_search(
    "[Technology] overview features 2025",
    numResults=10,
    type="deep"
)

# Code: Examples
examples = await exa_get_code_context(
    "[Technology] getting started examples",
    tokensNum=8000
)

# Web: Best Practices
practices = await exa_web_search(
    "[Technology] best practices 2025",
    numResults=8,
    type="deep"
)
```

### Pattern 2: Implementation Research
```python
# Web: Guides
guides = await exa_web_search(
    "how to implement [feature] in [Framework]",
    numResults=10,
    type="deep"
)

# Code: Working Examples
code = await exa_get_code_context(
    "[Framework] [feature] implementation examples",
    tokensNum=8000
)
```

### Pattern 3: Problem-Solution Research
```python
# Web: Problem Understanding
problem = await exa_web_search(
    "[error/issue] in [Technology] causes solutions",
    numResults=10,
    type="deep"
)

# Code: Solution Examples
solution = await exa_get_code_context(
    "[Technology] [error/issue] fix examples",
    tokensNum=5000
)
```

## Query Optimization Tips

### For Web Search

**Add Specificity:**
- ❌ "AI tools"
- ✅ "latest AI coding tools 2025"

**Add Context:**
- ❌ "Next.js"
- ✅ "Next.js 15 new features overview"

**Add Timeframe:**
- ❌ "React best practices"
- ✅ "React best practices 2025"

**Add Comparison:**
- ❌ "state management"
- ✅ "Redux vs Zustand comparison 2025"

### For Code Search

**Add Framework:**
- ❌ "authentication examples"
- ✅ "Next.js authentication examples"

**Add Feature:**
- ❌ "React code"
- ✅ "React useState hook examples"

**Add Context:**
- ❌ "API"
- ✅ "FastAPI REST API implementation examples"

**Add Use Case:**
- ❌ "database"
- ✅ "Next.js PostgreSQL integration examples"

## Common Query Mistakes

### Mistake 1: Too Broad
❌ "programming"
❌ "web development"
❌ "database"

✅ "Next.js server components tutorial"
✅ "React authentication implementation"
✅ "PostgreSQL full-text search examples"

### Mistake 2: Too Generic
❌ "code examples"
❌ "tutorial"
❌ "how to code"

✅ "FastAPI async database queries examples"
✅ "React custom hooks tutorial"
✅ "how to implement JWT authentication in Express"

### Mistake 3: Missing Context
❌ "useState"
❌ "API routes"
❌ "authentication"

✅ "React useState hook examples"
✅ "Next.js API routes implementation"
✅ "FastAPI JWT authentication setup"

### Mistake 4: Outdated
❌ "React best practices"
❌ "Node.js tutorial"
❌ "JavaScript features"

✅ "React best practices 2025"
✅ "Node.js 20 tutorial"
✅ "JavaScript ES2024 features"

## Advanced Query Techniques

### Technique 1: Layered Queries
Start broad, then narrow based on results:
1. "[Technology] overview"
2. "[Specific Feature from results] detailed guide"
3. "[Specific Implementation] code examples"

### Technique 2: Multi-Perspective
Same topic, different angles:
1. "[Technology] features" (what)
2. "[Technology] benefits" (why)
3. "[Technology] implementation" (how)
4. "[Technology] use cases" (when)

### Technique 3: Validation Queries
Cross-reference information:
1. "[Technology] official documentation"
2. "[Technology] community best practices"
3. "[Technology] real-world examples"
4. "[Technology] expert reviews"

### Technique 4: Temporal Queries
Understand evolution:
1. "[Technology] history evolution"
2. "[Technology] current state 2025"
3. "[Technology] future roadmap"

