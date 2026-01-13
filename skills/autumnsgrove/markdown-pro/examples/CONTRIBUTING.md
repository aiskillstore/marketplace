# Contributing to Project Name

Thank you for your interest in contributing! We welcome contributions from everyone and appreciate your help in making this project better.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

This project follows a Code of Conduct to ensure a welcoming environment for all contributors. By participating, you agree to:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards other community members

Report unacceptable behavior to [conduct@example.com](mailto:conduct@example.com).

## Getting Started

### Prerequisites

Before you begin, ensure you have:

- Python 3.8 or higher
- Git version control
- A GitHub account
- Familiarity with the project (read README.md)

### Find an Issue

1. Browse [open issues](https://github.com/username/repo/issues)
2. Look for issues labeled `good first issue` or `help wanted`
3. Comment on an issue you'd like to work on
4. Wait for assignment before starting work

Not sure where to start? Check out:
- [Good First Issues](https://github.com/username/repo/labels/good%20first%20issue)
- [Help Wanted](https://github.com/username/repo/labels/help%20wanted)
- [Documentation](https://github.com/username/repo/labels/documentation)

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/your-username/repo.git
cd repo

# Add upstream remote
git remote add upstream https://github.com/username/repo.git
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install package in editable mode with dev dependencies
pip install -e ".[dev]"

# Or install from requirements files
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 4. Install Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually (optional)
pre-commit run --all-files
```

### 5. Verify Setup

```bash
# Run tests to verify setup
pytest

# Check code quality
flake8 src/
black --check src/
mypy src/
```

## How to Contribute

### Reporting Bugs

Before creating a bug report:

1. Check existing issues to avoid duplicates
2. Use the latest version of the software
3. Determine which repository the issue belongs to

**Create a bug report with:**

- Clear, descriptive title
- Steps to reproduce the issue
- Expected vs actual behavior
- Screenshots (if applicable)
- Environment details (OS, Python version, etc.)
- Relevant logs or error messages

**Use the bug report template:**

```markdown
**Bug Description**
A clear description of the bug.

**To Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment**
- OS: [e.g., macOS 14.0]
- Python: [e.g., 3.11.5]
- Version: [e.g., 1.2.3]

**Additional Context**
Any other relevant information.
```

### Suggesting Features

Before creating a feature request:

1. Check if the feature already exists
2. Review open feature requests
3. Ensure it aligns with project goals

**Create a feature request with:**

- Clear, descriptive title
- Problem statement (what problem does this solve?)
- Proposed solution
- Alternative solutions considered
- Additional context

### Making Code Changes

#### 1. Create a Branch

```bash
# Update your fork
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

**Branch naming convention:**
- `feature/feature-name` - New features
- `fix/bug-description` - Bug fixes
- `docs/what-changed` - Documentation updates
- `refactor/what-changed` - Code refactoring
- `test/what-added` - Test additions/updates

#### 2. Make Your Changes

- Write clear, concise code
- Follow the coding standards (see below)
- Add tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic

#### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_feature.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run linting
flake8 src/
black src/
isort src/
mypy src/
```

#### 4. Commit Your Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add user authentication feature"

# Push to your fork
git push origin feature/your-feature-name
```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length**: 100 characters (not 79)
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes for strings, single quotes for string keys
- **Imports**: Organized with `isort`
- **Type hints**: Use type hints for function signatures

### Code Formatting

We use automated formatters:

```bash
# Format code with Black
black src/ tests/

# Sort imports with isort
isort src/ tests/

# Check with flake8
flake8 src/ tests/
```

### Code Structure

```python
"""Module docstring explaining the module purpose."""

import standard_library
import third_party_library

from package import local_module


CONSTANT_NAME = "value"


class ClassName:
    """Class docstring with description.

    Attributes:
        attribute_name: Description of attribute
    """

    def __init__(self, param: str) -> None:
        """Initialize class with parameters.

        Args:
            param: Description of parameter
        """
        self.attribute = param

    def method_name(self, arg: str) -> str:
        """Method with clear docstring.

        Args:
            arg: Description of argument

        Returns:
            Description of return value

        Raises:
            ValueError: When something goes wrong
        """
        return f"Result: {arg}"


def function_name(param: str, optional: bool = False) -> dict:
    """Function with clear documentation.

    Args:
        param: Description of parameter
        optional: Optional parameter description

    Returns:
        Dictionary with results

    Example:
        >>> function_name("test")
        {'result': 'test'}
    """
    return {"result": param}
```

### Documentation Standards

- Use Google-style docstrings
- Document all public APIs
- Include usage examples
- Keep documentation up-to-date with code
- Add inline comments for complex logic

## Commit Message Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting, missing semi-colons, etc.
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes

### Examples

```bash
# Feature
git commit -m "feat(auth): add OAuth2 authentication support"

# Bug fix
git commit -m "fix(api): resolve timeout issue with large payloads"

# Documentation
git commit -m "docs(readme): update installation instructions"

# Breaking change
git commit -m "feat(api): redesign user endpoint

BREAKING CHANGE: User endpoint now returns different format"
```

### Guidelines

- Use imperative mood ("add" not "added" or "adds")
- Capitalize first letter of subject
- No period at the end of subject
- Limit subject line to 50 characters
- Wrap body at 72 characters
- Reference issues/PRs in footer

## Pull Request Process

### Before Submitting

- [ ] All tests pass (`pytest`)
- [ ] Code is formatted (`black`, `isort`)
- [ ] Linting passes (`flake8`, `mypy`)
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] No merge conflicts with main branch

### Creating a Pull Request

1. **Push your branch** to your fork
2. **Navigate** to the original repository
3. **Click** "New Pull Request"
4. **Fill out** the PR template completely
5. **Link** related issues (e.g., "Closes #123")

### PR Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work)
- [ ] Documentation update

## Related Issues
Closes #123

## Testing
Describe the tests you ran and how to reproduce them.

## Screenshots
If applicable, add screenshots.

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code where necessary
- [ ] I have updated the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing tests pass locally
- [ ] I have updated CHANGELOG.md
```

### Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Push updates to the same branch
4. Once approved, your PR will be merged

**Review criteria:**
- Code quality and style
- Test coverage
- Documentation completeness
- Performance impact
- Backward compatibility

## Testing Guidelines

### Test Structure

```python
import pytest
from project import Module


class TestModule:
    """Test suite for Module class."""

    @pytest.fixture
    def module(self):
        """Create module instance for testing."""
        return Module(config="test")

    def test_basic_functionality(self, module):
        """Test basic module functionality."""
        result = module.process("input")
        assert result.success is True
        assert result.data == "expected"

    def test_error_handling(self, module):
        """Test error handling."""
        with pytest.raises(ValueError):
            module.process(None)

    @pytest.mark.parametrize("input,expected", [
        ("test1", "result1"),
        ("test2", "result2"),
    ])
    def test_multiple_inputs(self, module, input, expected):
        """Test with multiple input values."""
        result = module.process(input)
        assert result.data == expected
```

### Test Coverage

- Aim for >90% code coverage
- Write tests for all new features
- Test edge cases and error conditions
- Include integration tests where appropriate

```bash
# Run with coverage report
pytest --cov=src --cov-report=html --cov-report=term

# View coverage in browser
open htmlcov/index.html
```

## Documentation

### Types of Documentation

1. **Code Documentation**: Docstrings in code
2. **API Documentation**: Generated from docstrings
3. **User Guides**: How-to guides and tutorials
4. **README**: Project overview and quick start

### Building Documentation

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build documentation
cd docs
make html

# View documentation
open _build/html/index.html
```

### Documentation Style

- Write in clear, simple language
- Include code examples
- Use proper Markdown formatting
- Add screenshots where helpful
- Keep documentation up-to-date

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Discord**: [Join our server](https://discord.gg/example)
- **Email**: [dev@example.com](mailto:dev@example.com)

### Getting Help

- Read the documentation first
- Search existing issues
- Ask in GitHub Discussions
- Join our Discord for real-time help

### Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project README
- Social media mentions

## Thank You!

Your contributions, no matter how small, are valuable and appreciated. Thank you for helping make this project better!

---

**Questions?** Open an issue or reach out on [Discord](https://discord.gg/example).

**Need help?** Check our [FAQ](FAQ.md) or [documentation](https://docs.example.com).
