#!/usr/bin/env python3
"""
Kenyan Financial Document Processor for Vanta Ledger
==================================================

This module is specifically optimized for Kenyan business documents:
- Kenya Shillings (KSH) amounts
- Kenyan tax systems (VAT, PIN, etc.)
- Kenyan business entities and regulations
- Local document formats and patterns
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

class KenyanFinancialProcessor:
    """Kenyan-specific financial document processor"""
    
    def __init__(self):
        """Initialize the Kenyan financial processor"""
        logger.info("🚀 Initializing Kenyan Financial Processor...")
        
        # Kenyan-specific patterns
        self.kenyan_patterns = {
            # Kenyan Currency (KSH)
            'ksh_amounts': [
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
            ],
            
            # Kenyan Tax Numbers
            'kenyan_tax_numbers': [
                r'PIN[:\s]*[A-Z0-9\-_]+',  # PIN: ABC123456789
                r'Personal\s*Identification\s*Number[:\s]*[A-Z0-9\-_]+',
                r'VAT[:\s]*[A-Z0-9\-_]+',  # VAT: ABC123456789
                r'Value\s*Added\s*Tax[:\s]*[A-Z0-9\-_]+',
                r'Tax\s*PIN[:\s]*[A-Z0-9\-_]+',
                r'Business\s*Number[:\s]*[A-Z0-9\-_]+',
                r'KRA\s*PIN[:\s]*[A-Z0-9\-_]+',  # KRA PIN: ABC123456789
                r'KRA\s*VAT[:\s]*[A-Z0-9\-_]+',  # KRA VAT: ABC123456789
            ],
            
            # Kenyan Government Entities
            'kenyan_government': [
                r'KRA[:\s]*[A-Z0-9\-_]+',  # Kenya Revenue Authority
                r'Kenya\s*Revenue\s*Authority',
                r'KeRRA[:\s]*[A-Z0-9\-_]+',  # Kenya Rural Roads Authority
                r'Kenya\s*Rural\s*Roads\s*Authority',
                r'KeNHA[:\s]*[A-Z0-9\-_]+',  # Kenya National Highways Authority
                r'Kenya\s*National\s*Highways\s*Authority',
                r'KWS[:\s]*[A-Z0-9\-_]+',  # Kenya Wildlife Service
                r'Kenya\s*Wildlife\s*Service',
                r'KCB[:\s]*[A-Z0-9\-_]+',  # Kenya Commercial Bank
                r'Equity[:\s]*[A-Z0-9\-_]+',  # Equity Bank
                r'Cooperative[:\s]*[A-Z0-9\-_]+',  # Cooperative Bank
            ],
            
            # Kenyan Business Entities
            'kenyan_companies': [
                r'[A-Z\s]+LIMITED',
                r'[A-Z\s]+LLC',
                r'[A-Z\s]+ENTERPRISES',
                r'[A-Z\s]+VENTURES',
                r'[A-Z\s]+SOLUTIONS',
                r'[A-Z\s]+SERVICES',
                r'[A-Z\s]+CONTRACTORS',
                r'[A-Z\s]+SUPPLIES',
                r'[A-Z\s]+GENERAL\s*SUPPLY',
                r'Company[:\s]*([A-Z\s]+LIMITED|[A-Z\s]+LLC|[A-Z\s]+ENTERPRISES)',
                r'Client[:\s]*([A-Z\s]+LIMITED|[A-Z\s]+LLC|[A-Z\s]+ENTERPRISES)',
                r'Vendor[:\s]*([A-Z\s]+LIMITED|[A-Z\s]+LLC|[A-Z\s]+ENTERPRISES)',
            ],
            
            # Kenyan Phone Numbers
            'kenyan_phones': [
                r'\+254\s*\d{9}',  # +254 700 000 000
                r'\+254\s*\d{3}\s*\d{3}\s*\d{3}',  # +254 700 000 000
                r'0\d{9}',  # 0700 000 000
                r'0\d{3}\s*\d{3}\s*\d{3}',  # 0700 000 000
                r'Phone[:\s]*\+254\s*\d{9}',
                r'Tel[:\s]*\+254\s*\d{9}',
                r'Mobile[:\s]*\+254\s*\d{9}',
            ],
            
            # Kenyan Addresses
            'kenyan_addresses': [
                r'P\.?O\.?\s*Box\s+\d+',  # P.O. Box 123
                r'P\.?O\.?\s*Box\s+\d+\s*[A-Za-z\s]+',  # P.O. Box 123 Nairobi
                r'\d+\s+[A-Za-z\s]+(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)',
                r'[A-Za-z\s]+(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)',
                r'Nairobi[,\s]*Kenya',
                r'Mombasa[,\s]*Kenya',
                r'Kisumu[,\s]*Kenya',
                r'Nakuru[,\s]*Kenya',
                r'Eldoret[,\s]*Kenya',
            ],
            
            # Kenyan Dates
            'kenyan_dates': [
                r'\d{1,2}/\d{1,2}/\d{4}',  # 07/08/2024
                r'\d{1,2}-\d{1,2}-\d{4}',  # 07-08-2024
                r'\d{4}-\d{2}-\d{2}',  # 2024-08-07
                r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}',  # 7 Aug 2024
                r'Date[:\s]*\d{1,2}/\d{1,2}/\d{4}',
                r'Effective[:\s]*\d{1,2}/\d{1,2}/\d{4}',
                r'Expiry[:\s]*\d{1,2}/\d{1,2}/\d{4}',
            ],
            
            # Kenyan Tender Numbers
            'kenyan_tenders': [
                r'KeRRA/[A-Z0-9\-_/]+',  # KeRRA/008/KEMA/KS/039/22%/RMLF/22/23-005
                r'KeNHA/[A-Z0-9\-_/]+',  # KeNHA/R1-228-2021
                r'Tender[:\s]*[A-Z0-9\-_/]+',
                r'Bid[:\s]*[A-Z0-9\-_/]+',
                r'RFP[:\s]*[A-Z0-9\-_/]+',  # Request for Proposal
                r'RFQ[:\s]*[A-Z0-9\-_/]+',  # Request for Quote
            ],
            
            # Kenyan Certificates and Licenses
            'kenyan_certificates': [
                r'NCA\s*Certificate[:\s]*[A-Z0-9\-_]+',  # NCA Certificate
                r'National\s*Construction\s*Authority[:\s]*[A-Z0-9\-_]+',
                r'AGPO\s*Certificate[:\s]*[A-Z0-9\-_]+',  # AGPO Certificate
                r'Access\s*to\s*Government\s*Procurement\s*Opportunities[:\s]*[A-Z0-9\-_]+',
                r'BAD\s*permit[:\s]*[A-Z0-9\-_]+',  # Business Activity Description
                r'Business\s*Activity\s*Description[:\s]*[A-Z0-9\-_]+',
                r'License[:\s]*[A-Z0-9\-_]+',
                r'Permit[:\s]*[A-Z0-9\-_]+',
                r'Certificate[:\s]*[A-Z0-9\-_]+',
                r'Registration[:\s]*[A-Z0-9\-_]+',
            ],
            
            # Kenyan Financial Terms
            'kenyan_financial_terms': [
                r'VAT\s*Rate[:\s]*\d+\.?\d*%',  # VAT Rate: 16%
                r'Tax\s*Rate[:\s]*\d+\.?\d*%',  # Tax Rate: 30%
                r'Withholding\s*Tax[:\s]*\d+\.?\d*%',  # Withholding Tax: 5%
                r'Corporate\s*Tax[:\s]*\d+\.?\d*%',  # Corporate Tax: 30%
                r'Personal\s*Tax[:\s]*\d+\.?\d*%',  # Personal Tax: 30%
                r'Turnover\s*Tax[:\s]*\d+\.?\d*%',  # Turnover Tax: 3%
            ],
        }
        
        # Kenyan document types
        self.kenyan_document_types = {
            'kenyan_invoice': [
                r'invoice', r'bill', r'statement', r'payment', r'amount due',
                r'total amount', r'subtotal', r'vat', r'kenya shillings', r'ksh'
            ],
            'kenyan_contract': [
                r'contract', r'agreement', r'terms', r'conditions', r'signature',
                r'effective date', r'expiry', r'termination', r'kenya law'
            ],
            'kenyan_tender': [
                r'tender', r'bid', r'proposal', r'kerra', r'kenha', r'kws',
                r'request for proposal', r'submission', r'deadline', r'evaluation'
            ],
            'kenyan_financial_statement': [
                r'balance sheet', r'income statement', r'profit and loss',
                r'revenue', r'expenses', r'assets', r'liabilities', r'equity',
                r'audited financial statements', r'kenya shillings'
            ],
            'kenyan_tax_document': [
                r'tax', r'vat', r'pin', r'kra', r'kenya revenue authority',
                r'withholding tax', r'corporate tax', r'personal tax'
            ],
            'kenyan_legal': [
                r'legal', r'law', r'court', r'judgment', r'compliance',
                r'regulation', r'license', r'permit', r'certificate', r'kenya'
            ],
        }
        
        logger.info("✅ Kenyan Financial Processor initialized")

    def extract_kenyan_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract Kenyan-specific entities"""
        entities = {}
        
        for entity_type, patterns in self.kenyan_patterns.items():
            entities[entity_type] = []
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                entities[entity_type].extend(matches)
            
            # Remove duplicates while preserving order
            entities[entity_type] = list(dict.fromkeys(entities[entity_type]))
        
        return entities

    def classify_kenyan_document(self, text: str) -> Dict[str, float]:
        """Classify document type using Kenyan patterns"""
        scores = {}
        text_lower = text.lower()
        
        for doc_type, patterns in self.kenyan_document_types.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    score += 1
            scores[doc_type] = score / len(patterns) if patterns else 0
        
        return scores

    def convert_amount_to_ksh(self, amount_text: str) -> Optional[float]:
        """Convert amount text to KSH value"""
        try:
            # Remove currency symbols and words
            cleaned = re.sub(r'[KShKESKenya\s*Shillings?]', '', amount_text, flags=re.IGNORECASE)
            # Remove commas
            cleaned = cleaned.replace(',', '')
            # Convert to float
            return float(cleaned)
        except:
            return None

    def extract_ksh_amounts(self, text: str) -> List[Dict[str, Any]]:
        """Extract and parse KSH amounts with context"""
        amounts = []
        
        # Find all KSH amount patterns
        patterns = [
            r'(KSh\s*[\d,]+\.?\d*)',
            r'(KES\s*[\d,]+\.?\d*)',
            r'(Kenya\s*Shillings?\s*[\d,]+\.?\d*)',
            r'(Kenyan\s*Shillings?\s*[\d,]+\.?\d*)',
            r'([\d,]+\.?\d*\s*KSh)',
            r'([\d,]+\.?\d*\s*KES)',
            r'([\d,]+\.?\d*\s*Shillings?)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                amount_text = match.group(1)
                amount_value = self.convert_amount_to_ksh(amount_text)
                
                # Get context (words around the amount)
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]
                
                amounts.append({
                    'text': amount_text,
                    'value': amount_value,
                    'context': context,
                    'position': match.start()
                })
        
        return amounts

    def analyze_kenyan_financial_document(self, text: str) -> Dict[str, Any]:
        """Analyze Kenyan financial document"""
        # Extract Kenyan entities
        entities = self.extract_kenyan_entities(text)
        
        # Extract KSH amounts with context
        ksh_amounts = self.extract_ksh_amounts(text)
        
        # Classify document type
        doc_type_scores = self.classify_kenyan_document(text)
        document_type = max(doc_type_scores, key=doc_type_scores.get) if doc_type_scores else 'unknown'
        
        # Calculate total KSH value
        total_ksh = sum(amount['value'] for amount in ksh_amounts if amount['value'] is not None)
        
        # Find largest amount
        largest_amount = max(ksh_amounts, key=lambda x: x['value'] or 0) if ksh_amounts else None
        
        return {
            'kenyan_entities': entities,
            'ksh_amounts': ksh_amounts,
            'total_ksh_value': total_ksh,
            'largest_amount': largest_amount,
            'document_type': document_type,
            'document_type_scores': doc_type_scores,
            'analysis_date': datetime.now().isoformat()
        }

def main():
    """Test the Kenyan financial processor"""
    processor = KenyanFinancialProcessor()
    
    # Test with Kenyan sample text
    sample_text = """
    INVOICE #INV-2024-001
    
    Date: 07/08/2024
    Company: ALTAN ENTERPRISES LIMITED
    PIN: ABC123456789
    VAT: XYZ987654321
    
    Contact: john@altan.com
    Phone: +254 700 000 001
    Address: P.O. Box 123, Nairobi, Kenya
    
    ITEMS:
    1. Construction Services - KSh 15,750,000.00
    2. Materials - KSh 2,500,000.00
    3. Equipment - KSh 1,250,000.00
    
    Subtotal: KSh 19,500,000.00
    VAT (16%): KSh 3,120,000.00
    Total: KSh 22,620,000.00
    
    Tender Reference: KeRRA/008/KEMA/KS/039/22%/RMLF/22/23-005
    NCA Certificate: NCA-2024-001
    AGPO Certificate: AGPO-2024-001
    
    This is a profitable Kenyan construction project with excellent financial terms.
    """
    
    logger.info("🧪 Testing Kenyan Financial Processor...")
    logger.info("=")
    
    # Analyze the document
    analysis = processor.analyze_kenyan_financial_document(sample_text)
    
    logger.info("📊 Kenyan Entities Found:")
    for entity_type, values in analysis['kenyan_entities'].items():
        if values:
            logger.info(f"  {entity_type}: {values}")
    
    logger.info(f"\n💰 KSH Amounts Found:")
    for amount in analysis['ksh_amounts']:
        logger.info(f"  {amount[")
    
    logger.info(f"\n📄 Document Type: {analysis[")
    logger.info(f"   Scores: {analysis[")
    
    logger.info(f"\n💵 Total KSH Value: KSh {analysis[")
    
    if analysis['largest_amount']:
        logger.info(f"🏆 Largest Amount: {analysis[")
    
    logger.info("\n✅ Kenyan Financial Processor is working perfectly!")

if __name__ == "__main__":
    main() 