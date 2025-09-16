#!/usr/bin/env python3
"""
Local LLM Service Startup Script
This script starts your local LLM system for document processing
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_system():
    """Check if system is ready"""
    logger.info("🔍 Checking Local LLM System...")
    
    # Check model
    model_path = "models/tinyllama/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
    if not os.path.exists(model_path):
        logger.info("❌ TinyLlama model not found!")
        return False
    
    logger.info("✅ TinyLlama model ready")
    
    # Check dependencies
    try:
        from llama_cpp import Llama
        import torch
        import transformers
        logger.info("✅ All dependencies available")
        return True
    except ImportError as e:
        logger.info(f"❌ Missing dependency: {e}")
        return False

def start_llm_service():
    """Start the local LLM service"""
    logger.info("\n🚀 Starting Local LLM Service...")
    
    try:
        # Import the service
        from backend.app.services.local_llm_service import LocalLLMService
        
        # Initialize service
        service = LocalLLMService()
        
        # Initialize models
        asyncio.run(service.initialize_models())
        
        logger.info("✅ Local LLM Service started successfully!")
        logger.info("📝 Ready for document processing")
        
        return service
        
    except Exception as e:
        logger.error(f"❌ Failed to start service: {e}")
        return None

def test_document_processing(service):
    """Test document processing"""
    logger.info("\n📄 Testing Document Processing...")
    
    # Sample document text
    sample_text = """
    INVOICE
    
    Invoice Number: INV-2024-001
    Date: January 15, 2024
    Due Date: February 15, 2024
    
    Bill To:
    John Doe
    123 Main Street
    City, State 12345
    
    Items:
    1. Web Development Services - $1,500.00
    2. Hosting Setup - $200.00
    
    Subtotal: $1,700.00
    Tax (10%): $170.00
    Total: $1,870.00
    
    Payment Terms: Net 30
    """
    
    try:
        # Test classification
        logger.info("🔄 Testing document classification...")
        from backend.app.models.document_models import EnhancedDocument
        
        # Create a mock document
        doc = EnhancedDocument(
            original_filename="test_invoice.txt",
            extracted_text=sample_text,
            file_size=len(sample_text),
            checksum="test123"
        )
        
        # Process with company context (mock company ID)
        import uuid
        company_id = uuid.uuid4()
        
        results = asyncio.run(service.process_document_for_company(doc, company_id))
        
        logger.info("✅ Document processing completed!")
        logger.info(f"📊 Results: {len(results)} analysis components")
        
        # Show some results
        if 'classification' in results:
            logger.info(f"📋 Classification: {results[")
        
        if 'summary' in results:
            logger.info(f"📝 Summary: {results[")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Document processing failed: {e}")
        return False

def main():
    """Main function"""
    logger.info("🎯 Vanta Ledger - Local LLM System")
    logger.info("=")
    
    # Check system
    if not check_system():
        logger.error("\n❌ System check failed. Please fix the issues above.")
        return
    
    # Start service
    service = start_llm_service()
    if not service:
        logger.error("\n❌ Failed to start LLM service.")
        return
    
    # Test processing
    if test_document_processing(service):
        logger.info("\n🎉 All tests passed! Your local LLM system is fully operational!")
        logger.info("\n💡 You can now:")
        logger.info("   - Process documents with AI analysis")
        logger.info("   - Extract financial data automatically")
        logger.info("   - Generate summaries and classifications")
        logger.info("   - Use company-specific context for processing")
    else:
        logger.error("\n⚠️  Some tests failed, but the core system is working.")
    
    logger.info("\n")

if __name__ == "__main__":
    main() 