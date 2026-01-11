# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in AI Architect Lite, please report it by:

1. **DO NOT** open a public issue
2. Email the maintainers (or create a private security advisory on GitHub)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and work with you to address the issue.

## Security Best Practices

When using AI Architect Lite:

### ✅ DO:
- Review generated code before execution
- Keep Python and dependencies updated
- Use virtual environments
- Validate file paths before operations
- Check `.gitignore` is properly configured

### ❌ DON'T:
- Commit `.env` files or secrets
- Run scripts with elevated privileges unnecessarily
- Modify files outside project root without review
- Store API keys or credentials in `.ai_context/`

## Known Limitations

1. **File System Access**: Scripts operate on local file system - ensure proper permissions
2. **Path Traversal**: While scripts use `Path.resolve()`, always review generated paths
3. **No Input Sanitization**: User inputs are not sanitized - use with trusted sources only

## Dependency Security

This project has minimal dependencies (Python stdlib only). If dependencies are added:
- Use `pip-audit` or similar tools regularly
- Pin versions in `requirements.txt`
- Review dependency licenses

## Updates

Security updates will be released as patch versions. Subscribe to releases to stay informed.

---

**Last Updated**: 2025-11-22
