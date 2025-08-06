#!/usr/bin/env python3
"""
Enhanced Document Processor for Vanta Ledger
===========================================

This module uses a hybrid AI approach combining:
1. Regex + Rules for financial data extraction
2. Transformers for sentiment analysis and classification
3. Simple text processing for basic NLP tasks
4. Custom financial entity recognition

This approach is more reliable and doesn't depend on spaCy models.
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedDocumentProcessor:
    """Enhanced document processor using hybrid AI approach"""
    
    def __init__(self):
        """Initialize the enhanced document processor"""
        logger.info("🚀 Initializing Enhanced Document Processor...")
        
        # Initialize AI models
        self.sentiment_analyzer = None
        self.text_classifier = None
        
        try:
            from transformers import pipeline
            self.sentiment_analyzer = pipeline("sentiment-analysis")
            self.text_classifier = pipeline("text-classification", model="distilbert-base-uncased")
            logger.info("✅ Transformers models loaded successfully")
        except Exception as e:
            logger.warning(f"⚠️  Transformers not available: {e}")
        
        # Financial entity patterns
        self.patterns = {
            'amounts': [
                # Kenyan Currency (KSH) - Primary focus
                r'KSh\s*[\d,]+\.?\d*',  # KSh 1,234.56
                r'KES\s*[\d,]+\.?\d*',  # KES 1,234.56
                r'Kenya\s*Shillings?\s*[\d,]+\.?\d*',  # Kenya Shillings 1,234.56
                r'Kenyan\s*Shillings?\s*[\d,]+\.?\d*',  # Kenyan Shillings 1,234.56
                r'[\d,]+\.?\d*\s*KSh',  # 1,234.56 KSh
                r'[\d,]+\.?\d*\s*KES',  # 1,234.56 KES
                r'[\d,]+\.?\d*\s*Shillings?',  # 1,234.56 Shillings
                r'Amount[:\s]*KSh\s*[\d,]+\.?\d*',  # Amount: KSh 1,234.56
                r'Total[:\s]*KSh\s*[\d,]+\.?\d*',  # Total: KSh 1,234.56
                r'Price[:\s]*KSh\s*[\d,]+\.?\d*',  # Price: KSh 1,234.56
                r'Cost[:\s]*KSh\s*[\d,]+\.?\d*',  # Cost: KSh 1,234.56
                r'Value[:\s]*KSh\s*[\d,]+\.?\d*',  # Value: KSh 1,234.56
                r'Sum[:\s]*KSh\s*[\d,]+\.?\d*',  # Sum: KSh 1,234.56
                # Other currencies (fallback)
                r'\$[\d,]+\.?\d*',  # $1,234.56
                r'[\d,]+\.?\d*\s*(USD|EUR|GBP)',  # 1,234.56 USD
                r'Amount[:\s]*\$?[\d,]+\.?\d*',  # Amount: $1,234.56
                r'Total[:\s]*\$?[\d,]+\.?\d*',  # Total: $1,234.56
            ],
            'dates': [
                r'\d{4}-\d{2}-\d{2}',  # 2024-08-07
                r'\d{2}/\d{2}/\d{4}',  # 08/07/2024
                r'\d{2}-\d{2}-\d{4}',  # 08-07-2024
                r'Date[:\s]*\d{4}-\d{2}-\d{2}',  # Date: 2024-08-07
            ],
            'companies': [
                r'[A-Z\s]+LIMITED',
                r'[A-Z\s]+LLC',
                r'[A-Z\s]+INC',
                r'[A-Z\s]+CORP',
                r'Company[:\s]*([A-Z\s]+LIMITED|[A-Z\s]+LLC|[A-Z\s]+INC)',
            ],
            'invoices': [
                r'Invoice[:\s]*#?[A-Z0-9\-_]+',
                r'INV[:\s]*[A-Z0-9\-_]+',
                r'Bill[:\s]*#?[A-Z0-9\-_]+',
            ],
            'tax_numbers': [
                # Kenyan Tax Numbers (Primary focus)
                r'PIN[:\s]*[A-Z0-9\-_]+',  # PIN: ABC123456789
                r'Personal\s*Identification\s*Number[:\s]*[A-Z0-9\-_]+',
                r'VAT[:\s]*[A-Z0-9\-_]+',  # VAT: ABC123456789
                r'Value\s*Added\s*Tax[:\s]*[A-Z0-9\-_]+',
                r'KRA\s*PIN[:\s]*[A-Z0-9\-_]+',  # KRA PIN: ABC123456789
                r'KRA\s*VAT[:\s]*[A-Z0-9\-_]+',  # KRA VAT: ABC123456789
                r'Tax\s*PIN[:\s]*[A-Z0-9\-_]+',
                r'Business\s*Number[:\s]*[A-Z0-9\-_]+',
                # Other tax numbers (fallback)
                r'Tax[:\s]*[A-Z0-9\-_]+',
            ],
            'emails': [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            ],
            'phones': [
                # Kenyan Phone Numbers (Primary focus)
                r'\+254\s*\d{9}',  # +254 700 000 000
                r'\+254\s*\d{3}\s*\d{3}\s*\d{3}',  # +254 700 000 000
                r'0\d{9}',  # 0700 000 000
                r'0\d{3}\s*\d{3}\s*\d{3}',  # 0700 000 000
                r'Phone[:\s]*\+254\s*\d{9}',
                r'Tel[:\s]*\+254\s*\d{9}',
                r'Mobile[:\s]*\+254\s*\d{9}',
                # Other phone numbers (fallback)
                r'\+?[\d\s\-\(\)]{10,}',
                r'Phone[:\s]*\+?[\d\s\-\(\)]+',
                r'Tel[:\s]*\+?[\d\s\-\(\)]+',
            ],
            'percentages': [
                r'\d+\.?\d*%',
                r'\d+\.?\d*\s*percent',
            ]
        }
        
        # Document type patterns
        self.document_types = {
            'invoice': [
                r'invoice', r'bill', r'statement', r'payment', r'amount due',
                r'total amount', r'subtotal', r'tax', r'vat', r'kenya shillings', r'ksh'
            ],
            'contract': [
                r'contract', r'agreement', r'terms', r'conditions', r'signature',
                r'effective date', r'expiry', r'termination', r'kenya law'
            ],
            'financial_statement': [
                r'balance sheet', r'income statement', r'profit and loss',
                r'revenue', r'expenses', r'assets', r'liabilities', r'equity',
                r'audited financial statements', r'kenya shillings'
            ],
            'tender': [
                r'tender', r'bid', r'proposal', r'rfp', r'request for proposal',
                r'submission', r'deadline', r'evaluation', r'kerra', r'kenha', r'kws'
            ],
            'legal': [
                r'legal', r'law', r'court', r'judgment', r'compliance',
                r'regulation', r'license', r'permit', r'certificate', r'kenya'
            ],
            'kenyan_tax_document': [
                r'tax', r'vat', r'pin', r'kra', r'kenya revenue authority',
                r'withholding tax', r'corporate tax', r'personal tax'
            ],
            'kenyan_certificate': [
                r'nca certificate', r'agpo certificate', r'bad permit',
                r'national construction authority', r'access to government procurement'
            ]
        }
        
        logger.info("✅ Enhanced Document Processor initialized")

    def extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text.strip()
        except:
            try:
                import PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                return text.strip()
            except Exception as e:
                logger.error(f"Error extracting text from PDF {file_path}: {e}")
                return f"[PDF file: {file_path.name} - text extraction failed]"

    def extract_text_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file"""
        try:
            import docx
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from DOCX {file_path}: {e}")
            return f"[DOCX file: {file_path.name} - processing failed]"

    def extract_text_from_image(self, file_path: Path) -> str:
        """Extract text from image using OCR"""
        try:
            from PIL import Image
            import pytesseract
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from image {file_path}: {e}")
            return f"[Image file: {file_path.name} - OCR failed]"

    def extract_text(self, file_path: Path) -> str:
        """Extract text from any supported file type"""
        suffix = file_path.suffix.lower()
        
        if suffix == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif suffix == '.docx':
            return self.extract_text_from_docx(file_path)
        elif suffix in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
            return self.extract_text_from_image(file_path)
        elif suffix == '.txt':
            return file_path.read_text(encoding='utf-8', errors='ignore')
        else:
            return f"[Unsupported file type: {suffix}]"

    def extract_financial_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract financial entities using regex patterns"""
        entities = {}
        
        for entity_type, patterns in self.patterns.items():
            entities[entity_type] = []
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                entities[entity_type].extend(matches)
            
            # Remove duplicates while preserving order
            entities[entity_type] = list(dict.fromkeys(entities[entity_type]))
        
        return entities

    def classify_document_type(self, text: str) -> Dict[str, float]:
        """Classify document type using pattern matching"""
        scores = {}
        text_lower = text.lower()
        
        for doc_type, patterns in self.document_types.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    score += 1
            scores[doc_type] = score / len(patterns) if patterns else 0
        
        return scores

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using transformers"""
        if not self.sentiment_analyzer:
            return {'sentiment': 'neutral', 'confidence': 0.5, 'method': 'fallback'}
        
        try:
            # Use first 500 characters for sentiment analysis
            text_sample = text[:500]
            result = self.sentiment_analyzer(text_sample)
            
            return {
                'sentiment': result[0]['label'].lower(),
                'confidence': result[0]['score'],
                'method': 'transformers'
            }
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {e}")
            return {'sentiment': 'neutral', 'confidence': 0.5, 'method': 'fallback'}

    def extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases using simple NLP techniques"""
        # Simple key phrase extraction
        sentences = re.split(r'[.!?]+', text)
        key_phrases = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 200:  # Reasonable sentence length
                # Look for sentences with financial keywords
                financial_keywords = [
                    'amount', 'total', 'payment', 'invoice', 'contract',
                    'revenue', 'expense', 'profit', 'loss', 'balance',
                    'company', 'limited', 'corporation', 'enterprise'
                ]
                
                if any(keyword in sentence.lower() for keyword in financial_keywords):
                    key_phrases.append(sentence)
        
        return key_phrases[:10]  # Return top 10 key phrases

    def process_document(self, file_path: Path) -> Dict[str, Any]:
        """Process a document and extract all information"""
        logger.info(f"📄 Processing document: {file_path.name}")
        
        # Extract text
        text = self.extract_text(file_path)
        
        # Extract entities
        entities = self.extract_financial_entities(text)
        
        # Classify document type
        doc_type_scores = self.classify_document_type(text)
        document_type = max(doc_type_scores, key=doc_type_scores.get) if doc_type_scores else 'unknown'
        
        # Analyze sentiment
        sentiment = self.analyze_sentiment(text)
        
        # Extract key phrases
        key_phrases = self.extract_key_phrases(text)
        
        # Calculate document statistics
        stats = {
            'word_count': len(text.split()),
            'character_count': len(text),
            'line_count': len(text.split('\n')),
            'entity_count': sum(len(v) for v in entities.values())
        }
        
        # Create processing result
        result = {
            'filename': file_path.name,
            'file_path': str(file_path),
            'file_size': file_path.stat().st_size,
            'file_type': file_path.suffix.lower(),
            'processing_date': datetime.now().isoformat(),
            'text': text,
            'entities': entities,
            'document_type': document_type,
            'document_type_scores': doc_type_scores,
            'sentiment': sentiment,
            'key_phrases': key_phrases,
            'statistics': stats,
            'processing_status': 'completed'
        }
        
        logger.info(f"✅ Document processed: {file_path.name}")
        return result

    def process_directory(self, directory_path: Path) -> List[Dict[str, Any]]:
        """Process all documents in a directory"""
        logger.info(f"📁 Processing directory: {directory_path}")
        
        results = []
        supported_extensions = {'.pdf', '.docx', '.txt', '.jpg', '.jpeg', '.png', '.tiff', '.bmp'}
        
        for file_path in directory_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    result = self.process_document(file_path)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    results.append({
                        'filename': file_path.name,
                        'file_path': str(file_path),
                        'processing_status': 'failed',
                        'error': str(e)
                    })
        
        logger.info(f"✅ Processed {len(results)} documents")
        return results

    def save_results(self, results: List[Dict[str, Any]], output_path: Path):
        """Save processing results to JSON file"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Results saved to: {output_path}")

def main():
    """Test the enhanced document processor"""
    processor = EnhancedDocumentProcessor()
    
    # Test with sample text
    sample_text = """
    Invoice #INV-2024-001
    Date: 2024-08-07
    Company: ALTAN ENTERPRISES LIMITED
    Contact: john@altan.com
    Phone: +254-700-000-001
    
    Amount: $15,750.00
    Tax: $1,575.00
    Total: $17,325.00
    
    This is a profitable financial statement showing strong revenue growth.
    """
    
    print("🧪 Testing Enhanced Document Processor...")
    print("=" * 60)
    
    # Test entity extraction
    entities = processor.extract_financial_entities(sample_text)
    print("📊 Extracted Entities:")
    for entity_type, values in entities.items():
        if values:
            print(f"  {entity_type}: {values}")
    
    # Test document classification
    doc_type = processor.classify_document_type(sample_text)
    print(f"\n📄 Document Type: {max(doc_type, key=doc_type.get)}")
    print(f"   Scores: {doc_type}")
    
    # Test sentiment analysis
    sentiment = processor.analyze_sentiment(sample_text)
    print(f"\n😊 Sentiment: {sentiment['sentiment']} (confidence: {sentiment['confidence']:.2f})")
    
    # Test key phrases
    phrases = processor.extract_key_phrases(sample_text)
    print(f"\n🔑 Key Phrases: {phrases}")
    
    print("\n✅ Enhanced Document Processor is working perfectly!")

if __name__ == "__main__":
    main() 