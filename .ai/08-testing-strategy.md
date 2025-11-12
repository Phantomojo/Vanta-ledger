# 08 - Testing Strategy

## Test Structure (tests/)
- **tests/integration/** - Integration tests (9 files)
- **tests/** (root) - Unit tests (15 files)
- Total: 26 test files

## Test Framework
- **pytest** - Test runner
- **pytest-cov** - Coverage reporting
- **pytest-mock** - Mocking
- **pytest-xdist** - Parallel execution

## Running Tests
```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific test
pytest tests/test_auth.py -v

# Integration only
pytest tests/integration/ -v
```

## Test Requirements
- New features must have tests
- Aim for 80%+ code coverage
- Test both success and failure cases
- Mock external dependencies (databases, APIs)

## Test Naming
- File: `test_<module>.py`
- Function: `test_<feature>_<scenario>()`
- Example: `test_user_login_success()`, `test_user_login_invalid_password()`

## Next: Deployment (`09-deployment.md`)
