# Tests Directory

This directory contains all test files for the Vanta Ledger project.

## Test Structure

```
tests/
├── unit/              - Unit tests for individual components
├── integration/       - Integration tests for system interactions
├── e2e/              - End-to-end tests (future)
├── conftest.py       - Shared pytest fixtures and configuration
└── test_*.py         - Test modules
```

## Test Categories

### Unit Tests (`unit/` and root test files)
Test individual functions, classes, and modules in isolation:
- `test_auth.py` - Authentication and authorization tests
- `test_models.py` - Database model tests
- `test_crud.py` - CRUD operation tests
- `test_config.py` - Configuration tests
- `test_password_utils.py` - Password utility tests
- `test_users.py` - User management tests

### Integration Tests (`integration/`)
Test interactions between components:
- `test_backend_integration.py` - Backend service integration
- `test_database_integration.py` - Database connectivity tests
- `test_github_models_integration.py` - GitHub models API integration
- `test_llm_integration.py` - LLM service integration
- `test_local_llm_service.py` - Local LLM integration
- `test_api_endpoints.py` - API endpoint integration

### Service-Specific Tests
- `test_security.py` - Security feature tests
- `test_security_features.py` - Enhanced security tests
- `test_jules_audit_fixes.py` - Audit compliance tests
- `test_enhanced_documents.py` - Document processing tests
- `test_service_specific.py` - Service layer tests

### System Tests
- `test_comprehensive_system.py` - Full system tests
- `test_basic_structure.py` - Project structure validation
- `test_core_functionality.py` - Core feature tests

## Running Tests

### Run All Tests
```bash
# Using pytest
pytest

# With coverage
pytest --cov=src --cov-report=html

# Verbose output
pytest -v
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/ -k "not integration"

# Integration tests only
pytest tests/integration/

# Specific test file
pytest tests/test_auth.py

# Specific test function
pytest tests/test_auth.py::test_login
```

### Run Tests with Markers
```bash
# Quick tests only
pytest -m quick

# Slow tests only
pytest -m slow

# Skip slow tests
pytest -m "not slow"
```

## Test Configuration

Configuration is in `pyproject.toml` under `[tool.pytest.ini_options]`:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "-v --cov=src --cov-report=term-missing"
asyncio_mode = "auto"
```

## Writing Tests

### Test Naming Convention
- Files: `test_<module_name>.py`
- Classes: `Test<FeatureName>`
- Functions: `test_<specific_behavior>`

### Example Test Structure
```python
import pytest
from src.vanta_ledger.auth import AuthService

class TestAuthService:
    """Tests for authentication service"""
    
    @pytest.fixture
    def auth_service(self):
        """Create auth service instance"""
        return AuthService()
    
    def test_login_success(self, auth_service):
        """Test successful login"""
        # Arrange
        username = "testuser"
        password = "testpass"
        
        # Act
        result = auth_service.login(username, password)
        
        # Assert
        assert result.success is True
        assert result.token is not None
    
    def test_login_invalid_credentials(self, auth_service):
        """Test login with invalid credentials"""
        # Test implementation
        pass
```

### Test Fixtures

Shared fixtures are in `conftest.py`:
- Database connections
- Test users
- Mock services
- Test data

### Async Tests
```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

## Test Data

Test data should be:
- Created in test setup
- Cleaned up in teardown
- Not committed to repository
- Isolated between tests

## Mocking

Use pytest-mock for mocking:
```python
def test_with_mock(mocker):
    mock_service = mocker.patch('module.Service')
    mock_service.return_value.method.return_value = "mocked"
    # Test implementation
```

## Coverage

Aim for:
- 80%+ code coverage overall
- 90%+ for critical paths (auth, security, financial)
- 100% for security-critical code

View coverage report:
```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## Continuous Integration

Tests run automatically on:
- Pull requests
- Pushes to main/master
- Scheduled runs (nightly)

## Troubleshooting

### Tests Failing
1. Check test environment setup
2. Verify database is running
3. Check environment variables
4. Review test isolation
5. Check for stale fixtures

### Slow Tests
1. Use test markers to skip slow tests during development
2. Optimize database queries
3. Use mocks instead of real services
4. Consider parallel test execution

### Common Issues
- **Import errors**: Check PYTHONPATH and virtual environment
- **Database errors**: Ensure test database is initialized
- **Async errors**: Verify asyncio_mode configuration
- **Fixture errors**: Check conftest.py for circular dependencies

## Best Practices

1. **Isolate tests**: Each test should be independent
2. **Use fixtures**: Share setup code via fixtures
3. **Test edge cases**: Don't just test happy paths
4. **Keep tests fast**: Use mocks for external services
5. **Clear assertions**: Make test failures obvious
6. **Document complex tests**: Add comments explaining why
7. **Clean up**: Always clean up test data

## Contributing Tests

When adding features:
1. Write tests first (TDD approach)
2. Cover happy paths and edge cases
3. Add integration tests for new endpoints
4. Update this README if adding new test categories
5. Run full test suite before committing

For more information, see CONTRIBUTING.md
