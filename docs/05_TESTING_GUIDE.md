# 🧪 Vanta Ledger Testing Guide

## 📋 Testing Overview

This guide provides comprehensive testing strategies, test cases, and procedures for ensuring Vanta Ledger meets NASA-grade quality standards. It covers unit testing, integration testing, performance testing, and security testing.

## 🎯 Testing Strategy

### **Testing Pyramid**
```
Testing Layers
├── 🧪 Unit Tests (70%)
│   ├── Individual component testing
│   ├── Function and method testing
│   ├── Model validation testing
│   └── Utility function testing
├── 🔗 Integration Tests (20%)
│   ├── API endpoint testing
│   ├── Database integration testing
│   ├── Service interaction testing
│   └── Cross-feature workflow testing
├── 🚀 Performance Tests (5%)
│   ├── Load testing
│   ├── Stress testing
│   ├── Endurance testing
│   └── Scalability testing
└── 🔐 Security Tests (5%)
    ├── Authentication testing
    ├── Authorization testing
    ├── Vulnerability scanning
    └── Penetration testing
```

### **Testing Objectives**
- **Quality Assurance**: Ensure system reliability and accuracy
- **Performance Validation**: Verify system performance under load
- **Security Verification**: Confirm security measures effectiveness
- **Compliance Testing**: Validate regulatory compliance
- **User Experience**: Ensure intuitive and efficient operation

## 🧪 Unit Testing

### **Test Structure**
```python
# Example Unit Test Structure
import pytest
from vanta_ledger.models.document_models import Document
from vanta_ledger.services.document_service import DocumentService

class TestDocumentService:
    def setup_method(self):
        """Setup test fixtures"""
        self.document_service = DocumentService()
        self.test_document = Document(
            filename="test.pdf",
            content="Test content",
            company_id="test_company"
        )
    
    def test_create_document(self):
        """Test document creation"""
        result = self.document_service.create_document(self.test_document)
        assert result.id is not None
        assert result.filename == "test.pdf"
        assert result.status == "uploaded"
    
    def test_document_validation(self):
        """Test document validation"""
        invalid_document = Document(
            filename="",  # Invalid: empty filename
            content="",   # Invalid: empty content
            company_id=""  # Invalid: empty company_id
        )
        
        with pytest.raises(ValueError):
            self.document_service.create_document(invalid_document)
    
    def test_document_search(self):
        """Test document search functionality"""
        # Create test documents
        doc1 = self.document_service.create_document(self.test_document)
        doc2 = Document(
            filename="test2.pdf",
            content="Another test",
            company_id="test_company"
        )
        doc2 = self.document_service.create_document(doc2)
        
        # Test search
        results = self.document_service.search_documents("test")
        assert len(results) == 2
        assert doc1.id in [r.id for r in results]
        assert doc2.id in [r.id for r in results]
```

### **Test Categories**

#### **Model Testing**
```python
# Test data models
def test_user_model_validation():
    """Test user model validation"""
    from vanta_ledger.models.user_models import User
    
    # Valid user
    valid_user = User(
        username="test@company.com",
        email="test@company.com",
        role="user",
        company_id="test_company"
    )
    assert valid_user.username == "test@company.com"
    
    # Invalid user (missing required fields)
    with pytest.raises(ValueError):
        User(username="", email="", role="", company_id="")

def test_financial_model_validation():
    """Test financial model validation"""
    from vanta_ledger.models.financial_models import JournalEntry
    
    # Valid journal entry
    valid_entry = JournalEntry(
        date="2024-01-01",
        description="Test entry",
        total_amount=100.00,
        company_id="test_company"
    )
    assert valid_entry.total_amount == 100.00
    
    # Invalid entry (negative amount)
    with pytest.raises(ValueError):
        JournalEntry(
            date="2024-01-01",
            description="Test entry",
            total_amount=-100.00,
            company_id="test_company"
        )
```

#### **Service Testing**
```python
# Test business logic services
def test_document_processing_service():
    """Test document processing service"""
    from vanta_ledger.services.document_service import DocumentService
    
    service = DocumentService()
    
    # Test document upload
    document = service.upload_document("test.pdf", "test content", "test_company")
    assert document.status == "uploaded"
    
    # Test document processing
    processed_doc = service.process_document(document.id)
    assert processed_doc.status == "processed"
    
    # Test document search
    results = service.search_documents("test", company_id="test_company")
    assert len(results) > 0

def test_financial_service():
    """Test financial service"""
    from vanta_ledger.services.financial_service import FinancialService
    
    service = FinancialService()
    
    # Test account creation
    account = service.create_account(
        account_number="1000",
        name="Cash",
        account_type="asset",
        company_id="test_company"
    )
    assert account.account_number == "1000"
    
    # Test journal entry creation
    entry = service.create_journal_entry(
        date="2024-01-01",
        description="Test entry",
        lines=[
            {"account_id": account.id, "debit": 100.00, "credit": 0.00}
        ],
        company_id="test_company"
    )
    assert entry.total_amount == 100.00
```

## 🔗 Integration Testing

### **API Endpoint Testing**
```python
# Test API endpoints
import pytest
from fastapi.testclient import TestClient
from vanta_ledger.main import app

client = TestClient(app)

class TestDocumentAPI:
    def test_create_document(self):
        """Test document creation API"""
        response = client.post(
            "/api/v1/documents",
            files={"file": ("test.pdf", b"test content")},
            data={"type": "invoice", "company_id": "test_company"},
            headers={"Authorization": "Bearer test_token"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["filename"] == "test.pdf"
        assert data["status"] == "uploaded"
    
    def test_get_documents(self):
        """Test document retrieval API"""
        response = client.get(
            "/api/v1/documents",
            headers={"Authorization": "Bearer test_token", "X-Company-ID": "test_company"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert "total" in data
    
    def test_document_processing(self):
        """Test document processing API"""
        # First create a document
        create_response = client.post(
            "/api/v1/documents",
            files={"file": ("test.pdf", b"test content")},
            data={"type": "invoice", "company_id": "test_company"},
            headers={"Authorization": "Bearer test_token"}
        )
        document_id = create_response.json()["id"]
        
        # Then process it
        process_response = client.post(
            f"/api/v1/documents/{document_id}/process",
            json={"ai_model": "auto"},
            headers={"Authorization": "Bearer test_token", "X-Company-ID": "test_company"}
        )
        assert process_response.status_code == 200
        data = process_response.json()
        assert data["status"] == "processing"
```

### **Database Integration Testing**
```python
# Test database integration
import pytest
from vanta_ledger.database.connection import get_database
from vanta_ledger.models.document_models import Document

class TestDatabaseIntegration:
    @pytest.fixture(autouse=True)
    def setup_database(self):
        """Setup test database"""
        self.db = get_database()
        # Create test collections
        self.db.documents.create_index([("company_id", 1)])
        yield
        # Cleanup test data
        self.db.documents.delete_many({})
    
    def test_document_storage(self):
        """Test document storage in database"""
        document = Document(
            filename="test.pdf",
            content="test content",
            company_id="test_company"
        )
        
        # Store document
        result = self.db.documents.insert_one(document.dict())
        assert result.inserted_id is not None
        
        # Retrieve document
        stored_doc = self.db.documents.find_one({"_id": result.inserted_id})
        assert stored_doc["filename"] == "test.pdf"
        assert stored_doc["company_id"] == "test_company"
    
    def test_company_isolation(self):
        """Test company data isolation"""
        # Create documents for different companies
        doc1 = Document(
            filename="company1.pdf",
            content="company1 content",
            company_id="company1"
        )
        doc2 = Document(
            filename="company2.pdf",
            content="company2 content",
            company_id="company2"
        )
        
        self.db.documents.insert_one(doc1.dict())
        self.db.documents.insert_one(doc2.dict())
        
        # Verify isolation
        company1_docs = list(self.db.documents.find({"company_id": "company1"}))
        company2_docs = list(self.db.documents.find({"company_id": "company2"}))
        
        assert len(company1_docs) == 1
        assert len(company2_docs) == 1
        assert company1_docs[0]["filename"] == "company1.pdf"
        assert company2_docs[0]["filename"] == "company2.pdf"
```

## 🚀 Performance Testing

### **Load Testing**
```python
# Performance testing with locust
from locust import HttpUser, task, between

class VantaLedgerUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login at start"""
        response = self.client.post("/api/v1/auth/login", json={
            "username": "test@company.com",
            "password": "test_password"
        })
        self.token = response.json()["access_token"]
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "X-Company-ID": "test_company"
        }
    
    @task(3)
    def get_documents(self):
        """Test document retrieval performance"""
        self.client.get("/api/v1/documents", headers=self.headers)
    
    @task(2)
    def create_document(self):
        """Test document creation performance"""
        self.client.post(
            "/api/v1/documents",
            files={"file": ("test.pdf", b"test content")},
            data={"type": "invoice"},
            headers=self.headers
        )
    
    @task(1)
    def get_financial_reports(self):
        """Test financial report generation performance"""
        self.client.get("/api/v1/financial/reports/trial-balance", headers=self.headers)
```

### **Performance Benchmarks**
```python
# Performance benchmark tests
import time
import pytest
from vanta_ledger.services.document_service import DocumentService

class TestPerformance:
    def test_document_processing_performance(self):
        """Test document processing performance"""
        service = DocumentService()
        
        # Measure processing time
        start_time = time.time()
        
        # Process multiple documents
        for i in range(100):
            document = service.upload_document(
                f"test_{i}.pdf",
                f"test content {i}",
                "test_company"
            )
            service.process_document(document.id)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Performance assertions
        assert processing_time < 60  # Should complete within 60 seconds
        assert processing_time / 100 < 0.6  # Average < 0.6 seconds per document
    
    def test_search_performance(self):
        """Test search performance"""
        service = DocumentService()
        
        # Create test documents
        for i in range(1000):
            service.upload_document(
                f"test_{i}.pdf",
                f"test content {i}",
                "test_company"
            )
        
        # Measure search performance
        start_time = time.time()
        results = service.search_documents("test", company_id="test_company")
        search_time = time.time() - start_time
        
        # Performance assertions
        assert search_time < 1.0  # Search should complete within 1 second
        assert len(results) == 1000  # Should find all documents
```

## 🔐 Security Testing

### **Authentication Testing**
```python
# Security testing
class TestSecurity:
    def test_authentication_bypass(self):
        """Test authentication bypass attempts"""
        client = TestClient(app)
        
        # Try to access protected endpoint without token
        response = client.get("/api/v1/documents")
        assert response.status_code == 401
        
        # Try with invalid token
        response = client.get(
            "/api/v1/documents",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
    
    def test_authorization_bypass(self):
        """Test authorization bypass attempts"""
        client = TestClient(app)
        
        # Login as regular user
        login_response = client.post("/api/v1/auth/login", json={
            "username": "user@company.com",
            "password": "user_password"
        })
        user_token = login_response.json()["access_token"]
        
        # Try to access admin endpoint
        response = client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 403
    
    def test_company_isolation_bypass(self):
        """Test company isolation bypass attempts"""
        client = TestClient(app)
        
        # Login as user from company1
        login_response = client.post("/api/v1/auth/login", json={
            "username": "user@company1.com",
            "password": "user_password"
        })
        user_token = login_response.json()["access_token"]
        
        # Try to access company2 data
        response = client.get(
            "/api/v1/documents",
            headers={"Authorization": f"Bearer {user_token}", "X-Company-ID": "company2"}
        )
        assert response.status_code == 403
```

### **Input Validation Testing**
```python
# Input validation testing
class TestInputValidation:
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        client = TestClient(app)
        
        # Try SQL injection in search
        malicious_input = "'; DROP TABLE users; --"
        response = client.get(
            f"/api/v1/documents?search={malicious_input}",
            headers={"Authorization": "Bearer test_token", "X-Company-ID": "test_company"}
        )
        
        # Should not crash and should handle gracefully
        assert response.status_code in [200, 400, 422]
    
    def test_xss_prevention(self):
        """Test XSS prevention"""
        client = TestClient(app)
        
        # Try XSS in document description
        malicious_input = "<script>alert('xss')</script>"
        response = client.post(
            "/api/v1/documents",
            files={"file": ("test.pdf", b"test content")},
            data={"description": malicious_input, "company_id": "test_company"},
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Should sanitize input
        if response.status_code == 201:
            doc_id = response.json()["id"]
            get_response = client.get(
                f"/api/v1/documents/{doc_id}",
                headers={"Authorization": "Bearer test_token", "X-Company-ID": "test_company"}
            )
            description = get_response.json()["description"]
            assert "<script>" not in description
```

## 📊 Test Coverage

### **Coverage Requirements**
```python
# Test coverage configuration
COVERAGE_CONFIG = {
    "minimum_coverage": 90,
    "exclude_patterns": [
        "*/tests/*",
        "*/migrations/*",
        "*/__pycache__/*",
        "*/venv/*"
    ],
    "coverage_types": [
        "statements",
        "branches",
        "functions",
        "lines"
    ]
}
```

### **Coverage Report**
```bash
# Generate coverage report
pytest --cov=vanta_ledger --cov-report=html --cov-report=term-missing

# View coverage report
open htmlcov/index.html
```

## 🚀 Continuous Testing

### **CI/CD Pipeline**
```yaml
# GitHub Actions workflow
name: Vanta Ledger Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r constraints.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest --cov=vanta_ledger --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml
```

### **Test Automation**
```bash
#!/bin/bash
# Automated testing script

echo "🧪 Running Vanta Ledger Tests"

# Run unit tests
echo "Running unit tests..."
pytest tests/unit/ -v --cov=vanta_ledger --cov-report=term-missing

# Run integration tests
echo "Running integration tests..."
pytest tests/integration/ -v

# Run performance tests
echo "Running performance tests..."
pytest tests/performance/ -v

# Run security tests
echo "Running security tests..."
pytest tests/security/ -v

# Generate coverage report
echo "Generating coverage report..."
pytest --cov=vanta_ledger --cov-report=html

echo "✅ All tests completed!"
```

## 📋 Test Checklist

### **Pre-Deployment Testing**
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Performance benchmarks met
- [ ] Security tests pass
- [ ] Coverage requirements met
- [ ] Manual testing completed
- [ ] User acceptance testing passed

### **Post-Deployment Testing**
- [ ] Smoke tests pass
- [ ] Health checks pass
- [ ] Performance monitoring active
- [ ] Error logging configured
- [ ] Backup systems tested
- [ ] Recovery procedures tested

---

**🧪 This comprehensive testing guide ensures Vanta Ledger maintains NASA-grade quality and reliability standards.**
