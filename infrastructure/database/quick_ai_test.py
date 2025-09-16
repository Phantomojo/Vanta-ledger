#!/usr/bin/env python3
"""
Quick AI Test for Vanta Ledger
"""

import sys
import os
import logging
logger = logging.getLogger(__name__)

# Add the virtual environment to the path
venv_path = os.path.join(os.path.dirname(__file__), '..', 'venv', 'lib', 'python3.12', 'site-packages')
sys.path.insert(0, venv_path)

def test_imports():
    """Test all AI imports"""
    logger.info("🧪 Testing AI Imports...")
    
    try:
        import fitz
        logger.info("✅ PyMuPDF imported successfully")
    except ImportError as e:
        logger.error(f"❌ PyMuPDF import failed: {e}")
    
    try:
        import docx
        logger.info("✅ python-docx imported successfully")
    except ImportError as e:
        logger.error(f"❌ python-docx import failed: {e}")
    
    try:
        import fitz
        logger.info("✅ PyMuPDF imported successfully")
    except ImportError as e:
        logger.error(f"❌ PyMuPDF import failed: {e}")
    
    try:
        import spacy
        logger.info("✅ spaCy imported successfully")
    except ImportError as e:
        logger.error(f"❌ spaCy import failed: {e}")
    
    try:
        from transformers import pipeline
        logger.info("✅ Transformers imported successfully")
    except ImportError as e:
        logger.error(f"❌ Transformers import failed: {e}")
    
    try:
        import torch
        logger.info(f"✅ PyTorch imported successfully (CUDA: {torch.cuda.is_available()})")
    except ImportError as e:
        logger.error(f"❌ PyTorch import failed: {e}")

if __name__ == "__main__":
    test_imports() 