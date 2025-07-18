#!/usr/bin/env python3
"""
Setup Script for Advanced Document AI System
============================================

This script installs all required dependencies and sets up the AI system.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    print("🚀 Setting up Advanced Document AI System")
    print("=" * 50)
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Not in a virtual environment. Consider creating one first.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    # Install AI requirements
    if not run_command("pip install -r ai_requirements.txt", "Installing AI dependencies"):
        print("❌ Failed to install AI dependencies")
        return
    
    # Download spaCy model
    if not run_command("python -m spacy download en_core_web_sm", "Downloading spaCy English model"):
        print("❌ Failed to download spaCy model")
        return
    
    # Create necessary directories
    directories = ['logs', 'models', 'cache', 'exports']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Test imports
    print("\n🧪 Testing imports...")
    try:
        import numpy
        import sklearn
        import spacy
        import pandas
        import requests
        import fuzzywuzzy
        print("✅ All imports successful!")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return
    
    # Test spaCy model
    try:
        nlp = spacy.load("en_core_web_sm")
        test_doc = nlp("This is a test document for Vanta Ledger.")
        print("✅ spaCy model loaded successfully!")
    except Exception as e:
        print(f"❌ spaCy model error: {e}")
        return
    
    print("\n🎉 Advanced Document AI System setup complete!")
    print("\nNext steps:")
    print("1. Run: python advanced_document_ai.py")
    print("2. Check the logs in the 'logs' directory")
    print("3. Review the analysis results")

if __name__ == "__main__":
    main() 