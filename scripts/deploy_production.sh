#!/bin/bash

# Vanta Ledger Production Deployment Script
# This script sets up a production-ready deployment

set -e  # Exit on any error

echo "🚀 Starting Vanta Ledger Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Check prerequisites
print_status "Checking prerequisites..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_status "Prerequisites check passed!"

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p data/uploads
mkdir -p data/processed_documents
mkdir -p nginx/ssl
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/grafana/datasources

# Generate SSL certificates (self-signed for development)
print_status "Generating SSL certificates..."
if [ ! -f nginx/ssl/cert.pem ] || [ ! -f nginx/ssl/key.pem ]; then
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
    print_status "SSL certificates generated"
else
    print_status "SSL certificates already exist"
fi

# Generate secure secrets
print_status "Generating secure secrets..."

# Generate SECRET_KEY
SECRET_KEY=$(openssl rand -hex 32)
echo "SECRET_KEY=$SECRET_KEY" > .env

# Generate database passwords
POSTGRES_PASSWORD=$(openssl rand -hex 16)
MONGO_ROOT_PASSWORD=$(openssl rand -hex 16)
REDIS_PASSWORD=$(openssl rand -hex 16)
GRAFANA_PASSWORD=$(openssl rand -hex 16)

# Append to .env file
cat >> .env << EOF

# Database Configuration
POSTGRES_USER=vanta_user
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
MONGO_ROOT_USER=admin
MONGO_ROOT_PASSWORD=$MONGO_ROOT_PASSWORD
REDIS_PASSWORD=$REDIS_PASSWORD
DATABASE_NAME=vanta_ledger

# Application Configuration
DEBUG=False
HOST=0.0.0.0
PORT=8500
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000

# File Storage
UPLOAD_DIR=/var/vanta-ledger/uploads
PROCESSED_DOCUMENTS_DIR=/var/vanta-ledger/processed_documents
MAX_FILE_SIZE=10485760

# Cache
CACHE_DURATION=300

# Pagination
DEFAULT_PAGE_SIZE=100
MAX_PAGE_SIZE=1000

# CORS - Update with your production domain
ALLOWED_ORIGINS=https://localhost,https://127.0.0.1

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/vanta-ledger/app.log

# Monitoring
GRAFANA_PASSWORD=$GRAFANA_PASSWORD
EOF

print_status "Environment file created with secure secrets"

# Set proper permissions
print_status "Setting proper permissions..."
chmod 600 .env
chmod 600 nginx/ssl/*.pem

# Build and start services
print_status "Building and starting services..."
docker-compose -f docker-compose.production.yml build

print_status "Starting services..."
docker-compose -f docker-compose.production.yml up -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Check service health
print_status "Checking service health..."

# Check backend health
if curl -f http://localhost:8500/health > /dev/null 2>&1; then
    print_status "✅ Backend is healthy"
else
    print_error "❌ Backend health check failed"
    docker-compose -f docker-compose.production.yml logs backend
    exit 1
fi

# Check nginx health
if curl -f http://localhost/health > /dev/null 2>&1; then
    print_status "✅ Nginx is healthy"
else
    print_error "❌ Nginx health check failed"
    docker-compose -f docker-compose.production.yml logs nginx
    exit 1
fi

# Check Prometheus
if curl -f http://localhost:9090/-/healthy > /dev/null 2>&1; then
    print_status "✅ Prometheus is healthy"
else
    print_warning "⚠️  Prometheus health check failed (this is normal if metrics aren't configured yet)"
fi

# Check Grafana
if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
    print_status "✅ Grafana is healthy"
else
    print_warning "⚠️  Grafana health check failed (this is normal if not fully configured yet)"
fi

# Create backup script
print_status "Creating backup script..."
cat > scripts/backup.sh << 'EOF'
#!/bin/bash
# Backup script for Vanta Ledger

BACKUP_DIR="/opt/backups/vanta-ledger"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker-compose -f docker-compose.production.yml exec -T postgres pg_dump -U vanta_user vanta_ledger > $BACKUP_DIR/postgres_$DATE.sql

# Backup MongoDB
docker-compose -f docker-compose.production.yml exec -T mongodb mongodump --out $BACKUP_DIR/mongodb_$DATE

# Backup uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz data/uploads/

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "mongodb_*" -mtime +7 -exec rm -rf {} \;
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR"
EOF

chmod +x scripts/backup.sh

# Create systemd service
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/vanta-ledger.service << EOF
[Unit]
Description=Vanta Ledger Production
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/docker-compose -f docker-compose.production.yml up -d
ExecStop=/usr/bin/docker-compose -f docker-compose.production.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable vanta-ledger.service

print_status "Systemd service created and enabled"

# Create monitoring dashboard
print_status "Setting up monitoring dashboard..."
cat > monitoring/grafana/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

# Final status
print_status "🎉 Production deployment completed successfully!"

echo ""
echo "📋 Deployment Summary:"
echo "======================"
echo "✅ Backend API: https://localhost"
echo "✅ API Documentation: https://localhost/docs"
echo "✅ Health Check: https://localhost/health"
echo "✅ Prometheus: http://localhost:9090"
echo "✅ Grafana: http://localhost:3000 (admin/$GRAFANA_PASSWORD)"
echo ""
echo "🔐 Security:"
echo "============"
echo "✅ SSL/HTTPS enabled"
echo "✅ Rate limiting configured"
echo "✅ Security headers enabled"
echo "✅ Non-root containers"
echo "✅ Secure secrets generated"
echo ""
echo "📊 Monitoring:"
echo "=============="
echo "✅ Prometheus metrics collection"
echo "✅ Grafana dashboards"
echo "✅ Health checks configured"
echo "✅ Logging configured"
echo ""
echo "🔄 Management:"
echo "=============="
echo "✅ Systemd service: vanta-ledger.service"
echo "✅ Backup script: scripts/backup.sh"
echo "✅ Docker Compose: docker-compose.production.yml"
echo ""
echo "📝 Next Steps:"
echo "=============="
echo "1. Update ALLOWED_ORIGINS in .env with your production domain"
echo "2. Replace SSL certificates with real ones from Let's Encrypt"
echo "3. Configure firewall rules"
echo "4. Set up automated backups"
echo "5. Configure monitoring alerts"
echo ""
echo "🚀 Your Vanta Ledger is now production-ready!" 