# Contributing to NeMo Guardrails CAI

Thank you for your interest in contributing to NeMo Guardrails CAI! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [GitHub Actions](#github-actions)
- [Release Process](#release-process)

## Code of Conduct

This project adheres to professional open-source standards. Please be respectful and constructive in all interactions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/nemo-guardrails-cai.git
   cd nemo-guardrails-cai
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/cloudera/nemo-guardrails-cai.git
   ```

## Development Setup

### Prerequisites

- Python 3.9+
- Git
- Optional: Docker for local testing

### Install Development Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package in editable mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks (optional but recommended)
pip install pre-commit
pre-commit install
```

### Project Structure

```
nemo-guardrails-cai/
├── .github/                    # GitHub Actions workflows
│   ├── workflows/
│   │   ├── ci.yml              # CI/CD pipeline
│   │   ├── deploy-guardrails.yml  # CAI deployment
│   │   └── publish.yml         # PyPI publishing
│   └── README.md
├── nemo_guardrails_cai/        # Main package
│   ├── models/                 # Local model support
│   ├── actions/                # Custom guardrails actions
│   ├── config.py
│   └── server.py
├── cai_integration/            # CAI deployment scripts
├── examples/                   # Usage examples
├── docs/                       # Documentation
├── tests/                      # Test suite
└── pyproject.toml              # Package configuration
```

## Making Changes

### 1. Create a Branch

```bash
# Update your local main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Write Code

**Follow coding standards:**

- Use **Black** for code formatting (line length: 100)
- Follow **PEP 8** style guide
- Use type hints where appropriate
- Write docstrings for all public functions/classes
- Keep functions focused and modular

**Example:**

```python
"""Module for handling guardrails configuration."""

from pathlib import Path
from typing import Dict, Any


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load guardrails configuration from YAML file.

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    # Implementation here
    pass
```

### 3. Format and Lint

```bash
# Format code with Black
black nemo_guardrails_cai/ --line-length 100

# Lint with Ruff
ruff check nemo_guardrails_cai/ --fix

# Type check with MyPy (optional)
mypy nemo_guardrails_cai/ --ignore-missing-imports
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=nemo_guardrails_cai --cov-report=html

# Run specific test file
pytest tests/test_config.py

# Run with verbose output
pytest -v
```

### Writing Tests

Place tests in the `tests/` directory:

```python
# tests/test_config.py
import pytest
from pathlib import Path
from nemo_guardrails_cai import GuardrailsConfig


def test_config_from_yaml():
    """Test loading configuration from YAML file."""
    config = GuardrailsConfig.from_yaml("examples/server_config.yaml")

    assert config.host == "0.0.0.0"
    assert config.port == 8080
    assert config.llm_provider == "openai"


def test_config_with_local_models():
    """Test configuration with local models."""
    config = GuardrailsConfig(
        local_models={
            "jailbreak_detector": {
                "type": "huggingface",
                "model_name": "test-model"
            }
        }
    )

    assert "jailbreak_detector" in config.local_models
```

### Test Coverage

Maintain **>80% test coverage**. Check coverage:

```bash
pytest --cov=nemo_guardrails_cai --cov-report=term-missing
```

## Submitting Changes

### 1. Commit Your Changes

Use clear, descriptive commit messages:

```bash
git add .
git commit -m "feat: add support for custom model thresholds

- Add threshold parameter to model configuration
- Update documentation with examples
- Add tests for threshold validation"
```

**Commit message format:**

```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### 2. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 3. Create Pull Request

1. Go to your fork on GitHub
2. Click "Pull Request"
3. Select your branch
4. Fill in the PR template:

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
- [ ] Added new tests
- [ ] Updated documentation

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed the code
- [ ] Commented complex code
- [ ] Updated documentation
- [ ] No new warnings
```

### 4. Code Review

- Address reviewer feedback
- Make requested changes
- Push updates to your branch (PR updates automatically)

## GitHub Actions

All PRs trigger automated checks:

### CI Workflow (ci.yml)

Runs on every push/PR:

1. **Linting**
   - Black formatting check
   - Ruff linting
   - MyPy type checking

2. **Testing**
   - Pytest on Python 3.9, 3.10, 3.11
   - Coverage report
   - Upload to Codecov

3. **Build**
   - Package building
   - Distribution validation

**Viewing CI Results:**

```bash
# Via GitHub CLI
gh pr checks

# Or visit GitHub Actions tab in your PR
```

### Deployment Workflow (deploy-guardrails.yml)

Manual workflow for deploying to CAI:

```bash
# Trigger deployment (maintainers only)
gh workflow run deploy-guardrails.yml
```

### Local Pre-commit Checks

Install pre-commit hooks to catch issues before pushing:

```bash
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

## Release Process

### For Maintainers

1. **Update Version**

Edit `pyproject.toml`:
```toml
version = "0.2.0"  # Update version
```

2. **Update Changelog**

Add changes to `CHANGELOG.md`:
```markdown
## [0.2.0] - 2026-01-20

### Added
- Local model support for jailbreak detection
- Custom actions for guardrails

### Changed
- Improved configuration structure

### Fixed
- Port handling in CAI deployments
```

3. **Create Release**

```bash
# Tag the release
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0

# Create GitHub release
gh release create v0.2.0 \
  --title "v0.2.0" \
  --notes "See CHANGELOG.md for details"
```

4. **Publish to PyPI**

The `publish.yml` workflow automatically publishes when a release is created.

Manual publishing:
```bash
python -m build
twine upload dist/*
```

## Development Tips

### Local Testing with CAI

Test CAI integration locally:

```bash
# Set up environment
export CML_HOST="https://ml-dev.example.cloudera.site"
export CML_API_KEY="your-dev-api-key"

# Test project setup
python cai_integration/setup_project.py

# Test job creation
python cai_integration/create_jobs.py --project-id <project-id>
```

### Testing Local Models

```bash
# Install with local model support
pip install -e ".[local-models]"

# Test model loading
python -c "
from nemo_guardrails_cai.models import HuggingFaceModelService

config = {
    'model_name': 'distilbert-base-uncased',
    'device': 'cpu',
    'task_type': 'classification'
}

model = HuggingFaceModelService(config)
model.load()
result = model.predict_single('test input')
print(result)
"
```

### Documentation

Build documentation locally:

```bash
pip install -e ".[docs]"
mkdocs serve  # If using MkDocs

# Or just edit markdown files in docs/
```

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/cloudera/nemo-guardrails-cai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/cloudera/nemo-guardrails-cai/discussions)
- **Documentation**: [docs/](docs/)

## Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes
- Project documentation

Thank you for contributing! 🎉
