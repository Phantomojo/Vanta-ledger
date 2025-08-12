#!/bin/bash

# Vanta Ledger Secure Password Generator
# Generated: August 4, 2025

set -e

echo "🔐 Generating secure passwords for Vanta Ledger..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Generate secure passwords
print_status "Generating cryptographically secure passwords..."

POSTGRES_PASSWORD=$(openssl rand -base64 32)
MONGO_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)
PGADMIN_PASSWORD=$(openssl rand -base64 32)
MONGO_EXPRESS_PASSWORD=$(openssl rand -base64 32)
SESSION_SECRET=$(openssl rand -base64 32)

# Create .env file
print_status "Creating .env file with secure passwords..."

cat > .env << EOF
# Vanta Ledger Database Environment Variables
# Generated: $(date)
# WARNING: Keep this file secure and never commit to version control!

# PostgreSQL Configuration
POSTGRES_DB=vanta_ledger
POSTGRES_USER=vanta_user
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

# MongoDB Configuration
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=${MONGO_PASSWORD}
MONGO_DATABASE=vanta_ledger

# Redis Configuration
REDIS_PASSWORD=${REDIS_PASSWORD}

# Web Management Interfaces
PGADMIN_EMAIL=admin@vantaledger.com
PGADMIN_PASSWORD=${PGADMIN_PASSWORD}
MONGO_EXPRESS_USERNAME=admin
MONGO_EXPRESS_PASSWORD=${MONGO_EXPRESS_PASSWORD}

# Session Security
SESSION_SECRET=${SESSION_SECRET}

# SSL Configuration
SSL_COUNTRY=KE
SSL_STATE=Nairobi
SSL_LOCALITY=Nairobi
SSL_ORGANIZATION="Vanta Ledger"
SSL_ORGANIZATIONAL_UNIT=IT
SSL_COMMON_NAME=vantaledger.local
EOF

# Set proper permissions
chmod 600 .env

print_success "Secure passwords generated and saved to .env file"
print_success "File permissions set to 600 (owner read/write only)"

echo ""
echo "🔐 PASSWORD SUMMARY:"
echo "==================="
echo "PostgreSQL: ${POSTGRES_PASSWORD:0:20}..."
echo "MongoDB:    ${MONGO_PASSWORD:0:20}..."
echo "Redis:      ${REDIS_PASSWORD:0:20}..."
echo "pgAdmin:    ${PGADMIN_PASSWORD:0:20}..."
echo "Mongo Express: ${MONGO_EXPRESS_PASSWORD:0:20}..."
echo "Session Secret: ${SESSION_SECRET:0:20}..."
echo ""

print_status "Next steps:"
echo "1. Review the .env file"
echo "2. Run: ./update-configs.sh"
echo "3. Run: ./security-update.sh"
echo ""

print_success "Password generation complete!" 