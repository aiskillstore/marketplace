# Web Search Skill - Usage Examples

This document demonstrates practical usage examples of the web-search skill for various common scenarios.

## Example 1: Technical Information Research

**Objective**: Research the latest features in a framework or library

**Query**:
```bash
bash scripts/web-search.sh "What are the new features in Next.js 15? Include information from official release notes and technical articles."
```

**Expected Output**:
- List of new features with descriptions
- Code examples demonstrating new capabilities
- Links to official documentation and release notes
- Migration guides if applicable

---

## Example 2: Library Documentation Search

**Objective**: Understanding how to use a specific library function or hook

**Query**:
```bash
bash scripts/web-search.sh "How does React Query's useQuery hook work? Provide code examples from official documentation."
```

**Expected Output**:
- Hook API reference
- Code examples showing basic and advanced usage
- Common patterns and best practices
- Links to official documentation

---

## Example 3: Error Resolution

**Objective**: Finding solutions to specific error messages

**Query**:
```bash
bash scripts/web-search.sh "TypeScript error: Type 'string' is not assignable to type 'number'. Find solutions and explanations on Stack Overflow and GitHub Issues."
```

**Expected Output**:
- Explanation of the error cause
- Multiple solution approaches
- Code examples demonstrating fixes
- Links to Stack Overflow discussions and GitHub issues

---

## Example 4: Latest News and Updates

**Objective**: Staying current with technology updates and announcements

**Query**:
```bash
bash scripts/web-search.sh "What are Claude AI's latest updates and features in 2025? Search for Anthropic announcements and tech news."
```

**Expected Output**:
- Summary of recent announcements
- New features and capabilities
- Release dates and availability
- Links to official announcements and news articles

---

## Example 5: Best Practices Research

**Objective**: Learning recommended approaches and patterns

**Query**:
```bash
bash scripts/web-search.sh "React performance optimization techniques. Include official documentation and community best practices for 2025."
```

**Expected Output**:
- List of optimization techniques
- Code examples demonstrating each technique
- Performance benchmarks if available
- Links to official guides and community articles

---

## Example 6: Comparative Analysis

**Objective**: Comparing different technologies or approaches

**Query**:
```bash
bash scripts/web-search.sh "Compare Vite and Webpack build tools. Include advantages, disadvantages, performance comparisons, and use case recommendations."
```

**Expected Output**:
- Feature comparison table
- Performance metrics
- Pros and cons for each tool
- Use case recommendations
- Links to official documentation and benchmark articles

---

## Key Search Query Patterns

### 1. Clear and Explicit Questions

**Good**:
- "Please explain Next.js 15's new features"
- "How do I implement authentication in React?"

**Avoid**:
- "Next.js 15"
- "React auth"

### 2. Source Specification

**Good**:
- "Find information from official Next.js documentation"
- "Search Stack Overflow for TypeScript solutions"

**Avoid**:
- "Find information about Next.js"

### 3. Request Specific Formats

**Good**:
- "Provide code examples"
- "Present results in table format"
- "Include benchmarks and performance metrics"

**Avoid**:
- "Tell me about performance"

### 4. Include Temporal/Conditional Modifiers

**Good**:
- "Latest React features in 2025"
- "Beginner-friendly Python tutorials"
- "Production-ready TypeScript patterns"

**Avoid**:
- "React features"
- "Python tutorials"

### 5. Request Analysis and Comparison

**Good**:
- "Compare Vite and Webpack, including pros and cons"
- "Analyze trade-offs between REST and GraphQL APIs"
- "Evaluate different state management solutions"

**Avoid**:
- "Vite vs Webpack"
- "REST or GraphQL"

---

## Advanced Usage Tips

### Combining Multiple Requirements

```bash
bash scripts/web-search.sh "Research Next.js 15 App Router features. Include:
- Official documentation links
- Code examples demonstrating new patterns
- Migration guide from Pages Router
- Community feedback and gotchas
- Performance comparisons with Pages Router"
```

### Targeting Specific Sources

```bash
bash scripts/web-search.sh "Find TypeScript 5.5 release notes from:
- Official TypeScript blog
- GitHub release page
- Microsoft DevBlogs
Include breaking changes and migration notes"
```

### Requesting Structured Output

```bash
bash scripts/web-search.sh "Compare three CSS-in-JS libraries: styled-components, Emotion, and vanilla-extract.
Present results in a comparison table with:
- Bundle size
- Performance metrics
- Developer experience
- Community adoption
- Pros and cons for each"
```

---

## Common Use Cases

### 1. Debugging Assistance
```bash
bash scripts/web-search.sh "Error: Cannot read property 'map' of undefined in React. Find common causes and solutions with code examples."
```

### 2. Learning New Technology
```bash
bash scripts/web-search.sh "Beginner's guide to using Prisma ORM with PostgreSQL. Include setup steps, basic CRUD examples, and best practices."
```

### 3. Performance Investigation
```bash
bash scripts/web-search.sh "Why is my Next.js app loading slowly? Find common performance bottlenecks and optimization strategies."
```

### 4. Security Research
```bash
bash scripts/web-search.sh "Best practices for securing JWT tokens in React applications. Include storage options, XSS prevention, and CSRF protection."
```

### 5. Migration Planning
```bash
bash scripts/web-search.sh "How to migrate from Webpack to Vite in a large React application? Include step-by-step guide and common challenges."
```

---

## Notes

- Always verify information from multiple sources
- Check the recency of information, especially for rapidly evolving technologies
- Cross-reference official documentation with community experiences
- Keep track of useful sources for future reference
- Iterate on queries if initial results are insufficient
