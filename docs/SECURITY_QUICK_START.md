# Vanta Ledger Security Quick Start Guide

## Overview

This guide provides quick instructions for deploying and using the security-enhanced Vanta Ledger system.

## 🚀 Quick Deployment

### 1. Prerequisites
- Python 3.8+
- PostgreSQL
- MongoDB
- Redis
- Node.js (for frontend)

### 2. Environment Setup
Create a `.env` file in the project root:

```bash
# Security (REQUIRED - Generate a strong 64+ character key)
SECRET_KEY=your-very-long-and-very-random-secret-key-here-minimum-64-characters

# Database Connections
MONGO_URI=mongodb://user:password@localhost:27017/vanta_ledger
POSTGRES_URI=postgresql://user:password@localhost:5432/vanta_ledger
REDIS_URI=redis://localhost:6379/0

# Security Settings
DEBUG=False
ENABLE_HSTS=True
ENABLE_CSP=True
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
LOGIN_RATE_LIMIT_PER_MINUTE=5
```

### 3. Generate Secure Secret Key
```bash
# Generate a secure 64-character secret key
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

### 4. Deploy with Security
```bash
# Run the secure deployment script
./scripts/deploy_with_security.sh
```

## 🔐 Authentication

### Login
```bash
curl -X POST http://localhost:8500/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### Using the Token
```bash
# Get token from login response
TOKEN="your-jwt-token-here"

# Use token for authenticated requests
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8500/companies/
```

### Logout
```bash
curl -X POST http://localhost:8500/auth/logout \
  -H "Authorization: Bearer $TOKEN"
```

## 📁 Secure File Upload

### Upload a Document
```bash
curl -X POST http://localhost:8500/upload/documents \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@document.pdf"
```

**Security Features:**
- ✅ MIME type validation
- ✅ File extension validation
- ✅ Secure filename generation
- ✅ Path traversal prevention
- ✅ File size limits
- ✅ Malicious file detection

## 🛡️ Security Features

### 1. Input Validation
All inputs are automatically validated and sanitized:

```python
# Example: Company ID validation
company_id = input_validator.validate_integer(company_id, min_value=1)

# Example: String validation
username = input_validator.validate_string(username, min_length=3, max_length=50)

# Example: Email validation
email = input_validator.validate_email(email)
```

### 2. SQL Injection Prevention
All database queries use parameterized queries:

```python
# ✅ Secure (parameterized)
cursor.execute("SELECT * FROM companies WHERE id = %s", (company_id,))

# ❌ Insecure (string formatting)
cursor.execute(f"SELECT * FROM companies WHERE id = {company_id}")
```

### 3. XSS Prevention
All user inputs are sanitized to prevent XSS attacks:

```python
# Automatically blocks:
# <script>alert('xss')</script>
# <img src=x onerror=alert('xss')>
# javascript:alert('xss')
```

### 4. Rate Limiting
- **General API**: 100 requests per minute
- **Login**: 5 attempts per minute
- **File Uploads**: 10 per minute

### 5. Security Headers
All responses include security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`
- `Content-Security-Policy: default-src 'self'`

## 🧪 Testing Security

### Run Security Tests
```bash
cd backend
source venv/bin/activate
python -m pytest tests/test_security.py -v
```

### Test Coverage
- ✅ Authentication security
- ✅ Input validation
- ✅ SQL injection prevention
- ✅ File upload security
- ✅ XSS prevention
- ✅ Rate limiting
- ✅ Security headers

## 🔍 Security Monitoring

### Check Security Status
```bash
# Health check with security info
curl http://localhost:8500/health

# Check security headers
curl -I http://localhost:8500/health

# Test rate limiting
for i in {1..15}; do curl http://localhost:8500/health; done
```

### Logs
Security events are logged to:
- `backend/logs/app.log`
- Console output
- Structured JSON format

## 🚨 Security Incidents

### Common Issues

#### 1. "Invalid token" errors
- Check if token is expired
- Verify token format
- Check if token was blacklisted

#### 2. "Rate limit exceeded" errors
- Wait for rate limit to reset
- Reduce request frequency
- Check rate limit headers

#### 3. "File type not allowed" errors
- Check file extension
- Verify MIME type
- Ensure file is not corrupted

#### 4. "Input validation failed" errors
- Check input format
- Verify length limits
- Remove special characters if needed

### Emergency Response
```bash
# Stop the application
pkill -f uvicorn

# Check logs for security events
tail -f backend/logs/app.log | grep -i "security\|error\|warning"

# Restart with security checks
./scripts/deploy_with_security.sh
```

## 📋 Security Checklist

### Before Production
- [ ] Set strong SECRET_KEY (64+ characters)
- [ ] Configure secure database connections
- [ ] Enable HTTPS
- [ ] Set DEBUG=False
- [ ] Configure proper logging
- [ ] Set up monitoring
- [ ] Run security tests
- [ ] Review security headers
- [ ] Test rate limiting
- [ ] Verify file upload security

### Regular Maintenance
- [ ] Update dependencies monthly
- [ ] Review security logs weekly
- [ ] Run security tests after updates
- [ ] Monitor for suspicious activity
- [ ] Backup security configurations
- [ ] Review access logs

## 🔧 Configuration Options

### Security Settings
```python
# JWT Settings
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password Policy
MIN_PASSWORD_LENGTH = 8
REQUIRE_SPECIAL_CHARS = True
REQUIRE_NUMBERS = True
REQUIRE_UPPERCASE = True

# Rate Limiting
RATE_LIMIT_PER_MINUTE = 100
LOGIN_RATE_LIMIT_PER_MINUTE = 5

# File Security
MAX_FILE_SIZE = 10485760  # 10MB
ALLOWED_FILE_EXTENSIONS = [".pdf", ".docx", ".doc", ".txt", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"]
```

## 📞 Support

### Security Issues
For security-related issues:
1. Check the logs: `backend/logs/app.log`
2. Run security tests: `python -m pytest tests/test_security.py`
3. Review configuration: `backend/app/config.py`
4. Check deployment script: `scripts/deploy_with_security.sh`

### Documentation
- [Security Enhancement Summary](SECURITY_ENHANCEMENT_SUMMARY.md)
- [API Documentation](http://localhost:8500/docs)
- [Test Suite](tests/test_security.py)

---

**⚠️ Security Note**: This system implements enterprise-grade security measures. Always keep dependencies updated and monitor for security advisories. 