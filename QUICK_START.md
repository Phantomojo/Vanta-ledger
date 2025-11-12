# 🚀 Quick Start Guide - Vanta Ledger

Get Vanta Ledger up and running in **under 10 minutes** with this quick start guide.

---

## 📋 Prerequisites

Before you begin, make sure you have:

- **Python 3.11+** installed ([Download](https://python.org/downloads/))
- **Node.js 18+** and npm ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/))
- **Docker & Docker Compose** (optional, for full stack) ([Download](https://docker.com/))

**System Requirements:**
- **RAM**: 4GB minimum (8GB recommended for AI features)
- **Storage**: 5GB free space
- **OS**: Linux, macOS, or Windows (with WSL2)

---

## 🎯 Option 1: Quick Test (No Database) - 5 minutes

Perfect for exploring the API without setting up databases.

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/Phantomojo/Vanta-ledger.git
cd Vanta-ledger

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install base dependencies (fast - only core packages)
pip install -r requirements/base.txt
```

### Step 2: Start the Backend

```bash
# Start the minimal test server (no databases required)
python -m uvicorn src.vanta_ledger.main_simple:app --reload --port 8500
```

### Step 3: Access the Application

- **API Docs**: http://localhost:8500/docs
- **Alternative Docs**: http://localhost:8500/redoc

**You're done!** The API is now running in test mode. Explore the interactive documentation.

---

## 🐳 Option 2: Docker (Full Stack) - 10 minutes

Complete production-like environment with all databases and features.

### Step 1: Clone the Repository

```bash
git clone https://github.com/Phantomojo/Vanta-ledger.git
cd Vanta-ledger
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and set these required values:
# POSTGRES_PASSWORD=your_secure_password
# MONGO_INITDB_ROOT_PASSWORD=your_secure_password
# SECRET_KEY=your_secret_key_min_32_chars
```

**Quick setup** (for testing):
```bash
# Auto-generate secure values
cat > .env << 'EOF'
POSTGRES_DB=vanta_ledger
POSTGRES_USER=vanta_user
POSTGRES_PASSWORD=test_password_change_in_prod
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=test_password_change_in_prod
SECRET_KEY=test-secret-key-change-in-production-min-32-chars
DEBUG=True
ENVIRONMENT=development
EOF
```

### Step 3: Start All Services

```bash
# Start PostgreSQL, MongoDB, Redis, Backend, and Frontend
docker-compose up -d

# Check status
docker-compose ps
```

### Step 4: Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8500
- **API Docs**: http://localhost:8500/docs

**You're done!** Full stack is running.

---

## 💻 Option 3: Local Development (Recommended) - 10 minutes

Best for development with hot-reload and debugging.

### Step 1: Clone and Setup Backend

```bash
# Clone the repository
git clone https://github.com/Phantomojo/Vanta-ledger.git
cd Vanta-ledger

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install production dependencies
pip install -r requirements/prod.txt
```

### Step 2: Setup Databases

**Option A: Using Docker (Recommended)**
```bash
# Start only database services
docker-compose up -d postgres mongodb redis
```

**Option B: Install Locally**
```bash
# Install PostgreSQL, MongoDB, and Redis
# Ubuntu/Debian:
sudo apt install postgresql mongodb redis-server

# macOS:
brew install postgresql mongodb-community redis

# Windows: Download installers from official websites
```

### Step 3: Configure Environment

```bash
cp .env.example .env

# Edit .env with your database credentials
# For Docker databases, defaults work fine:
cat > .env << 'EOF'
POSTGRES_URI=postgresql://vanta_user:password@localhost:5432/vanta_ledger
MONGO_URI=mongodb://admin:password@localhost:27017/vanta_ledger?authSource=admin
REDIS_URI=redis://localhost:6379/0
SECRET_KEY=your-secret-key-change-in-production-min-32-characters
DEBUG=True
EOF
```

### Step 4: Initialize Database

```bash
# Run database initialization
python scripts/setup/create_initial_admin.py

# Or initialize manually
python -c "
from src.vanta_ledger.database import engine, Base
Base.metadata.create_all(bind=engine)
print('✅ Database initialized!')
"
```

### Step 5: Start Backend

```bash
# Option A: Using the startup script
python scripts/deployment/start_backend.py

# Option B: Direct uvicorn
python -m uvicorn src.vanta_ledger.main:app --reload --port 8500
```

### Step 6: Start Frontend (Optional)

```bash
# In a new terminal
cd frontend/frontend-web

# Install dependencies
npm install

# Start development server
npm run dev
```

### Step 7: Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8500
- **API Docs**: http://localhost:8500/docs

**You're done!** Development environment is ready.

---

## 🧪 Verify Installation

Test your setup with these quick checks:

```bash
# Test backend health
curl http://localhost:8500/

# Expected response:
# {"message":"Vanta Ledger API is running","version":"2.0.0"}

# Test API documentation
curl http://localhost:8500/docs
# Should return HTML of the Swagger UI
```

---

## 🎓 What's Next?

### 1. **Create Your First User**

```bash
# Run the admin creation script
python scripts/setup/create_admin_user.py
```

Or via API:
```bash
curl -X POST http://localhost:8500/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "SecurePass123!",
    "role": "admin"
  }'
```

### 2. **Explore the API**

Visit http://localhost:8500/docs to see:
- 17+ API endpoint groups
- Interactive testing interface
- Full documentation
- Authentication flows

### 3. **Read the Documentation**

- **Entry Points Guide**: [ENTRY_POINTS_GUIDE.md](ENTRY_POINTS_GUIDE.md) - Which main.py to use
- **Architecture**: [CODEBASE_REVIEW_RECOMMENDATIONS.md](CODEBASE_REVIEW_RECOMMENDATIONS.md)
- **Security**: [.github/SECURITY.md](.github/SECURITY.md)

---

## 🛠️ Troubleshooting

### Backend won't start

**Problem**: Import errors or missing dependencies
```bash
# Solution: Reinstall dependencies
pip install --upgrade -r requirements/prod.txt
```

### Database connection errors

**Problem**: Can't connect to PostgreSQL/MongoDB/Redis
```bash
# Check if Docker containers are running
docker-compose ps

# Restart databases
docker-compose restart postgres mongodb redis

# Check logs
docker-compose logs postgres
```

### Port already in use

**Problem**: Port 8500 or 5173 already taken
```bash
# Solution: Use different ports
uvicorn src.vanta_ledger.main:app --port 8501

# Or kill the process using the port
# Linux/Mac:
lsof -ti:8500 | xargs kill -9

# Windows:
netstat -ano | findstr :8500
taskkill /PID <PID> /F
```

### Frontend build errors

**Problem**: npm install fails
```bash
# Clear cache and reinstall
cd frontend/frontend-web
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

---

## 📊 Different Entry Points

Vanta Ledger has 3 entry points for different scenarios:

### 1. **Full Production** (`main.py`)
```bash
# All features: PostgreSQL + MongoDB + Redis + AI
python -m uvicorn src.vanta_ledger.main:app --port 8500
```
**Use when**: Running in production with all features

### 2. **Simplified Production** (`simple_main.py`)
```bash
# PostgreSQL only, no MongoDB/Redis
python -m uvicorn src.vanta_ledger.simple_main:app --port 8500
```
**Use when**: Limited infrastructure, cost-effective deployment

### 3. **Testing** (`main_simple.py`)
```bash
# No databases required
python -m uvicorn src.vanta_ledger.main_simple:app --port 8500
```
**Use when**: Quick testing, CI/CD, learning the API

See [ENTRY_POINTS_GUIDE.md](ENTRY_POINTS_GUIDE.md) for details.

---

## 🚀 Quick Commands Cheat Sheet

```bash
# Start everything with Docker
docker-compose up -d

# Start backend only (with databases)
python scripts/deployment/start_backend.py

# Start frontend only
cd frontend/frontend-web && npm run dev

# Run tests
pytest tests/ -v

# Stop everything
docker-compose down

# View logs
docker-compose logs -f backend

# Reset databases
docker-compose down -v  # Warning: deletes all data!
docker-compose up -d
```

---

## 💡 Pro Tips

1. **Use Docker for databases**: Easiest way to get started without manual DB installation
2. **Start with minimal setup**: Test with `main_simple.py` first, then upgrade
3. **Check the logs**: `docker-compose logs -f` shows what's happening
4. **Use environment variables**: Never commit secrets to `.env` file
5. **Read ENTRY_POINTS_GUIDE.md**: Understand which main file to use

---

## 🆘 Need Help?

- **Documentation**: Check the `/docs` folder and markdown files in root
- **API Docs**: http://localhost:8500/docs (interactive)
- **Issues**: Open an issue on GitHub
- **Security**: See [.github/SECURITY.md](.github/SECURITY.md) for vulnerability reporting

---

## 🎉 Success!

If you see this, you're all set:
- ✅ Backend running at http://localhost:8500
- ✅ API docs at http://localhost:8500/docs
- ✅ Frontend at http://localhost:5173 (if started)

**Happy coding!** 🚀

---

**Version**: 2.0.0  
**Last Updated**: November 12, 2025  
**Status**: Production Ready
