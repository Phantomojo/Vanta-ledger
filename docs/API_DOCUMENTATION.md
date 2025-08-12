# 📚 Vanta Ledger API Documentation

Complete API reference for the Vanta Ledger backend system.

## 🔐 Authentication

All API endpoints (except login/register) require authentication using JWT tokens.

### Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=YOUR_ADMIN_PASSWORD
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### Using Authentication
Include the token in the Authorization header:
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## 🏢 Companies

### List Companies
```http
GET /companies/
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Solopride Contractors & General Supplies Ltd",
    "registration_number": "C123456",
    "pin_number": "P123456789A",
    "phone": "+254729631861",
    "email": "info@solopride.com",
    "address": "P.O BOX 1092, NANYUKI",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "is_active": true
  }
]
```

### Create Company
```http
POST /companies/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "New Company Ltd",
  "registration_number": "C789012",
  "pin_number": "P987654321B",
  "phone": "+254700000000",
  "email": "info@newcompany.com",
  "address": "Nairobi, Kenya"
}
```

## 📁 Projects

### List Projects
```http
GET /projects/
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip`: Number of records to skip (pagination)
- `limit`: Number of records to return (max 100)
- `search`: Search term for project names
- `include_deleted`: Include soft-deleted projects

### Create Project
```http
POST /projects/
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "name": "Road Construction Project",
  "client": "Government of Kenya",
  "value": 50000000.00,
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "status": "active",
  "description": "Construction of major highway"
}
```

### Get Project Financial Summary
```http
GET /ledger/summary/{project_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "income": 45000000.00,
  "expenses": 35000000.00,
  "withdrawals": 5000000.00,
  "balance": 5000000.00
}
```

## 💰 Financial Management

### List Ledger Entries
```http
GET /ledger/
Authorization: Bearer <token>
```

**Query Parameters:**
- `skip`: Number of records to skip
- `limit`: Number of records to return
- `search`: Search in descriptions

### Add Financial Entry
```http
POST /ledger/
Authorization: Bearer <token>
Content-Type: application/json

{
  "company_id": 1,
  "project_id": 1,
  "type": "expense",
  "amount": 100000.00,
  "date": "2024-01-15",
  "description": "Purchase of construction materials"
}
```

**Entry Types:**
- `income`: Money received
- `expense`: Money spent
- `withdrawal`: Owner withdrawals

### Get Company Financial Summary
```http
GET /ledger/company/{company_id}
Authorization: Bearer <token>
```

## 📄 Document Management

### Upload Document
```http
POST /upload/document
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <file>
project_id: 1
company_id: 1
doc_type: invoice
notes: Monthly invoice for January
```

**Supported File Types:**
- PDF (.pdf)
- Word documents (.doc, .docx)
- Images (.jpg, .jpeg, .png)
- Text files (.txt)

### List Documents
```http
GET /upload/documents
Authorization: Bearer <token>
```

**Query Parameters:**
- `company_id`: Filter by company
- `project_id`: Filter by project
- `doc_type`: Filter by document type

## 👥 User Management

### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "username": "newuser",
  "name": "John Doe",
  "email": "john@company.com",
  "password": "securepassword123",
  "role": "user"
}
```

### Get Current User
```http
GET /auth/me
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "username": "admin",
  "name": "System Administrator",
  "email": "admin@vantaledger.com",
  "role": "admin",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-15T10:30:00Z"
}
```

## 📊 Analytics

### Get Dashboard Analytics
```http
GET /analytics/dashboard
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total_projects": 15,
  "active_projects": 8,
  "total_companies": 3,
  "total_documents": 1250,
  "total_income": 150000000.00,
  "total_expenses": 120000000.00,
  "monthly_trends": {
    "income": [10000000, 12000000, 15000000],
    "expenses": [8000000, 10000000, 12000000]
  }
}
```

## 🔍 Search and Filtering

### Search Projects
```http
GET /projects/?search=road&limit=10
Authorization: Bearer <token>
```

### Filter Documents by Type
```http
GET /upload/documents?doc_type=invoice&company_id=1
Authorization: Bearer <token>
```

### Date Range Filtering
```http
GET /ledger/?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer <token>
```

## 📝 Error Handling

### Standard Error Response
```json
{
  "detail": "Error message description"
}
```

### Common HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

### Validation Error Example
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## 🔄 Pagination

Most list endpoints support pagination:

```http
GET /projects/?skip=20&limit=10
```

**Response includes pagination info:**
```json
{
  "items": [...],
  "total": 150,
  "page": 3,
  "pages": 15,
  "has_next": true,
  "has_prev": true
}
```

## 📡 WebSocket Support

### Real-time Updates
```javascript
const ws = new WebSocket('ws://localhost:8500/ws');

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Real-time update:', data);
};
```

## 🔧 Rate Limiting

- **Authentication endpoints**: 5 requests per minute
- **API endpoints**: 100 requests per minute
- **File uploads**: 10 requests per minute

## 📋 Testing

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "message": "Vanta Ledger API is operational",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

### Database Status
```http
GET /health/db
```

## 🚀 Development

### Running in Development Mode
```bash
python run_backend.py
```

### API Documentation
- Interactive docs: `http://localhost:8500/docs`
- ReDoc: `http://localhost:8500/redoc`

### Environment Variables
See `env.example` for all available configuration options.

---

For more information, visit the main README or contact the development team. 