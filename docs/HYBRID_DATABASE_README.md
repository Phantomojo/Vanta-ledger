# Hybrid Database Readme

Use environment variables for credentials. Do not embed real usernames/passwords here. Example:

```
<<<<<<< Current (Your changes)
<<<<<<< Current (Your changes)

## 🚀 Quick Start

### 1. Setup the Hybrid System

```bash
# Run the complete setup script
python setup_hybrid_system.py
```

This will:
- Start PostgreSQL and MongoDB containers
- Initialize database schemas
- Populate the 10 family companies
- Create sample projects
- Set up admin user

### 2. Access Database Management

- **MongoDB Management**: http://localhost:8081
- **PostgreSQL Management**: http://localhost:8080
- **Redis Cache**: localhost:6379

### 3. Start the Application

```bash
# Start backend
python backend/app/main.py

# Start frontend
cd frontend/frontend-web && npm run dev
```

## 📊 Database Schema

### PostgreSQL Schema (Structured Data)

```sql
-- Companies (Core business entities)
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    registration_number VARCHAR(100) UNIQUE NOT NULL,
    industry VARCHAR(100),
    address JSONB,
    contact_info JSONB,
    tax_info JSONB,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Projects (Individual business projects)
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) NOT NULL,
    name VARCHAR(255) NOT NULL,
    client VARCHAR(255),
    value DECIMAL(15,2),
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'active',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ledger Entries (ACID-compliant financial transactions)
CREATE TABLE ledger_entries (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) NOT NULL,
    project_id INTEGER REFERENCES projects(id),
    entry_type VARCHAR(50) NOT NULL CHECK (entry_type IN ('income', 'expense', 'transfer', 'withdrawal')),
    category VARCHAR(100),
    description TEXT,
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'KES',
    reference_number VARCHAR(100),
    transaction_date DATE NOT NULL,
    approval_status VARCHAR(50) DEFAULT 'pending',
    approved_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Documents (Metadata only)
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    project_id INTEGER REFERENCES projects(id),
    document_type VARCHAR(100),
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploader_id INTEGER REFERENCES users(id),
    mongo_document_id VARCHAR(50), -- Link to MongoDB document
    status VARCHAR(50) DEFAULT 'active'
);
```

### MongoDB Schema (Document Storage)

```javascript
// Documents Collection
{
  _id: ObjectId,
  postgres_id: Number,           // Link to PostgreSQL
  company_id: Number,
  project_id: Number,
  
  // File metadata
  filename: String,
  file_path: String,
  file_size: Number,
  mime_type: String,
  upload_date: Date,
  uploader_id: Number,
  
  // Document classification
  document_type: String,         // "invoice", "contract", "certificate"
  category: String,              // "financial", "legal", "compliance"
  subcategory: String,           // "nca_certificate", "tax_compliance"
  
  // AI Analysis Results
  ai_analysis: {
    confidence_score: Number,
    classification: String,
    extracted_data: {
      amounts: [{
        value: Number,
        currency: String,
        type: String,            // "total", "tax", "subtotal"
        confidence: Number
      }],
      dates: [{
        date: Date,
        type: String,            // "issue_date", "due_date", "expiry_date"
        confidence: Number
      }],
      entities: {
        companies: [String],
        people: [String],
        locations: [String],
        project_codes: [String]
      }
    },
    ocr_text: String,
    processing_date: Date
  },
  
  // Business Intelligence
  business_insights: {
    risk_score: Number,
    payment_status: String,      // "paid", "pending", "overdue"
    due_date: Date,
    vendor_name: String,
    project_code: String,
    compliance_status: String,
    expiry_date: Date
  },
  
  // Search and filtering
  tags: [String],
  keywords: [String],
  custom_fields: Object
}

// Financial Extractions Collection
{
  _id: ObjectId,
  document_id: ObjectId,
  postgres_ledger_id: Number,   // Link to PostgreSQL ledger entry
  amount: Number,
  currency: String,
  transaction_type: String,
  vendor_name: String,
  invoice_number: String,
  tax_amount: Number,
  tax_rate: Number,
  confidence_score: Number,
  extracted_date: Date
}
```

## 🔧 API Endpoints

### Companies
```http
GET /api/companies/              # List all companies
GET /api/companies/{id}          # Get specific company
POST /api/companies/             # Create new company
PUT /api/companies/{id}          # Update company
DELETE /api/companies/{id}       # Delete company
```

### Projects
```http
GET /api/projects/               # List all projects
GET /api/projects/{id}           # Get specific project
GET /api/companies/{id}/projects # Get company projects
POST /api/projects/              # Create new project
PUT /api/projects/{id}           # Update project
DELETE /api/projects/{id}        # Delete project
```

### Financial Transactions
```http
GET /api/ledger/                 # List ledger entries
GET /api/ledger/{id}             # Get specific entry
POST /api/ledger/                # Create ledger entry
PUT /api/ledger/{id}             # Update entry
DELETE /api/ledger/{id}          # Delete entry
GET /api/ledger/summary          # Financial summary
```

### Documents
```http
GET /api/documents/              # List documents
GET /api/documents/{id}          # Get document details
POST /api/documents/upload       # Upload document
PUT /api/documents/{id}          # Update document
DELETE /api/documents/{id}       # Delete document
GET /api/documents/search        # Search documents
POST /api/documents/{id}/extract # Extract financial data
```

## 🔄 Hybrid Operations

### Document Upload with AI Analysis

```python
# Upload document to both databases
result = hybrid_db.upload_document(
    file_data={
        "company_id": 1,
        "project_id": 1,
        "filename": "invoice_001.pdf",
        "file_path": "/uploads/invoice_001.pdf",
        "file_size": 1024000,
        "mime_type": "application/pdf"
    },
    ai_analysis={
        "classification": "invoice",
        "confidence_score": 0.95,
        "extracted_data": {
            "amounts": [
                {"value": 250000.0, "currency": "KES", "type": "total"}
            ],
            "entities": {
                "companies": ["ABC Supplies Ltd"],
                "project_codes": ["PROJ-001"]
            }
        }
    }
)
```

### Financial Data Extraction

```python
# Extract financial data from document and create ledger entry
extraction = hybrid_db.extract_financial_data_from_document(document_id=123)

# Result:
{
    "ledger_id": 456,
    "amount": 250000.0,
    "status": "extracted",
    "confidence": 0.95
}
```

### Cross-Database Queries

```python
# Get documents with financial data
documents = hybrid_db.get_documents(company_id=1)

# Get financial summary
summary = hybrid_db.get_financial_summary(
    company_id=1,
    start_date="2024-01-01",
    end_date="2024-12-31"
)
```

## 📈 Performance Optimization

### PostgreSQL Indexes
```sql
-- Companies
CREATE INDEX idx_companies_name ON companies(name);
CREATE INDEX idx_companies_registration ON companies(registration_number);

-- Projects
CREATE INDEX idx_projects_company ON projects(company_id);
CREATE INDEX idx_projects_status ON projects(status);

-- Ledger Entries
CREATE INDEX idx_ledger_company ON ledger_entries(company_id);
CREATE INDEX idx_ledger_project ON ledger_entries(project_id);
CREATE INDEX idx_ledger_date ON ledger_entries(transaction_date);
CREATE INDEX idx_ledger_type ON ledger_entries(entry_type);

-- Documents
CREATE INDEX idx_documents_company ON documents(company_id);
CREATE INDEX idx_documents_project ON documents(project_id);
```

### MongoDB Indexes
```javascript
// Companies
db.companies.createIndex({ "name": 1 });
db.companies.createIndex({ "registration_number": 1 }, { unique: true });

// Documents
db.documents.createIndex({ "company_id": 1 });
db.documents.createIndex({ "project_id": 1 });
db.documents.createIndex({ "document_type": 1 });
db.documents.createIndex({ "upload_date": -1 });
db.documents.createIndex({ "postgres_id": 1 }, { unique: true });

// Text search for OCR content
db.documents.createIndex({ "ai_analysis.ocr_text": "text" });

// Financial extractions
db.financial_extractions.createIndex({ "document_id": 1 });
db.financial_extractions.createIndex({ "postgres_ledger_id": 1 });
```

## 🔒 Security Features

### Authentication
- JWT-based authentication
- Role-based access control
- Password hashing with bcrypt

### Database Security
- Encrypted connections (SSL/TLS)
- Environment variable configuration
- Input validation and sanitization

### File Security
- Secure file upload validation
- Virus scanning integration
- Access control for sensitive documents

## 📊 Monitoring and Health Checks

### Database Health
```python
# Check database health
health = hybrid_db.health_check()

# Result:
{
    "postgresql": {"status": "healthy", "error": None},
    "mongodb": {"status": "healthy", "error": None},
    "overall": "healthy"
}
```

### Performance Monitoring
- Query performance tracking
- Connection pool monitoring
- Cache hit rates
- Response time metrics

## 🚀 Deployment

### Docker Compose
```yaml
# Start all services
docker-compose -f database/docker-compose-hybrid.yml up -d

# Stop services
docker-compose -f database/docker-compose-hybrid.yml down
```

### Environment Variables
```bash
# Database URIs
POSTGRES_URI=postgresql://vanta_user:vanta_password@localhost:5432/vanta_ledger
MONGO_URI=mongodb://admin:admin123@localhost:27017/vanta_ledger

# Application Settings
DEBUG=True
HOST=0.0.0.0
PORT=8500

# Security
SECRET_KEY=your-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🔧 Maintenance

### Backup Strategy
```bash
# PostgreSQL backup
pg_dump -h localhost -U vanta_user vanta_ledger > backup_postgres.sql

# MongoDB backup
mongodump --host localhost --port 27017 --db vanta_ledger --out backup_mongo
```

### Data Migration
```python
# Migrate from MongoDB-only to hybrid
python database/hybrid_database_setup.py
```

## 📚 Additional Resources

- [API Documentation](http://localhost:8500/docs)
- [Database Schema](database/hybrid_database_setup.py)
- [Configuration](.env)
- [Docker Compose](database/docker-compose-hybrid.yml)

## 🤝 Support

For questions or issues with the hybrid database system:

1. Check the logs: `docker-compose logs`
2. Verify database connections
3. Review the setup documentation
4. Contact the development team

---

**Built with ❤️ for the Vanta Ledger family business** 
=======
POSTGRES_URI=postgresql://<user>:<password>@localhost:5432/vanta_ledger
MONGO_URI=mongodb://<user>:<password>@localhost:27017/vanta_ledger
``` 
>>>>>>> Incoming (Background Agent changes)
=======
POSTGRES_URI=postgresql://<user>:<password>@localhost:5432/vanta_ledger
MONGO_URI=mongodb://<user>:<password>@localhost:27017/vanta_ledger
``` 
>>>>>>> Incoming (Background Agent changes)
