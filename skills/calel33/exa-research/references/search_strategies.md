# Advanced Search Strategies for Exa Research

This guide provides advanced strategies for conducting effective research using Exa AI tools.

## Strategy 1: Progressive Refinement

Start broad and progressively narrow your search based on findings.

### Phase 1: Discovery
```python
# Get the landscape
landscape = await exa_web_search(
    query="[topic] overview 2025",
    numResults=15,
    type="deep"
)
```

### Phase 2: Deep Dive
```python
# Based on findings, drill into specific areas
specific = await exa_web_search(
    query="[specific subtopic from phase 1] detailed guide",
    numResults=10,
    type="deep"
)
```

### Phase 3: Implementation
```python
# Get code examples for implementation
code = await exa_get_code_context(
    query="[specific subtopic] implementation examples",
    tokensNum=8000
)
```

## Strategy 2: Multi-Angle Research

Approach the topic from multiple angles for comprehensive understanding.

### Angle 1: What (Overview)
```python
what = await exa_web_search(
    query="what is [technology] features capabilities",
    numResults=10,
    type="deep"
)
```

### Angle 2: Why (Use Cases)
```python
why = await exa_web_search(
    query="why use [technology] benefits advantages",
    numResults=8,
    type="deep"
)
```

### Angle 3: How (Implementation)
```python
how = await exa_get_code_context(
    query="how to implement [technology] tutorial",
    tokensNum=8000
)
```

### Angle 4: When (Best Practices)
```python
when = await exa_web_search(
    query="when to use [technology] best practices",
    numResults=8,
    type="deep"
)
```

## Strategy 3: Comparative Analysis

Compare multiple solutions systematically.

### Step 1: Individual Research
```python
# Research each solution independently
solution_a_overview = await exa_web_search(
    query="[Solution A] features overview 2025",
    numResults=10,
    type="deep"
)

solution_b_overview = await exa_web_search(
    query="[Solution B] features overview 2025",
    numResults=10,
    type="deep"
)
```

### Step 2: Direct Comparison
```python
# Find comparison articles
comparison = await exa_web_search(
    query="[Solution A] vs [Solution B] comparison 2025",
    numResults=15,
    type="deep"
)
```

### Step 3: Code Comparison
```python
# Get code examples for each
solution_a_code = await exa_get_code_context(
    query="[Solution A] implementation examples best practices",
    tokensNum=5000
)

solution_b_code = await exa_get_code_context(
    query="[Solution B] implementation examples best practices",
    tokensNum=5000
)
```

### Step 4: Community Insights
```python
# Find community opinions
community = await exa_web_search(
    query="[Solution A] vs [Solution B] developer experience reddit",
    numResults=10,
    type="deep"
)
```

## Strategy 4: Temporal Research

Research how something has evolved over time.

### Current State
```python
current = await exa_web_search(
    query="[technology] latest features 2025",
    numResults=10,
    livecrawl="preferred"
)
```

### Recent Changes
```python
changes = await exa_web_search(
    query="[technology] what's new updates 2024 2025",
    numResults=15,
    type="deep"
)
```

### Future Direction
```python
future = await exa_web_search(
    query="[technology] roadmap future plans 2025",
    numResults=8,
    type="deep"
)
```

## Strategy 5: Problem-Solution Research

Research specific problems and their solutions.

### Step 1: Problem Understanding
```python
problem = await exa_web_search(
    query="[problem description] common issues",
    numResults=10,
    type="deep"
)
```

### Step 2: Solution Discovery
```python
solutions = await exa_web_search(
    query="how to solve [problem] in [framework]",
    numResults=15,
    type="deep"
)
```

### Step 3: Code Solutions
```python
code_solutions = await exa_get_code_context(
    query="[framework] [problem] solution examples",
    tokensNum=8000
)
```

### Step 4: Best Practices
```python
best_practices = await exa_web_search(
    query="[problem] best practices prevention",
    numResults=8,
    type="deep"
)
```

## Strategy 6: Ecosystem Research

Research an entire ecosystem around a technology.

### Core Technology
```python
core = await exa_web_search(
    query="[technology] core features documentation",
    numResults=10,
    type="deep"
)
```

### Tools and Libraries
```python
tools = await exa_web_search(
    query="best [technology] tools libraries 2025",
    numResults=15,
    type="deep"
)
```

### Integration Patterns
```python
integrations = await exa_get_code_context(
    query="[technology] integration examples common patterns",
    tokensNum=8000
)
```

### Community Resources
```python
community = await exa_web_search(
    query="[technology] community resources tutorials courses",
    numResults=10,
    type="deep"
)
```

## Strategy 7: Learning Path Research

Create a structured learning path for a new technology.

### Beginner Level
```python
beginner = await exa_get_code_context(
    query="[technology] beginner tutorial getting started",
    tokensNum=8000
)
```

### Intermediate Level
```python
intermediate = await exa_web_search(
    query="[technology] intermediate concepts patterns",
    numResults=10,
    type="deep"
)

intermediate_code = await exa_get_code_context(
    query="[technology] intermediate examples real-world projects",
    tokensNum=8000
)
```

### Advanced Level
```python
advanced = await exa_web_search(
    query="[technology] advanced techniques optimization",
    numResults=10,
    type="deep"
)

advanced_code = await exa_get_code_context(
    query="[technology] advanced patterns architecture",
    tokensNum=10000
)
```

## Strategy 8: Validation Research

Validate information from multiple sources.

### Official Sources
```python
official = await exa_web_search(
    query="[technology] official documentation",
    numResults=5,
    type="deep"
)
```

### Community Validation
```python
community = await exa_web_search(
    query="[technology] community best practices",
    numResults=10,
    type="deep"
)
```

### Real-World Examples
```python
real_world = await exa_get_code_context(
    query="[technology] production examples real projects",
    tokensNum=8000
)
```

### Expert Opinions
```python
experts = await exa_web_search(
    query="[technology] expert review analysis",
    numResults=8,
    type="deep"
)
```

## Best Practices for All Strategies

1. **Always use `type="deep"`** for comprehensive research
2. **Use `livecrawl="preferred"`** for latest information
3. **Adjust `numResults`** based on topic complexity (10-20 for deep research)
4. **Adjust `tokensNum`** based on detail needed (5000-10000 for comprehensive)
5. **Combine web and code search** for complete understanding
6. **Iterate based on findings** - refine queries as you learn more
7. **Validate from multiple sources** - don't rely on single results
8. **Document your findings** - keep track of what you've learned

## Common Pitfalls to Avoid

1. **Too broad queries** - Be specific about what you want
2. **Ignoring dates** - Always include year for latest info
3. **Single-source research** - Use multiple angles and sources
4. **Skipping code examples** - Theory without practice is incomplete
5. **Not iterating** - First results may not be perfect
6. **Ignoring context** - Understand the bigger picture
7. **Over-relying on one tool** - Use both web and code search

