# 🏗️ Vanta Ledger Technical Architecture

## 📋 Architecture Overview

Vanta Ledger employs a modern, containerized microservices architecture designed for scalability, security, and performance. The system is built around a hybrid database approach with AI-powered document processing and real-time analytics.

## 🐳 Container Architecture

### **All-in-One Container Design**
```
Vanta Ledger Container
├── 🖥️ Base OS: Ubuntu 22.04 LTS
├── 🐍 Python 3.12 + Virtual Environment
├── 🗄️ Database Layer
│   ├── PostgreSQL 15 (Financial Data)
│   ├── MongoDB 8.0 (Document Storage)
│   └── Redis 7 (Caching & Sessions)
├── 🤖 AI/ML Layer
│   ├── PyTorch (CPU/GPU Support)
│   ├── Transformers
│   ├── TinyLlama (1GB)
│   ├── Phi-3 Mini (2.1GB)
│   └── Mistral 7B (4GB)
├── 🚀 Application Layer
│   ├── FastAPI Backend
│   ├── Business Logic Services
│   └── API Endpoints
├── 🛠️ Management Layer
│   ├── pgAdmin (PostgreSQL Management)
│   ├── Mongo Express (MongoDB Management)
│   └── Custom Dashboard
└── 📊 System Layer
    ├── Supervisor (Process Management)
    ├── Monitoring & Logging
    └── Security Framework
```

### **Container Specifications**
- **Base Image**: Ubuntu 22.04 LTS
- **Python Version**: 3.12+
- **Memory Requirements**: 8GB minimum, 16GB+ recommended
- **Storage**: 20GB minimum, 50GB+ recommended
- **CPU**: 4 cores minimum, 8+ cores recommended
- **GPU**: Optional (CUDA 11.8+ if available)

## 🗄️ Database Architecture

### **Hybrid Database Design**
```
Database Layer
├── 🐘 PostgreSQL 15
│   ├── Financial Data (GL, AP/AR, Reports)
│   ├── User Management & Authentication
│   ├── Company Configuration
│   └── Audit Trails & Logging
├── 🍃 MongoDB 8.0
│   ├── Document Storage & Metadata
│   ├── AI Analysis Results
│   ├── Search Indexes
│   └── Analytics Data
└── 🔴 Redis 7
    ├── Session Management
    ├── Caching Layer
    ├── Real-time Data
    └── Performance Optimization
```

### **PostgreSQL Schema**
```sql
-- Core Tables
companies (id, name, config, created_at, updated_at)
users (id, company_id, username, email, role, created_at)
documents (id, company_id, type, status, metadata, created_at)
financial_accounts (id, company_id, account_number, name, type, balance)
journal_entries (id, company_id, date, description, total_amount, created_at)
journal_entry_lines (id, journal_entry_id, account_id, debit, credit, description)

-- Audit Tables
audit_logs (id, company_id, user_id, action, table_name, record_id, changes, timestamp)
security_events (id, event_type, severity, description, ip_address, user_agent, timestamp)
```

### **MongoDB Collections**
```javascript
// Document Collections
documents: {
  _id: ObjectId,
  company_id: String,
  filename: String,
  content: String,
  metadata: Object,
  ai_analysis: Object,
  tags: Array,
  categories: Array,
  created_at: Date,
  updated_at: Date
}

// AI Analysis Results
ai_analyses: {
  _id: ObjectId,
  document_id: ObjectId,
  company_id: String,
  model_used: String,
  entities_extracted: Array,
  confidence_scores: Object,
  processing_time: Number,
  created_at: Date
}

// Analytics Data
analytics: {
  _id: ObjectId,
  company_id: String,
  metric_type: String,
  metric_value: Number,
  timestamp: Date,
  metadata: Object
}
```

### **Redis Data Structures**
```redis
# Session Management
sessions:{session_id} -> {user_id, company_id, role, permissions, expires_at}

# Caching Layer
cache:{cache_key} -> {data, expires_at}
cache:documents:{company_id}:{document_id} -> {document_data, ttl}
cache:financial:{company_id}:{account_id} -> {balance, last_updated}

# Real-time Data
realtime:company:{company_id}:metrics -> {cpu, memory, disk, network}
realtime:ai:models -> {model_status, performance_metrics}
```

## 🚀 Application Architecture

### **FastAPI Backend Structure**
```
src/vanta_ledger/
├── __init__.py
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration management
├── auth.py                # Authentication & authorization
├── models/                # Data models
│   ├── __init__.py
│   ├── user_models.py     # User & company models
│   ├── document_models.py # Document & metadata models
│   └── financial_models.py # Financial data models
├── routes/                # API endpoints
│   ├── __init__.py
│   ├── auth.py           # Authentication routes
│   ├── documents.py      # Document management
│   ├── financial.py      # Financial operations
│   ├── analytics.py      # Analytics & reporting
│   └── ai_analytics.py   # AI-powered analytics
├── services/              # Business logic
│   ├── __init__.py
│   ├── document_service.py    # Document processing
│   ├── financial_service.py   # Financial operations
│   ├── ai_analytics_service.py # AI analytics
│   └── analytics_dashboard.py # Dashboard services
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── document_utils.py     # Document processing utilities
│   ├── file_utils.py         # File handling utilities
│   └── validation.py         # Data validation
└── integration/           # System integration
    ├── __init__.py
    └── system_integrator.py  # Cross-feature integration
```

### **API Structure**
```
/api/v1/
├── /auth
│   ├── POST /login         # User authentication
│   ├── POST /refresh       # Token refresh
│   └── POST /logout        # User logout
├── /companies
│   ├── GET /               # List companies (GOD only)
│   ├── POST /              # Create company (GOD only)
│   ├── GET /{id}           # Get company details
│   └── PUT /{id}           # Update company
├── /users
│   ├── GET /               # List users
│   ├── POST /              # Create user
│   ├── GET /{id}           # Get user details
│   └── PUT /{id}           # Update user
├── /documents
│   ├── GET /               # List documents
│   ├── POST /              # Upload document
│   ├── GET /{id}           # Get document
│   ├── PUT /{id}           # Update document
│   └── DELETE /{id}        # Delete document
├── /financial
│   ├── /accounts           # Chart of accounts
│   ├── /journal-entries    # Journal entries
│   ├── /invoices           # Invoice management
│   └── /reports            # Financial reports
└── /ai-analytics
    ├── /predictions        # AI predictions
    ├── /anomalies          # Anomaly detection
    └── /insights           # Business insights
```

## 🤖 AI/ML Architecture

### **Local LLM Integration**
```
AI/ML Layer
├── 🧠 Model Management
│   ├── TinyLlama (1GB) - Fast inference, basic tasks
│   ├── Phi-3 Mini (2.1GB) - Balanced performance
│   └── Mistral 7B (4GB) - High accuracy, complex tasks
├── 🔄 Dynamic Model Selection
│   ├── Resource-based selection
│   ├── Task complexity analysis
│   └── Performance optimization
├── 📊 Document Processing
│   ├── OCR & text extraction
│   ├── Entity recognition
│   ├── Financial data extraction
│   └── Compliance checking
└── 🎯 Analytics & Insights
    ├── Trend analysis
    ├── Anomaly detection
    ├── Predictive modeling
    └── Business recommendations
```

### **AI Model Specifications**
```python
# Model Configuration
AI_MODELS = {
    "tinyllama": {
        "name": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        "size": "1GB",
        "use_case": "basic_document_processing",
        "performance": "fast",
        "accuracy": "medium"
    },
    "phi3_mini": {
        "name": "microsoft/Phi-3-mini-4k-instruct",
        "size": "2.1GB",
        "use_case": "balanced_processing",
        "performance": "balanced",
        "accuracy": "high"
    },
    "mistral_7b": {
        "name": "mistralai/Mistral-7B-Instruct-v0.2",
        "size": "4GB",
        "use_case": "complex_analytics",
        "performance": "thorough",
        "accuracy": "very_high"
    }
}
```

## 🔐 Security Architecture

### **Authentication & Authorization**
```
Security Framework
├── 🔐 Master Password System
│   ├── 64-character random generation
│   ├── Hardware security module simulation
│   ├── AES-256-GCM encryption
│   ├── Single-use tokens (30-second expiry)
│   └── Shamir's Secret Sharing (5-of-7)
├── 👤 User Authentication
│   ├── JWT tokens with refresh mechanism
│   ├── Role-based access control (RBAC)
│   ├── Company-specific permissions
│   └── Session management
├── 🛡️ Data Security
│   ├── Encryption at rest (AES-256)
│   ├── Encryption in transit (TLS 1.3)
│   ├── Row-level security
│   └── Data isolation per company
└── 🔍 Monitoring & Auditing
    ├── Real-time security monitoring
    ├── Comprehensive audit trails
    ├── Threat detection
    └── Automated response
```

### **Security Implementation Details**
```python
# Security Configuration
SECURITY_CONFIG = {
    "jwt_secret": "64-character-random-string",
    "jwt_algorithm": "HS256",
    "jwt_expiry": 3600,  # 1 hour
    "refresh_expiry": 604800,  # 7 days
    "password_min_length": 12,
    "password_complexity": "high",
    "session_timeout": 1800,  # 30 minutes
    "max_login_attempts": 5,
    "lockout_duration": 900,  # 15 minutes
    "encryption_algorithm": "AES-256-GCM",
    "key_derivation": "PBKDF2",
    "iterations": 100000
}
```

## 📊 Performance Architecture

### **Caching Strategy**
```
Multi-Level Caching
├── 🚀 Application Level
│   ├── Function result caching
│   ├── Query result caching
│   └── Object caching
├── 🗄️ Database Level
│   ├── Query optimization
│   ├── Index optimization
│   └── Connection pooling
├── 🔴 Redis Level
│   ├── Session storage
│   ├── Real-time data
│   └── Performance metrics
└── 🖥️ System Level
    ├── Memory management
    ├── Process optimization
    └── Resource monitoring
```

### **Performance Optimization**
```python
# Caching Configuration
CACHE_CONFIG = {
    "redis_ttl": 3600,  # 1 hour default
    "document_cache_ttl": 7200,  # 2 hours for documents
    "financial_cache_ttl": 1800,  # 30 minutes for financial data
    "user_cache_ttl": 3600,  # 1 hour for user data
    "max_cache_size": "1GB",
    "cache_cleanup_interval": 300,  # 5 minutes
    "cache_warmup_enabled": True,
    "cache_compression": True
}

# Database Optimization
DB_OPTIMIZATION = {
    "connection_pool_size": 20,
    "max_connections": 100,
    "query_timeout": 30,
    "index_optimization": True,
    "query_plan_analysis": True,
    "performance_monitoring": True
}
```

## 🛠️ Management & Monitoring

### **System Management Tools**
```
Management Layer
├── 🗄️ Database Management
│   ├── pgAdmin (PostgreSQL)
│   ├── Mongo Express (MongoDB)
│   └── Redis Commander
├── 📊 System Monitoring
│   ├── Custom Dashboard
│   ├── Performance Metrics
│   ├── Health Checks
│   └── Alert System
├── 🔧 Process Management
│   ├── Supervisor
│   ├── Service Management
│   └── Auto-restart
└── 📝 Logging & Debugging
    ├── Structured Logging
    ├── Log Aggregation
    ├── Error Tracking
    └── Performance Profiling
```

### **Monitoring Configuration**
```python
# Monitoring Configuration
MONITORING_CONFIG = {
    "metrics_collection_interval": 60,  # 1 minute
    "health_check_interval": 30,  # 30 seconds
    "alert_thresholds": {
        "cpu_usage": 80,
        "memory_usage": 85,
        "disk_usage": 90,
        "response_time": 2000,  # 2 seconds
        "error_rate": 5
    },
    "log_retention": 30,  # 30 days
    "performance_tracking": True,
    "security_monitoring": True,
    "business_metrics": True
}
```

## 🚀 Deployment Architecture

### **Container Deployment**
```yaml
# Docker Compose Configuration
version: '3.8'
services:
  vanta-ledger:
    build: .
    ports:
      - "8000:8000"    # FastAPI Backend
      - "5432:5432"    # PostgreSQL
      - "27017:27017"  # MongoDB
      - "6379:6379"    # Redis
      - "8080:8080"    # pgAdmin
      - "8081:8081"    # Mongo Express
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - LOG_LEVEL=info
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4'
        reservations:
          memory: 4G
          cpus: '2'
```

### **Environment Configuration**
```bash
# Environment Variables
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost/vanta_ledger
MONGODB_URL=mongodb://localhost:27017/vanta_ledger
REDIS_URL=redis://localhost:6379
AI_MODELS_PATH=/app/models
UPLOAD_PATH=/app/uploads
LOG_PATH=/app/logs
SECURITY_LEVEL=high
COMPANY_ISOLATION=true
AUDIT_LOGGING=true
```

## 📈 Scaling Considerations

### **Horizontal Scaling**
- **Load Balancing**: Multiple container instances
- **Database Sharding**: Company-based data distribution
- **Cache Distribution**: Redis cluster configuration
- **Service Discovery**: Dynamic service registration

### **Vertical Scaling**
- **Resource Allocation**: CPU, memory, storage optimization
- **Performance Tuning**: Database and application optimization
- **Caching Strategy**: Multi-level caching implementation
- **Monitoring**: Real-time performance tracking

---

**🏗️ This technical architecture provides the foundation for a scalable, secure, and high-performance financial management platform.**
