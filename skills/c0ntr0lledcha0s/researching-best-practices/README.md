# Researching Best Practices Skill Resources

This directory contains resources for the researching-best-practices skill.

## Directory Structure

### scripts/
Automation scripts for analyzing code against best practices:
- `check-practices.py` - Analyze code against best practice checklists
- `pattern-matcher.py` - Identify design patterns in code
- `security-audit.sh` - Quick security best practices check

### references/
Comprehensive best practice checklists covering all aspects of software development:

**Security**
- `security-checklist.md` - **OWASP-based security checklist** covering:
  - Input validation & sanitization
  - Authentication & authorization
  - Data protection & encryption
  - Injection prevention (SQL, XSS, etc.)
  - API security
  - Security headers
  - Dependency management
  - Error handling & logging
  - Infrastructure security

**Performance**
- `performance-checklist.md` - **Comprehensive performance optimization guide** covering:
  - Frontend performance (loading, runtime, third-party scripts)
  - Backend performance (code optimization, concurrency, caching, API design)
  - Database performance (query optimization, indexing, connection management)
  - Network & infrastructure (CDN, load balancing)
  - Mobile performance & PWA
  - Monitoring & debugging
  - Quick wins and common pitfalls
  - Performance budget template

**Code Quality**
- `code-quality-checklist.md` - **Clean code and quality practices** covering:
  - SOLID principles (SRP, OCP, LSP, ISP, DIP)
  - Clean code practices (naming, functions, comments, formatting)
  - DRY principle
  - Error handling strategies
  - Code organization & structure
  - Testing best practices
  - Security considerations
  - Documentation standards
  - Code review checklist
  - Language-specific best practices (TypeScript, JavaScript, Python, Go)
  - Refactoring indicators

**API Design**
- `api-design-checklist.md` - **RESTful and GraphQL API best practices** covering:
  - RESTful API design (resource naming, HTTP methods, status codes)
  - Request/response formats
  - Pagination, filtering, sorting
  - Error handling
  - Versioning strategies
  - Security (authentication, authorization, validation)
  - Performance (caching, rate limiting, optimization)
  - GraphQL best practices
  - Documentation requirements
  - Testing & monitoring
  - API governance
  - Common pitfalls to avoid

**Coming Soon:**
- `testing-strategies.md` - Testing approaches and methodologies
- `accessibility-checklist.md` - Web accessibility (WCAG) guidelines
- `devops-best-practices.md` - CI/CD, deployment, monitoring

### assets/
Templates for documenting research:
- `comparison-template.md` - Template for comparing different approaches
- `checklist-template.md` - Template for creating practice checklists
- `decision-matrix.md` - Template for evaluating technology options

## Usage

These resources are referenced in SKILL.md using the `{baseDir}` variable and are loaded on-demand when needed during research.

Example:
```markdown
See `{baseDir}/references/security-checklist.md` for comprehensive security guidelines.
```

## Contributing

To add new resources:
1. Create the file in the appropriate directory
2. Follow existing formatting conventions
3. Reference it in SKILL.md if needed
4. Update this README

---

*Part of research-agent plugin*
