#!/bin/bash

# Vanta Ledger Hardcoded Credentials Verification Script
# Generated: August 4, 2025

set -e

echo "🔍 Verifying no hardcoded credentials remain in the codebase..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to check for hardcoded passwords
check_for_hardcoded() {
    local pattern="$1"
    local description="$2"
    
    if grep -r "$pattern" . --exclude-dir=.git --exclude=*.md --exclude=*.txt --exclude=*.log 2>/dev/null; then
        print_error "Found hardcoded $description in:"
        grep -r "$pattern" . --exclude-dir=.git --exclude=*.md --exclude=*.txt --exclude=*.log 2>/dev/null || true
        return 1
    else
        print_success "No hardcoded $description found"
        return 0
    fi
}

print_status "Checking for hardcoded credentials..."

# Check for the old hardcoded passwords
old_passwords=(
    "hCwAlZ6cbJ81uIG3kag/Ius4FlVQ+ztG8mti04gotS4="
    "wY3iROCeRkgXCMFLlunjj4hTAlKSKr++KmbROTopYGo="
    "Py5IzCZmrBdkRYA1iyy9cO2jocXFR7HlBnUlXJM5WCM="
    "admin123"
    "vanta_password"
)

found_hardcoded=false

for password in "${old_passwords[@]}"; do
    if check_for_hardcoded "$password" "password"; then
        found_hardcoded=true
    fi
done

# Check for common weak passwords
weak_patterns=(
    "password"
    "123456"
    "admin"
    "root"
    "test"
)

print_status "Checking for weak password patterns..."

for pattern in "${weak_patterns[@]}"; do
    if grep -r -i "$pattern" . --exclude-dir=.git --exclude=*.md --exclude=*.txt --exclude=*.log --exclude=*.sh 2>/dev/null | grep -v "admin@" | grep -v "admin:"; then
        print_warning "Found potential weak password pattern: $pattern"
    fi
done

# Check for environment variable usage
print_status "Checking for proper environment variable usage..."

if grep -r "\${" . --exclude-dir=.git --exclude=*.md --exclude=*.txt --exclude=*.log 2>/dev/null; then
    print_success "Environment variables are being used"
else
    print_warning "No environment variable usage found"
fi

# Check for .env file
if [ -f ".env" ]; then
    print_success ".env file exists"
    if [ "$(stat -c %a .env)" = "600" ]; then
        print_success ".env file has correct permissions (600)"
    else
        print_error ".env file has incorrect permissions: $(stat -c %a .env)"
    fi
else
    print_warning ".env file not found"
fi

# Check for .gitignore
if [ -f ".gitignore" ]; then
    if grep -q "\.env" .gitignore; then
        print_success ".env is properly excluded from version control"
    else
        print_error ".env is not excluded from version control"
    fi
else
    print_warning ".gitignore file not found"
fi

echo ""
echo "🔍 VERIFICATION SUMMARY"
echo "======================"

if [ "$found_hardcoded" = true ]; then
    print_error "❌ HARDCODED CREDENTIALS FOUND!"
    echo "Please remove all hardcoded credentials before proceeding to production."
    exit 1
else
    print_success "✅ NO HARDCODED CREDENTIALS FOUND!"
    echo "The codebase is clean of hardcoded credentials."
fi

echo ""
print_success "Verification complete!" 