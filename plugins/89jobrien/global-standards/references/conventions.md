---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: global-standards
---

# Project Conventions

File structure, git workflows, and project organization standards.

## File Structure

### Organization

- Logical grouping of related files
- Consistent directory naming
- Clear separation of concerns
- Standard project layout

### Naming

- Use kebab-case for files and directories
- Match file names to their purpose
- Use descriptive names

## Git Workflows

### Commit Messages

- Use conventional commit format
- Write clear, descriptive messages
- Reference issues when applicable
- Keep commits focused and atomic

### Branching

- Use feature branches
- Follow branch naming conventions
- Keep branches up to date
- Clean up merged branches

## Configuration Files

### Environment Variables

- Use .env files for local development
- Document required variables
- Never commit secrets
- Provide .env.example template

### Dependencies

- Keep dependency files organized
- Document dependency purposes
- Use lock files for reproducibility
- Regularly update dependencies

## CI/CD

### Workflows

- Automate testing and linting
- Run checks before merging
- Deploy automatically on merge
- Monitor deployment status

### Quality Gates

- Require passing tests
- Enforce code style
- Check security vulnerabilities
- Validate configuration

## Documentation

### README

- Clear project description
- Setup instructions
- Usage examples
- Contributing guidelines

### Changelog

- Document all changes
- Use semantic versioning
- Group changes by type
- Include migration notes
