# Exa Research Skill - Usage Examples

Real-world examples of how AI agents can use the exa-research skill.

---

## Example 1: Learning a New Framework

**User Request:** "I want to learn Svelte 5"

**Agent Workflow:**

```python
# Step 1: Get overview
overview = await exa_web_search(
    query="Svelte 5 overview features runes 2025",
    numResults=10,
    type="deep"
)

# Step 2: Get code examples
examples = await exa_get_code_context(
    query="Svelte 5 runes examples getting started",
    tokensNum=8000
)

# Step 3: Find best practices
practices = await exa_web_search(
    query="Svelte 5 best practices 2025",
    numResults=8,
    type="deep"
)
```

**Result:** Comprehensive learning path with overview, working code, and best practices.

---

## Example 2: Solving a Specific Problem

**User Request:** "How do I fix hydration errors in Next.js?"

**Agent Workflow:**

```python
# Step 1: Understand the problem
problem = await exa_web_search(
    query="Next.js hydration errors causes solutions",
    numResults=10,
    type="deep"
)

# Step 2: Get working solutions
solutions = await exa_get_code_context(
    query="Next.js hydration error fix examples",
    tokensNum=5000
)
```

**Result:** Problem explanation and working code solutions.

---

## Example 3: Comparing Technologies

**User Request:** "Should I use Prisma or Drizzle ORM?"

**Agent Workflow:**

```python
# Step 1: Get comparison articles
comparison = await exa_web_search(
    query="Prisma vs Drizzle ORM comparison 2025",
    numResults=15,
    type="deep"
)

# Step 2: Get Prisma examples
prisma_code = await exa_get_code_context(
    query="Prisma ORM best practices examples",
    tokensNum=5000
)

# Step 3: Get Drizzle examples
drizzle_code = await exa_get_code_context(
    query="Drizzle ORM best practices examples",
    tokensNum=5000
)
```

**Result:** Detailed comparison with code examples for both options.

---

## Example 4: Discovering New Tools

**User Request:** "What are the latest AI coding assistants?"

**Agent Workflow:**

```python
# Step 1: Find latest tools
tools = await exa_web_search(
    query="latest AI coding assistants 2025",
    numResults=20,
    type="deep",
    livecrawl="preferred"
)

# Step 2: Get usage examples
usage = await exa_get_code_context(
    query="AI coding assistant integration examples",
    tokensNum=5000
)
```

**Result:** Comprehensive list of latest tools with integration examples.

---

## Example 5: Implementation Research

**User Request:** "How do I implement authentication in FastAPI?"

**Agent Workflow:**

```python
# Step 1: Find implementation guides
guides = await exa_web_search(
    query="how to implement authentication in FastAPI",
    numResults=8,
    type="deep"
)

# Step 2: Get working code
code = await exa_get_code_context(
    query="FastAPI JWT authentication implementation examples",
    tokensNum=8000
)
```

**Result:** Implementation guides and working code examples.

---

## Example 6: Staying Current

**User Request:** "What's new in the React ecosystem?"

**Agent Workflow:**

```python
# Step 1: Latest news
news = await exa_web_search(
    query="React ecosystem latest updates 2025",
    numResults=15,
    livecrawl="preferred"
)

# Step 2: New features code
features = await exa_get_code_context(
    query="React 19 new features examples",
    tokensNum=8000
)
```

**Result:** Latest news and code examples for new features.

---

## Example 7: Deep Technical Research

**User Request:** "Explain React Server Components in depth"

**Agent Workflow:**

```python
# Step 1: Conceptual overview
overview = await exa_web_search(
    query="React Server Components explained architecture",
    numResults=10,
    type="deep"
)

# Step 2: Implementation patterns
patterns = await exa_get_code_context(
    query="React Server Components implementation patterns",
    tokensNum=10000
)

# Step 3: Best practices
practices = await exa_web_search(
    query="React Server Components best practices 2025",
    numResults=8,
    type="deep"
)

# Step 4: Real-world examples
examples = await exa_get_code_context(
    query="React Server Components production examples",
    tokensNum=8000
)
```

**Result:** Comprehensive deep-dive with theory, patterns, practices, and examples.

---

## Example 8: Migration Planning

**User Request:** "How do I migrate from Create React App to Vite?"

**Agent Workflow:**

```python
# Step 1: Migration guides
guides = await exa_web_search(
    query="Create React App to Vite migration guide 2025",
    numResults=10,
    type="deep"
)

# Step 2: Migration code examples
code = await exa_get_code_context(
    query="CRA to Vite migration examples step by step",
    tokensNum=8000
)

# Step 3: Common issues
issues = await exa_web_search(
    query="CRA to Vite migration common issues solutions",
    numResults=8,
    type="deep"
)
```

**Result:** Complete migration guide with code and troubleshooting.

---

## Example 9: Ecosystem Research

**User Request:** "What tools work well with Next.js?"

**Agent Workflow:**

```python
# Step 1: Find ecosystem tools
tools = await exa_web_search(
    query="best Next.js tools libraries ecosystem 2025",
    numResults=15,
    type="deep"
)

# Step 2: Integration examples
integrations = await exa_get_code_context(
    query="Next.js popular libraries integration examples",
    tokensNum=8000
)
```

**Result:** Comprehensive ecosystem overview with integration examples.

---

## Example 10: Performance Optimization

**User Request:** "How can I optimize my React app performance?"

**Agent Workflow:**

```python
# Step 1: Optimization strategies
strategies = await exa_web_search(
    query="React performance optimization techniques 2025",
    numResults=10,
    type="deep"
)

# Step 2: Code optimization examples
code = await exa_get_code_context(
    query="React performance optimization code examples",
    tokensNum=8000
)

# Step 3: Profiling and debugging
profiling = await exa_web_search(
    query="React performance profiling debugging tools",
    numResults=8,
    type="deep"
)
```

**Result:** Complete optimization guide with strategies, code, and tools.

---

## Using Helper Scripts

### Query Optimizer

Before running research, optimize your query:

```bash
# Analyze and get recommendations
python skills/exa-research/scripts/query_optimizer.py analyze "authentication"

# Output:
# Recommended Tool: exa_get_code_context
# Optimized: authentication examples
# Suggestions:
#   1. Include framework/library name
#   2. Be more specific about the feature/API
```

### Research Workflows

Use pre-built workflows for common patterns:

```bash
# Technology research
python skills/exa-research/scripts/research_workflow.py technology "Astro"

# Implementation research
python skills/exa-research/scripts/research_workflow.py implementation "Next.js" "middleware"

# Comparison research
python skills/exa-research/scripts/research_workflow.py comparison "Tailwind" "UnoCSS"

# Discovery research
python skills/exa-research/scripts/research_workflow.py discovery "React state management"
```

---

## Tips for Effective Research

### 1. Start Broad, Then Narrow

```python
# First: Get the landscape
broad = await exa_web_search("GraphQL overview", numResults=10, type="deep")

# Then: Drill into specifics
specific = await exa_get_code_context("GraphQL mutations examples", tokensNum=5000)
```

### 2. Combine Both Tools

```python
# Web search for context
context = await exa_web_search("topic overview", numResults=10, type="deep")

# Code search for implementation
code = await exa_get_code_context("topic implementation", tokensNum=8000)
```

### 3. Use Live Crawl for Latest Info

```python
latest = await exa_web_search(
    "technology latest updates 2025",
    numResults=10,
    livecrawl="preferred"  # Get freshest content
)
```

### 4. Adjust Token Count Based on Need

```python
# Quick example
quick = await exa_get_code_context("React hooks", tokensNum=3000)

# Comprehensive guide
detailed = await exa_get_code_context("React hooks guide", tokensNum=10000)
```

### 5. Include Year for Current Info

```python
# Good
current = await exa_web_search("React best practices 2025", numResults=10)

# Less effective
outdated = await exa_web_search("React best practices", numResults=10)
```

---

## Common Patterns

### Pattern: Full Stack Research

```python
# Frontend
frontend = await exa_get_code_context("Next.js frontend examples", tokensNum=5000)

# Backend
backend = await exa_get_code_context("FastAPI backend examples", tokensNum=5000)

# Database
database = await exa_get_code_context("PostgreSQL integration examples", tokensNum=5000)

# Deployment
deployment = await exa_web_search("Next.js FastAPI deployment guide", numResults=8)
```

### Pattern: Learning Path

```python
# Beginner
beginner = await exa_get_code_context("technology getting started", tokensNum=5000)

# Intermediate
intermediate = await exa_get_code_context("technology intermediate patterns", tokensNum=8000)

# Advanced
advanced = await exa_get_code_context("technology advanced architecture", tokensNum=10000)
```

### Pattern: Problem Solving

```python
# Understand problem
problem = await exa_web_search("error description causes", numResults=10)

# Find solutions
solutions = await exa_get_code_context("error fix examples", tokensNum=5000)

# Best practices
practices = await exa_web_search("error prevention best practices", numResults=8)
```

---

## Advanced Usage

### Multi-Step Research

```python
# Step 1: Discovery
tools = await exa_web_search("category latest tools 2025", numResults=20)

# Step 2: Deep dive on interesting finds
for tool in interesting_tools:
    details = await exa_web_search(f"{tool} features review", numResults=5)
    code = await exa_get_code_context(f"{tool} examples", tokensNum=5000)
```

### Validation Research

```python
# Official docs
official = await exa_web_search("technology official documentation", numResults=5)

# Community validation
community = await exa_web_search("technology community best practices", numResults=10)

# Real-world examples
real_world = await exa_get_code_context("technology production examples", tokensNum=8000)
```

---

## Summary

The exa-research skill enables AI agents to:

1. ✅ Conduct comprehensive research on any technical topic
2. ✅ Find latest information with live crawling
3. ✅ Get working code examples
4. ✅ Compare different solutions
5. ✅ Discover new tools and trends
6. ✅ Learn new technologies effectively
7. ✅ Solve specific problems
8. ✅ Stay current with latest updates

All with optimized queries and proven workflows! 🚀

