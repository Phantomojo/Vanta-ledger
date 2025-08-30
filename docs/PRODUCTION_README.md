# 🚀 Vanta Ledger Production Deployment Guide

This guide covers the complete production deployment of Vanta Ledger with security, monitoring, and scalability.

## 📋 Prerequisites

### System Requirements
- **CPU**: 4+ cores (8+ recommended)
- **RAM**: 8GB+ (16GB recommended)
- **Storage**: 100GB+ available space
- **OS**: Ubuntu 20.04+ or CentOS 8+
- **Network**: Static IP address

### Software Requirements
- Docker 20.10+
- Docker Compose 2.0+
- OpenSSL
- curl

## 🔐 Security Features Implemented

### ✅ Security Hardening
- **Removed hardcoded secrets** from configuration files
- **Secure secret generation** using OpenSSL
- **Rate limiting** (100 requests/minute, 1000/hour)
- **Security headers** (HSTS, CSP, XSS Protection, etc.)
- **HTTPS/SSL** with modern cipher suites
- **Non-root containers** for all services
- **Input validation** and sanitization
- **CORS protection** with configurable origins

### ✅ Authentication & Authorization
- **JWT-based authentication** with secure tokens
- **Password hashing** using bcrypt
- **Token expiration** (30 minutes default)
- **Role-based access control**

### ✅ Database Security
- **Encrypted connections** to databases
- **Separate database users** with minimal privileges
- **Connection pooling** and timeout handling
- **Secure password generation** for all databases

## 🚀 Quick Production Deployment

### 1. Automated Deployment
```bash
# Clone repository
git clone <your-repo-url>
cd Vanta-ledger

# Run production deployment script
./scripts/deploy_production.sh
```

This script will:
- ✅ Generate secure SSL certificates
- ✅ Create secure environment variables
- ✅ Build and start all services
- ✅ Configure monitoring
- ✅ Set up automated backups
- ✅ Create systemd service

### 2. Manual Deployment
If you prefer manual deployment:

```bash
# 1. Copy environment template
cp env.production.example .env

# 2. Edit .env with your production values
nano .env

# 3. Generate SSL certificates
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/key.pem \
    -out nginx/ssl/cert.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=your-domain.com"

# 4. Start services
docker-compose -f docker-compose.production.yml up -d
```

## 🔧 Configuration

### Environment Variables
Key production environment variables:

```bash
# Security (CHANGE THESE!)
SECRET_KEY=your-super-secret-production-key
POSTGRES_PASSWORD=secure-postgres-password
MONGO_ROOT_PASSWORD=secure-mongo-password
REDIS_PASSWORD=secure-redis-password

# Application
DEBUG=False
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000

# File Storage
MAX_FILE_SIZE=10485760  # 10MB
```

### SSL Certificates
For production, replace self-signed certificates with real ones:

```bash
# Using Let's Encrypt
sudo certbot certonly --standalone -d your-domain.com
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
```

## 📊 Monitoring & Observability

### Prometheus Metrics
- **Application metrics**: Request count, duration, errors
- **Database metrics**: Connection pools, query performance
- **System metrics**: CPU, memory, disk usage
- **Custom metrics**: Business KPIs, document processing stats

### Grafana Dashboards
Access Grafana at `http://your-domain:3000`
- **System Overview**: CPU, memory, disk usage
- **Application Performance**: Response times, error rates
- **Database Performance**: Query times, connection pools
- **Business Metrics**: Document processing, user activity

### Health Checks
All services include health checks:
- **Backend**: `GET /health`
- **Databases**: Connection and query health
- **Nginx**: Reverse proxy health
- **Monitoring**: Prometheus and Grafana status

## 🔄 Backup & Recovery

### Automated Backups
```bash
# Run backup manually
./scripts/backup.sh

# Set up automated backups (cron)
crontab -e
# Add: 0 2 * * * /path/to/vanta-ledger/scripts/backup.sh
```

### Backup Contents
- **PostgreSQL**: Complete database dump
- **MongoDB**: Document metadata and analytics
- **Uploads**: All uploaded documents
- **Configuration**: Environment and SSL certificates

### Recovery Process
```bash
# Stop services
docker-compose -f docker-compose.production.yml down

# Restore PostgreSQL
docker-compose -f docker-compose.production.yml exec -T postgres psql -U vanta_user vanta_ledger < backup.sql

# Restore MongoDB
docker-compose -f docker-compose.production.yml exec -T mongodb mongorestore backup/mongodb/

# Restore uploads
tar -xzf backup/uploads.tar.gz

# Start services
docker-compose -f docker-compose.production.yml up -d
```

## 🔧 Maintenance

### Service Management
```bash
# Start services
sudo systemctl start vanta-ledger

# Stop services
sudo systemctl stop vanta-ledger

# Restart services
sudo systemctl restart vanta-ledger

# View logs
sudo journalctl -u vanta-ledger -f
```

### Updates
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d
```

### Scaling
```bash
# Scale backend workers
docker-compose -f docker-compose.production.yml up -d --scale backend=3

# Add load balancer
# Configure nginx upstream with multiple backend instances
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```bash
# Check database status
docker-compose -f docker-compose.production.yml logs postgres
docker-compose -f docker-compose.production.yml logs mongodb

# Test connections
docker-compose -f docker-compose.production.yml exec postgres pg_isready -U vanta_user
```

#### 2. SSL Certificate Issues
```bash
# Check certificate validity
openssl x509 -in nginx/ssl/cert.pem -text -noout

# Test SSL connection
openssl s_client -connect your-domain.com:443 -servername your-domain.com
```

#### 3. Rate Limiting Issues
```bash
# Check rate limit logs
docker-compose -f docker-compose.production.yml logs nginx | grep "rate limit"

# Adjust limits in nginx.conf if needed
```

#### 4. Performance Issues
```bash
# Check resource usage
docker stats

# Monitor application metrics
curl http://localhost:8500/metrics

# Check database performance
docker-compose -f docker-compose.production.yml exec postgres psql -U vanta_user -c "SELECT * FROM pg_stat_activity;"
```

## 🔒 Security Checklist

### ✅ Pre-Deployment
- [ ] Generate strong SECRET_KEY
- [ ] Set secure database passwords
- [ ] Configure ALLOWED_ORIGINS
- [ ] Generate SSL certificates
- [ ] Set up firewall rules

### ✅ Post-Deployment
- [ ] Test all endpoints with authentication
- [ ] Verify SSL certificate installation
- [ ] Check security headers
- [ ] Test rate limiting
- [ ] Verify backup functionality
- [ ] Test monitoring dashboards

### ✅ Ongoing Security
- [ ] Regular security updates
- [ ] Monitor access logs
- [ ] Review rate limiting effectiveness
- [ ] Update SSL certificates
- [ ] Audit user permissions

## 📈 Performance Optimization

### Database Optimization
```sql
-- PostgreSQL indexes
CREATE INDEX idx_documents_upload_date ON documents(upload_date);
CREATE INDEX idx_ledger_company_date ON ledger(company_id, date);

-- MongoDB indexes
db.documents.createIndex({"upload_date": -1})
db.extracted_data.createIndex({"confidence": -1})
```

### Application Optimization
- **Connection pooling**: Configured for all databases
- **Caching**: Redis for session and query caching
- **File compression**: Nginx gzip compression
- **CDN**: Configure for static assets

### Monitoring Alerts
Set up alerts for:
- High error rates (>5%)
- Slow response times (>2s)
- High resource usage (>80%)
- Database connection issues
- SSL certificate expiration

## 🎯 Production Checklist

### ✅ Infrastructure
- [ ] Dedicated server with sufficient resources
- [ ] Static IP address
- [ ] Domain name configured
- [ ] SSL certificates installed
- [ ] Firewall configured

### ✅ Application
- [ ] All services running and healthy
- [ ] Authentication working
- [ ] File uploads functional
- [ ] AI analysis operational
- [ ] API documentation accessible

### ✅ Security
- [ ] No hardcoded secrets
- [ ] HTTPS enforced
- [ ] Rate limiting active
- [ ] Security headers present
- [ ] Non-root containers

### ✅ Monitoring
- [ ] Prometheus collecting metrics
- [ ] Grafana dashboards accessible
- [ ] Health checks passing
- [ ] Logs being collected
- [ ] Alerts configured

### ✅ Backup
- [ ] Automated backups running
- [ ] Backup restoration tested
- [ ] Off-site backup storage
- [ ] Backup monitoring active

## 🚀 Next Steps

1. **Domain Configuration**: Update DNS and SSL certificates
2. **Load Balancing**: Add multiple backend instances
3. **CDN Setup**: Configure for static assets
4. **Advanced Monitoring**: Set up alerting and SLAs
5. **Disaster Recovery**: Test full system recovery
6. **Performance Tuning**: Optimize based on usage patterns

---

**🎉 Congratulations! Your Vanta Ledger is now production-ready with enterprise-grade security, monitoring, and scalability.**

For support, check the logs or contact the development team. 