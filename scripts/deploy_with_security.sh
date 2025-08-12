#!/bin/bash

# Vanta Ledger Secure Deployment Script
# This script deploys the Vanta Ledger system with comprehensive security checks

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
ENV_FILE="$PROJECT_ROOT/.env"
BACKUP_DIR="$PROJECT_ROOT/backups/$(date +%Y%m%d_%H%M%S)"

log "Starting Vanta Ledger Secure Deployment"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to validate environment variables
validate_env_vars() {
    log "Validating environment variables..."
    
    local required_vars=(
        "SECRET_KEY"
        "MONGO_URI"
        "POSTGRES_URI"
        "REDIS_URI"
    )
    
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        error "Missing required environment variables: ${missing_vars[*]}"
        error "Please set these variables in your .env file or environment"
        exit 1
    fi
    
    # Validate SECRET_KEY strength
    if [[ ${#SECRET_KEY} -lt 64 ]]; then
        error "SECRET_KEY must be at least 64 characters long"
        exit 1
    fi
    
    success "Environment variables validated"
}

# Function to create backup
create_backup() {
    log "Creating backup of current system..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup configuration files
    if [[ -f "$ENV_FILE" ]]; then
        cp "$ENV_FILE" "$BACKUP_DIR/"
    fi
    
    # Backup database (if possible)
    if command_exists pg_dump && [[ -n "$POSTGRES_URI" ]]; then
        log "Creating PostgreSQL backup..."
        pg_dump "$POSTGRES_URI" > "$BACKUP_DIR/database_backup.sql" 2>/dev/null || warning "Could not create database backup"
    fi
    
    success "Backup created in $BACKUP_DIR"
}

# Function to run security checks
run_security_checks() {
    log "Running security checks..."
    
    # Check for hardcoded credentials
    log "Checking for hardcoded credentials..."
    if grep -r "admin123\|password123\|secret" "$BACKEND_DIR" --exclude-dir=venv --exclude-dir=__pycache__ | grep -v "test\|example"; then
        warning "Potential hardcoded credentials found. Please review."
    else
        success "No hardcoded credentials detected"
    fi
    
    # Check for SQL injection vulnerabilities
    log "Checking for SQL injection vulnerabilities..."
    if grep -r "execute.*%s.*%" "$BACKEND_DIR" --exclude-dir=venv --exclude-dir=__pycache__ | grep -v "parameterized\|validation"; then
        warning "Potential SQL injection vulnerabilities found. Please review."
    else
        success "No obvious SQL injection vulnerabilities detected"
    fi
    
    # Check file permissions
    log "Checking file permissions..."
    find "$PROJECT_ROOT" -name "*.py" -exec chmod 644 {} \;
    find "$PROJECT_ROOT" -name "*.sh" -exec chmod 755 {} \;
    success "File permissions set correctly"
    
    # Check for security headers in middleware
    if grep -q "SecurityHeadersMiddleware" "$BACKEND_DIR/app/main.py"; then
        success "Security headers middleware is configured"
    else
        warning "Security headers middleware not found"
    fi
    
    # Check for input validation
    if grep -q "input_validator" "$BACKEND_DIR/app/main.py"; then
        success "Input validation is implemented"
    else
        warning "Input validation not found in main.py"
    fi
}

# Function to install dependencies
install_dependencies() {
    log "Installing Python dependencies..."
    
    cd "$BACKEND_DIR"
    
    # Create virtual environment if it doesn't exist
    if [[ ! -d "venv" ]]; then
        log "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    log "Installing security-enhanced dependencies..."
    pip install -r requirements-hybrid.txt
    
    # Verify critical security packages
    log "Verifying security packages..."
    python -c "import cryptography, passlib, python_magic; print('Security packages verified')"
    
    success "Dependencies installed successfully"
}

# Function to run tests
run_tests() {
    log "Running security tests..."
    
    cd "$BACKEND_DIR"
    source venv/bin/activate
    
    # Run security tests
    if python -m pytest tests/test_security.py -v; then
        success "Security tests passed"
    else
        error "Security tests failed"
        exit 1
    fi
    
    # Run all tests
    log "Running all tests..."
    if python -m pytest tests/ -v; then
        success "All tests passed"
    else
        error "Some tests failed"
        exit 1
    fi
}

# Function to validate configuration
validate_configuration() {
    log "Validating configuration..."
    
    cd "$BACKEND_DIR"
    source venv/bin/activate
    
    # Test configuration loading
    if python -c "from app.config import settings; print('Configuration loaded successfully')"; then
        success "Configuration validation passed"
    else
        error "Configuration validation failed"
        exit 1
    fi
    
    # Test database connections
    log "Testing database connections..."
    if python -c "
from app.config import settings
import psycopg2
import pymongo
import redis

# Test PostgreSQL
try:
    conn = psycopg2.connect(settings.POSTGRES_URI, connect_timeout=5)
    conn.close()
    print('PostgreSQL connection: OK')
except Exception as e:
    print(f'PostgreSQL connection: FAILED - {e}')
    exit(1)

# Test MongoDB
try:
    client = pymongo.MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    client.close()
    print('MongoDB connection: OK')
except Exception as e:
    print(f'MongoDB connection: FAILED - {e}')
    exit(1)

# Test Redis
try:
    r = redis.Redis.from_url(settings.REDIS_URI, decode_responses=True)
    r.ping()
    print('Redis connection: OK')
except Exception as e:
    print(f'Redis connection: FAILED - {e}')
    exit(1)
"; then
        success "Database connections validated"
    else
        error "Database connection validation failed"
        exit 1
    fi
}

# Function to deploy backend
deploy_backend() {
    log "Deploying backend..."
    
    cd "$BACKEND_DIR"
    source venv/bin/activate
    
    # Set production environment
    export DEBUG=False
    export ENVIRONMENT=production
    
    # Start the application
    log "Starting FastAPI application..."
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8500 --workers 4 > logs/app.log 2>&1 &
    
    # Wait for application to start
    sleep 5
    
    # Test application health
    if curl -f http://localhost:8500/health >/dev/null 2>&1; then
        success "Backend deployed successfully"
    else
        error "Backend deployment failed"
        exit 1
    fi
}

# Function to deploy frontend
deploy_frontend() {
    log "Deploying frontend..."
    
    cd "$FRONTEND_DIR/frontend-web"
    
    # Install dependencies
    if command_exists npm; then
        npm install
        npm run build
        success "Frontend built successfully"
    else
        warning "npm not found, skipping frontend deployment"
    fi
}

# Function to run final security validation
final_security_validation() {
    log "Running final security validation..."
    
    # Test authentication endpoints
    log "Testing authentication endpoints..."
    if [[ -z "${ADMIN_PASSWORD:-}" ]]; then
        warning "ADMIN_PASSWORD not set; skipping auth login test"
    else
        if curl -f -X POST http://localhost:8500/auth/login -H "Content-Type: application/x-www-form-urlencoded" -d "username=admin&password=${ADMIN_PASSWORD}" >/dev/null 2>&1; then
            success "Authentication endpoint is working"
        else
            warning "Authentication endpoint failed (check logs)"
        fi
    fi
    
    # Test security headers
    log "Testing security headers..."
    headers=$(curl -s -I http://localhost:8500/health)
    if echo "$headers" | grep -q "X-Content-Type-Options"; then
        success "Security headers are present"
    else
        warning "Security headers not detected"
    fi
    
    # Test rate limiting
    log "Testing rate limiting..."
    for i in {1..10}; do
        response=$(curl -s -w "%{http_code}" http://localhost:8500/health -o /dev/null)
        if [[ "$response" == "429" ]]; then
            success "Rate limiting is working"
            break
        fi
    done
    
    success "Final security validation completed"
}

# Main deployment process
main() {
    log "Starting Vanta Ledger secure deployment process..."
    
    # Check prerequisites
    if ! command_exists python3; then
        error "Python 3 is required but not installed"
        exit 1
    fi
    
    if ! command_exists pip; then
        error "pip is required but not installed"
        exit 1
    fi
    
    # Load environment variables
    if [[ -f "$ENV_FILE" ]]; then
        log "Loading environment variables from $ENV_FILE"
        export $(cat "$ENV_FILE" | grep -v '^#' | xargs)
    fi
    
    # Run deployment steps
    validate_env_vars
    create_backup
    run_security_checks
    install_dependencies
    run_tests
    validate_configuration
    deploy_backend
    deploy_frontend
    final_security_validation
    
    success "Vanta Ledger deployment completed successfully!"
    log "System is now running with enhanced security measures"
    log "Backup location: $BACKUP_DIR"
    log "Application URL: http://localhost:8500"
    log "API Documentation: http://localhost:8500/docs"
}

# Run main function
main "$@" 