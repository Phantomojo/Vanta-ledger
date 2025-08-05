# 🏢 Vanta Ledger - Digital Business Management System

A comprehensive digital records room and business management system designed for family-run organizations involved in government tenders, construction, management, and supply operations.

## 🎯 **Project Overview**

Vanta Ledger is a **one-stop digital system** for managing:
- **Multi-company operations** (3+ family companies)
- **Government tender management**
- **Project tracking and financial management**
- **Document organization and compliance**
- **Expense approval workflows** (Auntie Nyaruai approval system)

## 🏗️ **System Architecture**

### **Backend** (`src/vanta_ledger/`)
- **FastAPI** - Modern Python web framework
- **PostgreSQL/SQLite** - Database management
- **SQLAlchemy** - ORM for database operations
- **JWT Authentication** - Secure user management
- **File Upload/Management** - Document handling
- **RESTful API** - Complete business logic

### **Frontend** (`frontend-web/`)
- **React + TypeScript** - Modern web interface
- **Tailwind CSS** - Professional styling
- **Responsive Design** - Mobile and desktop support
- **Real-time Dashboard** - Live business data
- **JWT Authentication** - Secure login system

### **Archived Components** (`frontend-archive/`)
- Kivy desktop app
- Flutter mobile app
- Other non-web frontends
- **Status**: Archived - focusing on web version

## 🚀 **Quick Start**

### **🎯 One-Button Launch (Recommended)**
```bash
# Single command to start everything
python launch_vanta_ledger.py
```

**Or use platform-specific launchers:**
- **Windows**: Double-click `launch_vanta_ledger.bat`
- **Linux/Mac**: Run `./launch_vanta_ledger.sh`

**Create Desktop Shortcut:**
```bash
python create_desktop_shortcut.py
```

### **Prerequisites**
- Python 3.8+
- Node.js 16+
- PostgreSQL (optional - SQLite for development)

### **Manual Setup (Alternative)**
```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Setup environment
cp env.example .env
# Edit .env with your configuration

# 3. Initialize database
python setup_initial_data.py

# 4. Start backend server
python run_backend.py

# 5. In another terminal, start frontend
cd frontend-web/
npm install
npm run dev
```

### **Access Points**
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8500
- **API Documentation**: http://localhost:8500/docs

### **Default Login**
- **Username**: admin
- **Password**: admin123

## 📊 **Core Features**

### **Dashboard**
- **Company Overview** - Multi-company management
- **Financial Summary** - Income, expenses, cash flow
- **Project Status** - Active, completed, pending projects
- **Document Compliance** - Certificate and compliance tracking
- **Recent Transactions** - Latest financial entries

### **Company Management**
- **Multi-company Support** - Handle 3+ family companies
- **Company Profiles** - Registration, contact, status
- **Company-specific Data** - Projects, finances, documents

### **Project Management**
- **Project Tracking** - Status, timeline, progress
- **Financial Tracking** - Project-specific income/expenses
- **Document Management** - Project-related documents
- **Tender Pipeline** - Government tender tracking

### **Financial Management**
- **Ledger System** - Complete financial tracking
- **Income/Expense Tracking** - Detailed financial records
- **Cash Flow Analysis** - Financial insights
- **Budget Management** - Budget vs actual tracking

### **Document Management**
- **File Upload** - Secure document storage
- **Document Organization** - Categorization and search
- **Version Control** - Document versioning
- **Compliance Tracking** - Certificate expiry monitoring

### **User Management**
- **Role-based Access** - Admin, user permissions
- **Approval Workflows** - Auntie Nyaruai approval system
- **User Profiles** - Personal information management
- **Security** - JWT authentication and authorization

## 🔐 **Security Features**

- **JWT Authentication** - Secure token-based login
- **Role-based Access Control** - Different permission levels
- **Password Hashing** - Secure password storage
- **CORS Protection** - Cross-origin request security
- **Input Validation** - Data validation and sanitization

## 📱 **Mobile Support**

The web interface is **fully responsive** and works perfectly on:
- **Desktop computers** - Full feature access
- **Tablets** - Touch-optimized interface
- **Mobile phones** - Mobile-friendly navigation

## 🏢 **Business Intelligence**

### **Data Analysis**
- **3,000+ Documents Analyzed** - OCR text analysis
- **Business Insights** - Company patterns and operations
- **Financial Analytics** - Cash flow and profitability
- **Compliance Monitoring** - Certificate and document tracking

### **Reports**
- **Financial Reports** - Income, expenses, cash flow
- **Project Reports** - Status, progress, timelines
- **Compliance Reports** - Certificate expiry, compliance status
- **Custom Reports** - Tailored business insights

## 🚀 **Deployment**

### **Self-Hosting**
- **Office Computers** - Local network deployment
- **Docker Support** - Containerized deployment
- **Database Options** - PostgreSQL (production) or SQLite (development)

### **Environment Configuration**
- **Environment Variables** - Secure configuration management
- **Database Setup** - Easy database initialization
- **File Storage** - Local file system storage

## 📋 **Project Status**

### **✅ Completed**
- **Backend API** - Complete FastAPI implementation
- **Database Models** - All business entities
- **Authentication** - JWT-based security
- **File Management** - Document upload and storage
- **Web Frontend** - React dashboard with real data
- **Documentation** - Comprehensive guides and API docs

### **🔄 In Progress**
- **Enhanced Features** - Advanced business intelligence
- **Reporting System** - Custom report generation
- **Mobile Optimization** - Enhanced mobile experience

### **📅 Planned**
- **AI Integration** - Document analysis and insights
- **Advanced Analytics** - Business intelligence dashboard
- **Compliance Automation** - Automated compliance tracking

## 🎯 **Success Metrics**

### **Business Value**
- **Time Savings** - Faster document and financial management
- **Better Organization** - Clear data organization
- **Compliance** - Easy compliance monitoring
- **Decision Making** - Better business insights

### **User Experience**
- **Easy Navigation** - Intuitive interface design
- **Fast Loading** - Quick data access
- **Mobile Friendly** - Works on all devices
- **Professional Look** - Business-ready interface

## 📞 **Support**

For questions or support, refer to:
- **API Documentation**: http://localhost:8500/docs
- **Project Documentation**: `docs/` directory
- **Setup Guides**: `quick_start.sh` and `setup_frontend.sh`

---

**Vanta Ledger - Transforming family business operations into the digital age!** 🚀 