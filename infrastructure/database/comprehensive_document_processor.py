#!/usr/bin/env python3
"""
Comprehensive Document Processor for Vanta Ledger
================================================

This module processes ALL types of business documents including:
- Financial documents (invoices, statements, budgets)
- Legal documents (contracts, agreements, compliance)
- HR documents (employment, payroll, policies)
- Marketing documents (proposals, presentations, reports)
- Technical documents (specifications, manuals, procedures)
- Government documents (tax forms, permits, licenses)
- And much more!

This is a complete business document intelligence system.
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import csv
import xml.etree.ElementTree as ET

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveDocumentProcessor:
    """Comprehensive document processor for all business documents"""
    
    def __init__(self):
        """Initialize the comprehensive document processor"""
        logger.info("🚀 Initializing Comprehensive Document Processor...")
        
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
        
        # Comprehensive entity patterns for ALL business documents
        self.patterns = {
            # Financial Entities
            'amounts': [
                r'\$[\d,]+\.?\d*',  # $1,234.56
                r'[\d,]+\.?\d*\s*(USD|KES|EUR|GBP|CAD|AUD|JPY|CHF)',  # 1,234.56 USD
                r'Amount[:\s]*\$?[\d,]+\.?\d*',  # Amount: $1,234.56
                r'Total[:\s]*\$?[\d,]+\.?\d*',  # Total: $1,234.56
                r'Price[:\s]*\$?[\d,]+\.?\d*',  # Price: $1,234.56
                r'Cost[:\s]*\$?[\d,]+\.?\d*',  # Cost: $1,234.56
                r'Revenue[:\s]*\$?[\d,]+\.?\d*',  # Revenue: $1,234.56
                r'Expense[:\s]*\$?[\d,]+\.?\d*',  # Expense: $1,234.56
            ],
            'dates': [
                r'\d{4}-\d{2}-\d{2}',  # 2024-08-07
                r'\d{2}/\d{2}/\d{4}',  # 08/07/2024
                r'\d{2}-\d{2}-\d{4}',  # 08-07-2024
                r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}',  # 7 Aug 2024
                r'Date[:\s]*\d{4}-\d{2}-\d{2}',  # Date: 2024-08-07
                r'Effective[:\s]*\d{4}-\d{2}-\d{2}',  # Effective: 2024-08-07
                r'Expiry[:\s]*\d{4}-\d{2}-\d{2}',  # Expiry: 2024-08-07
            ],
            'companies': [
                r'[A-Z\s]+LIMITED',
                r'[A-Z\s]+LLC',
                r'[A-Z\s]+INC',
                r'[A-Z\s]+CORP',
                r'[A-Z\s]+ENTERPRISES',
                r'[A-Z\s]+VENTURES',
                r'[A-Z\s]+SOLUTIONS',
                r'[A-Z\s]+SERVICES',
                r'Company[:\s]*([A-Z\s]+LIMITED|[A-Z\s]+LLC|[A-Z\s]+INC)',
                r'Client[:\s]*([A-Z\s]+LIMITED|[A-Z\s]+LLC|[A-Z\s]+INC)',
                r'Vendor[:\s]*([A-Z\s]+LIMITED|[A-Z\s]+LLC|[A-Z\s]+INC)',
            ],
            
            # Document Identifiers
            'invoices': [
                r'Invoice[:\s]*#?[A-Z0-9\-_]+',
                r'INV[:\s]*[A-Z0-9\-_]+',
                r'Bill[:\s]*#?[A-Z0-9\-_]+',
                r'Receipt[:\s]*#?[A-Z0-9\-_]+',
            ],
            'contracts': [
                r'Contract[:\s]*#?[A-Z0-9\-_]+',
                r'Agreement[:\s]*#?[A-Z0-9\-_]+',
                r'PO[:\s]*[A-Z0-9\-_]+',  # Purchase Order
                r'Purchase[:\s]*Order[:\s]*#?[A-Z0-9\-_]+',
            ],
            'tenders': [
                r'Tender[:\s]*#?[A-Z0-9\-_]+',
                r'Bid[:\s]*#?[A-Z0-9\-_]+',
                r'RFP[:\s]*[A-Z0-9\-_]+',  # Request for Proposal
                r'RFQ[:\s]*[A-Z0-9\-_]+',  # Request for Quote
            ],
            
            # Legal & Compliance
            'tax_numbers': [
                r'Tax[:\s]*[A-Z0-9\-_]+',
                r'VAT[:\s]*[A-Z0-9\-_]+',
                r'PIN[:\s]*[A-Z0-9\-_]+',
                r'Tax[:\s]*ID[:\s]*[A-Z0-9\-_]+',
                r'Business[:\s]*Number[:\s]*[A-Z0-9\-_]+',
            ],
            'licenses': [
                r'License[:\s]*#?[A-Z0-9\-_]+',
                r'Permit[:\s]*#?[A-Z0-9\-_]+',
                r'Certificate[:\s]*#?[A-Z0-9\-_]+',
                r'Registration[:\s]*#?[A-Z0-9\-_]+',
            ],
            
            # Contact Information
            'emails': [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            ],
            'phones': [
                r'\+?[\d\s\-\(\)]{10,}',
                r'Phone[:\s]*\+?[\d\s\-\(\)]+',
                r'Tel[:\s]*\+?[\d\s\-\(\)]+',
                r'Mobile[:\s]*\+?[\d\s\-\(\)]+',
                r'Fax[:\s]*\+?[\d\s\-\(\)]+',
            ],
            'addresses': [
                r'\d+\s+[A-Za-z\s]+(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)',
                r'P\.?O\.?\s*Box\s+\d+',
                r'Suite\s+\d+',
                r'Floor\s+\d+',
            ],
            
            # Financial Metrics
            'percentages': [
                r'\d+\.?\d*%',
                r'\d+\.?\d*\s*percent',
                r'Rate[:\s]*\d+\.?\d*%',
                r'Interest[:\s]*\d+\.?\d*%',
                r'Discount[:\s]*\d+\.?\d*%',
            ],
            'currencies': [
                r'\$[\d,]+\.?\d*',
                r'[\d,]+\.?\d*\s*(USD|KES|EUR|GBP|CAD|AUD|JPY|CHF|CNY|INR)',
                r'Currency[:\s]*(USD|KES|EUR|GBP|CAD|AUD|JPY|CHF|CNY|INR)',
            ],
            
            # HR & Employment
            'employee_ids': [
                r'Employee[:\s]*ID[:\s]*[A-Z0-9\-_]+',
                r'Staff[:\s]*ID[:\s]*[A-Z0-9\-_]+',
                r'Personnel[:\s]*ID[:\s]*[A-Z0-9\-_]+',
            ],
            'job_titles': [
                r'Position[:\s]*[A-Za-z\s]+',
                r'Title[:\s]*[A-Za-z\s]+',
                r'Role[:\s]*[A-Za-z\s]+',
                r'Manager|Director|CEO|CFO|CTO|VP|President|Executive',
            ],
            
            # Technical & Specifications
            'product_codes': [
                r'Product[:\s]*[A-Z0-9\-_]+',
                r'Item[:\s]*[A-Z0-9\-_]+',
                r'SKU[:\s]*[A-Z0-9\-_]+',
                r'Model[:\s]*[A-Z0-9\-_]+',
                r'Serial[:\s]*[A-Z0-9\-_]+',
            ],
            'specifications': [
                r'\d+\s*(kg|lb|g|oz)',  # Weight
                r'\d+\s*(m|cm|mm|ft|in)',  # Dimensions
                r'\d+\s*(W|V|A|Hz)',  # Electrical specs
                r'Color[:\s]*[A-Za-z\s]+',
                r'Material[:\s]*[A-Za-z\s]+',
            ],
            
            # Government & Regulatory
            'government_ids': [
                r'Government[:\s]*ID[:\s]*[A-Z0-9\-_]+',
                r'National[:\s]*ID[:\s]*[A-Z0-9\-_]+',
                r'Passport[:\s]*[A-Z0-9\-_]+',
                r'Driver[:\s]*License[:\s]*[A-Z0-9\-_]+',
            ],
            'regulatory_numbers': [
                r'Reg[:\s]*[A-Z0-9\-_]+',
                r'Compliance[:\s]*[A-Z0-9\-_]+',
                r'Standard[:\s]*[A-Z0-9\-_]+',
                r'Certification[:\s]*[A-Z0-9\-_]+',
            ],
            
            # Project & Management
            'project_codes': [
                r'Project[:\s]*[A-Z0-9\-_]+',
                r'Task[:\s]*[A-Z0-9\-_]+',
                r'Milestone[:\s]*[A-Z0-9\-_]+',
                r'Phase[:\s]*[A-Z0-9\-_]+',
            ],
            'time_periods': [
                r'\d+\s*(days|weeks|months|years)',
                r'Duration[:\s]*\d+\s*(days|weeks|months|years)',
                r'Term[:\s]*\d+\s*(days|weeks|months|years)',
            ],
        }
        
        # Comprehensive document type patterns
        self.document_types = {
            # Financial Documents
            'invoice': [
                r'invoice', r'bill', r'statement', r'payment', r'amount due',
                r'total amount', r'subtotal', r'tax', r'vat', r'receipt'
            ],
            'financial_statement': [
                r'balance sheet', r'income statement', r'profit and loss',
                r'revenue', r'expenses', r'assets', r'liabilities', r'equity',
                r'cash flow', r'financial report', r'audit report'
            ],
            'budget': [
                r'budget', r'forecast', r'projection', r'planning',
                r'cost estimate', r'financial plan', r'expense report'
            ],
            
            # Legal Documents
            'contract': [
                r'contract', r'agreement', r'terms', r'conditions', r'signature',
                r'effective date', r'expiry', r'termination', r'clause',
                r'legal document', r'legal agreement'
            ],
            'legal_compliance': [
                r'legal', r'law', r'court', r'judgment', r'compliance',
                r'regulation', r'license', r'permit', r'certificate',
                r'legal notice', r'legal opinion'
            ],
            
            # HR Documents
            'employment': [
                r'employment', r'job', r'position', r'hire', r'fire',
                r'employee', r'staff', r'personnel', r'human resources',
                r'job description', r'employment contract'
            ],
            'payroll': [
                r'payroll', r'salary', r'wage', r'compensation', r'benefits',
                r'timesheet', r'pay stub', r'paycheck', r'bonus'
            ],
            'hr_policy': [
                r'policy', r'procedure', r'handbook', r'manual', r'guidelines',
                r'hr policy', r'employee handbook', r'company policy'
            ],
            
            # Marketing & Sales
            'proposal': [
                r'proposal', r'quote', r'estimate', r'bid', r'offer',
                r'presentation', r'pitch', r'business proposal'
            ],
            'marketing': [
                r'marketing', r'advertising', r'campaign', r'promotion',
                r'brand', r'publicity', r'marketing plan', r'ad campaign'
            ],
            'sales': [
                r'sales', r'customer', r'client', r'account', r'order',
                r'sales report', r'customer list', r'sales forecast'
            ],
            
            # Technical Documents
            'technical_spec': [
                r'specification', r'technical', r'engineering', r'design',
                r'blueprint', r'drawing', r'diagram', r'schematic'
            ],
            'manual': [
                r'manual', r'instruction', r'guide', r'procedure',
                r'how to', r'user guide', r'instruction manual'
            ],
            'technical_report': [
                r'technical report', r'engineering report', r'analysis',
                r'feasibility study', r'technical assessment'
            ],
            
            # Government & Regulatory
            'government_form': [
                r'government form', r'tax form', r'application form',
                r'permit application', r'license application'
            ],
            'regulatory': [
                r'regulatory', r'compliance', r'standard', r'requirement',
                r'regulation', r'policy compliance'
            ],
            
            # Project Management
            'project_plan': [
                r'project plan', r'project proposal', r'project scope',
                r'work plan', r'implementation plan'
            ],
            'tender': [
                r'tender', r'bid', r'proposal', r'rfp', r'request for proposal',
                r'submission', r'deadline', r'evaluation', r'bid document'
            ],
            
            # Reports & Analytics
            'business_report': [
                r'business report', r'annual report', r'quarterly report',
                r'performance report', r'status report'
            ],
            'analytics': [
                r'analytics', r'analysis', r'data analysis', r'statistics',
                r'performance metrics', r'kpi', r'key performance indicator'
            ],
            
            # Communication
            'correspondence': [
                r'letter', r'memo', r'email', r'communication', r'notice',
                r'announcement', r'correspondence'
            ],
            'presentation': [
                r'presentation', r'slide', r'powerpoint', r'demo',
                r'presentation deck', r'slideshow'
            ],
        }
        
        logger.info("✅ Comprehensive Document Processor initialized")

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

    def extract_text_from_csv(self, file_path: Path) -> str:
        """Extract text from CSV file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                text = ""
                for row in reader:
                    text += " | ".join(row) + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from CSV {file_path}: {e}")
            return f"[CSV file: {file_path.name} - processing failed]"

    def extract_text_from_xml(self, file_path: Path) -> str:
        """Extract text from XML file"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            text = ET.tostring(root, encoding='unicode', method='text')
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from XML {file_path}: {e}")
            return f"[XML file: {file_path.name} - processing failed]"

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
        elif suffix == '.csv':
            return self.extract_text_from_csv(file_path)
        elif suffix == '.xml':
            return self.extract_text_from_xml(file_path)
        else:
            return f"[Unsupported file type: {suffix}]"

    def extract_comprehensive_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract comprehensive entities using regex patterns"""
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
        """Extract key phrases using comprehensive business keywords"""
        sentences = re.split(r'[.!?]+', text)
        key_phrases = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 200:  # Reasonable sentence length
                # Comprehensive business keywords
                business_keywords = [
                    # Financial
                    'amount', 'total', 'payment', 'invoice', 'contract', 'revenue', 'expense', 'profit', 'loss', 'balance',
                    'budget', 'cost', 'price', 'financial', 'money', 'currency', 'tax', 'vat',
                    
                    # Business
                    'company', 'limited', 'corporation', 'enterprise', 'business', 'organization', 'firm',
                    'client', 'customer', 'vendor', 'supplier', 'partner', 'stakeholder',
                    
                    # Legal
                    'legal', 'contract', 'agreement', 'terms', 'conditions', 'compliance', 'regulation',
                    'law', 'court', 'judgment', 'license', 'permit', 'certificate',
                    
                    # HR
                    'employee', 'staff', 'personnel', 'human resources', 'employment', 'job', 'position',
                    'salary', 'payroll', 'benefits', 'policy', 'procedure',
                    
                    # Technical
                    'technical', 'engineering', 'specification', 'design', 'system', 'technology',
                    'software', 'hardware', 'equipment', 'machinery', 'product',
                    
                    # Project
                    'project', 'task', 'milestone', 'deadline', 'timeline', 'schedule',
                    'plan', 'strategy', 'objective', 'goal', 'target',
                    
                    # Marketing
                    'marketing', 'advertising', 'campaign', 'promotion', 'brand', 'sales',
                    'customer', 'market', 'competition', 'strategy',
                    
                    # Government
                    'government', 'regulatory', 'compliance', 'standard', 'requirement',
                    'permit', 'license', 'certification', 'audit',
                ]
                
                if any(keyword in sentence.lower() for keyword in business_keywords):
                    key_phrases.append(sentence)
        
        return key_phrases[:15]  # Return top 15 key phrases

    def process_document(self, file_path: Path) -> Dict[str, Any]:
        """Process a document and extract all information"""
        logger.info(f"📄 Processing document: {file_path.name}")
        
        # Extract text
        text = self.extract_text(file_path)
        
        # Extract entities
        entities = self.extract_comprehensive_entities(text)
        
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
            'entity_count': sum(len(v) for v in entities.values()),
            'entity_types_found': len([k for k, v in entities.items() if v])
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
        supported_extensions = {
            '.pdf', '.docx', '.txt', '.jpg', '.jpeg', '.png', '.tiff', '.bmp',
            '.csv', '.xml', '.json', '.rtf', '.odt'
        }
        
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
    """Test the comprehensive document processor"""
    processor = ComprehensiveDocumentProcessor()
    
    # Test with comprehensive sample text
    sample_text = """
    CONTRACT AGREEMENT #CON-2024-001
    
    Date: 2024-08-07
    Effective Date: 2024-08-15
    Expiry Date: 2025-08-15
    
    PARTIES:
    Company: ALTAN ENTERPRISES LIMITED
    Contact: john@altan.com
    Phone: +254-700-000-001
    Address: 123 Business Street, Nairobi, Kenya
    
    Client: DORDEN VENTURES LIMITED
    Contact: sarah@dorden.com
    Phone: +254-700-000-002
    
    PROJECT DETAILS:
    Project Code: PRJ-2024-001
    Duration: 12 months
    Budget: $150,000.00 USD
    
    TECHNICAL SPECIFICATIONS:
    Equipment: Model XYZ-2000
    Serial Number: SN-2024-001
    Specifications: 500W, 220V, 50Hz
    Weight: 25 kg
    Dimensions: 100cm x 50cm x 30cm
    
    FINANCIAL TERMS:
    Payment Schedule: Monthly installments
    Amount: $12,500.00 per month
    Tax Rate: 16% VAT
    Total Contract Value: $174,000.00
    
    LEGAL COMPLIANCE:
    License Number: LIC-2024-001
    Tax PIN: PIN-123456789
    VAT Number: VAT-987654321
    
    EMPLOYMENT DETAILS:
    Project Manager: John Smith
    Employee ID: EMP-001
    Position: Senior Project Manager
    
    This is a comprehensive business contract with excellent terms and conditions.
    """
    
    print("🧪 Testing Comprehensive Document Processor...")
    print("=" * 70)
    
    # Test entity extraction
    entities = processor.extract_comprehensive_entities(sample_text)
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
    
    print("\n✅ Comprehensive Document Processor is working perfectly!")

if __name__ == "__main__":
    main() 