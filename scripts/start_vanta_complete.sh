#!/bin/bash

# 🚀 VANTA LEDGER - COMPLETE STARTUP SCRIPT
# This script starts the entire Vanta Ledger project in one go
# Uses the permanent Cursor fix for reliable operation

set -e

echo "🚀 VANTA LEDGER - COMPLETE STARTUP"
echo "=================================="

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

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to wait for a service to be ready
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if nc -z "$host" "$port" 2>/dev/null; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name failed to start within $((max_attempts * 2)) seconds"
    return 1
}

# Step 1: Check and fix virtual environment
check_and_fix_environment() {
    print_status "Step 1: Checking virtual environment..."
    
    if [ -d "venv" ]; then
        # Check if environment is corrupted
        if [ -L "venv/bin/python3" ]; then
            TARGET=$(readlink venv/bin/python3)
            if [[ "$TARGET" == *"cursor"* ]]; then
                print_warning "Virtual environment is corrupted (links to Cursor)"
                print_status "Fixing corrupted environment..."
                
                # Backup dependencies if possible
                if [ -f "venv/bin/pip" ]; then
                    venv/bin/pip freeze > requirements_backup_$(date +%Y%m%d_%H%M%S).txt
                    print_status "Dependencies backed up"
                fi
                
                # Remove corrupted environment
                rm -rf venv
                print_status "Corrupted environment removed"
                
                # Create new isolated environment
                create-venv-safe venv
                print_success "New isolated environment created"
            else
                print_success "Virtual environment is healthy"
            fi
        else
            print_warning "Virtual environment exists but Python is not a symbolic link"
            print_status "Recreating environment for safety..."
            rm -rf venv
            create-venv-safe venv
            print_success "New isolated environment created"
        fi
    else
        print_status "No virtual environment found, creating new one..."
        create-venv-safe venv
        print_success "New isolated environment created"
    fi
}

# Step 2: Activate environment and install dependencies
setup_environment() {
    print_status "Step 2: Setting up environment and dependencies..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Verify Python is working correctly
    if ! python3 --version >/dev/null 2>&1; then
        print_error "Python is not working correctly in virtual environment"
        exit 1
    fi
    
    print_success "Virtual environment activated"
    print_status "Python version: $(python3 --version)"
    
    # Install project dependencies
    print_status "Installing project dependencies..."
    if ! pip install -e ".[dev]" >/dev/null 2>&1; then
        print_warning "Some dependencies may not be installed, continuing..."
    else
        print_success "Dependencies installed"
    fi
}

# Step 3: Set up environment variables
setup_environment_variables() {
    print_status "Step 3: Setting up environment variables..."
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating .env file with default values..."
        cat > .env << 'EOF'
# Database Configuration
MONGO_URI=mongodb://localhost:27017
POSTGRES_URI=postgresql://localhost:5432
REDIS_URI=redis://localhost:6379

# Application Configuration
APP_NAME=Vanta Ledger
DEBUG=true
LOG_LEVEL=INFO

# Security Configuration
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server Configuration
HOST=0.0.0.0
PORT=8500
EOF
        print_success ".env file created"
    else
        print_success ".env file already exists"
    fi
    
    # Load environment variables
    export $(grep -v '^#' .env | xargs)
    print_success "Environment variables loaded"
}

# Step 4: Check and start database services
start_database_services() {
    print_status "Step 4: Checking database services..."
    
    # Check if Docker is available
    if command_exists docker; then
        print_status "Docker detected, checking for database containers..."
        
        # Check if containers are running
        if docker ps | grep -q "postgres\|mongo\|redis"; then
            print_success "Database containers are running"
        else
            print_warning "Database containers not found, starting them..."
            
            # Start database services using docker-compose if available
            if [ -f "docker-compose.yml" ] && command_exists docker-compose; then
                print_status "Starting database services with docker-compose..."
                docker-compose up -d postgres mongodb redis
                
                # Wait for services to be ready
                wait_for_service localhost 5432 "PostgreSQL"
                wait_for_service localhost 27017 "MongoDB"
                wait_for_service localhost 6379 "Redis"
                
                print_success "Database services started"
            else
                print_warning "docker-compose.yml not found or docker-compose not available"
                print_status "Please start database services manually or install Docker"
            fi
        fi
    else
        print_warning "Docker not found, assuming database services are running locally"
    fi
}

# Step 5: Initialize database
initialize_database() {
    print_status "Step 5: Initializing database..."
    
    # Check if database initialization script exists
    if [ -f "scripts/init_database.py" ]; then
        print_status "Running database initialization..."
        if python3 scripts/init_database.py; then
            print_success "Database initialized"
        else
            print_warning "Database initialization failed, continuing..."
        fi
    else
        print_status "No database initialization script found, skipping..."
    fi
}

# Step 6: Run tests to verify setup
run_tests() {
    print_status "Step 6: Running tests to verify setup..."
    
    # Run basic structure test
    if [ -f "tests/test_basic_structure.py" ]; then
        print_status "Running basic structure test..."
        if python3 tests/test_basic_structure.py; then
            print_success "Basic structure test passed"
        else
            print_warning "Basic structure test failed, continuing..."
        fi
    fi
    
    # Run Jules audit fixes test
    if [ -f "tests/test_jules_audit_fixes.py" ]; then
        print_status "Running Jules audit fixes test..."
        if python3 tests/test_jules_audit_fixes.py; then
            print_success "Jules audit fixes test passed"
        else
            print_warning "Jules audit fixes test failed, continuing..."
        fi
    fi
}

# Step 7: Start the FastAPI application
start_application() {
    print_status "Step 7: Starting FastAPI application..."
    
    # Check if port is already in use
    if port_in_use 8500; then
        print_warning "Port 8500 is already in use"
        print_status "Attempting to kill existing process..."
        pkill -f "uvicorn.*8500" || true
        sleep 2
    fi
    
    # Start the application
    print_status "Starting Vanta Ledger on http://localhost:8500"
    print_status "API Documentation: http://localhost:8500/docs"
    print_status "Health Check: http://localhost:8500/health"
    echo ""
    
    # Start the server
    python3 -m uvicorn vanta_ledger.main:app --host 0.0.0.0 --port 8500 --reload
}

# Main execution
main() {
    echo "🚀 Starting Vanta Ledger project..."
    echo ""
    
    # Check if we're in the right directory
    if [ ! -f "pyproject.toml" ] || [ ! -d "src/vanta_ledger" ]; then
        print_error "This script must be run from the Vanta Ledger project root directory"
        exit 1
    fi
    
    # Execute all steps
    check_and_fix_environment
    setup_environment
    setup_environment_variables
    start_database_services
    initialize_database
    run_tests
    start_application
}

# Handle script interruption
trap 'echo ""; print_warning "Startup interrupted by user"; exit 1' INT

# Run main function
main "$@" 