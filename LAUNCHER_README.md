# 🚀 Vanta Ledger - Single Launcher Guide

## Quick Start (One Command!)

### Option 1: Python Launcher (Recommended)
```bash
cd /home/phantomojo/Vanta-ledger
python launch_vanta_ledger.py
```

### Option 2: Bash Script
```bash
cd /home/phantomojo/Vanta-ledger
./start_vanta.sh
```

## What the Launcher Does

The single launcher automatically:

1. **🔧 Environment Setup**
   - Sets all required environment variables
   - Configures database connections
   - Sets API keys and secrets

2. **🧪 Pre-flight Checks**
   - Tests backend import functionality
   - Verifies virtual environment exists
   - Checks frontend dependencies

3. **📦 Dependency Management**
   - Installs frontend dependencies if needed
   - Ensures all packages are ready

4. **🔥 Backend Startup**
   - Starts FastAPI server on http://localhost:8500
   - Enables hot reload for development
   - Provides API documentation at /docs

5. **🎨 Frontend Startup**
   - Starts React development server on http://localhost:5173
   - Enables hot module replacement
   - Connects to backend automatically

6. **🌍 Browser Integration**
   - Automatically opens your default browser
   - Navigates to the frontend dashboard

7. **📊 Service Monitoring**
   - Monitors both processes
   - Provides status updates
   - Handles graceful shutdown

## Access Points

Once launched, you can access:

- **🎨 Frontend Dashboard:** http://localhost:5173
- **📡 Backend API:** http://localhost:8500
- **📚 API Documentation:** http://localhost:8500/docs
- **🔍 API Health Check:** http://localhost:8500/health

## Features Available

### Backend (http://localhost:8500)
- ✅ **Authentication** - JWT-based login/logout
- ✅ **Document Management** - Upload, analyze, categorize
- ✅ **Financial Management** - GL, AP/AR, invoicing
- ✅ **Company Management** - Multi-tenant support
- ✅ **Project Management** - Task and resource tracking
- ✅ **AI Analytics** - Document processing insights
- ✅ **Security** - Enterprise-grade protection
- ✅ **Database Integration** - MongoDB + PostgreSQL + Redis

### Frontend (http://localhost:5173)
- ✅ **Modern Dashboard** - Real-time data visualization
- ✅ **Document Library** - File management interface
- ✅ **Financial Views** - Ledger, accounts, reporting
- ✅ **Analytics Pages** - Business intelligence
- ✅ **User Management** - Role-based access control
- ✅ **Settings** - Configuration management
- ✅ **Responsive Design** - Mobile and desktop friendly

## Stopping the Services

Press `Ctrl+C` in the terminal where the launcher is running. This will:
- Gracefully shut down both backend and frontend
- Clean up all processes
- Display confirmation messages

## Troubleshooting

### Backend Won't Start
```bash
# Check if virtual environment is activated
source .venv/bin/activate

# Test backend manually
python -c "from src.vanta_ledger.main import app; print('OK')"
```

### Frontend Won't Start
```bash
# Check if Node.js is installed
node --version
npm --version

# Install dependencies manually
cd frontend/frontend-web
npm install
```

### Port Conflicts
If ports 8500 or 5173 are already in use:
- Stop other services using these ports
- Or modify the ports in the launcher script

## Development Notes

- **Hot Reload:** Both backend and frontend support automatic reloading
- **Environment:** All environment variables are set automatically
- **Security:** Development mode with debug enabled
- **Databases:** Connects to local MongoDB, PostgreSQL, and Redis
- **AI Features:** GitHub Models integration (optional)

## Production Deployment

For production, use separate deployment scripts:
- Backend: Use gunicorn or similar WSGI server
- Frontend: Build with `npm run build` and serve statically
- Environment: Use production environment variables
- Security: Enable HTTPS and proper CORS settings

