# 🔍 Semantic Search Guide
## Paperless-AI-Inspired Intelligent Document Search and AI-Assisted Tagging

**Version**: 1.0  
**Feature**: Phase 1.3 - Semantic Search  
**Inspired By**: Paperless-AI  
**Status**: Production Ready

---

## 📋 Overview

Semantic Search in Vanta Ledger provides **intelligent document search and AI-assisted tagging capabilities** inspired by Paperless-AI. This feature enables natural language querying, semantic understanding, and automated document categorization.

### **Key Benefits**
- ✅ **Semantic Understanding**: Natural language search with meaning comprehension
- ✅ **AI-Assisted Tagging**: Automatic document categorization and tagging
- ✅ **Search Suggestions**: Intelligent query suggestions and autocomplete
- ✅ **Search Analytics**: Popular searches and trending topics
- ✅ **Relevance Scoring**: Intelligent ranking of search results

---

## 🏗️ Architecture

### **Core Components**

#### **1. Semantic Search Service**
```python
# backend/src/vanta_ledger/services/semantic_search_service.py
class SemanticSearchService:
    """Semantic search and AI-assisted tagging service inspired by Paperless-AI"""
    
    async def semantic_search(
        self,
        query: str,
        company_id: UUID,
        user_id: UUID,
        filters: Dict[str, Any] = None,
        limit: int = 20,
        threshold: float = 0.3
    ) -> Dict[str, Any]:
        """Perform semantic search on documents"""
```

#### **2. Database Schema**
```sql
-- Document embeddings table
CREATE TABLE document_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL,
    embedding_type VARCHAR(100) NOT NULL,
    embedding JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Search index table
CREATE TABLE search_index (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    search_term TEXT NOT NULL,
    document_id UUID NOT NULL,
    relevance_score DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI tags table
CREATE TABLE ai_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL,
    tag VARCHAR(255) NOT NULL,
    tag_type VARCHAR(100),
    confidence_score DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Search history table
CREATE TABLE search_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    company_id UUID NOT NULL,
    search_query TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **3. API Endpoints**
```
POST /api/v1/semantic-search/search          # Perform semantic search
POST /api/v1/semantic-search/generate-tags   # Generate AI tags
GET  /api/v1/semantic-search/suggestions     # Get search suggestions
GET  /api/v1/semantic-search/popular         # Get popular searches
GET  /api/v1/semantic-search/capabilities    # Get search capabilities
POST /api/v1/semantic-search/batch-tag       # Batch tag generation
GET  /api/v1/semantic-search/health          # Health check
```

---

## 🚀 Usage Examples

### **1. Semantic Search**

#### **Natural Language Search**
```python
import requests

# Perform semantic search
response = requests.post(
    "http://localhost:8000/api/v1/semantic-search/search",
    json={
        "query": "Show me all invoices over $10,000 from last month",
        "filters": {
            "date_from": "2024-01-01",
            "date_to": "2024-01-31",
            "document_type": "invoice"
        },
        "limit": 20,
        "threshold": 0.5
    },
    params={"company_id": "your-company-uuid"},
    headers={"Authorization": "Bearer your-token"}
)

print(response.json())
# {
#   "query": "Show me all invoices over $10,000 from last month",
#   "results": [
#     {
#       "document": {...},
#       "similarity": 0.85,
#       "relevance_score": 0.85,
#       "matches": 3
#     }
#   ],
#   "total_found": 5,
#   "search_time": 0.15,
#   "filters_applied": {...},
#   "search_method": "semantic"
# }
```

### **2. AI-Assisted Tagging**

#### **Generate Tags for Document**
```python
# Generate AI tags for a document
response = requests.post(
    "http://localhost:8000/api/v1/semantic-search/generate-tags",
    json={
        "document_id": "your-document-uuid"
    },
    headers={"Authorization": "Bearer your-token"}
)

print(response.json())
# {
#   "document_id": "uuid",
#   "tags": [
#     {
#       "tag": "invoice",
#       "confidence": 0.92,
#       "tag_type": "ai_generated"
#     },
#     {
#       "tag": "financial",
#       "confidence": 0.88,
#       "tag_type": "ai_generated"
#     },
#     {
#       "tag": "urgent",
#       "confidence": 0.75,
#       "tag_type": "ai_generated"
#     }
#   ],
#   "generation_method": "ai",
#   "timestamp": "2024-01-01T00:00:00Z"
# }
```

### **3. Search Suggestions**

#### **Get Intelligent Suggestions**
```python
# Get search suggestions
response = requests.get(
    "http://localhost:8000/api/v1/semantic-search/suggestions",
    params={
        "partial_query": "invo",
        "company_id": "your-company-uuid"
    },
    headers={"Authorization": "Bearer your-token"}
)

print(response.json())
# {
#   "suggestions": [
#     "invoice payment",
#     "invoice processing",
#     "invoice approval",
#     "invoice status",
#     "invoice amount"
#   ],
#   "partial_query": "invo"
# }
```

### **4. Popular Searches**

#### **Get Trending Topics**
```python
# Get popular searches
response = requests.get(
    "http://localhost:8000/api/v1/semantic-search/popular",
    params={
        "company_id": "your-company-uuid",
        "days": 30
    },
    headers={"Authorization": "Bearer your-token"}
)

print(response.json())
# {
#   "popular_searches": [
#     {"query": "invoice payment", "count": 45},
#     {"query": "expense report", "count": 32},
#     {"query": "contract review", "count": 28},
#     {"query": "financial statement", "count": 25},
#     {"query": "tax documents", "count": 22}
#   ],
#   "days": 30
# }
```

### **5. Batch Tagging**

#### **Tag Multiple Documents**
```python
# Batch tag generation
response = requests.post(
    "http://localhost:8000/api/v1/semantic-search/batch-tag",
    json=[
        "doc-uuid-1",
        "doc-uuid-2",
        "doc-uuid-3"
    ],
    headers={"Authorization": "Bearer your-token"}
)

print(response.json())
# {
#   "success": true,
#   "batch_results": [...],
#   "total_documents": 3,
#   "successful_tagging": 3,
#   "failed_tagging": 0
# }
```

---

## 🔍 API Reference

### **Semantic Search**
```http
POST /api/v1/semantic-search/search
Content-Type: application/json
Authorization: Bearer <token>

{
  "query": "Show me all invoices over $10,000",
  "filters": {
    "date_from": "2024-01-01",
    "date_to": "2024-01-31",
    "document_type": "invoice"
  },
  "limit": 20,
  "threshold": 0.5
}
```

**Response:**
```json
{
  "query": "Show me all invoices over $10,000",
  "results": [
    {
      "document": {...},
      "similarity": 0.85,
      "relevance_score": 0.85,
      "matches": 3
    }
  ],
  "total_found": 5,
  "search_time": 0.15,
  "filters_applied": {...},
  "search_method": "semantic"
}
```

### **Generate AI Tags**
```http
POST /api/v1/semantic-search/generate-tags
Content-Type: application/json
Authorization: Bearer <token>

{
  "document_id": "uuid"
}
```

**Response:**
```json
{
  "document_id": "uuid",
  "tags": [
    {
      "tag": "invoice",
      "confidence": 0.92,
      "tag_type": "ai_generated"
    }
  ],
  "generation_method": "ai",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### **Search Suggestions**
```http
GET /api/v1/semantic-search/suggestions?partial_query=invo&company_id=uuid
Authorization: Bearer <token>
```

**Response:**
```json
{
  "suggestions": ["invoice payment", "invoice processing"],
  "partial_query": "invo"
}
```

---

## 🛡️ Error Handling

### **Common Error Scenarios**

#### **1. Invalid Search Query**
```json
{
  "detail": "Search query cannot be empty"
}
```

#### **2. Document Not Found**
```json
{
  "detail": "Document not found"
}
```

#### **3. Access Denied**
```json
{
  "detail": "Access denied to specified company"
}
```

#### **4. Search Failed**
```json
{
  "detail": "Failed to perform semantic search: ML model not available"
}
```

### **Error Response Format**
```json
{
  "type": "about:blank",
  "title": "Bad Request",
  "status": 400,
  "detail": "Invalid search parameters",
  "instance": "/api/v1/semantic-search/search",
  "request_id": "uuid"
}
```

---

## 🔧 Configuration

### **Search Parameters**
```python
# Available search parameters
SEARCH_PARAMETERS = {
    "query": str,              # Search query (required)
    "filters": dict,           # Optional filters
    "limit": int,              # Max results (1-100)
    "threshold": float         # Similarity threshold (0.0-1.0)
}
```

### **AI Tagging Configuration**
```python
# AI tagging settings
TAGGING_CONFIG = {
    "confidence_threshold": 0.5,    # Minimum confidence for tags
    "max_tags_per_document": 10,    # Maximum tags per document
    "candidate_labels": [           # Available tag categories
        "invoice", "receipt", "contract", "report", "statement",
        "financial", "legal", "tax", "expense", "income",
        "urgent", "important", "confidential", "draft", "final"
    ]
}
```

### **System Requirements**
```python
# Required dependencies
REQUIRED_PACKAGES = [
    "sentence-transformers",   # Semantic embeddings
    "scikit-learn",           # Similarity calculations
    "transformers",           # AI tagging models
    "torch",                  # PyTorch for ML
    "numpy"                   # Numerical operations
]
```

---

## 📊 Performance & Monitoring

### **Key Metrics**
- **Search Response Time**: <500ms average
- **Semantic Accuracy**: >85% relevance
- **Tagging Accuracy**: >80% for common document types
- **System Availability**: >99.5%
- **Cache Hit Rate**: >90% for embeddings

### **Health Check**
```http
GET /api/v1/semantic-search/health
```

**Response:**
```json
{
  "service": "semantic_search_service",
  "status": "healthy",
  "version": "1.0.0",
  "capabilities": {
    "semantic_available": true,
    "tagging_available": true,
    "embedding_model_loaded": true,
    "tagging_pipeline_loaded": true,
    "gpu_available": true
  },
  "features": [
    "semantic_search",
    "ai_tagging",
    "search_suggestions",
    "popular_searches",
    "search_analytics"
  ]
}
```

---

## 🧪 Testing

### **Test Semantic Search**
```python
# Test semantic search functionality
response = requests.post(
    "/api/v1/semantic-search/search",
    json={
        "query": "financial documents",
        "limit": 10
    },
    params={"company_id": "test-company-uuid"}
)

assert response.status_code == 200
result = response.json()
assert "results" in result
assert "search_method" in result
```

### **Test AI Tagging**
```python
# Test AI tagging functionality
response = requests.post(
    "/api/v1/semantic-search/generate-tags",
    json={"document_id": "test-document-uuid"}
)

assert response.status_code == 200
result = response.json()
assert "tags" in result
assert "generation_method" in result
```

---

## 🔄 Integration with Existing System

### **Enhanced Document Service Integration**
```python
# Semantic search integrates with existing document service
from vanta_ledger.services.enhanced_document_service import enhanced_document_service
from vanta_ledger.services.semantic_search_service import semantic_search_service

# Search documents semantically
search_results = await semantic_search_service.semantic_search(
    query="invoice payment",
    company_id=company_id,
    user_id=user_id
)

# Generate tags for documents
tags = await semantic_search_service.generate_ai_tags(document_id)
```

### **Advanced Document Processing Integration**
```python
# Combine with advanced document processing
from vanta_ledger.services.advanced_document_processor import advanced_document_processor

# Process document with advanced features
processing_results = await advanced_document_processor.process_complex_document(document)

# Generate semantic tags based on processed content
tags = await semantic_search_service.generate_ai_tags(document.id)
```

---

## 🚀 Best Practices

### **1. Search Strategy**
- **Use natural language**: Write queries as you would speak them
- **Set appropriate thresholds**: Higher thresholds for more precise results
- **Use filters**: Combine semantic search with structured filters
- **Monitor performance**: Track search response times and accuracy

### **2. Tagging Strategy**
- **Batch processing**: Use batch tagging for large document sets
- **Review generated tags**: Validate AI-generated tags for accuracy
- **Customize tag categories**: Adapt candidate labels to your business needs
- **Confidence thresholds**: Adjust confidence levels based on requirements

### **3. Performance Optimization**
- **Caching**: Leverage Redis caching for embeddings and results
- **Indexing**: Ensure proper database indexes for fast queries
- **GPU acceleration**: Use GPU when available for ML models
- **Batch operations**: Process multiple documents together

### **4. Security**
- **Access control**: Validate user permissions for all operations
- **Query validation**: Sanitize and validate search queries
- **Rate limiting**: Implement rate limiting for search operations
- **Audit logging**: Log all search activities for compliance

---

## 📚 Related Documentation

- [Vanta Ledger Improvement Roadmap](VANTA_LEDGER_IMPROVEMENT_ROADMAP.md)
- [Atomic Transactions Guide](ATOMIC_TRANSACTIONS_GUIDE.md)
- [Advanced Document Processing Guide](ADVANCED_DOCUMENT_PROCESSING_GUIDE.md)
- [API Documentation](04_API_DOCUMENTATION.md)
- [Database Schema](HYBRID_DATABASE_README.md)

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Next Review**: Monthly  
**Owner**: Development Team  
**Status**: Production Ready
