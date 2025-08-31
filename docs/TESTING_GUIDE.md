# Vanta Ledger Testing Guide

## Overview

This guide provides comprehensive instructions for testing all components of the Vanta Ledger system. The testing suite includes multiple test categories designed to verify functionality, security, performance, and integration of all system components.

## Testing Architecture

### Test Categories

1. **Minimal LLM Test** (`test_minimal.py`)
   - Basic LLM functionality verification
   - Model loading and inference testing
   - Hardware detection validation

2. **Service-Specific Tests** (`tests/test_service_specific.py`)
   - Individual service functionality
   - LLM service testing
   - Document processing service testing
   - Analytics service testing
   - Authentication service testing
   - Database service testing
   - File service testing
   - Integration service testing
   - Optimization service testing

3. **API Endpoint Tests** (`tests/test_api_endpoints.py`)
   - REST API endpoint functionality
   - Authentication endpoints
   - Document processing endpoints
   - LLM-specific endpoints
   - Financial data endpoints
   - Analytics endpoints
   - Error handling
   - Performance endpoints

4. **Database Integration Tests** (`tests/test_database_integration.py`)
   - PostgreSQL connection testing
   - MongoDB connection testing
   - Redis connection testing
   - Database migrations
   - Data models validation
   - CRUD operations
   - Data integrity constraints
   - Query performance
   - Backup and recovery
   - Connection pooling

5. **Security Feature Tests** (`tests/test_security_features.py`)
   - Password security measures
   - Authentication mechanisms
   - Authorization rules
   - Input validation and sanitization
   - SQL injection prevention
   - XSS prevention
   - CSRF protection
   - Rate limiting
   - Secure HTTP headers
   - File upload security
   - Session management

6. **Existing Pytest Tests** (`tests/`)
   - Unit tests for individual components
   - Integration tests
   - Model tests
   - Configuration tests

## Quick Start

### Prerequisites

1. **Python Environment**
   ```bash
   # Ensure Python 3.8+ is installed
   python3 --version
   
   # Install required dependencies
   pip install -r requirements.txt
   pip install -r requirements-llm.txt
   ```

2. **System Requirements**
   - LLM model files in `models/tinyllama/`
   - Database services running (PostgreSQL, MongoDB, Redis)
   - Backend server running (optional for API tests)

3. **Environment Setup**
   ```bash
   # Copy environment file
   cp env.example .env
   
   # Configure database connections in .env
   # Set API_BASE_URL if testing against remote server
   ```

### Running Tests

#### Option 1: Using the Shell Script (Recommended)

```bash
# Make script executable (if not already)
chmod +x test_all.sh

# Run all tests
./test_all.sh

# Run quick tests only (minimal + service)
./test_all.sh --quick

# Run specific test categories
./test_all.sh --minimal-only
./test_all.sh --service-only
./test_all.sh --api-only
./test_all.sh --database-only
./test_all.sh --security-only
./test_all.sh --pytest-only

# Test against different API URL
./test_all.sh --api-url http://localhost:8000

# Skip health check (useful if backend is not running)
./test_all.sh --skip-health

# Show help
./test_all.sh --help
```

#### Option 2: Using Python Scripts Directly

```bash
# Run comprehensive test suite
python3 run_comprehensive_tests.py

# Run with options
python3 run_comprehensive_tests.py --quick
python3 run_comprehensive_tests.py --skip-health-check
python3 run_comprehensive_tests.py --base-url http://localhost:8000

# Run individual test scripts
python3 test_minimal.py
python3 tests/test_service_specific.py
python3 tests/test_api_endpoints.py
python3 tests/test_database_integration.py
python3 tests/test_security_features.py

# Run existing pytest tests
python3 -m pytest tests/ -v
```

#### Option 3: Using Pytest

```bash
# Run all pytest tests
python3 -m pytest tests/ -v

# Run specific test files
python3 -m pytest tests/test_auth.py -v
python3 -m pytest tests/test_models.py -v

# Run with coverage
python3 -m pytest tests/ --cov=backend --cov-report=html
```

## Test Execution Order

### Recommended Testing Sequence

1. **System Health Check**
   ```bash
   # Verify system is ready for testing
   ./test_all.sh --minimal-only
   ```

2. **Core Functionality Tests**
   ```bash
   # Test essential services
   ./test_all.sh --service-only
   ```

3. **Database Integration Tests**
   ```bash
   # Verify database connectivity and operations
   ./test_all.sh --database-only
   ```

4. **API Endpoint Tests**
   ```bash
   # Test REST API functionality
   ./test_all.sh --api-only
   ```

5. **Security Tests**
   ```bash
   # Verify security measures
   ./test_all.sh --security-only
   ```

6. **Complete Test Suite**
   ```bash
   # Run all tests for comprehensive validation
   ./test_all.sh
   ```

## Test Results and Reports

### Report Locations

- **Individual Test Reports**: Generated in project root
  - `test_service_results.json`
  - `test_api_results.json`
  - `test_database_results.json`
  - `test_security_results.json`

- **Unified Reports**: Generated in `test_reports/` directory
  - `unified_test_report_YYYYMMDD_HHMMSS.json`
  - `test_summary_YYYYMMDD_HHMMSS.json`

### Report Structure

```json
{
  "timestamp": "2024-01-01T12:00:00",
  "test_duration": 120.5,
  "overall_summary": {
    "total_tests": 50,
    "passed_tests": 45,
    "failed_tests": 5,
    "success_rate": 90.0,
    "overall_status": "PASS"
  },
  "suite_results": {
    "Minimal LLM Test": {
      "success": true,
      "details": "All tests passed",
      "timestamp": 1704110400.0
    }
  },
  "recommendations": [
    "All tests passed successfully. System appears ready for deployment."
  ]
}
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure backend is in Python path
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
   ```

2. **Database Connection Failures**
   ```bash
   # Check database services are running
   docker-compose ps
   
   # Verify connection parameters in .env
   cat .env | grep -E "(POSTGRES|MONGODB|REDIS)"
   ```

3. **LLM Model Not Found**
   ```bash
   # Check model files exist
   ls -la models/tinyllama/
   
   # Download models if missing
   # (Follow instructions in LOCAL_LLM_QUICK_START.md)
   ```

4. **API Tests Failing**
   ```bash
   # Ensure backend server is running
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8500
   
   # Test health endpoint manually
   curl http://localhost:8500/health
   ```

5. **Permission Errors**
   ```bash
   # Make scripts executable
   chmod +x test_all.sh
   chmod +x tests/*.py
   ```

### Debug Mode

```bash
# Run tests with verbose output
python3 -m pytest tests/ -v -s

# Run individual test with debug
python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)
exec(open('tests/test_service_specific.py').read())
"
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Vanta Ledger Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: password
          POSTGRES_DB: vanta_ledger_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      mongodb:
        image: mongo:5
        options: >-
          --health-cmd "mongosh --eval 'db.runCommand(\"ping\")'"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:6
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-llm.txt
    
    - name: Run tests
      run: |
        ./test_all.sh --skip-health
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-reports
        path: test_reports/
```

## Performance Testing

### Load Testing

```bash
# Install load testing tools
pip install locust

# Run load tests
locust -f tests/load_test.py --host=http://localhost:8500
```

### Memory Usage Monitoring

```bash
# Monitor memory usage during tests
python3 -m memory_profiler tests/test_performance.py
```

## Security Testing

### Vulnerability Scanning

```bash
# Install security testing tools
pip install bandit safety

# Run security scans
bandit -r backend/
safety check
```

### Penetration Testing

```bash
# Run security tests with detailed output
python3 tests/test_security_features.py --verbose
```

## Best Practices

### Test Development

1. **Write Testable Code**
   - Use dependency injection
   - Separate business logic from infrastructure
   - Mock external dependencies

2. **Test Organization**
   - Group related tests together
   - Use descriptive test names
   - Follow AAA pattern (Arrange, Act, Assert)

3. **Test Data Management**
   - Use fixtures for test data
   - Clean up after tests
   - Use separate test databases

### Test Execution

1. **Environment Isolation**
   - Use separate test environment
   - Mock external services
   - Use test-specific configuration

2. **Parallel Execution**
   - Run independent tests in parallel
   - Use test isolation
   - Avoid shared state

3. **Monitoring and Reporting**
   - Track test execution time
   - Monitor resource usage
   - Generate detailed reports

## Maintenance

### Regular Tasks

1. **Update Test Data**
   - Refresh test documents monthly
   - Update test user accounts
   - Maintain test database

2. **Review Test Coverage**
   - Monitor code coverage
   - Add tests for new features
   - Remove obsolete tests

3. **Performance Monitoring**
   - Track test execution time
   - Monitor resource usage
   - Optimize slow tests

### Documentation Updates

1. **Test Documentation**
   - Update test descriptions
   - Document new test scenarios
   - Maintain troubleshooting guide

2. **Configuration Management**
   - Keep test configuration current
   - Document environment requirements
   - Update CI/CD pipelines

## Support

### Getting Help

1. **Check Documentation**
   - Review this testing guide
   - Check individual test file comments
   - Read error messages carefully

2. **Debug Issues**
   - Run tests with verbose output
   - Check system logs
   - Verify environment setup

3. **Report Issues**
   - Document the problem clearly
   - Include error messages and logs
   - Provide reproduction steps

### Resources

- **Project Documentation**: `README.md`
- **API Documentation**: `docs/API_DOCUMENTATION.md`
- **Local LLM Setup**: `LOCAL_LLM_QUICK_START.md`
- **System Status**: `CURRENT_STATUS_REPORT.md`

---

**Happy Testing! 🧪**

This comprehensive testing suite ensures that your Vanta Ledger system is robust, secure, and ready for production deployment. 