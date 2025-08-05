# 🚀 Vanta Ledger Deployment Guide

Complete guide for deploying Vanta Ledger in different environments.

## 📋 Prerequisites

### System Requirements
- **CPU**: 2+ cores
- **RAM**: 4GB+ (8GB recommended)
- **Storage**: 50GB+ available space
- **OS**: Linux (Ubuntu 20.04+), Windows 10+, macOS 10.15+

### Software Requirements
- Python 3.8+
- Node.js 16+ (for web frontend)
- PostgreSQL 12+ (for production)
- Docker (optional)

## 🏠 Local Development Deployment

### Quick Start
```bash
# Clone repository
git clone <repository-url>
cd Vanta-ledger

# Setup Python environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
# Edit .env with your settings

# Setup database
python setup_initial_data.py

# Run backend
python run_backend.py
```

### Access Points
- **Backend API**: http://localhost:8500
- **API Docs**: http://localhost:8500/docs
- **Health Check**: http://localhost:8500/health

## 🏢 Office Deployment (Self-Hosted)

### Single Computer Setup

1. **Install Dependencies**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install python3 python3-pip postgresql postgresql-server
```

2. **Setup Database**
```bash
# Create database user
sudo -u postgres createuser vanta_user
sudo -u postgres createdb vanta_ledger
sudo -u postgres psql -c "ALTER USER vanta_user PASSWORD 'vanta_password';"
```

3. **Deploy Application**
```bash
# Clone to /opt/vanta-ledger
sudo git clone <repository-url> /opt/vanta-ledger
sudo chown -R $USER:$USER /opt/vanta-ledger
cd /opt/vanta-ledger

# Setup environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure for production
cp env.example .env
```

4. **Production Configuration** (`.env`)
```bash
DATABASE_URL=postgresql://vanta_user:vanta_password@localhost/vanta_ledger
SECRET_KEY=your-super-secret-production-key
ADMIN_PASSWORD=secure-admin-password
AUNTIE_PASSWORD=secure-auntie-password
HOST=0.0.0.0
PORT=8500
```

5. **Setup Systemd Service**
```bash
sudo tee /etc/systemd/system/vanta-ledger.service << EOF
[Unit]
Description=Vanta Ledger Backend
After=network.target postgresql.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/vanta-ledger
Environment=PATH=/opt/vanta-ledger/.venv/bin
ExecStart=/opt/vanta-ledger/.venv/bin/python run_backend.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable vanta-ledger
sudo systemctl start vanta-ledger
```

6. **Setup Nginx (Optional)**
```bash
sudo apt install nginx

sudo tee /etc/nginx/sites-available/vanta-ledger << EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8500;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/vanta-ledger /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Multi-Computer Setup

For multiple office computers:

1. **Designate Primary Server**
   - Install PostgreSQL and backend on one computer
   - Other computers connect to this server

2. **Network Configuration**
```bash
# On primary server
sudo ufw allow 5432/tcp  # PostgreSQL
sudo ufw allow 8500/tcp  # Backend API
sudo ufw allow 80/tcp    # Web interface
```

3. **Client Configuration**
   - Update `DATABASE_URL` to point to primary server
   - Use primary server's IP address

## 🐳 Docker Deployment

### Using Docker Compose

1. **Create docker-compose.yml**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: vanta_ledger
      POSTGRES_USER: vanta_user
      POSTGRES_PASSWORD: vanta_password
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: .
    environment:
      - DATABASE_URL=postgresql://vanta_user:vanta_password@postgres/vanta_ledger
      - SECRET_KEY=your-secret-key
    depends_on:
      - postgres
    ports:
      - "8500:8500"
    volumes:
      - ./uploads:/app/uploads

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend

volumes:
  pgdata:
```

2. **Create Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8500

CMD ["python", "run_backend.py"]
```

3. **Deploy**
```bash
docker-compose up -d
```

## ☁️ Cloud Deployment

### AWS EC2

1. **Launch EC2 Instance**
   - Ubuntu 20.04 LTS
   - t3.medium or larger
   - Security group: allow ports 22, 80, 443, 8500

2. **Setup Instance**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib nginx

# Clone application
git clone <repository-url> /opt/vanta-ledger
cd /opt/vanta-ledger

# Setup application
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp env.example .env
# Edit .env for production
```

3. **Setup SSL with Let's Encrypt**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Google Cloud Platform

1. **Create VM Instance**
   - Ubuntu 20.04 LTS
   - e2-medium or larger
   - Allow HTTP/HTTPS traffic

2. **Deploy using Cloud Run**
```bash
# Build and push container
gcloud builds submit --tag gcr.io/PROJECT_ID/vanta-ledger
gcloud run deploy vanta-ledger --image gcr.io/PROJECT_ID/vanta-ledger --platform managed
```

## 🔒 Security Configuration

### Production Security Checklist

- [ ] Change default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall
- [ ] Regular backups
- [ ] Update dependencies
- [ ] Monitor logs
- [ ] Set up alerts

### Environment Variables for Production
```bash
# Security
SECRET_KEY=your-very-long-random-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Passwords
ADMIN_PASSWORD=secure-admin-password
AUNTIE_PASSWORD=secure-auntie-password

# Server
HOST=0.0.0.0
PORT=8500

# File uploads
MAX_FILE_SIZE=10485760
UPLOAD_DIR=uploads

# CORS
ALLOWED_ORIGINS=https://your-domain.com
```

## 📊 Monitoring & Maintenance

### Log Management
```bash
# View application logs
sudo journalctl -u vanta-ledger -f

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Database Backups
```bash
# Create backup
pg_dump vanta_ledger > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
psql vanta_ledger < backup_file.sql
```

### Automated Backups
```bash
# Create backup script
sudo tee /opt/vanta-ledger/backup.sh << EOF
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=\$(date +%Y%m%d_%H%M%S)
pg_dump vanta_ledger > \$BACKUP_DIR/vanta_ledger_\$DATE.sql
find \$BACKUP_DIR -name "*.sql" -mtime +7 -delete
EOF

# Make executable and add to cron
chmod +x /opt/vanta-ledger/backup.sh
crontab -e
# Add: 0 2 * * * /opt/vanta-ledger/backup.sh
```

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Error**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U vanta_user -d vanta_ledger
```

2. **Port Already in Use**
```bash
# Find process using port
sudo netstat -tlnp | grep :8500

# Kill process
sudo kill -9 <PID>
```

3. **Permission Errors**
```bash
# Fix file permissions
sudo chown -R $USER:$USER /opt/vanta-ledger
chmod +x /opt/vanta-ledger/run_backend.py
```

4. **Memory Issues**
```bash
# Check memory usage
free -h

# Restart service
sudo systemctl restart vanta-ledger
```

### Performance Optimization

1. **Database Optimization**
```sql
-- Create indexes
CREATE INDEX idx_projects_company_id ON projects(company_id);
CREATE INDEX idx_ledger_project_id ON ledger_entries(project_id);
CREATE INDEX idx_documents_company_id ON documents(company_id);
```

2. **Application Optimization**
```bash
# Increase worker processes
# Edit run_backend.py to use multiple workers
uvicorn.run(app, host="0.0.0.0", port=8500, workers=4)
```

## 📞 Support

For deployment issues:
1. Check logs: `sudo journalctl -u vanta-ledger -f`
2. Verify configuration: `python -c "from src.vanta_ledger.main import app; print('OK')"`
3. Test database: `python setup_initial_data.py`
4. Contact support team

---

**Remember**: Always backup your data before making changes! 