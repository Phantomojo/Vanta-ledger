# 🚀 Vanta Ledger Deployment Guide

## 📋 Deployment Overview

This guide provides comprehensive deployment instructions for Vanta Ledger across different environments, from development to production. It covers containerized deployment, manual installation, and cloud deployment scenarios.

## 🎯 Deployment Scenarios

### **Deployment Types**
```
Deployment Options
├── 🐳 Containerized Deployment
│   ├── Docker All-in-One
│   ├── Docker Compose
│   ├── Kubernetes
│   └── Cloud Containers
├── 🖥️ Manual Installation
│   ├── Ubuntu/Debian
│   ├── CentOS/RHEL
│   ├── macOS
│   └── Windows
├── ☁️ Cloud Deployment
│   ├── AWS
│   ├── Azure
│   ├── Google Cloud
│   └── Digital Ocean
└── 🏢 Enterprise Deployment
    ├── On-Premises
    ├── Hybrid Cloud
    ├── Multi-Region
    └── High Availability
```

## 🐳 Containerized Deployment

### **Docker All-in-One Container**

#### **Quick Start**
```bash
# Clone repository
git clone https://github.com/yourusername/vanta-ledger.git
cd vanta-ledger

# Build container (Dockerfile is now in config/)
docker build -f config/Dockerfile -t vanta-ledger-all-in-one .

# Run container
docker run -d \
  --name vanta-ledger \
  -p 8000:8000 \
  -p 5432:5432 \
  -p 27017:27017 \
  -p 6379:6379 \
  -p 8080:8080 \
  -p 8081:8081 \
  --memory=8g \
  --cpus=4 \
  --env-file .env \
  vanta-ledger-all-in-one
```

#### **Environment Configuration**
```bash
# Copy environment template
cp env.example .env

# Edit environment variables
nano .env

# Key configuration:
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info
SECRET_KEY=your-64-character-secret-key
DATABASE_URL=postgresql://user:password@localhost/vanta_ledger
MONGODB_URL=mongodb://localhost:27017/vanta_ledger
REDIS_URL=redis://localhost:6379
AI_MODELS_PATH=/app/models
UPLOAD_PATH=/app/uploads
LOG_PATH=/app/logs
SECURITY_LEVEL=high
COMPANY_ISOLATION=true
AUDIT_LOGGING=true
```

### **Docker Compose Deployment**

#### **Development Environment**
```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  vanta-ledger:
    build: .
    ports:
      - "8000:8000"
      - "5432:5432"
      - "27017:27017"
      - "6379:6379"
      - "8080:8080"
      - "8081:8081"
    environment:
      - ENVIRONMENT=development
      - DEBUG=true
      - LOG_LEVEL=debug
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./models:/app/models
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2'
        reservations:
          memory: 2G
          cpus: '1'

  # Optional: External databases for development
  postgres-dev:
    image: postgres:15
    environment:
      POSTGRES_DB: vanta_ledger_dev
      POSTGRES_USER: vanta_user
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5433:5432"
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data

  mongodb-dev:
    image: mongo:8.0
    ports:
      - "27018:27017"
    volumes:
      - mongodb_dev_data:/data/db

volumes:
  postgres_dev_data:
  mongodb_dev_data:
```

#### **Production Environment**
```yaml
# docker-compose.production.yml
version: '3.8'

services:
  vanta-ledger:
    build: .
    ports:
      - "8000:8000"
      - "5432:5432"
      - "27017:27017"
      - "6379:6379"
      - "8080:8080"
      - "8081:8081"
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - LOG_LEVEL=warning
      - SECURITY_LEVEL=maximum
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./models:/app/models
      - ./ssl:/app/ssl
    restart: always
    deploy:
      resources:
        limits:
          memory: 16G
          cpus: '8'
        reservations:
          memory: 8G
          cpus: '4'
    networks:
      - vanta-network

  # Production database (optional external)
  postgres-prod:
    image: postgres:15
    environment:
      POSTGRES_DB: vanta_ledger_prod
      POSTGRES_USER: vanta_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_prod_data:/var/lib/postgresql/data
      - ./ssl/postgresql:/etc/ssl/private
    networks:
      - vanta-network

  # Load balancer
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    depends_on:
      - vanta-ledger
    networks:
      - vanta-network

networks:
  vanta-network:
    driver: bridge

volumes:
  postgres_prod_data:
```

### **Kubernetes Deployment**

#### **Kubernetes Manifests**
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: vanta-ledger

---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: vanta-ledger-config
  namespace: vanta-ledger
data:
  ENVIRONMENT: "production"
  DEBUG: "false"
  LOG_LEVEL: "info"
  SECURITY_LEVEL: "high"

---
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: vanta-ledger-secrets
  namespace: vanta-ledger
type: Opaque
data:
  SECRET_KEY: <base64-encoded-secret>
  DATABASE_PASSWORD: <base64-encoded-password>
  MONGODB_PASSWORD: <base64-encoded-password>

---
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vanta-ledger
  namespace: vanta-ledger
spec:
  replicas: 3
  selector:
    matchLabels:
      app: vanta-ledger
  template:
    metadata:
      labels:
        app: vanta-ledger
    spec:
      containers:
      - name: vanta-ledger
        image: vanta-ledger:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: vanta-ledger-config
        - secretRef:
            name: vanta-ledger-secrets
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: vanta-ledger-service
  namespace: vanta-ledger
spec:
  selector:
    app: vanta-ledger
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer

---
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: vanta-ledger-ingress
  namespace: vanta-ledger
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - vanta-ledger.com
    secretName: vanta-ledger-tls
  rules:
  - host: vanta-ledger.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: vanta-ledger-service
            port:
              number: 80
```

## 🖥️ Manual Installation

### **Ubuntu/Debian Installation**

#### **System Preparation**
```bash
#!/bin/bash
# Ubuntu/Debian installation script

echo "🚀 Installing Vanta Ledger on Ubuntu/Debian"

# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y \
  python3.12 \
  python3.12-venv \
  python3.12-dev \
  python3-pip \
  postgresql \
  postgresql-contrib \
  mongodb \
  redis-server \
  nginx \
  certbot \
  python3-certbot-nginx \
  git \
  curl \
  wget \
  unzip \
  build-essential

# Install Node.js for frontend (optional)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

echo "✅ System packages installed"
```

#### **Python Environment Setup**
```bash
# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt
pip install -r constraints.txt

# Install additional development tools
pip install pytest pytest-cov black flake8 mypy
```

#### **Database Setup**
```bash
# PostgreSQL setup
sudo -u postgres psql << EOF
CREATE DATABASE vanta_ledger;
CREATE USER vanta_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE vanta_ledger TO vanta_user;
ALTER USER vanta_user CREATEDB;
\q
EOF

# MongoDB setup
sudo systemctl start mongodb
sudo systemctl enable mongodb

# Redis setup
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify services
sudo systemctl status postgresql
sudo systemctl status mongodb
sudo systemctl status redis-server
```

#### **AI Models Download**
```bash
# Create models directory
mkdir -p models
cd models

# Download AI models based on system resources
echo "Downloading AI models..."

# TinyLlama (1GB) - Fast, basic tasks
wget -O tinyllama.bin https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0/resolve/main/pytorch_model.bin

# Phi-3 Mini (2.1GB) - Balanced performance
wget -O phi3_mini.bin https://huggingface.co/microsoft/Phi-3-mini-4k-instruct/resolve/main/pytorch_model.bin

# Mistral 7B (4GB) - High accuracy, complex tasks
wget -O mistral_7b.bin https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2/resolve/main/pytorch_model.bin

echo "✅ AI models downloaded"
```

### **CentOS/RHEL Installation**

#### **System Preparation**
```bash
#!/bin/bash
# CentOS/RHEL installation script

echo "🚀 Installing Vanta Ledger on CentOS/RHEL"

# Enable EPEL repository
sudo yum install -y epel-release

# Install required packages
sudo yum install -y \
  python3.12 \
  python3.12-devel \
  python3.12-pip \
  postgresql \
  postgresql-server \
  postgresql-contrib \
  mongodb-org \
  redis \
  nginx \
  git \
  curl \
  wget \
  unzip \
  gcc \
  gcc-c++ \
  make

# Start and enable services
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql

sudo systemctl start mongod
sudo systemctl enable mongod

sudo systemctl start redis
sudo systemctl enable redis

echo "✅ System packages installed"
```

### **macOS Installation**

#### **Using Homebrew**
```bash
#!/bin/bash
# macOS installation script

echo "🚀 Installing Vanta Ledger on macOS"

# Install Homebrew if not present
if ! command -v brew &> /dev/null; then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install required packages
brew install \
  python@3.12 \
  postgresql@15 \
  mongodb/brew/mongodb-community \
  redis \
  nginx \
  git \
  curl \
  wget

# Start services
brew services start postgresql@15
brew services start mongodb/brew/mongodb-community
brew services start redis

echo "✅ System packages installed"
```

## ☁️ Cloud Deployment

### **AWS Deployment**

#### **EC2 Instance Setup**
```bash
#!/bin/bash
# AWS EC2 setup script

echo "🚀 Setting up Vanta Ledger on AWS EC2"

# Update system
sudo yum update -y

# Install required packages
sudo yum install -y \
  python3.12 \
  python3.12-devel \
  python3.12-pip \
  postgresql \
  postgresql-server \
  postgresql-contrib \
  mongodb-org \
  redis \
  nginx \
  git \
  curl \
  wget

# Configure security groups
# - Port 22 (SSH)
# - Port 80 (HTTP)
# - Port 443 (HTTPS)
# - Port 8000 (Vanta Ledger API)
# - Port 5432 (PostgreSQL)
# - Port 27017 (MongoDB)
# - Port 6379 (Redis)

# Setup SSL certificates
sudo yum install -y certbot python3-certbot-nginx

# Configure firewall
sudo yum install -y firewalld
sudo systemctl start firewalld
sudo systemctl enable firewalld

sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

echo "✅ AWS EC2 setup completed"
```

#### **AWS RDS Setup**
```bash
# Create RDS instance for PostgreSQL
aws rds create-db-instance \
  --db-instance-identifier vanta-ledger-postgres \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username vanta_user \
  --master-user-password secure_password \
  --allocated-storage 20 \
  --storage-type gp2 \
  --vpc-security-group-ids sg-xxxxxxxxx \
  --db-name vanta_ledger

# Create ElastiCache for Redis
aws elasticache create-cache-cluster \
  --cache-cluster-id vanta-ledger-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1 \
  --vpc-security-group-ids sg-xxxxxxxxx
```

### **Azure Deployment**

#### **Azure VM Setup**
```bash
#!/bin/bash
# Azure VM setup script

echo "🚀 Setting up Vanta Ledger on Azure VM"

# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y \
  python3.12 \
  python3.12-venv \
  python3.12-dev \
  python3-pip \
  postgresql \
  postgresql-contrib \
  mongodb \
  redis-server \
  nginx \
  certbot \
  python3-certbot-nginx \
  git \
  curl \
  wget

# Configure Azure Network Security Group
# - Port 22 (SSH)
# - Port 80 (HTTP)
# - Port 443 (HTTPS)
# - Port 8000 (Vanta Ledger API)

# Setup SSL certificates
sudo certbot --nginx -d your-domain.com

echo "✅ Azure VM setup completed"
```

#### **Azure Database Services**
```bash
# Create Azure Database for PostgreSQL
az postgres flexible-server create \
  --name vanta-ledger-postgres \
  --resource-group vanta-ledger-rg \
  --location eastus \
  --admin-user vanta_user \
  --admin-password secure_password \
  --sku-name Standard_B1ms \
  --storage-size 32

# Create Azure Cache for Redis
az redis create \
  --name vanta-ledger-redis \
  --resource-group vanta-ledger-rg \
  --location eastus \
  --sku Basic \
  --vm-size C0
```

### **Google Cloud Deployment**

#### **GCP VM Setup**
```bash
#!/bin/bash
# Google Cloud VM setup script

echo "🚀 Setting up Vanta Ledger on Google Cloud"

# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y \
  python3.12 \
  python3.12-venv \
  python3.12-dev \
  python3-pip \
  postgresql \
  postgresql-contrib \
  mongodb \
  redis-server \
  nginx \
  certbot \
  python3-certbot-nginx \
  git \
  curl \
  wget

# Configure Google Cloud Firewall
# - Port 22 (SSH)
# - Port 80 (HTTP)
# - Port 443 (HTTPS)
# - Port 8000 (Vanta Ledger API)

# Setup SSL certificates
sudo certbot --nginx -d your-domain.com

echo "✅ Google Cloud VM setup completed"
```

## 🏢 Enterprise Deployment

### **High Availability Setup**

#### **Load Balancer Configuration**
```nginx
# nginx/nginx.conf
upstream vanta_backend {
    least_conn;
    server 192.168.1.10:8000;
    server 192.168.1.11:8000;
    server 192.168.1.12:8000;
}

server {
    listen 80;
    server_name vanta-ledger.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name vanta-ledger.com;
    
    ssl_certificate /etc/ssl/certs/vanta-ledger.crt;
    ssl_certificate_key /etc/ssl/private/vanta-ledger.key;
    
    location / {
        proxy_pass http://vanta_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Health check
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
    }
    
    location /health {
        proxy_pass http://vanta_backend;
        access_log off;
    }
}
```

#### **Database Clustering**
```bash
# PostgreSQL replication setup
# Primary server
sudo -u postgres psql << EOF
ALTER SYSTEM SET wal_level = replica;
ALTER SYSTEM SET max_wal_senders = 3;
ALTER SYSTEM SET max_replication_slots = 3;
SELECT pg_reload_conf();
EOF

# Create replication user
sudo -u postgres psql << EOF
CREATE USER replicator REPLICATION LOGIN PASSWORD 'replica_password';
\q
EOF

# Secondary server
sudo -u postgres psql << EOF
CREATE DATABASE vanta_ledger;
\q
EOF

# Setup replication
sudo -u postgres pg_basebackup -h primary_ip -D /var/lib/postgresql/15/main -U replicator -v -P -W
```

### **Multi-Region Deployment**

#### **Global Load Balancer**
```yaml
# GCP Global Load Balancer
apiVersion: v1
kind: Service
metadata:
  name: vanta-ledger-global
  annotations:
    cloud.google.com/load-balancer-type: "Global"
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: vanta-ledger
```

## 🔧 Deployment Scripts

### **Automated Deployment**
```bash
#!/bin/bash
# deploy.sh - Automated deployment script

set -e

echo "🚀 Starting Vanta Ledger deployment..."

# Configuration
ENVIRONMENT=${1:-production}
DOMAIN=${2:-vanta-ledger.com}
DB_PASSWORD=${3:-secure_password}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    log_info "Prerequisites check passed"
}

# Setup environment
setup_environment() {
    log_info "Setting up environment: $ENVIRONMENT"
    
    # Copy environment file
    if [ ! -f .env ]; then
        cp env.$ENVIRONMENT.example .env
        log_info "Environment file created"
    fi
    
    # Update environment variables
    sed -i "s/DOMAIN=.*/DOMAIN=$DOMAIN/" .env
    sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=$DB_PASSWORD/" .env
    
    log_info "Environment configured"
}

# Build and deploy
deploy_application() {
    log_info "Building and deploying application..."
    
    # Build container
    docker build -t vanta-ledger:$ENVIRONMENT .
    
    # Deploy with docker-compose
    docker-compose -f config/docker-compose.$ENVIRONMENT.yml up -d
    
    log_info "Application deployed successfully"
}

# Setup SSL certificates
setup_ssl() {
    log_info "Setting up SSL certificates..."
    
    if [ "$ENVIRONMENT" = "production" ]; then
        # Install certbot
        sudo apt update
        sudo apt install -y certbot python3-certbot-nginx
        
        # Get SSL certificate
        sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
        
        log_info "SSL certificates configured"
    else
        log_warn "Skipping SSL setup for non-production environment"
    fi
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    # Wait for services to start
    sleep 30
    
    # Check API health
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_info "API health check passed"
    else
        log_error "API health check failed"
        exit 1
    fi
    
    # Check database connections
    if docker exec vanta-ledger pg_isready -U vanta_user -d vanta_ledger > /dev/null 2>&1; then
        log_info "Database health check passed"
    else
        log_error "Database health check failed"
        exit 1
    fi
    
    log_info "Health check completed successfully"
}

# Main deployment flow
main() {
    log_info "Starting deployment process..."
    
    check_prerequisites
    setup_environment
    deploy_application
    setup_ssl
    health_check
    
    log_info "🎉 Deployment completed successfully!"
    log_info "Access your application at: https://$DOMAIN"
    log_info "API Documentation: https://$DOMAIN/docs"
}

# Run deployment
main "$@"
```

### **Rollback Script**
```bash
#!/bin/bash
# rollback.sh - Deployment rollback script

set -e

echo "🔄 Starting deployment rollback..."

# Configuration
PREVIOUS_VERSION=${1:-latest}
CURRENT_VERSION=${2:-$(docker images -q vanta-ledger:latest)}

# Functions
log_info() {
    echo -e "\033[0;32m[INFO]\033[0m $1"
}

log_error() {
    echo -e "\033[0;31m[ERROR]\033[0m $1"
}

# Stop current deployment
stop_current() {
    log_info "Stopping current deployment..."
    docker-compose down
}

# Rollback to previous version
rollback_version() {
    log_info "Rolling back to version: $PREVIOUS_VERSION"
    
    # Update docker-compose to use previous version
    sed -i "s/image: vanta-ledger:.*/image: vanta-ledger:$PREVIOUS_VERSION/" config/docker-compose.yml
    
    # Start previous version
    docker-compose -f config/docker-compose.yml up -d
    
    log_info "Rollback completed"
}

# Verify rollback
verify_rollback() {
    log_info "Verifying rollback..."
    
    # Wait for services to start
    sleep 30
    
    # Check health
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_info "Rollback verification successful"
    else
        log_error "Rollback verification failed"
        exit 1
    fi
}

# Main rollback flow
main() {
    log_info "Starting rollback process..."
    
    stop_current
    rollback_version
    verify_rollback
    
    log_info "🔄 Rollback completed successfully!"
}

# Run rollback
main "$@"
```

## 📊 Deployment Monitoring

### **Health Check Endpoints**
```python
# Health check implementation
@app.get("/health")
async def health_check():
    """System health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {},
        "system": {}
    }
    
    # Check database health
    try:
        db = get_database()
        db.command("ping")
        health_status["services"]["database"] = {
            "status": "healthy",
            "response_time": 0
        }
    except Exception as e:
        health_status["services"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # Check cache health
    try:
        redis_client = get_redis_client()
        redis_client.ping()
        health_status["services"]["cache"] = {
            "status": "healthy",
            "response_time": 0
        }
    except Exception as e:
        health_status["services"]["cache"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # Check system resources
    import psutil
    health_status["system"] = {
        "cpu_usage": psutil.cpu_percent(),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "uptime": time.time() - psutil.boot_time()
    }
    
    return health_status
```

### **Deployment Status Dashboard**
```python
# Deployment status endpoint
@app.get("/deployment/status")
async def deployment_status():
    """Deployment status and information"""
    return {
        "deployment_info": {
            "version": os.getenv("APP_VERSION", "unknown"),
            "environment": os.getenv("ENVIRONMENT", "unknown"),
            "deployment_date": os.getenv("DEPLOYMENT_DATE", "unknown"),
            "commit_hash": os.getenv("COMMIT_HASH", "unknown")
        },
        "system_status": {
            "uptime": time.time() - psutil.boot_time(),
            "services": get_services_status(),
            "performance": get_performance_metrics()
        },
        "last_updated": datetime.utcnow().isoformat()
    }
```

## 📋 Deployment Checklist

### **Pre-Deployment Checklist**
- [ ] Environment configuration completed
- [ ] Database migrations tested
- [ ] Security audit passed
- [ ] Performance benchmarks met
- [ ] Backup systems configured
- [ ] Monitoring systems active
- [ ] Rollback plan prepared
- [ ] Team notifications sent

### **Deployment Checklist**
- [ ] Stop current services
- [ ] Backup current data
- [ ] Deploy new version
- [ ] Run database migrations
- [ ] Start new services
- [ ] Verify health checks
- [ ] Test critical functionality
- [ ] Monitor system performance

### **Post-Deployment Checklist**
- [ ] All health checks pass
- [ ] Performance monitoring active
- [ ] Error logging configured
- [ ] User notifications sent
- [ ] Documentation updated
- [ ] Team debrief completed
- [ ] Next deployment planned

---

**🚀 This comprehensive deployment guide ensures successful deployment of Vanta Ledger across all environments and scenarios.**
