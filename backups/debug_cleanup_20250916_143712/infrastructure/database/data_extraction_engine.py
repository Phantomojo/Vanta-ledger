#!/usr/bin/env python3
"""
Vanta Ledger Data Extraction Engine
===================================

This engine processes migrated documents and extracts structured data
for financial analysis, reporting, and business intelligence.

Author: Vanta Ledger Team
"""

import os
import json
import re
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from decimal import Decimal
import asyncio
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from sqlalchemy import create_engine, text
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
POSTGRES_URI = f"postgresql://vanta_user:{os.getenv('POSTGRES_PASSWORD')}@localhost:5432/vanta_ledger"
MONGO_URI = f"mongodb://admin:{os.getenv('MONGO_INITDB_ROOT_PASSWORD')}@localhost:27017/vanta_ledger?authSource=admin"

@dataclass
class ExtractedData:
    """Structured data extracted from documents"""
    document_id: int
    filename: str
    company_name: Optional[str] = None
    transaction_date: Optional[datetime] = None
    amount: Optional[Decimal] = None
    currency: str = "KES"
    transaction_type: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    reference_number: Optional[str] = None
    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None
    tax_amount: Optional[Decimal] = None
    payment_method: Optional[str] = None
    confidence_score: float = 0.0
    extraction_method: str = "regex"
    extracted_at: datetime = None

class DataExtractionEngine:
    """Advanced data extraction engine for financial documents"""
    
    def __init__(self):
        self.postgres_engine = None
        self.mongo_client = None
        self.mongo_db = None
        self.extraction_patterns = self._load_extraction_patterns()
        self.company_patterns = self._load_company_patterns()
        
    def connect_databases(self):
        """Connect to both databases"""
        try:
            # Connect to PostgreSQL
            self.postgres_engine = create_engine(POSTGRES_URI)
            logger.info("✅ Connected to PostgreSQL")
            
            # Connect to MongoDB
            self.mongo_client = MongoClient(MONGO_URI)
            self.mongo_db = self.mongo_client.vanta_ledger
            logger.info("✅ Connected to MongoDB")
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def _load_extraction_patterns(self) -> Dict[str, List[str]]:
        """Load regex patterns for data extraction"""
        return {
            "amount": [
                r"KES\s*([\d,]+\.?\d*)",
                r"KSh\s*([\d,]+\.?\d*)",
                r"Amount:\s*([\d,]+\.?\d*)",
                r"Total:\s*([\d,]+\.?\d*)",
                r"([\d,]+\.?\d*)\s*KES",
                r"([\d,]+\.?\d*)\s*KSh"
            ],
            "date": [
                r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"(\d{4}-\d{2}-\d{2})",
                r"Date:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})"
            ],
            "invoice_number": [
                r"Invoice\s*#?\s*([A-Z0-9-]+)",
                r"INV\s*([A-Z0-9-]+)",
                r"Reference:\s*([A-Z0-9-]+)",
                r"([A-Z]{2,}\d{4,})"
            ],
            "vendor_name": [
                r"From:\s*([A-Za-z\s&]+)",
                r"Vendor:\s*([A-Za-z\s&]+)",
                r"Supplier:\s*([A-Za-z\s&]+)",
                r"Company:\s*([A-Za-z\s&]+)"
            ],
            "tax": [
                r"VAT:\s*([\d,]+\.?\d*)",
                r"Tax:\s*([\d,]+\.?\d*)",
                r"GST:\s*([\d,]+\.?\d*)"
            ],
            "payment_method": [
                r"Payment:\s*([A-Za-z\s]+)",
                r"Method:\s*([A-Za-z\s]+)",
                r"(Cash|Cheque|Bank Transfer|M-Pesa|Card)"
            ]
        }
    
    def _load_company_patterns(self) -> Dict[str, List[str]]:
        """Load company name patterns"""
        return {
            "construction": [
                "ALTAN ENTERPRISES", "DORDEN VENTURES", "AMROLAC COMPANY",
                "RUCTUS GROUP", "NIFTY VENTURES", "YUMI VENTURES",
                "SOLOPRIDE CONTRACTORS", "MEGUMI VENTURES", "CADIMO", "MOATENG"
            ],
            "financial": [
                "BANK", "FINANCE", "INSURANCE", "INVESTMENT", "CREDIT"
            ],
            "government": [
                "GOVERNMENT", "COUNTY", "MINISTRY", "DEPARTMENT", "AUTHORITY"
            ]
        }
    
    def extract_amount(self, text: str) -> Tuple[Optional[Decimal], float]:
        """Extract monetary amounts from text"""
        for pattern in self.extraction_patterns["amount"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    # Clean the amount string
                    amount_str = matches[0].replace(',', '')
                    amount = Decimal(amount_str)
                    confidence = 0.9 if 'KES' in pattern or 'KSh' in pattern else 0.7
                    return amount, confidence
                except (ValueError, TypeError):
                    continue
        return None, 0.0
    
    def extract_date(self, text: str) -> Tuple[Optional[datetime], float]:
        """Extract dates from text"""
        for pattern in self.extraction_patterns["date"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    date_str = matches[0]
                    # Try different date formats
                    for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d %b %Y']:
                        try:
                            date_obj = datetime.strptime(date_str, fmt)
                            confidence = 0.9 if 'Date:' in pattern else 0.7
                            return date_obj, confidence
                        except ValueError:
                            continue
                except Exception:
                    continue
        return None, 0.0
    
    def extract_invoice_number(self, text: str) -> Tuple[Optional[str], float]:
        """Extract invoice numbers from text"""
        for pattern in self.extraction_patterns["invoice_number"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                invoice_num = matches[0].strip()
                confidence = 0.9 if 'Invoice' in pattern else 0.7
                return invoice_num, confidence
        return None, 0.0
    
    def extract_vendor_name(self, text: str) -> Tuple[Optional[str], float]:
        """Extract vendor/supplier names from text"""
        for pattern in self.extraction_patterns["vendor_name"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                vendor = matches[0].strip()
                confidence = 0.8
                return vendor, confidence
        return None, 0.0
    
    def extract_tax_amount(self, text: str) -> Tuple[Optional[Decimal], float]:
        """Extract tax amounts from text"""
        for pattern in self.extraction_patterns["tax"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    tax_str = matches[0].replace(',', '')
                    tax_amount = Decimal(tax_str)
                    confidence = 0.9
                    return tax_amount, confidence
                except (ValueError, TypeError):
                    continue
        return None, 0.0
    
    def extract_payment_method(self, text: str) -> Tuple[Optional[str], float]:
        """Extract payment methods from text"""
        for pattern in self.extraction_patterns["payment_method"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                method = matches[0].strip()
                confidence = 0.8
                return method, confidence
        return None, 0.0
    
    def classify_transaction_type(self, text: str, amount: Optional[Decimal]) -> Tuple[Optional[str], float]:
        """Classify transaction type based on text content"""
        text_lower = text.lower()
        
        # Income indicators
        income_keywords = ['income', 'revenue', 'sales', 'payment received', 'credit']
        if any(keyword in text_lower for keyword in income_keywords):
            return 'income', 0.8
        
        # Expense indicators
        expense_keywords = ['expense', 'payment', 'purchase', 'cost', 'debit', 'bill']
        if any(keyword in text_lower for keyword in expense_keywords):
            return 'expense', 0.8
        
        # Default based on amount sign (if available)
        if amount:
            return 'expense' if amount > 0 else 'income', 0.6
        
        return None, 0.0
    
    def categorize_transaction(self, text: str, vendor: Optional[str]) -> Tuple[Optional[str], float]:
        """Categorize transaction based on content"""
        text_lower = text.lower()
        
        categories = {
            'construction': ['construction', 'building', 'contractor', 'infrastructure'],
            'transportation': ['transport', 'fuel', 'vehicle', 'logistics'],
            'utilities': ['electricity', 'water', 'gas', 'utility'],
            'office': ['office', 'stationery', 'equipment', 'supplies'],
            'marketing': ['advertising', 'marketing', 'promotion', 'media'],
            'legal': ['legal', 'lawyer', 'attorney', 'court'],
            'insurance': ['insurance', 'premium', 'coverage'],
            'taxes': ['tax', 'vat', 'gst', 'government'],
            'salary': ['salary', 'wage', 'payroll', 'employee'],
            'rent': ['rent', 'lease', 'property']
        }
        
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category, 0.8
        
        # Check vendor name for categorization
        if vendor:
            vendor_lower = vendor.lower()
            for category, keywords in categories.items():
                if any(keyword in vendor_lower for keyword in keywords):
                    return category, 0.7
        
        return 'general', 0.5
    
    def extract_company_name(self, text: str) -> Tuple[Optional[str], float]:
        """Extract company name from text"""
        # Check for known company patterns
        for category, companies in self.company_patterns.items():
            for company in companies:
                if company.lower() in text.lower():
                    return company, 0.9
        
        # Look for company name patterns
        company_patterns = [
            r"([A-Z][A-Za-z\s&]+)\s+LIMITED",
            r"([A-Z][A-Za-z\s&]+)\s+COMPANY",
            r"([A-Z][A-Za-z\s&]+)\s+CORP",
            r"Company:\s*([A-Za-z\s&]+)"
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, text)
            if matches:
                company_name = matches[0].strip()
                return company_name, 0.7
        
        return None, 0.0
    
    def extract_data_from_text(self, text: str, document_id: int, filename: str) -> ExtractedData:
        """Extract structured data from document text"""
        extracted = ExtractedData(
            document_id=document_id,
            filename=filename,
            extracted_at=datetime.now(timezone.utc)
        )
        
        # Extract basic information
        amount, amount_conf = self.extract_amount(text)
        extracted.amount = amount
        
        date, date_conf = self.extract_date(text)
        extracted.transaction_date = date
        
        invoice_num, invoice_conf = self.extract_invoice_number(text)
        extracted.invoice_number = invoice_num
        
        vendor, vendor_conf = self.extract_vendor_name(text)
        extracted.vendor_name = vendor
        
        tax_amount, tax_conf = self.extract_tax_amount(text)
        extracted.tax_amount = tax_amount
        
        payment_method, payment_conf = self.extract_payment_method(text)
        extracted.payment_method = payment_method
        
        company_name, company_conf = self.extract_company_name(text)
        extracted.company_name = company_name
        
        # Classify transaction type
        transaction_type, type_conf = self.classify_transaction_type(text, amount)
        extracted.transaction_type = transaction_type
        
        # Categorize transaction
        category, cat_conf = self.categorize_transaction(text, vendor)
        extracted.category = category
        
        # Generate reference number
        if invoice_num:
            extracted.reference_number = invoice_num
        elif date and amount:
            extracted.reference_number = f"REF-{date.strftime('%Y%m%d')}-{int(amount)}"
        
        # Calculate overall confidence score
        confidences = [amount_conf, date_conf, invoice_conf, vendor_conf, 
                      tax_conf, payment_conf, company_conf, type_conf, cat_conf]
        extracted.confidence_score = sum(confidences) / len(confidences) if confidences else 0.0
        
        return extracted
    
    def process_document(self, document_id: int, filename: str, text_content: str) -> ExtractedData:
        """Process a single document and extract data"""
        try:
            extracted_data = self.extract_data_from_text(text_content, document_id, filename)
            
            # Save to PostgreSQL
            self._save_to_postgresql(extracted_data)
            
            # Save to MongoDB
            self._save_to_mongodb(extracted_data, text_content)
            
            logger.info(f"✅ Processed document {filename} (ID: {document_id}) - Confidence: {extracted_data.confidence_score:.2f}")
            return extracted_data
            
        except Exception as e:
            logger.error(f"❌ Failed to process document {filename}: {e}")
            raise
    
    def _save_to_postgresql(self, data: ExtractedData):
        """Save extracted data to PostgreSQL"""
        try:
            with self.postgres_engine.begin() as conn:
                # Insert into extracted_data table
                conn.execute(text("""
                    INSERT INTO extracted_data 
                    (document_id, company_name, transaction_date, amount, currency, 
                     transaction_type, category, description, reference_number, 
                     vendor_name, invoice_number, tax_amount, payment_method, 
                     confidence_score, extraction_method, extracted_at)
                    VALUES (:document_id, :company_name, :transaction_date, :amount, :currency,
                           :transaction_type, :category, :description, :reference_number,
                           :vendor_name, :invoice_number, :tax_amount, :payment_method,
                           :confidence_score, :extraction_method, :extracted_at)
                """), {
                    "document_id": data.document_id,
                    "company_name": data.company_name,
                    "transaction_date": data.transaction_date,
                    "amount": data.amount,
                    "currency": data.currency,
                    "transaction_type": data.transaction_type,
                    "category": data.category,
                    "description": data.description,
                    "reference_number": data.reference_number,
                    "vendor_name": data.vendor_name,
                    "invoice_number": data.invoice_number,
                    "tax_amount": data.tax_amount,
                    "payment_method": data.payment_method,
                    "confidence_score": data.confidence_score,
                    "extraction_method": data.extraction_method,
                    "extracted_at": data.extracted_at
                })
                
        except Exception as e:
            logger.error(f"❌ Failed to save to PostgreSQL: {e}")
            raise
    
    def _save_to_mongodb(self, data: ExtractedData, original_text: str):
        """Save extracted data to MongoDB"""
        try:
            mongo_document = {
                "postgres_id": data.document_id,
                "filename": data.filename,
                "extracted_data": {
                    "company_name": data.company_name,
                    "transaction_date": data.transaction_date,
                    "amount": float(data.amount) if data.amount else None,
                    "currency": data.currency,
                    "transaction_type": data.transaction_type,
                    "category": data.category,
                    "description": data.description,
                    "reference_number": data.reference_number,
                    "vendor_name": data.vendor_name,
                    "invoice_number": data.invoice_number,
                    "tax_amount": float(data.tax_amount) if data.tax_amount else None,
                    "payment_method": data.payment_method,
                    "confidence_score": data.confidence_score,
                    "extraction_method": data.extraction_method
                },
                "original_text": original_text,
                "extracted_at": data.extracted_at
            }
            
            self.mongo_db.extracted_data.insert_one(mongo_document)
            
        except Exception as e:
            logger.error(f"❌ Failed to save to MongoDB: {e}")
            raise
    
    def process_all_documents(self, limit: int = None) -> Dict[str, Any]:
        """Process all documents in the database"""
        try:
            # Get documents from PostgreSQL
            with self.postgres_engine.begin() as conn:
                result = conn.execute(text("""
                    SELECT id, filename, file_path 
                    FROM documents 
                    WHERE status = 'active'
                    ORDER BY id
                """))
                documents = result.fetchall()
            
            if limit:
                documents = documents[:limit]
            
            logger.info(f"🚀 Starting data extraction for {len(documents)} documents...")
            
            processed_count = 0
            failed_count = 0
            total_confidence = 0.0
            
            # Process documents in batches
            batch_size = 50
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                
                for doc in batch:
                    try:
                        # Get document text from MongoDB
                        mongo_doc = self.mongo_db.documents.find_one({"postgres_id": doc[0]})
                        if mongo_doc and mongo_doc.get("analysis"):
                            text_content = mongo_doc["analysis"].get("text", "")
                        else:
                            text_content = ""
                        
                        # Process document
                        extracted = self.process_document(doc[0], doc[1], text_content)
                        processed_count += 1
                        total_confidence += extracted.confidence_score
                        
                    except Exception as e:
                        logger.error(f"❌ Failed to process document {doc[1]}: {e}")
                        failed_count += 1
                
                logger.info(f"📊 Progress: {processed_count}/{len(documents)} documents processed")
            
            # Calculate statistics
            avg_confidence = total_confidence / processed_count if processed_count > 0 else 0.0
            
            results = {
                "total_documents": len(documents),
                "processed_count": processed_count,
                "failed_count": failed_count,
                "success_rate": f"{(processed_count / len(documents) * 100):.2f}%" if documents else "0%",
                "average_confidence": f"{avg_confidence:.2f}",
                "extraction_date": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"✅ Data extraction completed!")
            logger.info(f"   📊 Successfully processed: {processed_count} documents")
            logger.info(f"   ❌ Failed extractions: {failed_count} documents")
            logger.info(f"   📈 Average confidence: {avg_confidence:.2f}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Data extraction failed: {e}")
            raise
    
    def generate_extraction_report(self, results: Dict[str, Any]):
        """Generate extraction report"""
        report = {
            "extraction_date": datetime.now(timezone.utc).isoformat(),
            "results": results,
            "engine_version": "1.0.0",
            "patterns_used": len(self.extraction_patterns),
            "company_patterns": len(self.company_patterns)
        }
        
        # Save report
        report_path = "data_extraction_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📋 Extraction report saved to: {report_path}")
        return report

def main():
    """Main extraction function"""
    try:
        engine = DataExtractionEngine()
        
        # Connect to databases
        engine.connect_databases()
        
        # Process documents (limit to first 100 for testing)
        results = engine.process_all_documents(limit=100)
        
        # Generate report
        report = engine.generate_extraction_report(results)
        
        print("\n🎉 Data Extraction Complete!")
        print("=" * 50)
        print(f"✅ Successfully processed: {results['processed_count']} documents")
        print(f"❌ Failed extractions: {results['failed_count']} documents")
        print(f"📊 Success rate: {results['success_rate']}")
        print(f"📈 Average confidence: {results['average_confidence']}")
        print("\n📊 Extraction Features:")
        print("   - Amount extraction")
        print("   - Date extraction")
        print("   - Invoice number extraction")
        print("   - Vendor name extraction")
        print("   - Transaction classification")
        print("   - Category classification")
        print("   - Company name extraction")
        
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise

if __name__ == "__main__":
    main() 