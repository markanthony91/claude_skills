# Test Suite Documentation

## 📊 Overview

This directory contains the comprehensive test suite for the `claude_skills` multi-project repository. The test suite is built using pytest and provides coverage for all critical functionality across the 4 main projects.

## 📁 Directory Structure

```
tests/
├── README.md                          # This file
├── unit/                             # Unit tests (isolated components)
│   ├── test_config_manager.py        # Config management tests
│   ├── test_credentials.py           # Credentials security tests
│   └── ...
├── integration/                      # Integration tests (multi-component)
│   ├── test_camera_downloader.py    # Camera download workflow tests
│   └── ...
└── fixtures/                         # Test data and fixtures
    └── ...
```

## 🚀 Quick Start

### Installation

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Set up test environment variables
cp .env.example .env
# Edit .env with test credentials (optional, fixtures provide defaults)
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run specific test file
pytest tests/unit/test_config_manager.py

# Run specific test class
pytest tests/unit/test_config_manager.py::TestCarregarConfig

# Run specific test
pytest tests/unit/test_config_manager.py::TestCarregarConfig::test_carregar_config_arquivo_nao_existe

# Run with verbose output
pytest -v

# Run in parallel (faster)
pytest -n auto
```

### Running Tests by Marker

```bash
# Run only critical tests
pytest -m critical

# Run only security tests
pytest -m security

# Skip slow tests
pytest -m "not slow"

# Run only Selenium tests
pytest -m selenium

# Run only network tests
pytest -m network

# Run only ML tests
pytest -m ml
```

## 📋 Test Markers

Tests are organized using pytest markers:

| Marker | Description | Usage |
|--------|-------------|-------|
| `@pytest.mark.unit` | Unit tests (fast, isolated) | `pytest -m unit` |
| `@pytest.mark.integration` | Integration tests | `pytest -m integration` |
| `@pytest.mark.selenium` | Tests requiring Selenium | `pytest -m selenium` |
| `@pytest.mark.network` | Tests requiring network | `pytest -m network` |
| `@pytest.mark.ml` | Machine learning tests | `pytest -m ml` |
| `@pytest.mark.security` | Security-related tests | `pytest -m security` |
| `@pytest.mark.critical` | Critical business tests | `pytest -m critical` |
| `@pytest.mark.slow` | Slow-running tests | `pytest -m "not slow"` |

## 🧪 Test Categories

### Unit Tests (`tests/unit/`)

Fast, isolated tests for individual functions and classes.

**Current Coverage:**
- ✅ `test_config_manager.py` - Configuration management (40+ tests)
- ✅ `test_credentials.py` - Credentials security (30+ tests)

**Recommended Additions:**
- `test_cleanup_manager.py` - File cleanup logic
- `test_image_comparison.py` - Image analysis algorithms
- `test_metadata_parser.py` - Metadata extraction

### Integration Tests (`tests/integration/`)

Tests for multi-component workflows and system integration.

**Current Coverage:**
- ✅ `test_camera_downloader.py` - Camera download workflow (50+ tests)

**Recommended Additions:**
- `test_parallel_downloader.py` - Parallel execution
- `test_file_server_extraction.py` - File server integration
- `test_alphaville_scraper.py` - Web scraping workflow

## 🔧 Configuration

### pytest.ini

The main configuration file defines:
- Test discovery patterns
- Coverage settings
- Markers
- Default command-line options

Key settings:
```ini
[pytest]
testpaths = tests
addopts = -v --cov --cov-report=html
```

### conftest.py

Shared fixtures available to all tests:

**Environment Fixtures:**
- `test_env_vars` - Mock environment variables
- `temp_dir` - Temporary directory for test files

**Mock Fixtures:**
- `mock_selenium_driver` - Mocked Selenium WebDriver
- `mock_requests_session` - Mocked HTTP session
- `mock_beautifulsoup` - BeautifulSoup parser

**Data Fixtures:**
- `sample_config_dict` - Sample configuration
- `sample_camera_metadata` - Camera metadata
- `sample_image_path` - Valid JPEG file

See `conftest.py` for complete list of available fixtures.

## 📊 Coverage Reports

### Generating Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov --cov-report=html

# View report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows

# Terminal report with missing lines
pytest --cov --cov-report=term-missing

# XML report (for CI/CD)
pytest --cov --cov-report=xml
```

### Current Coverage Targets

| Module | Target Coverage | Current Status |
|--------|----------------|----------------|
| config_manager.py | 80%+ | ✅ Achieved |
| credentials.py | 90%+ | ✅ Achieved |
| camera_downloader | 60%+ | 🚧 In Progress |
| cleanup_manager | 70%+ | ⏳ Pending |
| image_comparison | 60%+ | ⏳ Pending |
| Overall | 50%+ | 🚧 30%+ achieved |

## 🔒 Security Testing

### Credential Security Tests

Located in `tests/unit/test_credentials.py`:

- ✅ Tests credential loading from environment
- ✅ Validates error handling for missing credentials
- ✅ Ensures credentials are not logged
- ✅ Verifies error messages don't reveal secrets

**Running Security Tests:**
```bash
pytest -m security -v
```

### Security Scanning

The CI/CD pipeline includes:
- **Bandit** - Security vulnerability scanning
- **Safety** - Known vulnerability checking

Run locally:
```bash
# Security scan
bandit -r captura_cameras captura_cameras_debug sistema_recupera

# Check for known vulnerabilities
safety check
```

## 🎯 Best Practices

### Writing New Tests

#### 1. Follow AAA Pattern

```python
def test_example():
    # Arrange - Set up test data
    config = {"storage_mode": "snapshot"}

    # Act - Execute the code
    result = salvar_config(config)

    # Assert - Verify the results
    assert result is True
```

#### 2. Use Descriptive Names

```python
# ❌ Bad
def test_1():
    ...

# ✅ Good
def test_carregar_config_arquivo_nao_existe():
    ...
```

#### 3. One Assertion Per Test (when possible)

```python
# ❌ Bad
def test_config():
    assert config['mode'] == 'snapshot'
    assert config['days'] == 7
    assert config['workers'] == 10

# ✅ Good
def test_config_mode():
    assert config['mode'] == 'snapshot'

def test_config_retention_days():
    assert config['days'] == 7
```

#### 4. Use Fixtures for Setup

```python
@pytest.fixture
def sample_config():
    return {"storage_mode": "snapshot", "retention_days": 7}

def test_with_fixture(sample_config):
    assert sample_config['storage_mode'] == 'snapshot'
```

#### 5. Mark Tests Appropriately

```python
@pytest.mark.integration
@pytest.mark.selenium
@pytest.mark.slow
def test_full_download_workflow():
    ...
```

## 🐛 Debugging Tests

### Running Tests with Debugging

```bash
# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Drop into debugger on failure
pytest --pdb

# Set breakpoint in code
import pdb; pdb.set_trace()  # Python < 3.7
breakpoint()  # Python >= 3.7
```

### Verbose Output

```bash
# Show print statements
pytest -s

# Very verbose
pytest -vv

# Show test durations
pytest --durations=10
```

## 🔄 CI/CD Integration

### GitHub Actions Workflow

Located in `.github/workflows/test.yml`:

**Runs on:**
- Push to `main`, `develop`, `claude/*` branches
- Pull requests to `main`, `develop`
- Daily at 2 AM UTC

**Test Matrix:**
- Python versions: 3.8, 3.9, 3.10, 3.11
- OS: Ubuntu Latest

**Steps:**
1. Install dependencies
2. Run linters (flake8, pylint)
3. Run unit tests
4. Run integration tests
5. Upload coverage to Codecov
6. Security scanning (bandit, safety)
7. Code quality checks (black, isort)

### Coverage Reports

Coverage reports are automatically uploaded to Codecov and available as GitHub Actions artifacts.

## 📝 Test Data

### Using Fixtures

Fixtures provide reusable test data:

```python
def test_with_camera_data(sample_camera_metadata):
    assert sample_camera_metadata['camera_id'] == 'CAM_001'
    assert sample_camera_metadata['position'] in ['P1', 'P2', 'P3']
```

### Creating Test Files

Use the `temp_dir` fixture for temporary files:

```python
def test_file_creation(temp_dir):
    test_file = temp_dir / "test.txt"
    test_file.write_text("test content")

    assert test_file.exists()
    # Cleanup is automatic
```

## 🚨 Common Issues

### Issue: "ModuleNotFoundError"

**Solution:**
```bash
# Ensure the module path is correct
export PYTHONPATH="${PYTHONPATH}:${PWD}"

# Or install package in development mode
pip install -e .
```

### Issue: "Environment variable not found"

**Solution:**
```bash
# Create .env file
cp .env.example .env

# Or export manually
export AIVISUAL_USER=test@example.com
export AIVISUAL_PASS=test_password
```

### Issue: "Selenium WebDriver not found"

**Solution:**
```bash
# Install chromedriver
python3 -c "import chromedriver_autoinstaller; chromedriver_autoinstaller.install()"
```

### Issue: Tests are slow

**Solution:**
```bash
# Run in parallel
pytest -n auto

# Skip slow tests
pytest -m "not slow"

# Run only unit tests (faster)
pytest tests/unit/
```

## 📚 Additional Resources

### Documentation
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Python Mock Documentation](https://docs.python.org/3/library/unittest.mock.html)

### Tutorials
- [Real Python: pytest Guide](https://realpython.com/pytest-python-testing/)
- [pytest Best Practices](https://docs.pytest.org/en/latest/explanation/goodpractices.html)

### Related Files
- `pytest.ini` - Test configuration
- `conftest.py` - Shared fixtures
- `.github/workflows/test.yml` - CI/CD configuration
- `requirements-dev.txt` - Test dependencies
- `MIGRATION_GUIDE.md` - Credentials migration

## 🎯 Testing Roadmap

### Current Status (Phase 1 Complete)
- ✅ Test infrastructure setup
- ✅ Config manager tests (80%+ coverage)
- ✅ Credentials security tests (90%+ coverage)
- ✅ Basic integration tests
- ✅ CI/CD pipeline

### Phase 2 (Next Steps)
- ⏳ Cleanup manager tests
- ⏳ Image comparison algorithm tests
- ⏳ Metadata parser tests
- ⏳ Parallel downloader tests

### Phase 3 (Future)
- ⏳ ML model tests (Isolation Forest)
- ⏳ RL algorithm tests
- ⏳ End-to-end workflow tests
- ⏳ Performance benchmarks

### Phase 4 (Advanced)
- ⏳ Mutation testing
- ⏳ Property-based testing
- ⏳ Load testing
- ⏳ UI testing (if applicable)

## 💡 Contributing

### Adding New Tests

1. Determine test type (unit vs integration)
2. Create test file in appropriate directory
3. Import required fixtures from `conftest.py`
4. Write tests following AAA pattern
5. Add appropriate markers
6. Run tests locally: `pytest path/to/test_file.py -v`
7. Check coverage: `pytest --cov=module_name`
8. Commit with descriptive message

### Review Checklist

- [ ] Tests follow naming conventions
- [ ] Appropriate markers are applied
- [ ] Tests are isolated (no side effects)
- [ ] Fixtures are used for setup
- [ ] Coverage increased or maintained
- [ ] Tests pass locally
- [ ] Tests pass in CI/CD

## 📧 Support

For questions or issues:
1. Check this README
2. Review `conftest.py` for available fixtures
3. Check CI/CD logs for failures
4. Review test output with `pytest -vv`

---

**Last Updated:** 2026-01-12
**Test Suite Version:** 1.0.0
**Minimum Coverage Target:** 30% (increasing to 50%+)
