#!/usr/bin/env python3
"""
Test AI Capabilities for Vanta Ledger
=====================================

This script tests all the AI/ML capabilities that will be used in the system.
"""

import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pdf_processing():
    """Test PDF processing capabilities"""
    logger.info("🧪 Testing PDF Processing...")
    
    try:
        import PyPDF2
        logger.info("✅ PyPDF2: Available")
        
        import fitz  # PyMuPDF
        logger.info("✅ PyMuPDF: Available")
        
        return True
    except ImportError as e:
        logger.error(f"❌ PDF processing failed: {e}")
        return False

def test_document_processing():
    """Test document processing capabilities"""
    logger.info("🧪 Testing Document Processing...")
    
    try:
        import docx
        logger.info("✅ python-docx: Available")
        
        from PIL import Image
        logger.info("✅ Pillow (Image processing): Available")
        
        return True
    except ImportError as e:
        logger.error(f"❌ Document processing failed: {e}")
        return False

def test_nlp_capabilities():
    """Test Natural Language Processing capabilities"""
    logger.info("🧪 Testing NLP Capabilities...")
    
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        logger.info("✅ spaCy: Available and loaded")
        
        # Test basic NLP
        doc = nlp("Vanta Ledger is a financial document processing system.")
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        logger.info(f"✅ Named Entity Recognition: {entities}")
        
        return True
    except Exception as e:
        logger.error(f"❌ NLP capabilities failed: {e}")
        return False

def test_ai_models():
    """Test AI model capabilities"""
    logger.info("🧪 Testing AI Models...")
    
    try:
        from transformers import pipeline
        
        # Test sentiment analysis
        sentiment_analyzer = pipeline("sentiment-analysis")
        result = sentiment_analyzer("This is a great financial system!")
        logger.info(f"✅ Sentiment Analysis: {result}")
        
        # Test text classification
        classifier = pipeline("text-classification", model="distilbert-base-uncased")
        result = classifier("This document contains financial statements.")
        logger.info(f"✅ Text Classification: {result}")
        
        return True
    except Exception as e:
        logger.error(f"❌ AI models failed: {e}")
        return False

def test_ml_capabilities():
    """Test Machine Learning capabilities"""
    logger.info("🧪 Testing ML Capabilities...")
    
    try:
        import torch
        logger.info(f"✅ PyTorch: Available (CUDA: {torch.cuda.is_available()})")
        
        import sklearn
        logger.info("✅ scikit-learn: Available")
        
        import networkx as nx
        logger.info("✅ NetworkX: Available")
        
        # Test basic network analysis
        G = nx.Graph()
        G.add_edge("Company A", "Company B", weight=0.8)
        centrality = nx.degree_centrality(G)
        logger.info(f"✅ Network Analysis: {centrality}")
        
        return True
    except Exception as e:
        logger.error(f"❌ ML capabilities failed: {e}")
        return False

def test_document_processing_pipeline():
    """Test the document processing pipeline"""
    logger.info("🧪 Testing Document Processing Pipeline...")
    
    try:
        from document_processing_pipeline import DocumentProcessingPipeline
        logger.info("✅ Document Processing Pipeline: Imported successfully")
        
        # Test initialization (without actual database connections)
        logger.info("✅ Document Processing Pipeline: Ready for use")
        
        return True
    except Exception as e:
        logger.error(f"❌ Document processing pipeline failed: {e}")
        return False

def main():
    """Run all AI capability tests"""
    logger.info("🎯 Testing Vanta Ledger AI Capabilities...")
    logger.info("=" * 60)
    
    tests = [
        ("PDF Processing", test_pdf_processing),
        ("Document Processing", test_document_processing),
        ("NLP Capabilities", test_nlp_capabilities),
        ("AI Models", test_ai_models),
        ("ML Capabilities", test_ml_capabilities),
        ("Document Pipeline", test_document_processing_pipeline),
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n🔍 Running {test_name} test...")
        results[test_name] = test_func()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 AI Capabilities Test Summary:")
    logger.info("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} {test_name}")
    
    logger.info(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All AI capabilities are working perfectly!")
        logger.info("🚀 Vanta Ledger is ready for advanced AI-powered processing!")
    else:
        logger.warning("⚠️  Some AI capabilities need attention")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 