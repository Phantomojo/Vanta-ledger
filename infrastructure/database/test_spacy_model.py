#!/usr/bin/env python3
"""
Test spaCy Model for Vanta Ledger
"""

import sys
import os

# Add the virtual environment to the path
venv_path = os.path.join(os.path.dirname(__file__), '..', 'venv', 'lib', 'python3.12', 'site-packages')
sys.path.insert(0, venv_path)

def test_spacy_model():
    """Test spaCy model loading and basic NLP"""
    print("🧪 Testing spaCy Model...")
    
    try:
        import spacy
        print("✅ spaCy imported successfully")
        
        # Try to load the model
        nlp = spacy.load("en_core_web_sm")
        print("✅ spaCy model loaded successfully")
        
        # Test basic NLP
        doc = nlp("Vanta Ledger is a financial document processing system for 29 companies.")
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        print(f"✅ Named Entity Recognition: {entities}")
        
        # Test tokenization
        tokens = [token.text for token in doc]
        print(f"✅ Tokenization: {tokens[:5]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ spaCy test failed: {e}")
        return False

if __name__ == "__main__":
    test_spacy_model() 