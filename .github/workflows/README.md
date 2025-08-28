# GitHub Workflows

This directory contains GitHub Actions workflows for the smartconnect-client project.

## Available Workflows

### 1. `tests.yml` - Comprehensive Testing Workflow
**File:** `.github/workflows/tests.yml`

This is the main workflow that runs on every push and pull request to `main` and `develop` branches.

**Features:**
- **Multi-Python Testing**: Tests against Python 3.8, 3.9, 3.10, and 3.11
- **Dependency Caching**: Caches pip and Poetry dependencies for faster builds
- **Code Coverage**: Generates coverage reports and uploads to Codecov
- **Linting**: Runs flake8 for code quality checks
- **Security Scanning**: Runs bandit for security vulnerability scanning

**Jobs:**
1. **test**: Runs unit tests with coverage
2. **lint**: Runs code linting with flake8
3. **security**: Runs security scanning with bandit

### 2. `test-simple.yml` - Simple Testing Workflow
**File:** `.github/workflows/test-simple.yml`

A streamlined workflow focused on core testing functionality.

**Features:**
- **Multi-Python Testing**: Tests against Python 3.8, 3.9, and 3.10
- **Basic Testing**: Runs pytest with verbose output
- **Fast Execution**: Minimal setup for quick feedback

## Usage

### Automatic Execution
Workflows run automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

### Manual Execution
You can manually trigger workflows from the GitHub Actions tab in your repository.

### Local Testing
To run the same tests locally:

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest tests/ -v

# Run with coverage
poetry run pytest tests/ -v --cov=smartconnect --cov-report=term-missing

# Run linting
poetry run flake8 smartconnect/ tests/

# Run security checks
poetry run bandit -r smartconnect/
```

## Configuration

### Python Versions
The workflows test against multiple Python versions to ensure compatibility:
- Python 3.8 (minimum supported)
- Python 3.9 (recommended)
- Python 3.10
- Python 3.11 (comprehensive workflow only)

### Dependencies
The workflows use Poetry for dependency management and automatically install:
- All project dependencies from `pyproject.toml`
- Development dependencies including pytest, coverage tools, and linting tools

### Caching
Dependencies are cached to speed up workflow execution:
- Poetry virtual environments
- pip cache
- Cache keys based on `pyproject.toml` and `poetry.lock` hashes

## Coverage Reports

The comprehensive workflow generates coverage reports and uploads them to Codecov. Coverage includes:
- Line coverage for the `smartconnect` package
- Missing lines report
- XML format for CI integration

## Security Scanning

The comprehensive workflow includes security scanning with bandit:
- Scans the `smartconnect` package for common security issues
- Generates JSON reports
- Uploads reports as workflow artifacts

## Troubleshooting

### Common Issues

1. **Dependency Installation Failures**
   - Check that `pyproject.toml` and `poetry.lock` are up to date
   - Ensure all dependencies are compatible with the Python versions being tested

2. **Test Failures**
   - Run tests locally first: `poetry run pytest tests/ -v`
   - Check that all test dependencies are installed
   - Verify that test data files are present

3. **Coverage Issues**
   - Ensure `pytest-cov` is installed
   - Check that the `smartconnect` package is properly structured

### Workflow Customization

To customize the workflows:

1. **Add Python Versions**: Modify the `matrix.python-version` array
2. **Add Test Commands**: Modify the test step commands
3. **Add Jobs**: Add new jobs for additional checks
4. **Modify Triggers**: Change the `on` section to trigger on different events

## Contributing

When contributing to this project:

1. Ensure your code passes all workflow checks
2. Add tests for new functionality
3. Update documentation as needed
4. Follow the existing code style (enforced by flake8)
