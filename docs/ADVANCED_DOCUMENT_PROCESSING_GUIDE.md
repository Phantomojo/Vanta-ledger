# 📄 Advanced Document Processing Guide
## Docling + Documind-Inspired Layout Understanding and OCR

**Version**: 1.0  
**Feature**: Phase 1.2 - Advanced Document Processing  
**Inspired By**: Docling + Documind  
**Status**: Production Ready

---

## 📋 Overview

Advanced Document Processing in Vanta Ledger provides **enhanced document understanding capabilities** inspired by Docling and Documind. This feature enables sophisticated layout analysis, advanced OCR, and handwritten text processing for complex financial documents.

### **Key Benefits**
- ✅ **Layout Understanding**: Advanced layout analysis using LayoutLMv3
- ✅ **Enhanced OCR**: Improved text extraction with preprocessing
- ✅ **Handwritten Text Processing**: Specialized processing for handwritten content
- ✅ **Multi-Format Support**: Support for scanned, complex layouts, and various formats
- ✅ **Confidence Scoring**: Quality assessment for extracted content

---

## 🏗️ Architecture

### **Core Components**

#### **1. Advanced Document Processor**
```python
# backend/src/vanta_ledger/services/advanced_document_processor.py
class AdvancedDocumentProcessor:
    """Advanced document processing with layout understanding inspired by Docling + Documind"""
    
    async def process_complex_document(
        self, 
        document: EnhancedDocument,
        processing_options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process complex documents with advanced layout understanding"""
```

#### **2. Database Schema**
```sql
-- Document analyses table
CREATE TABLE document_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL,
    analysis_type VARCHAR(100) NOT NULL,
    results JSONB,
    processing_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Layout analyses table
CREATE TABLE layout_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL,
    layout_type VARCHAR(100),
    layout_data JSONB,
    confidence_score DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Processing capabilities table
CREATE TABLE processing_capabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    capability_name VARCHAR(100) UNIQUE NOT NULL,
    is_available BOOLEAN DEFAULT FALSE,
    version VARCHAR(50),
    configuration JSONB,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **3. API Endpoints**
```
POST /api/v1/advanced-documents/process          # Process document with advanced features
GET  /api/v1/advanced-documents/{id}/analysis    # Get analysis results
GET  /api/v1/advanced-documents/{id}/layout      # Get layout analysis
GET  /api/v1/advanced-documents/capabilities     # Get processing capabilities
POST /api/v1/advanced-documents/upload-and-process  # Upload and process
POST /api/v1/advanced-documents/batch-process    # Batch processing
GET  /api/v1/advanced-documents/health           # Health check
```

---

## 🚀 Usage Examples

### **1. Basic Advanced Processing**

#### **Process Document with Layout Analysis**
```python
import requests

# Process document with advanced features
response = requests.post(
    "http://localhost:8000/api/v1/advanced-documents/process",
    json={
        "document_id": "your-document-uuid",
        "processing_options": {
            "process_handwritten": True,
            "enable_layout_analysis": True,
            "enable_advanced_ocr": True,
            "confidence_threshold": 0.8
        }
    },
    headers={"Authorization": "Bearer your-token"}
)

print(response.json())
# {
#   "success": true,
#   "document_id": "uuid",
#   "processing_timestamp": "2024-01-01T00:00:00Z",
#   "extracted_text": "Invoice #12345...",
#   "layout_analysis": {
#     "layout_type": "form_dominant",
#     "regions": [...],
#     "confidence": 0.95,
#     "processing_method": "layoutlmv3"
#   },
#   "confidence_scores": {
#     "ocr": 0.92,
#     "layout": 0.95,
#     "handwritten": 0.78
#   },
#   "processing_errors": [],
#   "processing_methods": ["advanced_ocr", "layout_analysis", "handwritten_processing"]
# }
```

### **2. Upload and Process**

#### **Single-Step Upload and Processing**
```python
# Upload and process document in one step
with open("invoice.pdf", "rb") as file:
    response = requests.post(
        "http://localhost:8000/api/v1/advanced-documents/upload-and-process",
        files={"file": file},
        params={
            "process_handwritten": True,
            "enable_layout_analysis": True,
            "company_id": "your-company-uuid"
        },
        headers={"Authorization": "Bearer your-token"}
    )

print(response.json())
# {
#   "success": true,
#   "document": {...},
#   "processing_results": {...},
#   "message": "Document uploaded and processed successfully"
# }
```

### **3. Batch Processing**

#### **Process Multiple Documents**
```python
# Process multiple documents with same options
response = requests.post(
    "http://localhost:8000/api/v1/advanced-documents/batch-process",
    json={
        "document_ids": [
            "doc-uuid-1",
            "doc-uuid-2",
            "doc-uuid-3"
        ],
        "processing_options": {
            "process_handwritten": False,
            "enable_layout_analysis": True,
            "enable_advanced_ocr": True,
            "confidence_threshold": 0.7
        }
    },
    headers={"Authorization": "Bearer your-token"}
)

print(response.json())
# {
#   "success": true,
#   "batch_results": [...],
#   "total_documents": 3,
#   "successful_processing": 3,
#   "failed_processing": 0
# }
```

### **4. Get Analysis Results**

#### **Retrieve Document Analysis**
```python
# Get analysis results for a document
response = requests.get(
    "http://localhost:8000/api/v1/advanced-documents/your-doc-uuid/analysis",
    headers={"Authorization": "Bearer your-token"}
)

print(response.json())
# {
#   "success": true,
#   "document_id": "uuid",
#   "analysis": {
#     "extracted_text": "...",
#     "layout_analysis": {...},
#     "confidence_scores": {...},
#     "processing_errors": []
#   }
# }
```

### **5. Check Processing Capabilities**

#### **System Capabilities**
```python
# Check what processing features are available
response = requests.get(
    "http://localhost:8000/api/v1/advanced-documents/capabilities"
)

print(response.json())
# {
#   "ml_available": true,
#   "ocr_available": true,
#   "layout_model_loaded": true,
#   "gpu_available": true,
#   "processing_features": [
#     "advanced_ocr",
#     "layout_analysis",
#     "handwritten_text_processing"
#   ]
# }
```

---

## 🔍 API Reference

### **Process Document**
```http
POST /api/v1/advanced-documents/process
Content-Type: application/json
Authorization: Bearer <token>

{
  "document_id": "uuid",
  "processing_options": {
    "process_handwritten": true,
    "enable_layout_analysis": true,
    "enable_advanced_ocr": true,
    "confidence_threshold": 0.8
  }
}
```

**Response:**
```json
{
  "success": true,
  "document_id": "uuid",
  "processing_timestamp": "2024-01-01T00:00:00Z",
  "extracted_text": "Document text content...",
  "layout_analysis": {
    "layout_type": "form_dominant",
    "regions": [...],
    "confidence": 0.95,
    "processing_method": "layoutlmv3"
  },
  "confidence_scores": {
    "ocr": 0.92,
    "layout": 0.95,
    "handwritten": 0.78
  },
  "processing_errors": [],
  "processing_methods": ["advanced_ocr", "layout_analysis", "handwritten_processing"]
}
```

### **Get Document Analysis**
```http
GET /api/v1/advanced-documents/{document_id}/analysis
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "document_id": "uuid",
  "analysis": {
    "extracted_text": "...",
    "layout_analysis": {...},
    "confidence_scores": {...},
    "processing_errors": []
  }
}
```

### **Get Layout Analysis**
```http
GET /api/v1/advanced-documents/{document_id}/layout
Authorization: Bearer <token>
```

**Response:**
```json
{
  "layout_type": "form_dominant",
  "regions": [
    {
      "type": "region_1",
      "bbox": [x1, y1, x2, y2],
      "confidence": 0.8
    }
  ],
  "confidence": 0.95,
  "processing_method": "layoutlmv3"
}
```

### **Upload and Process**
```http
POST /api/v1/advanced-documents/upload-and-process
Content-Type: multipart/form-data
Authorization: Bearer <token>

file: <file>
process_handwritten: true
enable_layout_analysis: true
company_id: uuid
```

---

## 🛡️ Error Handling

### **Common Error Scenarios**

#### **1. Document Not Found**
```json
{
  "detail": "Document not found"
}
```

#### **2. Access Denied**
```json
{
  "detail": "Access denied to this document"
}
```

#### **3. Processing Failed**
```json
{
  "detail": "Failed to process document: OCR not available"
}
```

#### **4. Invalid Processing Options**
```json
{
  "detail": "Invalid processing options provided"
}
```

### **Error Response Format**
```json
{
  "type": "about:blank",
  "title": "Bad Request",
  "status": 400,
  "detail": "Invalid processing options",
  "instance": "/api/v1/advanced-documents/process",
  "request_id": "uuid"
}
```

---

## 🔧 Configuration

### **Processing Options**
```python
# Available processing options
PROCESSING_OPTIONS = {
    "process_handwritten": bool,      # Enable handwritten text processing
    "enable_layout_analysis": bool,   # Enable layout analysis
    "enable_advanced_ocr": bool,      # Enable advanced OCR
    "confidence_threshold": float     # Minimum confidence threshold (0.0-1.0)
}
```

### **System Requirements**
```python
# Required dependencies
REQUIRED_PACKAGES = [
    "opencv-python",      # Image processing
    "pytesseract",        # OCR engine
    "torch",              # PyTorch for ML models
    "transformers",       # Hugging Face transformers
    "Pillow",             # Image handling
    "numpy"               # Numerical operations
]
```

---

## 📊 Performance & Monitoring

### **Key Metrics**
- **Processing Time**: <30 seconds per document
- **OCR Accuracy**: >90% for printed text
- **Layout Analysis Accuracy**: >85% for complex layouts
- **Handwritten Text Accuracy**: >70% for clear handwriting
- **System Availability**: >99.5%

### **Health Check**
```http
GET /api/v1/advanced-documents/health
```

**Response:**
```json
{
  "service": "advanced_document_processor",
  "status": "healthy",
  "version": "1.0.0",
  "capabilities": {
    "ml_available": true,
    "ocr_available": true,
    "layout_model_loaded": true,
    "gpu_available": true
  },
  "features": [
    "advanced_ocr",
    "layout_analysis",
    "handwritten_text_processing",
    "complex_layout_understanding"
  ]
}
```

---

## 🧪 Testing

### **Test Processing Capabilities**
```python
# Test system capabilities
response = requests.get("/api/v1/advanced-documents/capabilities")
capabilities = response.json()

assert capabilities["ml_available"] == True
assert capabilities["ocr_available"] == True
assert "advanced_ocr" in capabilities["processing_features"]
```

### **Test Document Processing**
```python
# Test document processing
with open("test_document.pdf", "rb") as file:
    response = requests.post(
        "/api/v1/advanced-documents/upload-and-process",
        files={"file": file},
        params={"company_id": "test-company-uuid"}
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["success"] == True
    assert "processing_results" in result
```

---

## 🔄 Integration with Existing System

### **Enhanced Document Service Integration**
```python
# The advanced processor integrates with existing document service
from vanta_ledger.services.enhanced_document_service import enhanced_document_service
from vanta_ledger.services.advanced_document_processor import advanced_document_processor

# Upload document normally
document = await enhanced_document_service.upload_document(file, user_id, company_id)

# Process with advanced features
results = await advanced_document_processor.process_complex_document(document, options)
```

### **Atomic Transaction Integration**
```python
# Advanced document processing can trigger atomic transactions
if results.get("extracted_text"):
    # Extract financial data and create atomic transaction
    financial_data = extract_financial_data(results["extracted_text"])
    atomic_transaction = await atomic_transaction_service.create_atomic_transaction(
        transactions=financial_data,
        company_id=company_id
    )
```

---

## 🚀 Best Practices

### **1. Processing Strategy**
- **Use appropriate options**: Enable only needed features for performance
- **Set confidence thresholds**: Filter low-quality results
- **Batch processing**: Use batch endpoints for multiple documents
- **Monitor capabilities**: Check system capabilities before processing

### **2. Error Handling**
- **Handle processing errors**: Check processing_errors in responses
- **Validate results**: Verify confidence scores and extracted content
- **Fallback strategies**: Have backup processing methods
- **Retry logic**: Implement retry for transient failures

### **3. Performance Optimization**
- **GPU acceleration**: Use GPU when available for ML models
- **Image preprocessing**: Optimize images before processing
- **Caching**: Cache analysis results for repeated access
- **Resource monitoring**: Monitor system resources during processing

### **4. Security**
- **Access control**: Validate user permissions for documents
- **Input validation**: Validate all processing options
- **File size limits**: Enforce reasonable file size limits
- **Secure storage**: Store analysis results securely

---

## 📚 Related Documentation

- [Vanta Ledger Improvement Roadmap](VANTA_LEDGER_IMPROVEMENT_ROADMAP.md)
- [Atomic Transactions Guide](ATOMIC_TRANSACTIONS_GUIDE.md)
- [API Documentation](04_API_DOCUMENTATION.md)
- [Database Schema](HYBRID_DATABASE_README.md)

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Next Review**: Monthly  
**Owner**: Development Team  
**Status**: Production Ready
