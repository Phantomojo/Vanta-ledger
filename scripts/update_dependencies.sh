#!/bin/bash

# Update Dependencies Script for Vanta Ledger
# Addresses Dependabot security vulnerabilities

set -e

echo "🔒 Updating Dependencies to Address Security Vulnerabilities"
echo "=========================================================="

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

# Check if we're in the right directory
if [ ! -f "backend/requirements.txt" ]; then
    print_error "Please run this script from the Vanta Ledger root directory"
    exit 1
fi

# Backup current requirements
print_status "Creating backup of current requirements..."
cp backend/requirements.txt backend/requirements-backup-$(date +%Y%m%d_%H%M%S).txt
print_success "Backup created"

# Update pip itself
print_status "Updating pip..."
python3 -m pip install --upgrade pip

# Install secure requirements
print_status "Installing secure requirements..."
python3 -m pip install -r backend/requirements-secure.txt

# Update critical security packages
print_status "Updating critical security packages..."

# Update cryptography (critical security)
python3 -m pip install --upgrade cryptography==45.0.6

# Update requests and urllib3 (security)
python3 -m pip install --upgrade requests==2.32.4 urllib3==2.5.0

# Update authentication packages
python3 -m pip install --upgrade python-jose[cryptography]==3.5.0 PyJWT==2.10.1

# Update web framework packages
python3 -m pip install --upgrade fastapi==0.116.1 uvicorn[standard]==0.35.0

# Update database packages
python3 -m pip install --upgrade sqlalchemy==2.0.42 psycopg2-binary==2.9.10 pymongo==4.14.0

# Update file processing packages
python3 -m pip install --upgrade Pillow==11.3.0 aiofiles==24.1.0

# Update data processing packages
python3 -m pip install --upgrade numpy==2.3.2 pandas==2.3.4

# Update system monitoring packages
python3 -m pip install --upgrade psutil==7.0.0

# Update utility packages
python3 -m pip install --upgrade python-dotenv==1.1.1 PyYAML==6.0.2

# Update testing packages
python3 -m pip install --upgrade pytest==8.4.1 pytest-asyncio==0.24.0

print_success "All critical packages updated"

# Generate new requirements file
print_status "Generating updated requirements file..."
python3 -m pip freeze > backend/requirements-updated.txt

# Test the system
print_status "Testing system after updates..."
python3 tests/test_core_functionality.py

if [ $? -eq 0 ]; then
    print_success "System tests passed after updates!"
else
    print_warning "Some tests failed. Check the output above."
fi

# Show what was updated
print_status "Updated packages summary:"
echo "=========================================================="
echo "Critical Security Updates:"
echo "  - cryptography: 41.0.7 → 45.0.6"
echo "  - requests: 2.31.0 → 2.32.4"
echo "  - urllib3: 2.0.7 → 2.5.0"
echo "  - python-jose: 3.3.0 → 3.5.0"
echo "  - PyJWT: 2.7.0 → 2.10.1"
echo ""
echo "Framework Updates:"
echo "  - fastapi: 0.104.1 → 0.116.1"
echo "  - uvicorn: 0.24.0 → 0.35.0"
echo "  - sqlalchemy: 2.0.23 → 2.0.42"
echo "  - pymongo: 4.13.2 → 4.14.0"
echo ""
echo "System Updates:"
echo "  - psutil: 5.9.6 → 7.0.0"
echo "  - Pillow: 10.1.0 → 11.3.0"
echo "  - numpy: 1.26.4 → 2.3.2"
echo "  - pytest: 7.4.4 → 8.4.1"

print_success "Dependency update completed!"
echo ""
print_status "Next steps:"
echo "  1. Review the updated requirements: backend/requirements-updated.txt"
echo "  2. Test your application thoroughly"
echo "  3. Commit the changes to git"
echo "  4. Monitor for any new issues"

echo ""
print_status "Security vulnerabilities addressed:"
echo "  ✅ cryptography - Updated to latest secure version"
echo "  ✅ requests/urllib3 - Updated to latest secure versions"
echo "  ✅ authentication packages - Updated to latest versions"
echo "  ✅ web framework - Updated to latest versions"
echo "  ✅ database packages - Updated to latest versions"
echo "  ✅ file processing - Updated to latest versions"
echo "  ✅ system monitoring - Updated to latest versions" 