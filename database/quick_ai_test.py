#!/usr/bin/env python3
"""
Quick AI Test for Vanta Ledger
"""

import sys
import os

# Add the virtual environment to the path
venv_path = os.path.join(os.path.dirname(__file__), '..', 'venv', 'lib', 'python3.12', 'site-packages')
sys.path.insert(0, venv_path)

def test_imports():
    """Test all AI imports"""
    print("🧪 Testing AI Imports...")
    
    try:
        import PyPDF2
        print("✅ PyPDF2 imported successfully")
    except ImportError as e:
        print(f"❌ PyPDF2 import failed: {e}")
    
    try:
        import docx
        print("✅ python-docx imported successfully")
    except ImportError as e:
        print(f"❌ python-docx import failed: {e}")
    
    try:
        import fitz
        print("✅ PyMuPDF imported successfully")
    except ImportError as e:
        print(f"❌ PyMuPDF import failed: {e}")
    
    try:
        import spacy
        print("✅ spaCy imported successfully")
    except ImportError as e:
        print(f"❌ spaCy import failed: {e}")
    
    try:
        from transformers import pipeline
        print("✅ Transformers imported successfully")
    except ImportError as e:
        print(f"❌ Transformers import failed: {e}")
    
    try:
        import torch
        print(f"✅ PyTorch imported successfully (CUDA: {torch.cuda.is_available()})")
    except ImportError as e:
        print(f"❌ PyTorch import failed: {e}")

if __name__ == "__main__":
    test_imports() 