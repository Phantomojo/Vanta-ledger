# 🛠️ **Local LLM Implementation Roadmap**

## 🎯 **Phase 1: Foundation & Infrastructure**

### **Step 1: Environment Setup**

#### **1.1 Install Required Dependencies**
```bash
# Add to requirements.txt
llama-cpp-python==0.2.11
transformers==4.35.0
torch==2.1.0
pillow==10.0.1
opencv-python==4.8.1.78
sentence-transformers==2.2.2
redis==5.0.1
psutil==5.9.6
```

#### **1.2 Create Model Directory Structure**
```bash
mkdir -p models/{mistral,layoutlm,phi3,tinyllama}
mkdir -p models/cache
mkdir -p models/configs
mkdir -p logs/llm
```

### **Step 2: Core LLM Service Implementation**

#### **2.1 Create Local LLM Service**
```python
# backend/app/services/local_llm_service.py
import asyncio
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import hashlib
import json
import time
from datetime import datetime

from llama_cpp import Llama
from transformers import LayoutLMv3Processor, LayoutLMv3ForSequenceClassification
import torch
from PIL import Image
import redis

from ..config import settings
from ..models.document_models import EnhancedDocument

logger = logging.getLogger(__name__)

class LocalLLMService:
    """Local LLM orchestration and management service"""
    
    def __init__(self):
        self.models = {}
        self.model_configs = self._load_model_configs()
        self.redis_client = redis.Redis.from_url(settings.REDIS_URI, decode_responses=True)
        self.performance_metrics = {}
        
    def _load_model_configs(self) -> Dict[str, Dict]:
        """Load model configurations"""
        return {
            "mistral_7b": {
                "model_path": "models/mistral/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
                "context_length": 4096,
                "max_tokens": 512,
                "temperature": 0.7,
                "top_p": 0.9,
                "priority": "high"
            },
            "layoutlmv3": {
                "model_path": "models/layoutlm/layoutlmv3-base",
                "processor_path": "models/layoutlm/layoutlmv3-base",
                "max_length": 512,
                "priority": "high"
            },
            "phi3_mini": {
                "model_path": "models/phi3/phi-3-mini-4k-instruct.Q4_K_M.gguf",
                "context_length": 4096,
                "max_tokens": 256,
                "temperature": 0.8,
                "priority": "medium"
            }
        }
    
    async def initialize_models(self):
        """Initialize all required models"""
        try:
            logger.info("Initializing local LLM models...")
            
            # Initialize Mistral 7B for general text processing
            await self._load_mistral_model()
            
            # Initialize LayoutLMv3 for document understanding
            await self._load_layoutlm_model()
            
            # Initialize Phi-3 Mini for quick analysis
            await self._load_phi3_model()
            
            logger.info("All local LLM models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing models: {str(e)}")
            raise
    
    async def _load_mistral_model(self):
        """Load Mistral 7B model"""
        try:
            config = self.model_configs["mistral_7b"]
            model_path = Path(config["model_path"])
            
            if not model_path.exists():
                logger.warning(f"Mistral model not found at {model_path}")
                return
            
            self.models["mistral"] = Llama(
                model_path=str(model_path),
                n_ctx=config["context_length"],
                n_threads=8,  # Adjust based on CPU cores
                n_gpu_layers=0  # Set to > 0 if GPU available
            )
            
            logger.info("Mistral 7B model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading Mistral model: {str(e)}")
    
    async def _load_layoutlm_model(self):
        """Load LayoutLMv3 model"""
        try:
            config = self.model_configs["layoutlmv3"]
            model_path = Path(config["model_path"])
            
            if not model_path.exists():
                logger.warning(f"LayoutLMv3 model not found at {model_path}")
                return
            
            self.models["layoutlm"] = {
                "processor": LayoutLMv3Processor.from_pretrained(str(model_path)),
                "model": LayoutLMv3ForSequenceClassification.from_pretrained(str(model_path))
            }
            
            logger.info("LayoutLMv3 model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading LayoutLMv3 model: {str(e)}")
    
    async def _load_phi3_model(self):
        """Load Phi-3 Mini model"""
        try:
            config = self.model_configs["phi3_mini"]
            model_path = Path(config["model_path"])
            
            if not model_path.exists():
                logger.warning(f"Phi-3 model not found at {model_path}")
                return
            
            self.models["phi3"] = Llama(
                model_path=str(model_path),
                n_ctx=config["context_length"],
                n_threads=4,
                n_gpu_layers=0
            )
            
            logger.info("Phi-3 Mini model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading Phi-3 model: {str(e)}")
    
    async def process_document(self, document: EnhancedDocument) -> Dict[str, Any]:
        """Process document with local LLM pipeline"""
        try:
            start_time = time.time()
            
            # Generate cache key
            cache_key = self._generate_cache_key(document)
            
            # Check cache first
            cached_result = await self._get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            # Process document with appropriate models
            results = {}
            
            # Document classification
            if document.extracted_text:
                results["classification"] = await self._classify_document(document.extracted_text)
                results["summary"] = await self._generate_summary(document.extracted_text)
                results["entities"] = await self._extract_entities(document.extracted_text)
            
            # Document understanding (if image available)
            if hasattr(document, 'file_path') and document.file_path:
                results["document_understanding"] = await self._understand_document_layout(document.file_path)
            
            # Financial data extraction
            if document.extracted_text:
                results["financial_data"] = await self._extract_financial_data(document.extracted_text)
            
            # Cache results
            await self._cache_result(cache_key, results)
            
            # Record performance metrics
            processing_time = time.time() - start_time
            self._record_performance_metrics("document_processing", processing_time)
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise
    
    async def _classify_document(self, text: str) -> Dict[str, Any]:
        """Classify document type using Mistral 7B"""
        try:
            if "mistral" not in self.models:
                return {"type": "unknown", "confidence": 0.0}
            
            prompt = f"""
            Classify the following document into one of these categories:
            - invoice
            - receipt
            - contract
            - financial_statement
            - tax_document
            - legal_document
            - other
            
            Document text: {text[:1000]}
            
            Respond with only the category name and confidence score (0-1).
            """
            
            response = self.models["mistral"](
                prompt,
                max_tokens=50,
                temperature=0.3,
                stop=["\n"]
            )
            
            result = response["choices"][0]["text"].strip().lower()
            
            # Parse response
            if "invoice" in result:
                return {"type": "invoice", "confidence": 0.9}
            elif "receipt" in result:
                return {"type": "receipt", "confidence": 0.9}
            elif "contract" in result:
                return {"type": "contract", "confidence": 0.8}
            elif "financial" in result:
                return {"type": "financial_statement", "confidence": 0.8}
            else:
                return {"type": "other", "confidence": 0.5}
                
        except Exception as e:
            logger.error(f"Error classifying document: {str(e)}")
            return {"type": "unknown", "confidence": 0.0}
    
    async def _generate_summary(self, text: str) -> str:
        """Generate document summary using Mistral 7B"""
        try:
            if "mistral" not in self.models:
                return "Summary not available"
            
            prompt = f"""
            Generate a concise summary (2-3 sentences) of the following document:
            
            {text[:2000]}
            
            Summary:
            """
            
            response = self.models["mistral"](
                prompt,
                max_tokens=150,
                temperature=0.5,
                stop=["\n\n"]
            )
            
            return response["choices"][0]["text"].strip()
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return "Summary generation failed"
    
    async def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities from document text"""
        try:
            if "mistral" not in self.models:
                return {}
            
            prompt = f"""
            Extract the following entities from the document text:
            - Company names
            - Dates
            - Amounts (money)
            - Invoice numbers
            - Email addresses
            - Phone numbers
            
            Document: {text[:1500]}
            
            Return as JSON format:
            {{
                "companies": ["company1", "company2"],
                "dates": ["date1", "date2"],
                "amounts": ["amount1", "amount2"],
                "invoice_numbers": ["inv1", "inv2"],
                "emails": ["email1", "email2"],
                "phones": ["phone1", "phone2"]
            }}
            """
            
            response = self.models["mistral"](
                prompt,
                max_tokens=300,
                temperature=0.3
            )
            
            result_text = response["choices"][0]["text"].strip()
            
            # Try to parse JSON response
            try:
                import re
                # Extract JSON-like structure
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except:
                pass
            
            # Fallback: simple extraction
            return self._simple_entity_extraction(text)
            
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return {}
    
    def _simple_entity_extraction(self, text: str) -> Dict[str, List[str]]:
        """Simple rule-based entity extraction as fallback"""
        import re
        
        entities = {
            "amounts": [],
            "dates": [],
            "emails": [],
            "phones": []
        }
        
        # Extract amounts
        amount_pattern = r'[\$]?[\d,]+\.?\d*'
        entities["amounts"] = re.findall(amount_pattern, text)
        
        # Extract dates
        date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'
        entities["dates"] = re.findall(date_pattern, text)
        
        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        entities["emails"] = re.findall(email_pattern, text)
        
        # Extract phone numbers
        phone_pattern = r'[\+]?[1-9][\d]{0,15}'
        entities["phones"] = re.findall(phone_pattern, text)
        
        return entities
    
    async def _understand_document_layout(self, file_path: str) -> Dict[str, Any]:
        """Understand document layout using LayoutLMv3"""
        try:
            if "layoutlm" not in self.models:
                return {"layout": "unknown"}
            
            # Load and process image
            image = Image.open(file_path).convert("RGB")
            processor = self.models["layoutlm"]["processor"]
            model = self.models["layoutlm"]["model"]
            
            # Process image
            encoding = processor(image, return_tensors="pt")
            
            # Get predictions
            with torch.no_grad():
                outputs = model(**encoding)
                predictions = outputs.logits.argmax(-1)
            
            # Analyze layout
            layout_analysis = {
                "has_table": "table" in str(predictions).lower(),
                "has_form": "form" in str(predictions).lower(),
                "text_regions": len(encoding["input_ids"][0]),
                "layout_type": "structured" if "table" in str(predictions).lower() else "unstructured"
            }
            
            return layout_analysis
            
        except Exception as e:
            logger.error(f"Error understanding document layout: {str(e)}")
            return {"layout": "unknown"}
    
    async def _extract_financial_data(self, text: str) -> Dict[str, Any]:
        """Extract financial data using Phi-3 Mini for quick analysis"""
        try:
            if "phi3" not in self.models:
                return {}
            
            prompt = f"""
            Extract financial information from this document:
            - Total amount
            - Tax amount
            - Due date
            - Invoice number
            - Customer/vendor name
            
            Document: {text[:1000]}
            
            Return as JSON:
            {{
                "total_amount": "amount",
                "tax_amount": "amount",
                "due_date": "date",
                "invoice_number": "number",
                "customer_name": "name"
            }}
            """
            
            response = self.models["phi3"](
                prompt,
                max_tokens=200,
                temperature=0.3
            )
            
            result_text = response["choices"][0]["text"].strip()
            
            # Try to parse JSON
            try:
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except:
                pass
            
            return {}
            
        except Exception as e:
            logger.error(f"Error extracting financial data: {str(e)}")
            return {}
    
    def _generate_cache_key(self, document: EnhancedDocument) -> str:
        """Generate cache key for document"""
        content_hash = hashlib.md5(
            f"{document.original_filename}{document.file_size}{document.checksum}".encode()
        ).hexdigest()
        return f"llm_cache:{content_hash}"
    
    async def _get_cached_result(self, cache_key: str) -> Optional[Dict]:
        """Get cached result from Redis"""
        try:
            cached = self.redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            return None
        except Exception as e:
            logger.error(f"Error getting cached result: {str(e)}")
            return None
    
    async def _cache_result(self, cache_key: str, result: Dict):
        """Cache result in Redis"""
        try:
            self.redis_client.setex(
                cache_key,
                3600,  # 1 hour TTL
                json.dumps(result, default=str)
            )
        except Exception as e:
            logger.error(f"Error caching result: {str(e)}")
    
    def _record_performance_metrics(self, operation: str, duration: float):
        """Record performance metrics"""
        if operation not in self.performance_metrics:
            self.performance_metrics[operation] = []
        
        self.performance_metrics[operation].append({
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep only last 100 metrics
        if len(self.performance_metrics[operation]) > 100:
            self.performance_metrics[operation] = self.performance_metrics[operation][-100:]
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        metrics = {}
        
        for operation, data in self.performance_metrics.items():
            if data:
                durations = [item["duration"] for item in data]
                metrics[operation] = {
                    "avg_duration": sum(durations) / len(durations),
                    "min_duration": min(durations),
                    "max_duration": max(durations),
                    "total_operations": len(data)
                }
        
        return metrics

# Global instance
local_llm_service = LocalLLMService()
```

### **Step 3: Integration with Existing Services**

#### **3.1 Enhance Document Service**
```python
# Extend backend/app/services/enhanced_document_service.py

# Add to imports
from .local_llm_service import local_llm_service

# Add to EnhancedDocumentService class
async def create_document_with_llm(self, document_data: Dict[str, Any], user_id: UUID) -> EnhancedDocument:
    """Create document with local LLM enhancement"""
    try:
        # Create basic document
        document = self.create_document(document_data, user_id)
        
        # Process with local LLM
        llm_results = await local_llm_service.process_document(document)
        
        # Enhance document with LLM insights
        await self._enhance_document_with_llm_insights(document, llm_results)
        
        return document
        
    except Exception as e:
        logger.error(f"Error creating document with LLM: {str(e)}")
        raise

async def _enhance_document_with_llm_insights(self, document: EnhancedDocument, llm_results: Dict[str, Any]):
    """Enhance document with LLM processing results"""
    try:
        # Update document type if LLM classification is confident
        if llm_results.get("classification", {}).get("confidence", 0) > 0.8:
            doc_type = llm_results["classification"]["type"]
            if hasattr(DocumentType, doc_type.upper()):
                document.metadata.document_type = DocumentType(doc_type.upper())
        
        # Add LLM-generated summary
        if llm_results.get("summary"):
            document.metadata.description = llm_results["summary"]
        
        # Add extracted entities as custom fields
        if llm_results.get("entities"):
            document.metadata.custom_fields["extracted_entities"] = llm_results["entities"]
        
        # Add financial data if available
        if llm_results.get("financial_data"):
            document.metadata.custom_fields["financial_data"] = llm_results["financial_data"]
        
        # Update document in database
        self.documents.update_one(
            {"_id": str(document.id)},
            {"$set": {
                "metadata": document.metadata.dict(),
                "modified_at": datetime.utcnow()
            }}
        )
        
    except Exception as e:
        logger.error(f"Error enhancing document with LLM insights: {str(e)}")
```

#### **3.2 Enhance Financial Service**
```python
# Extend backend/app/services/financial_service.py

# Add to imports
from .local_llm_service import local_llm_service

# Add to FinancialService class
async def extract_financial_data_with_llm(self, document: EnhancedDocument) -> Dict[str, Any]:
    """Extract financial data using local LLM"""
    try:
        # Process document with LLM
        llm_results = await local_llm_service.process_document(document)
        
        # Extract financial data
        financial_data = llm_results.get("financial_data", {})
        
        # Create financial records based on extracted data
        financial_records = {}
        
        if financial_data.get("total_amount"):
            # Create invoice if it's an invoice
            if llm_results.get("classification", {}).get("type") == "invoice":
                invoice_data = {
                    "invoice_number": financial_data.get("invoice_number", f"INV-{document.id}"),
                    "customer_id": str(uuid.uuid4()),  # Create or find customer
                    "invoice_date": datetime.utcnow().isoformat(),
                    "due_date": financial_data.get("due_date", (datetime.utcnow() + timedelta(days=30)).isoformat()),
                    "lines": [{
                        "item_description": document.metadata.title or "Document Processing",
                        "quantity": "1.00",
                        "unit_price": financial_data["total_amount"],
                        "tax_rate": "0.00"
                    }]
                }
                
                invoice = self.create_invoice(invoice_data, document.created_by)
                financial_records["invoice"] = invoice.dict()
        
        return financial_records
        
    except Exception as e:
        logger.error(f"Error extracting financial data with LLM: {str(e)}")
        return {}
```

### **Step 4: API Integration**

#### **4.1 Create LLM API Routes**
```python
# backend/app/routes/local_llm.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse

from ..auth import get_current_user, User
from ..services.local_llm_service import local_llm_service
from ..services.enhanced_document_service import enhanced_document_service

router = APIRouter(prefix="/api/v2/llm", tags=["Local LLM"])

@router.post("/process-document")
async def process_document_with_llm(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Process document with local LLM"""
    try:
        # Create document data
        document_data = {
            "original_filename": file.filename,
            "secure_filename": f"user_{current_user.id}_{file.filename}",
            "file_path": f"/tmp/{file.filename}",
            "file_size": 0,  # Will be set after file save
            "file_extension": file.filename.split(".")[-1] if "." in file.filename else "",
            "mime_type": file.content_type,
            "checksum": "temp_checksum"
        }
        
        # Create document with LLM enhancement
        document = await enhanced_document_service.create_document_with_llm(
            document_data, current_user.id
        )
        
        return {
            "success": True,
            "document": document.dict(),
            "message": "Document processed with local LLM successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )

@router.get("/performance")
async def get_llm_performance(
    current_user: User = Depends(get_current_user)
):
    """Get LLM performance metrics"""
    try:
        metrics = await local_llm_service.get_performance_metrics()
        
        return {
            "success": True,
            "performance_metrics": metrics
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance metrics: {str(e)}"
        )

@router.post("/analyze-text")
async def analyze_text_with_llm(
    text: str,
    analysis_type: str = "general",  # general, financial, entities
    current_user: User = Depends(get_current_user)
):
    """Analyze text with local LLM"""
    try:
        if analysis_type == "financial":
            result = await local_llm_service._extract_financial_data(text)
        elif analysis_type == "entities":
            result = await local_llm_service._extract_entities(text)
        else:
            result = {
                "classification": await local_llm_service._classify_document(text),
                "summary": await local_llm_service._generate_summary(text)
            }
        
        return {
            "success": True,
            "analysis": result,
            "analysis_type": analysis_type
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze text: {str(e)}"
        )
```

#### **4.2 Update Main Application**
```python
# Add to backend/app/main.py

# Import local LLM routes
from .routes.local_llm import router as local_llm_router

# Include local LLM routes
app.include_router(local_llm_router)

# Initialize local LLM service on startup
@app.on_event("startup")
async def startup_event():
    # ... existing startup code ...
    
    # Initialize local LLM models
    await local_llm_service.initialize_models()
```

---

## 🎯 **Phase 2: Model Download & Setup**

### **Step 1: Download Models**

#### **1.1 Create Model Download Script**
```python
# scripts/download_models.py
import requests
import os
from pathlib import Path
from tqdm import tqdm

def download_file(url: str, filepath: str):
    """Download file with progress bar"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(filepath, 'wb') as file, tqdm(
        desc=os.path.basename(filepath),
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            pbar.update(size)

def main():
    """Download required models"""
    models = {
        "mistral_7b": {
            "url": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
            "path": "models/mistral/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
        },
        "layoutlmv3": {
            "url": "https://huggingface.co/microsoft/layoutlmv3-base",
            "path": "models/layoutlm/layoutlmv3-base"
        },
        "phi3_mini": {
            "url": "https://huggingface.co/TheBloke/Phi-3-mini-4k-instruct-GGUF/resolve/main/phi-3-mini-4k-instruct.Q4_K_M.gguf",
            "path": "models/phi3/phi-3-mini-4k-instruct.Q4_K_M.gguf"
        }
    }
    
    # Create directories
    for model_info in models.values():
        Path(model_info["path"]).parent.mkdir(parents=True, exist_ok=True)
    
    # Download models
    for model_name, model_info in models.items():
        print(f"Downloading {model_name}...")
        
        if not os.path.exists(model_info["path"]):
            download_file(model_info["url"], model_info["path"])
            print(f"{model_name} downloaded successfully!")
        else:
            print(f"{model_name} already exists, skipping...")

if __name__ == "__main__":
    main()
```

#### **1.2 Run Model Download**
```bash
# Install required packages
pip install requests tqdm

# Run download script
python scripts/download_models.py
```

---

## 🧪 **Phase 3: Testing & Validation**

### **Step 1: Create Test Suite**
```python
# tests/test_local_llm.py
import pytest
import asyncio
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.local_llm_service import LocalLLMService

client = TestClient(app)

class TestLocalLLM:
    """Test local LLM functionality"""
    
    @pytest.fixture
    def llm_service(self):
        return LocalLLMService()
    
    def test_model_initialization(self, llm_service):
        """Test model initialization"""
        # This would test model loading in a real environment
        assert llm_service.model_configs is not None
        assert "mistral_7b" in llm_service.model_configs
    
    @pytest.mark.asyncio
    async def test_document_classification(self, llm_service):
        """Test document classification"""
        # Mock model response
        with patch.object(llm_service, 'models', {"mistral": Mock()}):
            llm_service.models["mistral"].return_value = {
                "choices": [{"text": "invoice"}]
            }
            
            result = await llm_service._classify_document("This is an invoice for services")
            assert result["type"] == "invoice"
            assert result["confidence"] > 0.8
    
    @pytest.mark.asyncio
    async def test_entity_extraction(self, llm_service):
        """Test entity extraction"""
        text = "Invoice #12345 for $1000.00 due 12/31/2024"
        
        with patch.object(llm_service, 'models', {"mistral": Mock()}):
            llm_service.models["mistral"].return_value = {
                "choices": [{"text": '{"amounts": ["$1000.00"], "dates": ["12/31/2024"]}'}]
            }
            
            result = await llm_service._extract_entities(text)
            assert "amounts" in result
            assert "dates" in result
    
    def test_cache_functionality(self, llm_service):
        """Test caching functionality"""
        # Test cache key generation
        document = Mock()
        document.original_filename = "test.pdf"
        document.file_size = 1024
        document.checksum = "abc123"
        
        cache_key = llm_service._generate_cache_key(document)
        assert cache_key.startswith("llm_cache:")
        assert len(cache_key) > 20

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### **Step 2: Performance Testing**
```python
# scripts/performance_test.py
import asyncio
import time
import statistics
from backend.app.services.local_llm_service import LocalLLMService

async def performance_test():
    """Test LLM performance"""
    llm_service = LocalLLMService()
    await llm_service.initialize_models()
    
    test_texts = [
        "This is an invoice for consulting services totaling $5,000.00",
        "Receipt for office supplies purchased on 12/15/2024",
        "Contract agreement between Company A and Company B",
        "Financial statement for Q4 2024 showing revenue of $100,000"
    ]
    
    results = {
        "classification": [],
        "summary": [],
        "entities": []
    }
    
    print("Running performance tests...")
    
    for i, text in enumerate(test_texts):
        print(f"Processing text {i+1}/{len(test_texts)}")
        
        # Test classification
        start_time = time.time()
        await llm_service._classify_document(text)
        results["classification"].append(time.time() - start_time)
        
        # Test summary generation
        start_time = time.time()
        await llm_service._generate_summary(text)
        results["summary"].append(time.time() - start_time)
        
        # Test entity extraction
        start_time = time.time()
        await llm_service._extract_entities(text)
        results["entities"].append(time.time() - start_time)
    
    # Print results
    print("\nPerformance Results:")
    print("=" * 50)
    
    for operation, times in results.items():
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"{operation.capitalize()}:")
        print(f"  Average: {avg_time:.3f}s")
        print(f"  Min: {min_time:.3f}s")
        print(f"  Max: {max_time:.3f}s")
        print()

if __name__ == "__main__":
    asyncio.run(performance_test())
```

---

## 🚀 **Deployment Checklist**

### **Pre-Deployment**
- [ ] Download all required models
- [ ] Test model loading and initialization
- [ ] Verify hardware requirements
- [ ] Set up monitoring and logging
- [ ] Configure caching and performance settings

### **Deployment**
- [ ] Deploy updated backend with LLM integration
- [ ] Initialize models on startup
- [ ] Monitor performance and resource usage
- [ ] Test all API endpoints
- [ ] Validate document processing pipeline

### **Post-Deployment**
- [ ] Monitor system performance
- [ ] Track LLM accuracy and user feedback
- [ ] Optimize model configurations
- [ ] Scale hardware if needed
- [ ] Document lessons learned

---

**🎯 This roadmap provides a complete path to integrate local LLMs into Vanta Ledger, transforming it into a truly intelligent, privacy-first document processing system!** 