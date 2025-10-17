# Contributing to Data MCP

Thank you for your interest in contributing to Data MCP! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Code Style](#code-style)
- [Documentation](#documentation)
- [Reporting Issues](#reporting-issues)
- [Feature Requests](#feature-requests)
- [Questions and Discussion](#questions-and-discussion)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/dmcp.git
   cd dmcp
   ```
3. **Add the upstream remote**:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/dmcp.git
   ```

## Development Setup

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Git

### Installation

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Initialize the database**:
   ```bash
   uv run alembic upgrade head
   ```

4. **Run tests** to verify setup:
   ```bash
   uv run pytest
   ```

## Making Changes

### Branch Strategy

- Create a new branch for each feature or bugfix
- Use descriptive branch names: `feature/add-mysql-support`, `fix/connection-pool-issue`
- Keep branches focused and small

```bash
git checkout -b feature/your-feature-name
```

### Commit Messages

Follow conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
- `feat(datasource): add MongoDB support`
- `fix(auth): resolve JWT token validation issue`
- `docs(api): update endpoint documentation`

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_datasource_api.py

# Run with coverage
uv run pytest --cov=app

# Run with verbose output
uv run pytest -v
```

### Writing Tests

- Write tests for all new functionality
- Follow the existing test patterns in the `tests/` directory
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies appropriately

### Test Structure

```python
def test_feature_name():
    """Test description."""
    # Arrange
    # Act
    # Assert
```

## Submitting Changes

### Pull Request Process

1. **Ensure your code follows the style guidelines**
2. **Update documentation** if needed
3. **Add tests** for new functionality
4. **Update the changelog** if applicable
5. **Submit a pull request** with a clear description

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Updated existing tests

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## Code Style

### Python

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use type hints where appropriate
- Maximum line length: 88 characters
- Use Ruff for code formatting and linting
- Use mypy for type checking

### Formatting and Linting

Use the provided Makefile targets for code quality checks:

```bash
# Format code
make format

# Check for linting issues
make lint

# Auto-fix linting issues
make lint-fix

# Check formatting without changing files
make format-check

# Type checking
make typecheck

# Run all checks (lint, format-check, typecheck)
make check

# Auto-fix and format
make fix
```

Alternatively, you can use the underlying commands directly:

```bash
# Format code
uv run ruff format .

# Check for issues
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Type checking
uv run mypy .
```

### Pre-commit Hooks

The project includes pre-commit hooks to automatically check code quality before commits. To enable them:

```bash
# Install hooks (pre-commit is already in dev dependencies)
uv run pre-commit install

# Run manually on all files
uv run pre-commit run --all-files
```

The pre-commit hooks will automatically run Ruff linting, formatting, and mypy type checking on staged files before each commit.

## Documentation

### Code Documentation

- Use docstrings for all public functions and classes
- Follow Google or NumPy docstring format
- Include examples for complex functions

### API Documentation

- Update OpenAPI schemas when adding new endpoints
- Include example requests and responses
- Document error codes and messages

### README Updates

- Update README.md for new features
- Add usage examples
- Update installation instructions if needed

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

- **Description**: Clear description of the problem
- **Steps to reproduce**: Detailed steps to reproduce the issue
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Environment**: OS, Python version, dependencies
- **Logs**: Relevant error messages or logs

### Issue Template

```markdown
## Bug Description
Brief description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., macOS 14.0]
- Python: [e.g., 3.11.0]
- Data MCP Version: [e.g., 0.1.0]

## Additional Information
Any other context, logs, or screenshots
```

## Feature Requests

For feature requests:

- **Describe the problem** you're trying to solve
- **Explain why** this feature would be useful
- **Provide examples** of how it would work
- **Consider alternatives** that might already exist

## Questions and Discussion

- **GitHub Issues**: For bugs, feature requests, and questions
- **GitHub Discussions**: For general questions and community discussion
- **Pull Requests**: For code contributions

## Getting Help

If you need help:

1. Check the [documentation](https://dmcp.opsloom.io/)
2. Search existing [issues](https://github.com/ORIGINAL_OWNER/dmcp/issues)
3. Create a new issue with your question
4. Join community discussions

## Recognition

Contributors will be recognized in:

- The project README
- Release notes
- The project's contributors page

## License

By contributing to Data MCP, you agree that your contributions will be licensed under the same license as the project (GNU Affero General Public License v3.0).

---

Thank you for contributing to Data MCP! Your contributions help make this project better for everyone.
