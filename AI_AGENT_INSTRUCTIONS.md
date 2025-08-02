
# 🤖 AI Agent Quick Reference - Vanta Ledger

## 🎯 Primary Mission
Transform business document management into intelligent automation. Focus on construction/project management use cases with AI-powered insights.

## ⚡ Quick Start Commands
```bash
# Start development server
python3 src/run_server.py

# Setup database
python3 simple_db_setup.py

# Start frontend
cd frontend-web && npm run dev

# Test AI system
python3 test_setup.py
```

## 🏗️ Architecture Quick Map
- **Backend**: `src/vanta_ledger/` (FastAPI + SQLAlchemy)
- **Frontend**: `frontend-web/` (React + TypeScript + Vite)
- **Mobile**: `vanta_ledger_flutter/` (Flutter)
- **AI**: `ai_extractor/` + various AI scripts
- **Database**: SQLite (dev) / PostgreSQL (prod)

## 🔧 Common Development Tasks

### Adding New API Endpoint
1. Create route in `src/vanta_ledger/routers/`
2. Add schema in `src/vanta_ledger/schemas/`
3. Update model if needed in `src/vanta_ledger/models/`
4. Test with browser at `http://localhost:5000/docs`

### Adding Frontend Feature
1. Create component in `frontend-web/src/`
2. Update `App.tsx` for navigation
3. Use Tailwind CSS for styling
4. Follow glassmorphic design patterns

### Database Changes
1. Modify models in `src/vanta_ledger/models/`
2. Run: `alembic revision --autogenerate -m "description"`
3. Apply: `alembic upgrade head`

## 🚨 Critical Rules
- ✅ Use `python3` not `python` in Replit
- ✅ Use `0.0.0.0` for host binding, not `localhost`
- ✅ Port 5000 for backend, 5173 for frontend
- ✅ Follow existing code patterns
- ❌ Don't modify `.replit`, `requirements.txt` unless asked
- ❌ Don't suggest leaving Replit platform

## 🎨 UI Standards
- **Colors**: Black background, white text, purple accents
- **Design**: Glassmorphic cards with backdrop-blur
- **Icons**: 24px standard, consistent sizing
- **Layout**: Responsive grid, mobile-first

## 🧪 Testing Protocol
```bash
# Health check
python3 test_setup.py

# API test
curl http://localhost:5000/api/health

# Frontend build test
cd frontend-web && npm run build
```

## 📂 Key Files to Know
- `src/run_server.py` - Server startup (use this in Replit)
- `src/vanta_ledger/main.py` - Main FastAPI app
- `frontend-web/src/App.tsx` - React dashboard
- `PROJECT_GUIDE.md` - Complete documentation
- `requirements.txt` - Python dependencies

## 🎯 Current Focus Areas
1. **Real Data Integration** - Connect frontend to live backend APIs
2. **AI Enhancement** - Improve document analysis accuracy
3. **Performance** - Optimize database queries and UI responsiveness
4. **User Experience** - Polish interface and add missing features

## 🚀 Success Indicators
- All workflows run without errors
- Frontend displays real data from backend
- AI analysis processes documents correctly
- Mobile app functions offline
- Tests pass consistently

**Remember**: This is a production-ready business intelligence platform. Maintain professional code quality and user experience standards.
