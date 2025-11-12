# Application Entry Points Guide

Vanta Ledger has multiple entry points for different deployment scenarios. Choose the appropriate one based on your needs.

## 📋 Quick Decision Matrix

| Scenario | Use This Entry Point | File |
|----------|---------------------|------|
| **Production (Full Features)** | `main.py` | `src/vanta_ledger/main.py` |
| **Production (Simplified)** | `simple_main.py` | `src/vanta_ledger/simple_main.py` |
| **Testing/Development** | `main_simple.py` | `src/vanta_ledger/main_simple.py` |
| **Docker Deployment** | `main.py` (default) | Referenced in `Dockerfile` |

---

## 🚀 main.py - Full Production Application

**Recommended for**: Production deployments with full features

### Features
- ✅ All routes and endpoints
- ✅ Multi-database support (PostgreSQL, MongoDB, Redis)
- ✅ AI-powered document processing
- ✅ Local LLM integration
- ✅ Advanced analytics and reporting
- ✅ Comprehensive security and monitoring
- ✅ Full middleware stack
- ✅ Prometheus metrics

### Requirements
- PostgreSQL database
- MongoDB (for document storage)
- Redis (for caching and sessions)
- All environment variables configured

### Start Command
```bash
# Via uvicorn
uvicorn src.vanta_ledger.main:app --host 0.0.0.0 --port 8500 --workers 4

# Via Docker
docker-compose up

# Via launcher script
python scripts/deployment/launch_vanta_ledger.py
```

### Environment Variables
```env
POSTGRES_URI=postgresql://user:pass@localhost:5432/vanta_ledger
MONGO_URI=mongodb://localhost:27017/vanta_ledger
REDIS_URI=redis://localhost:6379/0
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-api-key (optional)
```

### When to Use
- Production deployments
- Full feature set needed
- Have all infrastructure available
- AI features required
- High-traffic applications

---

## 🎯 simple_main.py - Simplified Production

**Recommended for**: Production with limited infrastructure

### Features
- ✅ Core functionality
- ✅ Single PostgreSQL database
- ✅ Authentication and authorization
- ✅ Basic monitoring
- ✅ Production security
- ❌ No MongoDB
- ❌ No Redis caching
- ❌ No AI features
- ❌ Simplified monitoring

### Requirements
- PostgreSQL database only
- Basic environment variables

### Start Command
```bash
uvicorn src.vanta_ledger.simple_main:app --host 0.0.0.0 --port 8500
```

### Environment Variables
```env
POSTGRES_URI=postgresql://user:pass@localhost:5432/vanta_ledger
SECRET_KEY=your-secret-key
```

### When to Use
- Limited infrastructure
- Don't need AI features
- Simpler deployment
- Cost-conscious deployments
- Getting started quickly

---

## 🧪 main_simple.py - Testing/Development

**Recommended for**: Development and testing only

### Features
- ✅ Minimal dependencies
- ✅ Fast startup
- ✅ Basic CORS
- ✅ Simple routing
- ❌ No database connections
- ❌ No authentication
- ❌ No production features
- ⚠️ **NOT FOR PRODUCTION**

### Requirements
- Python 3.8+
- No database needed

### Start Command
```bash
# Development mode with auto-reload
uvicorn src.vanta_ledger.main_simple:app --reload

# Testing
pytest tests/ --backend=main_simple
```

### Environment Variables
```env
# Minimal or none required
DEBUG=True
```

### When to Use
- Local development
- Quick testing
- CI/CD smoke tests
- Verifying installation
- Learning the codebase

---

## 🐳 Docker Deployment

The `Dockerfile` references `main.py` by default:

```dockerfile
CMD ["uvicorn", "src.vanta_ledger.main:app", "--host", "0.0.0.0", "--port", "8500"]
```

### Using Different Entry Point in Docker
To use a different entry point, override the CMD:

```bash
# Use simplified version
docker run vanta-ledger uvicorn src.vanta_ledger.simple_main:app --host 0.0.0.0 --port 8500

# Or modify docker-compose.yml
services:
  backend:
    command: uvicorn src.vanta_ledger.simple_main:app --host 0.0.0.0 --port 8500
```

---

## 🔄 Migration Path

### From Testing to Production
```bash
# 1. Start with testing version
uvicorn src.vanta_ledger.main_simple:app --reload

# 2. Move to simplified production
uvicorn src.vanta_ledger.simple_main:app

# 3. Upgrade to full production
uvicorn src.vanta_ledger.main:app
```

### From Simplified to Full Production
```bash
# 1. Set up MongoDB and Redis
docker-compose up mongodb redis

# 2. Update environment variables
export MONGO_URI=mongodb://localhost:27017/vanta_ledger
export REDIS_URI=redis://localhost:6379/0

# 3. Start full application
uvicorn src.vanta_ledger.main:app
```

---

## 🛠️ Development Workflow

### Recommended Development Setup

```bash
# Terminal 1: Run backend with auto-reload
uvicorn src.vanta_ledger.main_simple:app --reload --port 8500

# Terminal 2: Run frontend
cd frontend/frontend-web
npm run dev

# Terminal 3: Run tests
pytest tests/ --watch
```

### Production Deployment Checklist

- [ ] All environment variables configured
- [ ] Database services running and accessible
- [ ] Secrets properly secured (not in code)
- [ ] Using `main.py` or `simple_main.py` (NOT `main_simple.py`)
- [ ] Workers configured appropriately
- [ ] HTTPS/TLS configured
- [ ] Monitoring and logging set up
- [ ] Backup strategy in place

---

## 🔧 Troubleshooting

### "Module not found" errors
```bash
# Ensure you're in the right directory
cd /path/to/Vanta-ledger

# Activate virtual environment
source venv/bin/activate  # or: .\venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### Database connection errors
```bash
# Check if databases are running
docker ps | grep -E '(postgres|mongo|redis)'

# Test connections
python -c "import psycopg2; print('PostgreSQL: OK')"
python -c "import pymongo; print('MongoDB: OK')"
python -c "import redis; print('Redis: OK')"
```

### Wrong entry point in Docker
```bash
# Check Dockerfile
cat Dockerfile | grep CMD

# Override in docker-compose.yml
services:
  backend:
    command: uvicorn src.vanta_ledger.main:app --host 0.0.0.0 --port 8500
```

---

## 📚 Additional Resources

- **Main README**: `README.md` - Project overview
- **Development Guide**: `DEVELOPMENT.md` - Development setup
- **Deployment Guide**: `DEPLOYMENT.md` - Production deployment
- **API Documentation**: http://localhost:8500/docs (when running)

---

## ❓ Which Entry Point Should I Use?

**Choose based on your answers:**

1. **Is this for production?**
   - No → Use `main_simple.py`
   - Yes → Continue to #2

2. **Do you have MongoDB and Redis available?**
   - No → Use `simple_main.py`
   - Yes → Continue to #3

3. **Do you need AI features?**
   - No → Use `simple_main.py`
   - Yes → Use `main.py`

**Still unsure?** Start with `simple_main.py` and upgrade to `main.py` when you need more features.
