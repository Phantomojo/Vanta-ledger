# 📚 Vanta Ledger API Documentation

## 📋 API Overview

The Vanta Ledger API provides a comprehensive RESTful interface for managing multi-company financial operations, document processing, and AI-powered analytics. All endpoints support company isolation and role-based access control.

## 🔐 Authentication & Authorization

### **Authentication Methods**
- **JWT Token Authentication**: Bearer token in Authorization header
- **Company Context**: All requests include company context for data isolation
- **Role-Based Access Control**: Different permissions based on user roles

### **Authentication Flow**
```bash
# 1. Login to get access token
POST /api/v1/auth/login
{
  "username": "user@company.com",
  "password": "secure_password"
}

# 2. Use token in subsequent requests
Authorization: Bearer <access_token>
X-Company-ID: <company_id>
```

### **Token Management**
```bash
# Refresh expired token
POST /api/v1/auth/refresh
Authorization: Bearer <refresh_token>

# Logout (invalidate token)
POST /api/v1/auth/logout
Authorization: Bearer <access_token>
```

## 🏢 Company Management API

### **Company Operations**

#### **List Companies (GOD Only)**
```http
GET /api/v1/companies
Authorization: Bearer <god_token>
```

**Response:**
```json
{
  "companies": [
    {
      "id": "uuid",
      "name": "Company Name",
      "domain": "company.com",
      "status": "active",
      "user_count": 24,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 10
}
```

#### **Create Company (GOD Only)**
```http
POST /api/v1/companies
Authorization: Bearer <god_token>
Content-Type: application/json

{
  "name": "New Company",
  "domain": "newcompany.com",
  "admin_email": "admin@newcompany.com",
  "admin_password": "secure_password",
  "subscription_plan": "enterprise"
}
```

#### **Get Company Details**
```http
GET /api/v1/companies/{company_id}
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
```

#### **Update Company**
```http
PUT /api/v1/companies/{company_id}
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
Content-Type: application/json

{
  "name": "Updated Company Name",
  "status": "active"
}
```

## 👥 User Management API

### **User Operations**

#### **List Users**
```http
GET /api/v1/users
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
Query Parameters:
- page: 1
- size: 20
- role: admin|manager|user|viewer
- status: active|inactive
```

**Response:**
```json
{
  "users": [
    {
      "id": "uuid",
      "username": "user@company.com",
      "email": "user@company.com",
      "role": "user",
      "status": "active",
      "last_login": "2024-01-01T00:00:00Z",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 24,
  "page": 1,
  "size": 20
}
```

#### **Create User**
```http
POST /api/v1/users
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
Content-Type: application/json

{
  "username": "newuser@company.com",
  "email": "newuser@company.com",
  "password": "secure_password",
  "role": "user",
  "first_name": "John",
  "last_name": "Doe"
}
```

#### **Get User Details**
```http
GET /api/v1/users/{user_id}
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
```

#### **Update User**
```http
PUT /api/v1/users/{user_id}
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
Content-Type: application/json

{
  "role": "manager",
  "status": "active"
}
```

#### **Delete User**
```http
DELETE /api/v1/users/{user_id}
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
```

## 📄 Document Management API

### **Document Operations**

#### **List Documents**
```http
GET /api/v1/documents
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
Query Parameters:
- page: 1
- size: 20
- type: invoice|receipt|contract|other
- status: uploaded|processing|processed|archived
- tags: tag1,tag2
- date_from: 2024-01-01
- date_to: 2024-12-31
- search: search_term
```

**Response:**
```json
{
  "documents": [
    {
      "id": "uuid",
      "filename": "invoice_001.pdf",
      "type": "invoice",
      "status": "processed",
      "size": 1024000,
      "tags": ["invoice", "vendor_a"],
      "categories": ["accounts_payable"],
      "ai_analysis": {
        "entities": ["amount", "date", "vendor"],
        "confidence": 0.95
      },
      "created_at": "2024-01-01T00:00:00Z",
      "processed_at": "2024-01-01T00:01:00Z"
    }
  ],
  "total": 1000,
  "page": 1,
  "size": 20
}
```

#### **Upload Document**
```http
POST /api/v1/documents
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
Content-Type: multipart/form-data

Form Data:
- file: <file>
- type: invoice
- tags: invoice,vendor_a
- categories: accounts_payable
- priority: high
```

#### **Get Document**
```http
GET /api/v1/documents/{document_id}
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
```

#### **Update Document**
```http
PUT /api/v1/documents/{document_id}
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
Content-Type: application/json

{
  "tags": ["invoice", "vendor_a", "urgent"],
  "categories": ["accounts_payable", "high_priority"],
  "metadata": {
    "vendor_id": "vendor_123",
    "due_date": "2024-02-01"
  }
}
```

#### **Delete Document**
```http
DELETE /api/v1/documents/{document_id}
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
```

#### **Process Document with AI**
```http
POST /api/v1/documents/{document_id}/process
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
Content-Type: application/json

{
  "ai_model": "auto",  # auto, tinyllama, phi3_mini, mistral_7b
  "extract_entities": true,
  "categorize": true,
  "priority": "high"
}
```

### **Document Search & Analytics**

#### **Advanced Search**
```http
POST /api/v1/documents/search
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
Content-Type: application/json

{
  "query": "invoice amount > 1000",
  "filters": {
    "type": ["invoice", "receipt"],
    "date_range": {
      "from": "2024-01-01",
      "to": "2024-12-31"
    },
    "tags": ["urgent", "high_priority"],
    "ai_confidence": {
      "min": 0.8
    }
  },
  "sort": {
    "field": "created_at",
    "order": "desc"
  },
  "pagination": {
    "page": 1,
    "size": 50
  }
}
```

#### **Document Analytics**
```http
GET /api/v1/documents/analytics
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
Query Parameters:
- period: day|week|month|quarter|year
- date_from: 2024-01-01
- date_to: 2024-12-31
```

**Response:**
```json
{
  "total_documents": 10000,
  "documents_by_type": {
    "invoice": 4000,
    "receipt": 3000,
    "contract": 2000,
    "other": 1000
  },
  "documents_by_status": {
    "uploaded": 100,
    "processing": 50,
    "processed": 9500,
    "archived": 350
  },
  "processing_metrics": {
    "average_processing_time": 45.2,
    "success_rate": 0.98,
    "ai_accuracy": 0.94
  },
  "trends": {
    "daily_uploads": [100, 120, 95, 110],
    "processing_volume": [95, 115, 100, 105]
  }
}
```

## 💰 Financial Management API

### **Chart of Accounts**

#### **List Accounts**
```http
GET /api/v1/financial/accounts
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
Query Parameters:
- type: asset|liability|equity|revenue|expense
- parent_id: uuid
- active: true|false
```

**Response:**
```json
{
  "accounts": [
    {
      "id": "uuid",
      "account_number": "1000",
      "name": "Cash",
      "type": "asset",
      "parent_id": null,
      "balance": 50000.00,
      "currency": "USD",
      "active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "size": 20
}
```

#### **Create Account**
```http
POST /api/v1/financial/accounts
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
Content-Type: application/json

{
  "account_number": "1100",
  "name": "Accounts Receivable",
  "type": "asset",
  "parent_id": "uuid",
  "currency": "USD",
  "description": "Amounts owed by customers"
}
```

#### **Get Account Details**
```http
GET /api/v1/financial/accounts/{account_id}
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
```

#### **Update Account**
```http
PUT /api/v1/financial/accounts/{account_id}
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
Content-Type: application/json

{
  "name": "Updated Account Name",
  "description": "Updated description"
}
```

### **Journal Entries**

#### **List Journal Entries**
```http
GET /api/v1/financial/journal-entries
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
Query Parameters:
- page: 1
- size: 20
- date_from: 2024-01-01
- date_to: 2024-12-31
- account_id: uuid
- amount_min: 100
- amount_max: 10000
```

**Response:**
```json
{
  "journal_entries": [
    {
      "id": "uuid",
      "entry_number": "JE-2024-001",
      "date": "2024-01-01",
      "description": "Monthly rent payment",
      "total_amount": 5000.00,
      "currency": "USD",
      "status": "posted",
      "lines": [
        {
          "account_id": "uuid",
          "account_name": "Rent Expense",
          "debit": 5000.00,
          "credit": 0.00,
          "description": "Monthly rent"
        },
        {
          "account_id": "uuid",
          "account_name": "Cash",
          "debit": 0.00,
          "credit": 5000.00,
          "description": "Cash payment"
        }
      ],
      "created_at": "2024-01-01T00:00:00Z",
      "posted_at": "2024-01-01T00:05:00Z"
    }
  ],
  "total": 500,
  "page": 1,
  "size": 20
}
```

#### **Create Journal Entry**
```http
POST /api/v1/financial/journal-entries
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
Content-Type: application/json

{
  "date": "2024-01-01",
  "description": "Monthly rent payment",
  "lines": [
    {
      "account_id": "uuid",
      "debit": 5000.00,
      "credit": 0.00,
      "description": "Monthly rent"
    },
    {
      "account_id": "uuid",
      "debit": 0.00,
      "credit": 5000.00,
      "description": "Cash payment"
    }
  ],
  "reference": "RENT-2024-01",
  "notes": "Monthly office rent payment"
}
```

#### **Post Journal Entry**
```http
POST /api/v1/financial/journal-entries/{entry_id}/post
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
```

#### **Void Journal Entry**
```http
POST /api/v1/financial/journal-entries/{entry_id}/void
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
Content-Type: application/json

{
  "reason": "Entry was created in error",
  "reversal_date": "2024-01-01"
}
```

### **Financial Reports**

#### **Trial Balance**
```http
GET /api/v1/financial/reports/trial-balance
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
Query Parameters:
- date: 2024-01-31
- include_zero_balances: true|false
```

**Response:**
```json
{
  "report_date": "2024-01-31",
  "accounts": [
    {
      "account_number": "1000",
      "account_name": "Cash",
      "type": "asset",
      "debit_balance": 50000.00,
      "credit_balance": 0.00,
      "net_balance": 50000.00
    }
  ],
  "totals": {
    "debits": 150000.00,
    "credits": 150000.00,
    "net": 0.00
  },
  "generated_at": "2024-01-31T23:59:59Z"
}
```

#### **Income Statement**
```http
GET /api/v1/financial/reports/income-statement
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
Query Parameters:
- period: month|quarter|year
- start_date: 2024-01-01
- end_date: 2024-12-31
```

#### **Balance Sheet**
```http
GET /api/v1/financial/reports/balance-sheet
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
Query Parameters:
- date: 2024-12-31
```

## 🤖 AI Analytics API

### **Predictive Analytics**

#### **Financial Trends**
```http
POST /api/v1/ai-analytics/predictions/financial-trends
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
Content-Type: application/json

{
  "metric": "revenue",
  "period": "monthly",
  "forecast_periods": 12,
  "confidence_level": 0.95,
  "include_seasonality": true
}
```

**Response:**
```json
{
  "metric": "revenue",
  "forecast": [
    {
      "period": "2024-02",
      "predicted_value": 125000.00,
      "confidence_interval": {
        "lower": 115000.00,
        "upper": 135000.00
      },
      "trend": "increasing",
      "growth_rate": 0.15
    }
  ],
  "trend_analysis": {
    "overall_trend": "increasing",
    "average_growth_rate": 0.12,
    "seasonality_detected": true,
    "confidence_score": 0.89
  },
  "generated_at": "2024-01-31T23:59:59Z"
}
```

#### **Anomaly Detection**
```http
POST /api/v1/ai-analytics/anomalies/detect
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
Content-Type: application/json

{
  "data_type": "financial_transactions",
  "time_period": "last_30_days",
  "sensitivity": "medium",
  "include_context": true
}
```

**Response:**
```json
{
  "anomalies": [
    {
      "id": "uuid",
      "type": "high_value_transaction",
      "severity": "high",
      "description": "Unusually high invoice amount",
      "detected_at": "2024-01-31T23:59:59Z",
      "context": {
        "transaction_id": "uuid",
        "amount": 50000.00,
        "normal_range": [1000.00, 10000.00],
        "confidence": 0.95
      },
      "recommendations": [
        "Review transaction details",
        "Verify vendor authenticity",
        "Check approval workflow"
      ]
    }
  ],
  "summary": {
    "total_anomalies": 5,
    "high_severity": 2,
    "medium_severity": 2,
    "low_severity": 1,
    "detection_confidence": 0.92
  }
}
```

### **Business Insights**

#### **Financial Health Score**
```http
GET /api/v1/ai-analytics/insights/financial-health
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
Query Parameters:
- period: month|quarter|year
- include_recommendations: true|false
```

**Response:**
```json
{
  "health_score": 85,
  "score_breakdown": {
    "liquidity": 90,
    "profitability": 85,
    "efficiency": 80,
    "growth": 85
  },
  "key_metrics": {
    "current_ratio": 2.5,
    "debt_to_equity": 0.3,
    "return_on_equity": 0.15,
    "cash_flow_margin": 0.12
  },
  "trends": {
    "score_trend": "improving",
    "improvement_rate": 0.05,
    "key_improvements": [
      "Increased cash reserves",
      "Reduced debt levels",
      "Improved profit margins"
    ]
  },
  "recommendations": [
    "Consider increasing marketing spend to accelerate growth",
    "Monitor inventory levels to improve efficiency",
    "Evaluate expansion opportunities given strong financial position"
  ],
  "generated_at": "2024-01-31T23:59:59Z"
}
```

#### **Document Processing Insights**
```http
GET /api/v1/ai-analytics/insights/document-processing
Authorization: Bearer <access_token>
X-Company-ID: {company_id}
Query Parameters:
- period: week|month|quarter
- include_optimization_tips: true|false
```

## 📊 System Monitoring API

### **Health Checks**

#### **System Health**
```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-31T23:59:59Z",
  "services": {
    "database": {
      "status": "healthy",
      "response_time": 15,
      "connections": 5
    },
    "cache": {
      "status": "healthy",
      "hit_rate": 0.85,
      "memory_usage": "512MB"
    },
    "ai_models": {
      "status": "healthy",
      "active_models": 3,
      "queue_length": 0
    }
  },
  "system": {
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "disk_usage": 23.4,
    "uptime": "7 days, 12 hours"
  }
}
```

#### **Detailed Health Check**
```http
GET /api/v1/health/detailed
Authorization: Bearer <access_token>
```

### **Performance Metrics**

#### **System Performance**
```http
GET /api/v1/metrics/system
Authorization: Bearer <access_token>
Query Parameters:
- period: hour|day|week
- include_history: true|false
```

#### **API Performance**
```http
GET /api/v1/metrics/api
Authorization: Bearer <access_token>
Query Parameters:
- endpoint: /documents
- period: hour|day|week
- include_response_times: true|false
```

## 🔧 Error Handling

### **Error Response Format**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ],
    "timestamp": "2024-01-31T23:59:59Z",
    "request_id": "uuid"
  }
}
```

### **Common Error Codes**
- `AUTHENTICATION_ERROR`: Invalid or expired token
- `AUTHORIZATION_ERROR`: Insufficient permissions
- `VALIDATION_ERROR`: Invalid input data
- `NOT_FOUND`: Resource not found
- `CONFLICT`: Resource conflict
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Server error

### **Rate Limiting**
- **Standard Users**: 100 requests per minute
- **Managers**: 500 requests per minute
- **Admins**: 1000 requests per minute
- **GOD Account**: Unlimited

## 📝 API Versioning

### **Version Information**
- **Current Version**: v1
- **Base URL**: `/api/v1/`
- **Deprecation Policy**: 12 months notice for breaking changes
- **Backward Compatibility**: Maintained within major versions

### **Version Headers**
```http
Accept: application/vnd.vanta-ledger.v1+json
X-API-Version: v1
```

## 🔗 SDKs & Libraries

### **Official SDKs**
- **Python**: `pip install vanta-ledger-sdk`
- **JavaScript/Node.js**: `npm install vanta-ledger-sdk`
- **Java**: Maven dependency available
- **C#**: NuGet package available

### **SDK Usage Example (Python)**
```python
from vanta_ledger import VantaLedger

# Initialize client
client = VantaLedger(
    base_url="https://api.vanta-ledger.com",
    api_key="your_api_key",
    company_id="your_company_id"
)

# Upload document
document = client.documents.upload(
    file_path="invoice.pdf",
    document_type="invoice",
    tags=["urgent", "high_priority"]
)

# Get financial insights
insights = client.ai_analytics.get_financial_health()
print(f"Financial Health Score: {insights.health_score}")
```

## 📚 Additional Resources

### **Interactive Documentation**
- **Swagger UI**: `/api/v1/docs`
- **ReDoc**: `/api/v1/redoc`
- **OpenAPI Spec**: `/api/v1/openapi.json`

### **Code Examples**
- **GitHub Repository**: [vanta-ledger-examples](https://github.com/vanta-ledger/examples)
- **Postman Collection**: Available in repository
- **cURL Examples**: Included in this documentation

### **Support & Community**
- **API Status**: [status.vanta-ledger.com](https://status.vanta-ledger.com)
- **Developer Forum**: [forum.vanta-ledger.com](https://forum.vanta-ledger.com)
- **GitHub Issues**: [Report bugs and request features](https://github.com/vanta-ledger/vanta-ledger/issues)

---

**📚 This comprehensive API documentation provides everything needed to integrate with and utilize the Vanta Ledger platform.**
