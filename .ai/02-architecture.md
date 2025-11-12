# 02 - System Architecture

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Vanta Ledger System                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐              ┌──────────────┐              │
│  │   Frontend   │◄────────────►│   Backend    │              │
│  │  React + TS  │   REST API   │   FastAPI    │              │
│  │  Port: 5173  │              │  Port: 8500  │              │
│  └─────────────┘              └──────┬───────┘              │
│                                       │                       │
│                    ┌──────────────────┼──────────────────┐  │
│                    │                  │                  │  │
│             ┌──────▼─────┐   ┌───────▼──────┐   ┌──────▼────┐
│             │ PostgreSQL  │   │   MongoDB    │   │   Redis   │
│             │ Port: 5432  │   │ Port: 27017  │   │Port: 6379 │
│             │ (Structured)│   │(Unstructured)│   │ (Cache)   │
│             └─────────────┘   └──────────────┘   └───────────┘
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 🗄️ Hybrid Database Strategy

### PostgreSQL (Primary - Structured Data)
**Purpose**: ACID-compliant storage for critical business data

**Stores**:
- Users and authentication
- Companies (multi-tenant isolation)
- Financial transactions and ledger
- Projects and metadata
- Audit logs

**Why**: Relational integrity, ACID compliance, complex queries

### MongoDB (Secondary - Unstructured Data)
**Purpose**: Flexible schema for documents and AI results

**Stores**:
- Uploaded documents (PDFs, images, etc.)
- AI processing results
- OCR extracted data
- Document metadata
- Unstructured analytics

**Why**: Schema flexibility, document storage, JSON-native

### Redis (Cache - Fast Access)
**Purpose**: In-memory cache for performance

**Stores**:
- Session data
- JWT token blacklist
- Rate limiting counters
- Temporary processing results
- Cache for frequent queries

**Why**: Sub-millisecond latency, TTL support, pub/sub

## 🔧 Backend Architecture (FastAPI)

### Layer Structure
```
┌─────────────────────────────────────┐
│         Routes (API Layer)          │  ← HTTP endpoints
├─────────────────────────────────────┤
│        Middleware Stack             │  ← CORS, Auth, Logging, Rate Limit
├─────────────────────────────────────┤
│       Services (Business Logic)     │  ← Core functionality
├─────────────────────────────────────┤
│      Models (Data Layer)            │  ← Pydantic + SQLAlchemy
├─────────────────────────────────────┤
│   Database Connections              │  ← PostgreSQL, MongoDB, Redis
└─────────────────────────────────────┘
```

### 17 Route Modules (3,671 lines total)
Located in `src/vanta_ledger/routes/`:
1. `auth.py` - Authentication & authorization
2. `users.py` - User management
3. `companies.py` - Multi-tenant company management
4. `financial.py` - Financial transactions
5. `ledger.py` - Ledger management
6. `documents.py` - Document upload/retrieve
7. `enhanced_documents.py` - Advanced document features
8. `extracted_data.py` - OCR/AI extraction results
9. `projects.py` - Project management
10. `analytics.py` - Analytics dashboards
11. `ai_analytics.py` - AI-powered analytics
12. `local_llm.py` - Local LLM integration
13. `github_models.py` - GitHub Models (deprecated)
14. `notifications.py` - User notifications
15. `paperless_integration.py` - Paperless integration
16. `config.py` - Configuration management
17. `simple_auth.py` - Simplified auth for frontend

### 11 Service Modules (~200KB total)
Located in `src/vanta_ledger/services/`:
1. `user_service.py` (11KB) - User operations
2. `financial_service.py` (19KB) - Financial logic
3. `document_processor.py` (18KB) - Document processing
4. `enhanced_document_service.py` (20KB) - Advanced docs
5. `ai_analytics_service.py` (25KB) - AI analytics
6. `analytics_dashboard.py` (29KB) - Dashboard logic
7. `local_llm_service.py` (32KB) - LLM integration
8. `system_analysis_service.py` (18KB) - System analysis
9. `github_models_service.py` (empty) - Deprecated
10. `llm/hardware_detector.py` - Hardware detection
11. `llm/company_context.py` - Company context for AI

### Middleware Stack (In Order)
1. **CORS Middleware** - Frontend access control
2. **SecurityHeadersMiddleware** - HSTS, CSP, X-Frame-Options
3. **LoggingMiddleware** - Request/response logging
4. **RateLimitMiddleware** - DDoS protection (100/min, 1000/hr)

### Authentication Flow
```
User Request → JWT Token → Validate → Check Role → Allow/Deny
                    ↓
              Redis (token blacklist check)
```

## 🎨 Frontend Architecture (React + TypeScript)

### Structure
```
frontend/frontend-web/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/          # Page components
│   ├── hooks/          # Custom React hooks
│   ├── services/       # API communication
│   ├── types/          # TypeScript types
│   ├── utils/          # Helper functions
│   └── styles/         # TailwindCSS styles
```

### Key Technologies
- **React 18.3.1** - UI framework
- **TypeScript 5.7.2** - Type safety
- **Vite** - Build tool & dev server
- **TailwindCSS** - Styling
- **ApexCharts** - Data visualization
- **FullCalendar** - Calendar views
- **Axios** - HTTP client

### State Management
- React hooks (useState, useEffect, useContext)
- API calls via Axios to backend
- JWT token storage in localStorage

## 🔐 Security Architecture

### Multi-Layer Security
1. **Network Layer**: HTTPS, CORS, Rate Limiting
2. **Application Layer**: JWT auth, input validation
3. **Data Layer**: Row-level security, encryption
4. **User Layer**: Password policies, 2FA ready

### Authentication
- **JWT Tokens**: HS256 algorithm
- **Access Token**: 30 minutes (configurable)
- **Refresh Token**: 7 days (configurable)
- **Token Blacklist**: Redis-based

### Authorization
- **Role-Based Access Control (RBAC)**
- **Company-Based Isolation**: Row-level security
- **Route Protection**: Middleware checks

### Input Validation
- **Pydantic Models**: Automatic validation
- **Type Checking**: TypeScript + Python typing
- **Sanitization**: SQL injection prevention

## 🤖 AI/ML Architecture

### Local LLM Integration
- **Hardware Detection**: Auto-detect GPU/CPU capabilities
- **Model Selection**: Choose based on available resources
- **Models Supported**:
  - TinyLlama: 1GB (CPU-friendly)
  - Phi-3 Mini: 2.1GB (Balanced)
  - Mistral 7B: 4GB (Most capable)

### Document Processing Pipeline
```
Upload → OCR → Text Extraction → AI Analysis → Storage → Results
  │       │           │               │            │         │
  │       │           │               │            │         └→ MongoDB
  │       │           │               │            └→ PostgreSQL (metadata)
  │       │           │               └→ LLM Service
  │       │           └→ pytesseract, pdf2image
  │       └→ Pillow, OpenCV
  └→ FastAPI endpoint
```

## 🔄 Data Flow Examples

### User Login
```
1. POST /api/auth/login {username, password}
2. Validate credentials (PostgreSQL)
3. Generate JWT token
4. Store session (Redis)
5. Return token + user data
```

### Document Upload & Processing
```
1. POST /api/documents/upload (file + company_id)
2. Store file (MongoDB)
3. Create metadata entry (PostgreSQL)
4. Queue for OCR processing
5. Extract text (pytesseract)
6. AI analysis (Local LLM)
7. Store results (MongoDB + PostgreSQL)
8. Return processing status
```

### Financial Transaction
```
1. POST /api/financial/transaction {amount, type, company_id}
2. Validate user permission (company match)
3. Create transaction (PostgreSQL)
4. Update ledger balances
5. Create audit log
6. Clear relevant caches (Redis)
7. Return transaction ID
```

## 📊 Scalability Considerations

### Horizontal Scaling
- **Backend**: Multiple FastAPI instances behind load balancer
- **Databases**: Read replicas for PostgreSQL
- **Cache**: Redis cluster for distributed caching

### Vertical Scaling
- **AI Processing**: GPU acceleration when available
- **Database**: Connection pooling (SQLAlchemy)
- **Async Operations**: FastAPI async/await

### Performance Optimizations
- **Caching**: Redis for frequent queries
- **Pagination**: All list endpoints
- **Lazy Loading**: Large datasets
- **Connection Pooling**: Database connections
- **CDN**: Static assets (future)

## ➡️ Next: Codebase Structure

Now that you understand the architecture, proceed to:
**`03-codebase-structure.md`** to learn WHERE everything is located.
