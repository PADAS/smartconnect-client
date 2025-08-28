# GitHub Workflows

This directory contains GitHub Actions workflows for the smartconnect-client project.

## Workflows

### `test.yml`

A simple workflow that runs tests on multiple Python versions.

**Triggers:**
- Push to `main` or `master` branches
- Pull requests to `main` or `master` branches

**Python Versions:**
- 3.9
- 3.10
- 3.11

**Steps:**
1. **Checkout** - Clones the repository
2. **Setup Python** - Installs the specified Python version
3. **Install Poetry** - Installs Poetry package manager
4. **Configure Poetry** - Sets up Poetry to create virtual environments in-project
5. **Install Dependencies** - Installs project dependencies using `poetry install`
6. **Run Tests** - Runs the full pytest test suite

## Test Files

The workflow runs the full pytest test suite located in the `tests/` directory, which includes:
- Unit tests for all modules
- Integration tests for API interactions
- Model validation tests
- Exception handling tests
- Utility function tests

All tests are run in a Poetry-managed virtual environment with proper dependency isolation.

## Usage

The workflow runs automatically on:
- Every push to the main branch
- Every pull request to the main branch

You can also trigger it manually from the GitHub Actions tab.

## Troubleshooting

If the workflow fails:

1. **Check the logs** - Look at the specific step that failed
2. **Poetry installation issues** - Check if Poetry installation is successful
3. **Dependency conflicts** - Verify that all dependencies in `pyproject.toml` are compatible
4. **Test failures** - Review the specific test failures in the pytest output

## Adding New Tests

Add new tests to the `tests/` directory following the existing test structure. The tests will be automatically discovered and run by pytest.
