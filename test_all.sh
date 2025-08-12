#!/bin/bash

# Comprehensive Test Runner for Vanta Ledger
# This script provides easy access to run all tests with different options

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Vanta Ledger Comprehensive Test Runner"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --quick              Run only essential tests (minimal + service)"
    echo "  --skip-health        Skip system health check"
    echo "  --api-url URL        Set API base URL (default: http://localhost:8500)"
    echo "  --minimal-only       Run only the minimal LLM test"
    echo "  --service-only       Run only service-specific tests"
    echo "  --api-only           Run only API endpoint tests"
    echo "  --database-only      Run only database integration tests"
    echo "  --security-only      Run only security feature tests"
    echo "  --pytest-only        Run only existing pytest tests"
    echo "  --core-only          Run only core functionality tests (recommended)"
    echo "  --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run all tests"
    echo "  $0 --quick           # Run essential tests only"
    echo "  $0 --minimal-only    # Run only minimal LLM test"
    echo "  $0 --api-url http://localhost:8000  # Test against different API"
    echo ""
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Python is available
    if ! command -v /usr/bin/python3 &> /dev/null; then
        print_error "Python 3 is not installed or not in PATH"
        exit 1
    fi
    
    # Check if required files exist
    if [ ! -f "test_minimal.py" ]; then
        print_error "test_minimal.py not found"
        exit 1
    fi
    
    if [ ! -f "run_comprehensive_tests.py" ]; then
        print_error "run_comprehensive_tests.py not found"
        exit 1
    fi
    
    if [ ! -d "tests" ]; then
        print_error "tests directory not found"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to run minimal test only
run_minimal_test() {
    print_status "Running minimal LLM test..."
    /usr/bin/python3 test_minimal.py
    if [ $? -eq 0 ]; then
        print_success "Minimal test completed successfully"
    else
        print_error "Minimal test failed"
        exit 1
    fi
}

# Function to run service tests only
run_service_tests() {
    print_status "Running service-specific tests..."
    /usr/bin/python3 tests/test_service_specific.py
    if [ $? -eq 0 ]; then
        print_success "Service tests completed successfully"
    else
        print_error "Service tests failed"
        exit 1
    fi
}

# Function to run API tests only
run_api_tests() {
    print_status "Running API endpoint tests..."
    API_BASE_URL="${API_URL:-http://localhost:8500}" /usr/bin/python3 tests/test_api_endpoints.py
    if [ $? -eq 0 ]; then
        print_success "API tests completed successfully"
    else
        print_error "API tests failed"
        exit 1
    fi
}

# Function to run database tests only
run_database_tests() {
    print_status "Running database integration tests..."
    /usr/bin/python3 tests/test_database_integration.py
    if [ $? -eq 0 ]; then
        print_success "Database tests completed successfully"
    else
        print_error "Database tests failed"
        exit 1
    fi
}

# Function to run security tests only
run_security_tests() {
    print_status "Running security feature tests..."
    API_BASE_URL="${API_URL:-http://localhost:8500}" /usr/bin/python3 tests/test_security_features.py
    if [ $? -eq 0 ]; then
        print_success "Security tests completed successfully"
    else
        print_error "Security tests failed"
        exit 1
    fi
}

# Function to run pytest tests only
run_pytest_tests() {
    print_status "Running existing pytest tests..."
    /usr/bin/python3 -m pytest tests/ -v
    if [ $? -eq 0 ]; then
        print_success "Pytest tests completed successfully"
    else
        print_error "Pytest tests failed"
        exit 1
    fi
}

# Function to run core functionality tests only
run_core_tests() {
    print_status "Running core functionality tests..."
    /usr/bin/python3 tests/test_core_functionality.py
    if [ $? -eq 0 ]; then
        print_success "Core tests completed successfully"
    else
        print_error "Core tests failed"
        exit 1
    fi
}

# Function to run comprehensive tests
run_comprehensive_tests() {
    print_status "Running comprehensive test suite..."
    
    # Build command arguments
    CMD_ARGS=""
    
    if [ "$QUICK_MODE" = "true" ]; then
        CMD_ARGS="$CMD_ARGS --quick"
    fi
    
    if [ "$SKIP_HEALTH" = "true" ]; then
        CMD_ARGS="$CMD_ARGS --skip-health-check"
    fi
    
    if [ -n "$API_URL" ]; then
        CMD_ARGS="$CMD_ARGS --base-url $API_URL"
    fi
    
    # Run the comprehensive test runner
    /usr/bin/python3 run_comprehensive_tests.py $CMD_ARGS
    
    if [ $? -eq 0 ]; then
        print_success "Comprehensive tests completed successfully"
    else
        print_error "Comprehensive tests failed"
        exit 1
    fi
}

# Main script logic
main() {
    # Parse command line arguments
    QUICK_MODE=false
    SKIP_HEALTH=false
    API_URL=""
    MINIMAL_ONLY=false
    SERVICE_ONLY=false
    API_ONLY=false
    DATABASE_ONLY=false
    SECURITY_ONLY=false
    PYTEST_ONLY=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --quick)
                QUICK_MODE=true
                shift
                ;;
            --skip-health)
                SKIP_HEALTH=true
                shift
                ;;
            --api-url)
                API_URL="$2"
                shift 2
                ;;
            --minimal-only)
                MINIMAL_ONLY=true
                shift
                ;;
            --service-only)
                SERVICE_ONLY=true
                shift
                ;;
            --api-only)
                API_ONLY=true
                shift
                ;;
            --database-only)
                DATABASE_ONLY=true
                shift
                ;;
            --security-only)
                SECURITY_ONLY=true
                shift
                ;;
            --pytest-only)
                PYTEST_ONLY=true
                shift
                ;;
            --core-only)
                CORE_ONLY=true
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Check prerequisites
    check_prerequisites
    
    # Set API URL environment variable if provided
    if [ -n "$API_URL" ]; then
        export API_BASE_URL="$API_URL"
        print_status "Using API URL: $API_URL"
    fi
    
    # Run appropriate tests based on options
    if [ "$MINIMAL_ONLY" = "true" ]; then
        run_minimal_test
    elif [ "$SERVICE_ONLY" = "true" ]; then
        run_service_tests
    elif [ "$API_ONLY" = "true" ]; then
        run_api_tests
    elif [ "$DATABASE_ONLY" = "true" ]; then
        run_database_tests
    elif [ "$SECURITY_ONLY" = "true" ]; then
        run_security_tests
    elif [ "$PYTEST_ONLY" = "true" ]; then
        run_pytest_tests
    elif [ "$CORE_ONLY" = "true" ]; then
        run_core_tests
    else
        # Run comprehensive tests
        run_comprehensive_tests
    fi
    
    print_success "All tests completed!"
}

# Run main function with all arguments
main "$@" 