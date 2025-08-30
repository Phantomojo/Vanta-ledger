# 🔒 Vanta Ledger - Secure Setup Guide

## Security Overview

This application has been hardened to eliminate all hardcoded passwords and secrets. All authentication credentials must be provided via environment variables or secure prompts.

## 🚨 CRITICAL: No Hardcoded Secrets

✅ **All hardcoded passwords removed**
✅ **Environment variable-based configuration**
✅ **Secure password hashing (bcrypt)**
✅ **JWT token-based authentication**
✅ **Automated security scanning**

## 🔧 Initial Setup

### 1. Set Environment Variables

```bash
# Required Database Configuration
export POSTGRES_URI="postgresql://username:password@localhost:5432/vanta_ledger"
export MONGO_URI="mongodb://username:password@localhost:27017/vanta_ledger"
export REDIS_URI="redis://localhost:6379/0"

# Required Security Configuration
export SECRET_KEY="your-secret-key-here"  # Use openssl rand -base64 64

# Admin User Configuration (for initial setup)
export ADMIN_USERNAME="admin"
export ADMIN_EMAIL="admin@yourdomain.com"
export ADMIN_PASSWORD="your-secure-password-here"  # Min 8 characters
```

### 2. Create Secure Admin User

**Option A: Use the secure script**
```bash
python create_secure_admin.py
```

**Option B: Set environment variables and start the application**
```bash
# Application will create admin user on startup if ADMIN_PASSWORD is set
python -m uvicorn src.vanta_ledger.main:app --host 0.0.0.0 --port 8500
```

### 3. Clear Sensitive Environment Variables

After initial setup:
```bash
unset ADMIN_PASSWORD
```

## 🔐 Security Features

### Password Requirements
- Minimum 8 characters
- Bcrypt hashing with salt
- No password storage in plain text
- Secure password validation

### Authentication
- JWT tokens with expiration
- Token blacklisting for logout
- Role-based access control (RBAC)
- Secure session management

### Environment-Based Configuration
- No secrets in source code
- Environment variable validation
- Secure defaults in development
- Production-ready configuration

## 🚀 Application Startup

### Development Mode
```bash
# Start with debug logging
DEBUG=true python launch_vanta_ledger.py
```

### Production Mode
```bash
# Ensure all environment variables are set
DEBUG=false python launch_vanta_ledger.py
```

## 📋 Security Checklist

Before deployment, verify:

- [ ] All environment variables are set
- [ ] No hardcoded passwords in configuration files
- [ ] Admin password is secure (>12 characters, mixed case, numbers, symbols)
- [ ] Database connections use encrypted connections
- [ ] SECRET_KEY is cryptographically secure
- [ ] Debug mode is disabled in production
- [ ] Log files don't contain sensitive information

## 🔧 Login Credentials

### For Development/Testing

Use the secure admin creation script:
```bash
python create_secure_admin.py
```

This will:
1. Prompt for secure credentials (if not in environment)
2. Create database tables
3. Hash and store the password securely
4. Clear sensitive data from memory

### No Default Passwords

❌ **There are NO default passwords**
❌ **admin123 has been completely removed**
❌ **All credentials must be explicitly set**

## 🔍 Security Validation

Run security checks:
```bash
# Check for hardcoded secrets
grep -r "admin123\|password123\|secret.*=" src/ || echo "✅ No hardcoded secrets found"

# Validate configuration
python -c "from src.vanta_ledger.config import settings; settings.validate_required_config(); print('✅ Configuration valid')"
```

## 🆘 Troubleshooting

### Cannot Login
1. Verify admin user was created: Check application logs
2. Reset admin password: Use `create_secure_admin.py`
3. Check environment variables: Ensure `ADMIN_PASSWORD` was set during creation

### Database Connection Issues
1. Verify `POSTGRES_URI` is correct
2. Ensure PostgreSQL is running
3. Check database permissions

### Token Issues
1. Verify `SECRET_KEY` is set
2. Check token expiration settings
3. Clear browser localStorage

## 📞 Support

For security-related issues:
1. Check application logs
2. Verify environment variable configuration
3. Run the security validation script
4. Review this setup guide

---

**Remember: Security is only as strong as your weakest configuration. Always use secure, unique passwords and keep your environment variables protected.**
