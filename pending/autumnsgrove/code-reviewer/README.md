# Code Reviewer Skill

Comprehensive automated code review skill for identifying security vulnerabilities, quality issues, performance problems, and ensuring best practices.

## Overview

This skill provides structured workflows and automated tools for conducting thorough code reviews across security, quality, performance, and maintainability dimensions.

## What's Included

### SKILL.md
Main skill file with:
- Systematic code review workflow (6 phases)
- Security vulnerability patterns
- Code quality analysis guidelines
- Performance review checklist
- Testing assessment criteria
- Documentation standards

### scripts/review_helper.py
Automated analysis tool supporting:
- Security scanning with Bandit
- Complexity analysis with Radon
- Quality checks with Pylint
- Dependency vulnerability scanning with Safety
- Report generation (Markdown, JSON, text)

**Usage:**
```bash
# Full review
python scripts/review_helper.py --file path/to/code --report full

# Security scan only
python scripts/review_helper.py --file path/to/code --security-scan

# Complexity analysis
python scripts/review_helper.py --file path/to/code --complexity

# Generate report to file
python scripts/review_helper.py --file path/to/code --report full --output report.md
```

**Installation:**
```bash
pip install radon bandit safety pylint
```

### examples/review_checklist.md
Comprehensive checklist covering:
- Security review (authentication, input validation, data protection)
- Code quality (design, structure, complexity, naming)
- Performance (algorithms, memory, database, network)
- Testing (coverage, quality, completeness)
- Documentation (code comments, API docs, external docs)
- Language-specific considerations (Python, JS/TS, Java, Go)

### examples/security_patterns.md
Security vulnerability catalog:
- Injection attacks (SQL, command, path traversal)
- Authentication & authorization issues
- Sensitive data exposure
- Security misconfiguration
- Cross-site scripting (XSS)
- Insecure deserialization
- Cryptographic weaknesses
- Security headers

Each pattern includes:
- Vulnerable code examples
- Secure implementations
- Detection tips
- Prevention strategies

### references/performance_guide.md
Performance optimization reference:
- Algorithm efficiency (Big-O analysis, common optimizations)
- Database optimization (N+1 queries, indexing, query optimization)
- Memory management (leak prevention, streaming, pooling)
- Network & I/O (async operations, timeouts, batching)
- Caching strategies (memoization, application-level, invalidation)
- Concurrency & parallelism (thread pools, process pools)
- Language-specific optimizations (Python, JavaScript, Go)
- Profiling tools and techniques

## Quick Start

1. **Activate the skill** by mentioning "code review" or specific review needs
2. **Run automated scans** using the review_helper.py script
3. **Use the checklist** from examples/review_checklist.md for systematic reviews
4. **Reference security patterns** when reviewing for vulnerabilities
5. **Consult performance guide** when optimizing code

## Review Workflow

1. **Initial Analysis** - Understand context and scope
2. **Security Review** - Check for vulnerabilities and security issues
3. **Code Quality Analysis** - Evaluate structure, complexity, and maintainability
4. **Performance Review** - Identify bottlenecks and optimization opportunities
5. **Testing Assessment** - Verify coverage and test quality
6. **Documentation Review** - Ensure completeness and clarity

## When to Use

- Reviewing pull requests or merge requests
- Conducting security audits
- Evaluating code before deployment
- Identifying technical debt
- Establishing team review standards
- Learning effective code review practices

## Supported Languages

Primary focus: Python, JavaScript/TypeScript, Java, Go

The patterns and principles apply broadly across languages, with specific guidance provided for:
- Python (type hints, context managers, comprehensions)
- JavaScript/TypeScript (async/await, TypeScript typing, event listeners)
- Java (exception handling, try-with-resources, thread safety)
- Go (error handling, goroutines, context usage)

## Integration with Development Workflow

The review_helper.py script can be integrated into:
- Pre-commit hooks
- CI/CD pipelines
- Pull request automation
- Local development workflows

Example GitHub Actions integration:
```yaml
- name: Run Code Review
  run: |
    pip install radon bandit safety pylint
    python code-reviewer/scripts/review_helper.py \
      --file . \
      --report full \
      --output review-report.md
```

## Customization

Adapt the skill to your team's needs:
- Modify complexity thresholds in SKILL.md
- Add language-specific patterns to security_patterns.md
- Extend review_helper.py with additional tools
- Customize the checklist for your tech stack

## License

Part of ClaudeSkills library. See main repository for license information.

## Contributing

Contributions welcome! Please:
- Add new security patterns with examples
- Expand performance optimization techniques
- Include additional language-specific guidance
- Share real-world review scenarios
