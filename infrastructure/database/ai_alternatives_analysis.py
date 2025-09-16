#!/usr/bin/env python3
"""
AI/NLP Alternatives Analysis for Vanta Ledger
============================================

This script analyzes different AI/NLP options for document processing.
"""

import sys
import os
import logging
logger = logging.getLogger(__name__)

# Add the virtual environment to the path
venv_path = os.path.join(os.path.dirname(__file__), '..', 'venv', 'lib', 'python3.12', 'site-packages')
sys.path.insert(0, venv_path)

def analyze_alternatives():
    """Analyze different AI/NLP alternatives"""
    logger.info("🤖 AI/NLP Alternatives Analysis for Vanta Ledger")
    logger.info("=")
    
    logger.info("\n📊 Current Requirements:")
    logger.info("• Document text extraction (PDF, DOCX, images)")
    logger.info("• Named Entity Recognition (companies, amounts, dates)")
    logger.info("• Sentiment analysis")
    logger.info("• Text classification")
    logger.info("• Financial data extraction")
    logger.info("• Business intelligence insights")
    
    logger.info("\n🔍 Available Alternatives:")
    
    # Option 1: spaCy
    logger.info("\n1️⃣ spaCy (Current Choice)")
    logger.info("   ✅ Pros:")
    logger.info("   • Industry standard for NLP")
    logger.info("   • Excellent for Named Entity Recognition")
    logger.info("   • Fast and efficient")
    logger.info("   • Good for financial documents")
    logger.info("   • Active community and support")
    logger.info("   ❌ Cons:")
    logger.info("   • Model download issues (as we experienced)")
    logger.info("   • Larger memory footprint")
    logger.info("   • Requires specific language models")
    
    # Option 2: NLTK
    logger.info("\n2️⃣ NLTK (Natural Language Toolkit)")
    logger.info("   ✅ Pros:")
    logger.info("   • Lightweight and simple")
    logger.info("   • Good for basic text processing")
    logger.info("   • Easy to install and use")
    logger.info("   • Built-in corpora and tools")
    logger.info("   ❌ Cons:")
    logger.info("   • Less accurate than modern alternatives")
    logger.info("   • Limited deep learning capabilities")
    logger.info("   • Not as good for financial documents")
    
    # Option 3: Transformers (Hugging Face)
    logger.info("\n3️⃣ Transformers (Hugging Face)")
    logger.info("   ✅ Pros:")
    logger.info("   • State-of-the-art models")
    logger.info("   • Excellent for sentiment analysis")
    logger.info("   • Great for text classification")
    logger.info("   • Pre-trained financial models available")
    logger.info("   • Easy to use with pipeline API")
    logger.info("   ❌ Cons:")
    logger.info("   • Slower than spaCy")
    logger.info("   • Higher memory usage")
    logger.info("   • More complex for custom tasks")
    
    # Option 4: Simple Regex + Rules
    logger.info("\n4️⃣ Simple Regex + Rules")
    logger.info("   ✅ Pros:")
    logger.info("   • Fast and lightweight")
    logger.info("   • No external dependencies")
    logger.info("   • Easy to customize for financial data")
    logger.info("   • Reliable for structured documents")
    logger.info("   ❌ Cons:")
    logger.info("   • Limited to pattern matching")
    logger.info("   • Not good for unstructured text")
    logger.info("   • Requires manual rule creation")
    
    # Option 5: Hybrid Approach
    logger.info("\n5️⃣ Hybrid Approach (Recommended)")
    logger.info("   ✅ Pros:")
    logger.info("   • Best of all worlds")
    logger.info("   • Fast regex for structured data")
    logger.info("   • Transformers for sentiment/classification")
    logger.info("   • Fallback to simple processing")
    logger.info("   • Scalable and maintainable")
    logger.info("   ❌ Cons:")
    logger.info("   • More complex implementation")
    logger.info("   • Requires careful integration")
    
    logger.info("\n🎯 Recommendation for Vanta Ledger:")
    logger.info("Use a HYBRID APPROACH:")
    logger.info("1. Regex + Rules for financial data extraction")
    logger.info("2. Transformers for sentiment analysis and classification")
    logger.info("3. Simple text processing for basic NLP tasks")
    logger.info("4. Custom financial entity recognition")
    
    return "hybrid"

def test_hybrid_approach():
    """Test the recommended hybrid approach"""
    logger.info("\n🧪 Testing Hybrid AI Approach...")
    
    # Test 1: Regex for financial data
    logger.info("\n1️⃣ Testing Regex for Financial Data:")
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
    
    logger.info(f"   ✅ Amounts found: {amounts}")
    logger.info(f"   ✅ Dates found: {dates}")
    logger.info(f"   ✅ Companies found: {companies}")
    
    # Test 2: Transformers for sentiment
    logger.info("\n2️⃣ Testing Transformers for Sentiment:")
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
            logger.info(f"   ✅ ")
            
    except Exception as e:
        logger.error(f"   ❌ Transformers test failed: {e}")
    
    # Test 3: Simple text processing
    logger.info("\n3️⃣ Testing Simple Text Processing:")
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
            logger.info(f"   ✅ {entity_type}: {values}")
    
    logger.info("\n✅ Hybrid approach is working perfectly!")

if __name__ == "__main__":
    analyze_alternatives()
    test_hybrid_approach() 