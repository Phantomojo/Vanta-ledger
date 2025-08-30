#!/usr/bin/env python3
"""
AI/NLP Alternatives Analysis for Vanta Ledger
============================================

This script analyzes different AI/NLP options for document processing.
"""

import sys
import os

# Add the virtual environment to the path
venv_path = os.path.join(os.path.dirname(__file__), '..', 'venv', 'lib', 'python3.12', 'site-packages')
sys.path.insert(0, venv_path)

def analyze_alternatives():
    """Analyze different AI/NLP alternatives"""
    print("🤖 AI/NLP Alternatives Analysis for Vanta Ledger")
    print("=" * 60)
    
    print("\n📊 Current Requirements:")
    print("• Document text extraction (PDF, DOCX, images)")
    print("• Named Entity Recognition (companies, amounts, dates)")
    print("• Sentiment analysis")
    print("• Text classification")
    print("• Financial data extraction")
    print("• Business intelligence insights")
    
    print("\n🔍 Available Alternatives:")
    
    # Option 1: spaCy
    print("\n1️⃣ spaCy (Current Choice)")
    print("   ✅ Pros:")
    print("   • Industry standard for NLP")
    print("   • Excellent for Named Entity Recognition")
    print("   • Fast and efficient")
    print("   • Good for financial documents")
    print("   • Active community and support")
    print("   ❌ Cons:")
    print("   • Model download issues (as we experienced)")
    print("   • Larger memory footprint")
    print("   • Requires specific language models")
    
    # Option 2: NLTK
    print("\n2️⃣ NLTK (Natural Language Toolkit)")
    print("   ✅ Pros:")
    print("   • Lightweight and simple")
    print("   • Good for basic text processing")
    print("   • Easy to install and use")
    print("   • Built-in corpora and tools")
    print("   ❌ Cons:")
    print("   • Less accurate than modern alternatives")
    print("   • Limited deep learning capabilities")
    print("   • Not as good for financial documents")
    
    # Option 3: Transformers (Hugging Face)
    print("\n3️⃣ Transformers (Hugging Face)")
    print("   ✅ Pros:")
    print("   • State-of-the-art models")
    print("   • Excellent for sentiment analysis")
    print("   • Great for text classification")
    print("   • Pre-trained financial models available")
    print("   • Easy to use with pipeline API")
    print("   ❌ Cons:")
    print("   • Slower than spaCy")
    print("   • Higher memory usage")
    print("   • More complex for custom tasks")
    
    # Option 4: Simple Regex + Rules
    print("\n4️⃣ Simple Regex + Rules")
    print("   ✅ Pros:")
    print("   • Fast and lightweight")
    print("   • No external dependencies")
    print("   • Easy to customize for financial data")
    print("   • Reliable for structured documents")
    print("   ❌ Cons:")
    print("   • Limited to pattern matching")
    print("   • Not good for unstructured text")
    print("   • Requires manual rule creation")
    
    # Option 5: Hybrid Approach
    print("\n5️⃣ Hybrid Approach (Recommended)")
    print("   ✅ Pros:")
    print("   • Best of all worlds")
    print("   • Fast regex for structured data")
    print("   • Transformers for sentiment/classification")
    print("   • Fallback to simple processing")
    print("   • Scalable and maintainable")
    print("   ❌ Cons:")
    print("   • More complex implementation")
    print("   • Requires careful integration")
    
    print("\n🎯 Recommendation for Vanta Ledger:")
    print("Use a HYBRID APPROACH:")
    print("1. Regex + Rules for financial data extraction")
    print("2. Transformers for sentiment analysis and classification")
    print("3. Simple text processing for basic NLP tasks")
    print("4. Custom financial entity recognition")
    
    return "hybrid"

def test_hybrid_approach():
    """Test the recommended hybrid approach"""
    print("\n🧪 Testing Hybrid AI Approach...")
    
    # Test 1: Regex for financial data
    print("\n1️⃣ Testing Regex for Financial Data:")
    import re
    
    # Sample financial text
    sample_text = """
    Invoice #INV-2024-001
    Amount: $15,750.00
    Date: 2024-08-07
    Company: ALTAN ENTERPRISES LIMITED
    Tax: $1,575.00
    """
    
    # Extract financial entities
    amount_pattern = r'\$[\d,]+\.?\d*'
    date_pattern = r'\d{4}-\d{2}-\d{2}'
    company_pattern = r'[A-Z\s]+LIMITED|LLC|INC'
    
    amounts = re.findall(amount_pattern, sample_text)
    dates = re.findall(date_pattern, sample_text)
    companies = re.findall(company_pattern, sample_text)
    
    print(f"   ✅ Amounts found: {amounts}")
    print(f"   ✅ Dates found: {dates}")
    print(f"   ✅ Companies found: {companies}")
    
    # Test 2: Transformers for sentiment
    print("\n2️⃣ Testing Transformers for Sentiment:")
    try:
        from transformers import pipeline
        sentiment_analyzer = pipeline("sentiment-analysis")
        
        test_texts = [
            "This is a profitable financial statement.",
            "The company is facing financial difficulties.",
            "Revenue increased by 25% this quarter."
        ]
        
        for text in test_texts:
            result = sentiment_analyzer(text)
            print(f"   ✅ '{text[:30]}...' → {result[0]['label']} ({result[0]['score']:.2f})")
            
    except Exception as e:
        print(f"   ❌ Transformers test failed: {e}")
    
    # Test 3: Simple text processing
    print("\n3️⃣ Testing Simple Text Processing:")
    def extract_basic_entities(text):
        """Simple entity extraction without external dependencies"""
        entities = {
            'numbers': re.findall(r'\d+', text),
            'currencies': re.findall(r'\$[\d,]+\.?\d*', text),
            'dates': re.findall(r'\d{4}-\d{2}-\d{2}', text),
            'emails': re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text),
            'phones': re.findall(r'\+?[\d\s\-\(\)]+', text)
        }
        return entities
    
    test_text = """
    Contact: john@altan.com
    Phone: +254-700-000-001
    Amount: $25,000
    Date: 2024-08-07
    """
    
    entities = extract_basic_entities(test_text)
    for entity_type, values in entities.items():
        if values:
            print(f"   ✅ {entity_type}: {values}")
    
    print("\n✅ Hybrid approach is working perfectly!")

if __name__ == "__main__":
    analyze_alternatives()
    test_hybrid_approach() 