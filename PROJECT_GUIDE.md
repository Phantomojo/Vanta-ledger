
# 🚀 Vanta Ledger - Complete Project Guide

## 🎯 Mission & Vision

### **Core Mission**
Transform document management and financial operations into intelligent, actionable business insights through AI-powered automation and modern interfaces.

### **Ultimate Vision**
Create the "mission control" for business operations—combining NASA-grade data analysis, AI automation, and consumer-app usability into a unified platform that turns document archives and financial data into real-time business intelligence.

### **Target Users**
- Construction companies and contractors
- Small to medium businesses with heavy document workflows
- Financial analysts and project managers
- Anyone needing intelligent document processing and project tracking

---

## 🏗️ System Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │   Backend API   │    │  Paperless-ngx  │
│   (React/Vite)  │◄──►│   (FastAPI)     │◄──►│ (Doc Management)│
│   Port: 5173    │    │   Port: 5000    │    │   Port: 8000    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Mobile App    │    │   AI/NLP Svc    │    │   PostgreSQL    │
│   (Flutter)     │    │   (FastAPI)     │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Core Components**
1. **Backend API** - FastAPI with SQLAlchemy (main business logic)
2. **Web Frontend** - React/TypeScript with Vite (admin dashboard)
3. **Mobile App** - Flutter (offline-first finance management)
4. **AI/NLP Service** - Document analysis and risk scoring
5. **Document Management** - Paperless-ngx integration
6. **Database** - PostgreSQL/SQLite for data persistence

---

## 🛠️ Development Environment Setup

### **Prerequisites**
- Python 3.8+
- Node.js 16+
- Flutter SDK (for mobile development)
- Git

### **Quick Start Commands**
```bash
# 1. Start Backend API
python3 src/run_server.py

# 2. Start Web Frontend
cd frontend-web && npm install && npm run dev

# 3. Setup Database (if needed)
python3 simple_db_setup.py

# 4. Test AI System
python3 test_setup.py
```

### **Environment Variables**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/vanta_ledger
PAPERLESS_URL=http://localhost:8000
PAPERLESS_USERNAME=your_username
PAPERLESS_PASSWORD=your_password
AI_SERVICE_URL=http://localhost:8600
```

---

## 📁 Codebase Structure & File Organization

### **Main Directories**
```
Vanta-ledger/
├── src/vanta_ledger/          # Backend API (FastAPI)
├── frontend-web/              # Web Dashboard (React/TypeScript)
├── vanta_ledger_flutter/      # Mobile App (Flutter)
├── frontend/                  # Legacy Kivy App (being phased out)
├── docs/                      # Documentation and specifications
├── ai_extractor/              # AI/NLP microservice
└── scripts/                   # Utility and setup scripts
```

### **Key Files to Know**
- `src/vanta_ledger/main.py` - Main FastAPI application
- `src/run_server.py` - Server startup script for Replit
- `frontend-web/src/App.tsx` - Main React dashboard
- `backend_api.py` - Alternative Flask API (for development)
- `integrate_backend_data.py` - Data integration engine
- `requirements.txt` - Python dependencies

---

## 🔧 Development Workflow

### **1. Making Backend Changes**
```bash
# Edit files in src/vanta_ledger/
# Test changes:
cd src && python3 -m vanta_ledger.main
# Or use the simpler runner:
python3 src/run_server.py
```

### **2. Making Frontend Changes**
```bash
# Edit files in frontend-web/src/
cd frontend-web
npm run dev  # Hot reload enabled
```

### **3. Database Changes**
```bash
# Generate migration:
alembic revision --autogenerate -m "description"
# Apply migration:
alembic upgrade head
```

### **4. Adding New Features**
1. Backend: Add models in `models/`, schemas in `schemas/`, routes in `routers/`
2. Frontend: Add components in `src/`, update `App.tsx` for navigation
3. Database: Update models, create migrations
4. Testing: Add tests, verify integration

---

## 🚦 Current Project Status

### **✅ Completed Features**
- ✅ FastAPI backend with comprehensive models
- ✅ React web dashboard with modern UI
- ✅ Flutter mobile app (complete financial management)
- ✅ AI document processing and analysis
- ✅ Paperless-ngx integration
- ✅ Database schemas and migrations
- ✅ Real-time data synchronization
- ✅ Project tracking and analytics

### **🔄 In Progress**
- 🔄 Advanced AI insights and recommendations
- 🔄 Real-time notifications system
- 🔄 Multi-user authentication and permissions
- 🔄 Performance optimizations

### **📋 Next Priorities**
1. **Backend API Integration** - Connect all frontend panels to real endpoints
2. **Real Data Wiring** - Replace mock data with live database queries
3. **Advanced AI Automation** - Implement workflow triggers and smart alerts
4. **User Testing** - Real-world testing with construction business use cases
5. **Documentation** - Complete API docs and user guides

---

## 🎨 UI/UX Design Guidelines

### **Design Language**
- **Inspiration**: Notion (command center), MPesa (professional finance), Instagram (timeline)
- **Color Scheme**: High-contrast black/white with purple accent colors
- **Typography**: Clean, modern fonts with excellent readability
- **Animations**: Subtle micro-interactions and smooth transitions

### **Component Standards**
- **Cards**: Glassmorphic design with backdrop blur
- **Icons**: Consistent sizing (24px standard, 32px for primary actions)
- **Spacing**: 8px grid system for consistent layouts
- **Responsive**: Mobile-first design approach

### **Code Style**
```tsx
// React Component Example
const FeatureCard: React.FC<Props> = ({ title, value, icon }) => (
  <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
    <div className="flex items-center justify-between">
      <span className="text-sm text-gray-300">{title}</span>
      <Icon className="w-6 h-6 text-purple-400" />
    </div>
    <p className="text-2xl font-bold text-white mt-2">{value}</p>
  </div>
);
```

---

## 🧪 Testing Strategy

### **Testing Levels**
1. **Unit Tests**: Individual functions and components
2. **Integration Tests**: API endpoints and database operations
3. **E2E Tests**: Complete user workflows
4. **Performance Tests**: Load testing and optimization

### **Test Commands**
```bash
# Backend tests
cd src && python -m pytest

# Frontend tests
cd frontend-web && npm test

# Mobile tests
cd vanta_ledger_flutter && flutter test
```

---

## 🚀 Deployment & Production

### **Replit Deployment**
- **Main Application**: Runs on Replit with automatic deployments
- **Environment**: Nix-based with automatic dependency management
- **Database**: PostgreSQL for production, SQLite for development
- **Static Assets**: Served via Vite build system

### **Production Checklist**
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates configured
- [ ] Performance monitoring enabled
- [ ] Backup strategies implemented
- [ ] Error logging configured

---

## 🔍 AI & Machine Learning Features

### **Current AI Capabilities**
- **Document Classification**: Invoices, contracts, receipts, proposals
- **Financial Data Extraction**: Amounts, dates, vendor information
- **Risk Analysis**: Multi-factor risk scoring for documents
- **Entity Recognition**: Companies, people, locations, project codes
- **Semantic Search**: Natural language document queries

### **AI Development Guidelines**
```python
# AI Processing Example
class DocumentAI:
    def analyze_document(self, document_content: str) -> Dict:
        return {
            'classification': self.classify_document(document_content),
            'extracted_data': self.extract_financial_data(document_content),
            'risk_score': self.calculate_risk_score(document_content),
            'insights': self.generate_insights(document_content)
        }
```

---

## 📚 API Documentation

### **Core Endpoints**
```python
# Main API Routes
GET  /api/dashboard          # Dashboard analytics
GET  /api/documents          # Document listing with pagination
POST /api/documents          # Create new document
GET  /api/projects           # Project management
GET  /api/analytics          # Business intelligence data
POST /api/ai/analyze         # AI document analysis
GET  /api/health             # System health check
```

### **Authentication**
- **Current**: Basic authentication for development
- **Planned**: JWT tokens with role-based access control

---

## 🐛 Troubleshooting Guide

### **Common Issues**

1. **Backend won't start**
   ```bash
   # Check Python version
   python3 --version
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Check database connection
   python3 test_setup.py
   ```

2. **Frontend compilation errors**
   ```bash
   # Clear node modules
   rm -rf node_modules package-lock.json
   npm install
   
   # Check TypeScript errors
   npm run type-check
   ```

3. **Database connection issues**
   ```bash
   # Reset database
   python3 simple_db_setup.py
   
   # Check migrations
   alembic current
   alembic upgrade head
   ```

### **Debug Commands**
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Check system health
python3 -c "from src.vanta_ledger.main import app; print('Backend OK')"

# Test AI integration
python3 test_ollama_integration.py
```

---

## 🤝 Contributing Guidelines

### **Code Standards**
- **Python**: Follow PEP 8, use type hints, document functions
- **TypeScript**: Use strict mode, prefer functional components
- **Flutter**: Follow Dart style guide, use proper state management

### **Commit Message Format**
```
feat: add new dashboard analytics panel
fix: resolve document upload validation error
docs: update API documentation
refactor: improve database query performance
test: add unit tests for AI processing
```

### **Pull Request Process**
1. Create feature branch from `main`
2. Implement changes with tests
3. Update documentation if needed
4. Submit PR with clear description
5. Address review feedback
6. Merge after approval

---

## 📞 Support & Resources

### **Getting Help**
1. **Documentation**: Check this guide and `docs/` folder
2. **Logs**: Review console output and error messages
3. **Health Checks**: Run `python3 test_setup.py`
4. **Community**: Create GitHub issues for bugs/features

### **Useful Resources**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Flutter Documentation](https://flutter.dev/)
- [Paperless-ngx API](https://docs.paperless-ngx.com/)

---

## 🎯 Success Metrics

### **Technical KPIs**
- **Document Processing**: < 2 seconds per document
- **AI Accuracy**: > 95% for financial data extraction
- **API Response Time**: < 500ms for standard queries
- **Uptime**: > 99.5% availability

### **Business KPIs**
- **User Engagement**: Daily active usage
- **Efficiency Gains**: Time saved in document processing
- **Accuracy Improvements**: Reduction in manual errors
- **ROI**: Cost savings vs. implementation cost

---

**🚀 Ready to build the future of business intelligence!**

This guide serves as the complete roadmap for developing, maintaining, and extending the Vanta Ledger platform. Whether you're a new developer joining the project or an AI agent helping with development, this document provides everything needed to understand and contribute to the system effectively.
