# Contributing to Claude Mac Manager

Thank you for your interest in contributing! This document provides guidelines for development.

## Development Setup

### Prerequisites

- **macOS 13+** (Ventura or later)
- **Python 3.10+**
- **Poetry 1.7.1+**
- **Git**

### Installation

```bash
# Clone repository
git clone https://github.com/vladimir-ks/claude-mac-manager.git
cd claude-mac-manager

# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install
```

## Development Workflow

### 1. Specification-Driven Development (SDD)

All features start with specifications **before** code:

1. Create specification in `01_SPECS/` directory
2. Document expected behavior, inputs, outputs
3. Get approval before implementation
4. Specifications must be code-free and accessible to non-technical users

### 2. Behavior-Driven Development (BDD)

Features require Gherkin scenarios:

1. Create `.feature` file in `02_FEATURES/`
2. Write Given/When/Then scenarios
3. Scenarios drive test implementation
4. Examples:

```gherkin
Feature: Protected Path Validation
  Scenario: System directories cannot be deleted
    Given a protected system path "/System/Library"
    When I attempt to validate deletion
    Then validation should fail with ProtectedPathError
```

### 3. Test-Driven Development (TDD)

Write tests before implementation:

```bash
# 1. Write failing test
poetry run pytest tests/safety/test_protected_paths.py -k test_system_paths

# 2. Implement minimal code to pass
# Edit claude_mac_manager/safety/protected_paths.py

# 3. Verify test passes
poetry run pytest tests/safety/test_protected_paths.py -k test_system_paths

# 4. Refactor while keeping tests green
```

## Testing Requirements

### Coverage Targets

- **Safety-critical modules:** 100% coverage (mandatory)
  - `claude_mac_manager/safety/protected_paths.py`
  - `claude_mac_manager/safety/validator.py`
- **All other modules:** 85% coverage (minimum)

### Running Tests

```bash
# All tests
poetry run pytest

# With coverage report
poetry run pytest --cov --cov-report=term-missing

# Safety-critical tests only
poetry run pytest tests/safety/ -m safety --cov-fail-under=100

# Specific test file
poetry run pytest tests/safety/test_protected_paths.py -v

# Specific test function
poetry run pytest tests/safety/test_protected_paths.py::test_system_paths -v
```

### Test Markers

- `@pytest.mark.safety` - Safety-critical tests (100% coverage required)
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow tests (skip with `-m "not slow"`)
- `@pytest.mark.requires_filesystem` - Tests needing real filesystem

## Code Quality

### Formatting

```bash
# Format all code
poetry run black .

# Check formatting
poetry run black --check --diff .
```

### Linting

```bash
# Run all linters
poetry run ruff check .

# Fix auto-fixable issues
poetry run ruff check --fix .
```

### Type Checking

```bash
# Check types
poetry run mypy claude_mac_manager/
```

### Pre-commit Hooks

All quality checks run automatically on commit:

```bash
# Install hooks
poetry run pre-commit install

# Run manually
poetry run pre-commit run --all-files
```

## Code Style Guidelines

### General Principles

1. **Safety First:** All code must prioritize data safety
2. **Type Hints:** All functions must have type annotations
3. **Docstrings:** All public functions need docstrings
4. **Error Handling:** Use specific exceptions, not bare `except:`
5. **Line Length:** 100 characters maximum

### Example

```python
def validate_deletion(
    path: str,
    category: Optional[str] = None,
    dry_run: bool = True
) -> ValidationResult:
    """
    Validate path for safe deletion.

    Args:
        path: Path to validate
        category: Optional deletion category
        dry_run: Whether to enforce dry-run mode

    Returns:
        ValidationResult with detailed feedback

    Raises:
        ProtectedPathError: If path is protected
        ValidationError: If validation fails

    Example:
        >>> result = validate_deletion("/tmp/cache", "caches")
        >>> print(result.valid)
        True
    """
    # Implementation...
```

## Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

- `feat:` New feature
- `fix:` Bug fix
- `test:` Add/update tests
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `style:` Formatting changes
- `chore:` Build/tooling changes

### Examples

```bash
feat(safety): add protected path validation
test(validator): achieve 100% coverage for validator module
docs(readme): update installation instructions
fix(cli): handle missing database gracefully
```

## Pull Request Process

### Before Submitting

1. ✅ All tests pass: `poetry run pytest`
2. ✅ Coverage ≥85%: `poetry run pytest --cov --cov-fail-under=85`
3. ✅ Safety tests 100%: `poetry run pytest tests/safety/ -m safety --cov-fail-under=100`
4. ✅ Linting passes: `poetry run ruff check .`
5. ✅ Type checking passes: `poetry run mypy claude_mac_manager/`
6. ✅ Formatting clean: `poetry run black --check .`

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Coverage maintained/improved

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Comments added where needed
- [ ] Documentation updated
- [ ] No new warnings
```

## Safety Requirements

### Critical: Never Skip Safety Checks

All deletion operations **must**:

1. Pass through `validate_deletion()` or `DeletionValidator`
2. Check `is_protected_path()` for Layer 1 protection
3. Query database for category permissions
4. Enforce dry-run mode by default
5. Log all operations to audit trail

### Prohibited Operations

❌ **Never:**
- Use `rm -rf` directly
- Delete without validation
- Skip dry-run checks
- Bypass protected path checks
- Delete without logging

✅ **Always:**
- Use `send2trash.send2trash()`
- Validate before deletion
- Default to dry-run mode
- Check protected paths
- Log to `cleanup_history` table

## Project Structure

### Package Layout

```
claude_mac_manager/
├── __init__.py           # Package initialization
├── cli.py                # CLI interface (click)
├── install.py            # Post-install automation
├── safety/               # Multi-layer safety system
│   ├── __init__.py
│   ├── protected_paths.py   # Layer 1: Path protection (100% coverage)
│   └── validator.py         # Layers 2-6: Validation (100% coverage)
├── scanner/              # Filesystem scanning (pending)
├── analyzer/             # Analysis engine (pending)
├── database/             # Database operations (pending)
└── utils/                # Shared utilities (pending)
```

### Test Layout

```
tests/
├── conftest.py           # Shared fixtures
├── safety/               # Safety-critical tests (100% coverage)
│   ├── test_protected_paths.py
│   └── test_validator.py
├── unit/                 # Unit tests
│   ├── test_cli.py
│   └── test_database.py
├── integration/          # Integration tests
│   └── test_workflows.py
└── utils/                # Test utilities
    ├── fixtures.py       # Fake filesystem helpers
    └── assertions.py     # Custom assertions
```

## Versioning Strategy

- **0.0.x** - Pre-alpha development
- **0.x.0** - Alpha releases
- **1.0.0** - First production release

Increment patch version (last digit) for each release unless specified otherwise.

## Getting Help

- **Issues:** Open an issue on GitHub
- **Discussions:** Use GitHub Discussions for questions
- **Documentation:** Check `docs/` directory

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Author:** Vladimir K.S.
**Updated:** 2025-11-24
