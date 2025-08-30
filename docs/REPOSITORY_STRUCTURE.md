# 📁 Vanta Ledger Repository Structure

## 🎯 Overview

This document provides a comprehensive guide to the Vanta Ledger repository structure. The repository has been organized into logical directories that separate concerns and make it easy for developers to navigate and contribute.

## 🏗️ Directory Structure

```
vanta-ledger/
├── README.md                    # Main project documentation
├── LICENSE                      # MIT License
│
├── backend/                     # Backend Application
│   ├── src/vanta_ledger/       # Main application source code
│   │   ├── __init__.py         # Package initialization
│   │   ├── main.py             # FastAPI application entry point
│   │   ├── config.py           # Application configuration
│   │   ├── database.py         # Database connections
│   │   ├── auth.py             # Authentication logic
│   │   ├── middleware.py       # FastAPI middleware
│   │   ├── startup.py          # Application startup logic
│   │   ├── routes/             # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── auth.py         # Authentication routes
│   │   │   ├── companies.py    # Company management
│   │   │   ├── documents.py    # Document processing
│   │   │   ├── financial.py    # Financial operations
│   │   │   ├── users.py        # User management
│   │   │   └── ...             # Other route modules
│   │   ├── services/           # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── document_processor.py    # Document processing
│   │   │   ├── financial_service.py     # Financial operations
│   │   │   ├── user_service.py          # User management
│   │   │   ├── ai_analytics_service.py  # AI analytics
│   │   │   ├── local_llm_service.py     # Local LLM integration
│   │   │   └── ...                      # Other services
│   │   ├── models/             # Data models (SQLAlchemy, Pydantic)
│   │   │   ├── __init__.py
│   │   │   ├── company.py      # Company models
│   │   │   ├── user.py         # User models
│   │   │   ├── document.py     # Document models
│   │   │   └── ...             # Other models
│   │   └── utils/              # Utility functions
│   │       ├── __init__.py
│   │       ├── document_utils.py       # Document utilities
│   │       ├── file_utils.py           # File operations
│   │       └── validation.py           # Data validation
│   └── tests/                  # Backend-specific tests
│       ├── test_company_model.py
│       └── ...
│
├── frontend/                   # Frontend Application
│   └── frontend-web/           # React/TypeScript web application
│       ├── package.json        # Node.js dependencies
│       ├── tsconfig.json       # TypeScript configuration
│       ├── vite.config.ts      # Vite build configuration
│       ├── tailwind.config.js  # Tailwind CSS configuration
│       ├── src/                # Frontend source code
│       │   ├── main.tsx        # Application entry point
│       │   ├── App.tsx         # Main App component
│       │   ├── api.ts          # API client
│       │   ├── components/     # React components
│       │   ├── pages/          # Page components
│       │   ├── context/        # React contexts
│       │   ├── hooks/          # Custom React hooks
│       │   └── layout/         # Layout components
│       └── public/             # Static assets
│           ├── index.html
│           └── images/         # Image assets
│
├── infrastructure/             # Infrastructure & Deployment
│   ├── database/               # Database setup & migrations
│   │   ├── postgresql/         # PostgreSQL configuration
│   │   ├── mongodb/            # MongoDB configuration
│   │   ├── redis/              # Redis configuration
│   │   ├── ssl/                # SSL certificates
│   │   └── *.py                # Database setup scripts
│   ├── monitoring/             # Monitoring configurations
│   │   └── prometheus.yml      # Prometheus monitoring
│   ├── nginx/                  # Web server configuration
│   │   └── nginx.conf          # Nginx configuration
│   ├── models/                 # AI models storage
│   │   └── tinyllama/          # Local AI models
│   └── prompts/                # AI prompts & templates
│       ├── financial_analysis/ # Financial analysis prompts
│       └── program_analysis/   # Code analysis prompts
│
├── config/                     # Configuration Files
│   ├── docker-compose.yml      # Docker Compose configuration
│   ├── docker-compose.dev.yml  # Development environment
│   ├── docker-compose.production.yml # Production environment
│   ├── Dockerfile              # Container build instructions
│   ├── Dockerfile.production   # Production container build
│   ├── requirements.txt        # Python dependencies
│   ├── pyproject.toml          # Python project configuration
│   ├── setup.cfg               # Setup configuration
│   ├── alembic.ini             # Database migration configuration
│   ├── env.example             # Environment variables template
│   ├── env.production.example  # Production environment template
│   └── *.json                  # Various configuration files
│
├── docs/                       # Documentation
│   ├── 00_INDEX.md             # Documentation index
│   ├── 01_PROJECT_OVERVIEW.md  # Project overview
│   ├── 02_TECHNICAL_ARCHITECTURE.md # Architecture guide
│   ├── 03_IMPLEMENTATION_GUIDE.md   # Implementation guide
│   ├── 04_API_DOCUMENTATION.md     # API reference
│   ├── 05_SECURITY_GUIDE.md        # Security documentation
│   ├── 06_DEPLOYMENT_GUIDE.md      # Deployment instructions
│   ├── CONTRIBUTING.md             # Contribution guidelines
│   ├── SECURITY.md                 # Security policy
│   ├── PRIVACY.md                  # Privacy policy
│   └── ...                         # Additional documentation
│
├── scripts/                    # Utility & Automation Scripts
│   ├── quick_start.sh          # Quick setup script
│   ├── start_vanta.sh          # Application launcher
│   ├── stop_vanta.sh           # Application stopper
│   ├── test_all.sh             # Test runner
│   ├── security_monitor.sh     # Security monitoring
│   ├── backup_and_migrate.py   # Backup utilities
│   ├── setup_initial_data.py   # Data initialization
│   └── ...                     # Other utility scripts
│
├── tests/                      # Main Test Suite
│   ├── conftest.py             # Pytest configuration
│   ├── test_api_endpoints.py   # API endpoint tests
│   ├── test_auth.py            # Authentication tests
│   ├── test_database_integration.py # Database tests
│   ├── test_security.py        # Security tests
│   └── ...                     # Other test modules
│
├── data/                       # Application Data
│   ├── processed_documents/    # Processed documents storage
│   └── uploads/                # File upload storage
│
├── logs/                       # Application Logs
│   ├── app.log                 # Main application log
│   ├── backend.log             # Backend specific logs
│   ├── frontend.log            # Frontend specific logs
│   └── vanta_ledger.log        # System logs
│
├── videos/                     # Demo Videos
│   ├── Deconstructing_Vanta_Ledger.mp4
│   └── Vanta_Ledger__AI-Powered_Financial_Document_Management.mp4
│
└── uploads/                    # User Uploads
    └── (user uploaded files)
```

## 🎯 Directory Purposes

### **Backend (`backend/`)**
Contains all server-side application code including:
- FastAPI application and routes
- Business logic services
- Data models and database interactions
- Authentication and authorization
- API endpoints and middleware

### **Frontend (`frontend/`)**
Contains the web application interface:
- React/TypeScript application
- UI components and pages
- State management
- API client integration
- Responsive design assets

### **Infrastructure (`infrastructure/`)**
Contains deployment and infrastructure code:
- Database configurations and setup scripts
- Monitoring and logging configurations
- Web server configurations
- AI models and prompts
- SSL certificates and security configurations

### **Config (`config/`)**
Contains all configuration files:
- Container orchestration (Docker Compose)
- Environment configurations
- Dependency management
- Build configurations
- Database migration settings

### **Docs (`docs/`)**
Contains comprehensive documentation:
- Technical documentation
- User guides and tutorials
- API documentation
- Security and deployment guides
- Contributing guidelines

### **Scripts (`scripts/`)**
Contains utility and automation scripts:
- Setup and deployment scripts
- Testing and validation scripts
- Maintenance and monitoring scripts
- Data migration utilities
- Security monitoring tools

### **Tests (`tests/`)**
Contains the main test suite:
- Integration tests
- Unit tests
- Security tests
- Performance tests
- API endpoint tests

## 🚀 Getting Started

### **For Developers**
1. Start with the `README.md` for project overview
2. Read `docs/CONTRIBUTING.md` for contribution guidelines
3. Explore `backend/src/vanta_ledger/` for application code
4. Check `frontend/frontend-web/src/` for UI components

### **For DevOps**
1. Review `config/` for deployment configurations
2. Check `infrastructure/` for infrastructure setup
3. Use `scripts/` for automation and deployment
4. Monitor using configurations in `infrastructure/monitoring/`

### **For Users**
1. Start with the main `README.md`
2. Follow installation instructions
3. Use `scripts/quick_start.sh` for quick setup
4. Refer to `docs/` for detailed documentation

## 🔧 Development Workflow

### **Adding New Features**
1. **Backend**: Add routes in `backend/src/vanta_ledger/routes/`
2. **Services**: Implement business logic in `backend/src/vanta_ledger/services/`
3. **Models**: Define data models in `backend/src/vanta_ledger/models/`
4. **Frontend**: Create components in `frontend/frontend-web/src/components/`
5. **Tests**: Add tests in `tests/` or `backend/tests/`
6. **Documentation**: Update relevant docs in `docs/`

### **Configuration Changes**
1. **Environment**: Update `config/env.example`
2. **Dependencies**: Modify `config/requirements.txt` or `frontend/package.json`
3. **Deployment**: Update Docker configurations in `config/`
4. **Infrastructure**: Modify `infrastructure/` configurations

### **Scripts and Utilities**
1. **Development**: Use scripts in `scripts/` for common tasks
2. **Testing**: Run `scripts/test_all.sh` for comprehensive testing
3. **Deployment**: Use `scripts/start_vanta.sh` for application startup
4. **Maintenance**: Use utility scripts for system maintenance

## 📝 Best Practices

### **File Organization**
- Keep related files together in appropriate directories
- Use descriptive file names that indicate their purpose
- Maintain consistent naming conventions across the project
- Add new files to the appropriate directory based on their function

### **Documentation**
- Update documentation when adding new features
- Keep README files current with directory changes
- Document configuration changes in appropriate guides
- Maintain API documentation for new endpoints

### **Configuration Management**
- Store all configuration in the `config/` directory
- Use environment variables for sensitive data
- Maintain separate configurations for development and production
- Document configuration changes and their purposes

This structure ensures maintainability, scalability, and ease of contribution while keeping the project organized and professional.
