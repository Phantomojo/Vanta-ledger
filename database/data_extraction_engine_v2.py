#!/usr/bin/env python3
"""
Vanta Ledger Data Extraction Engine v2
=======================================

This engine processes the actual JSON analysis files and extracts structured data
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
import glob
from sqlalchemy import create_engine, text
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from database_utils import connect_databases as db_connect

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
    extraction_method: str = "json_analysis"
    extracted_at: datetime = None

class DataExtractionEngineV2:
    """Advanced data extraction engine for processed JSON documents"""
    
    def __init__(self):
        self.postgres_engine = None
        self.mongo_client = None
        self.mongo_db = None
        self.processed_docs_path = "../data/processed_documents"
        
    def connect_databases(self):
        """Connect to both databases"""
        try:
            # Use shared database connection utility
            self.postgres_engine, self.mongo_client, self.mongo_db = db_connect()
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def load_analysis_file(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Load analysis file for a document"""
        try:
            analysis_file = os.path.join(self.processed_docs_path, f"{doc_id}_analysis.json")
            if os.path.exists(analysis_file):
                with open(analysis_file, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"❌ Failed to load analysis file for doc {doc_id}: {e}")
            return None
    
    def load_entities_file(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Load entities file for a document"""
        try:
            entities_file = os.path.join(self.processed_docs_path, f"{doc_id}_entities.json")
            if os.path.exists(entities_file):
                with open(entities_file, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"❌ Failed to load entities file for doc {doc_id}: {e}")
            return None
    
    def extract_financial_data(self, analysis_data: Dict[str, Any]) -> Tuple[Optional[Decimal], Optional[str], float]:
        """Extract financial data from analysis"""
        financial_data = analysis_data.get('financial_data', [])
        if financial_data:
            # Get the first financial entry
            entry = financial_data[0]
            amount = Decimal(str(entry.get('amount', 0)))
            currency = entry.get('currency', 'KES')
            transaction_type = entry.get('type', 'unknown')
            confidence = 0.9 if amount > 0 else 0.7
            return amount, transaction_type, confidence
        return None, None, 0.0
    
    def extract_dates(self, analysis_data: Dict[str, Any]) -> Tuple[Optional[datetime], float]:
        """Extract dates from analysis"""
        dates = analysis_data.get('dates', [])
        if dates:
            try:
                date_str = dates[0]
                # Try different date formats
                for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        return date_obj, 0.9
                    except ValueError:
                        continue
            except Exception:
                pass
        return None, 0.0
    
    def extract_companies(self, analysis_data: Dict[str, Any], entities_data: Optional[Dict[str, Any]]) -> Tuple[Optional[str], float]:
        """Extract company information"""
        companies = analysis_data.get('companies', [])
        if companies:
            return companies[0], 0.9
        
        # Check entities data for companies
        if entities_data:
            entity_companies = entities_data.get('companies', [])
            if entity_companies:
                return entity_companies[0], 0.8
        
        return None, 0.0
    
    def categorize_document(self, analysis_data: Dict[str, Any]) -> Tuple[Optional[str], float]:
        """Categorize document based on type and keywords"""
        doc_type = analysis_data.get('type', 'unknown')
        keywords = analysis_data.get('keywords', [])
        
        # Map document types to categories
        type_categories = {
            'invoice': 'billing',
            'receipt': 'payment',
            'contract': 'legal',
            'statement': 'financial',
            'report': 'reporting'
        }
        
        if doc_type in type_categories:
            return type_categories[doc_type], 0.8
        
        # Categorize based on keywords
        keyword_categories = {
            'construction': ['construction', 'building', 'contractor'],
            'transportation': ['transport', 'fuel', 'vehicle'],
            'utilities': ['electricity', 'water', 'gas', 'utility'],
            'office': ['office', 'stationery', 'equipment'],
            'marketing': ['advertising', 'marketing', 'promotion'],
            'legal': ['legal', 'lawyer', 'attorney'],
            'insurance': ['insurance', 'premium'],
            'taxes': ['tax', 'vat', 'gst'],
            'salary': ['salary', 'wage', 'payroll'],
            'rent': ['rent', 'lease', 'property']
        }
        
        for category, category_keywords in keyword_categories.items():
            if any(keyword in keywords for keyword in category_keywords):
                return category, 0.7
        
        return 'general', 0.5
    
    def extract_data_from_analysis(self, doc_id: str, filename: str) -> ExtractedData:
        """Extract structured data from analysis files"""
        extracted = ExtractedData(
            document_id=int(doc_id),
            filename=filename,
            extracted_at=datetime.now(timezone.utc)
        )
        
        # Load analysis and entities data
        analysis_data = self.load_analysis_file(doc_id)
        entities_data = self.load_entities_file(doc_id)
        
        if not analysis_data:
            return extracted
        
        # Extract financial data
        amount, transaction_type, amount_conf = self.extract_financial_data(analysis_data)
        extracted.amount = amount
        extracted.transaction_type = transaction_type
        
        # Extract dates
        date, date_conf = self.extract_dates(analysis_data)
        extracted.transaction_date = date
        
        # Extract companies
        company, company_conf = self.extract_companies(analysis_data, entities_data)
        extracted.company_name = company
        extracted.vendor_name = company
        
        # Categorize document
        category, cat_conf = self.categorize_document(analysis_data)
        extracted.category = category
        
        # Generate reference number
        if doc_id:
            extracted.reference_number = f"DOC-{doc_id}"
        
        # Set description based on document type
        doc_type = analysis_data.get('type', 'unknown')
        extracted.description = f"{doc_type.title()} document"
        
        # Calculate overall confidence score
        confidences = [amount_conf, date_conf, company_conf, cat_conf]
        valid_confidences = [c for c in confidences if c > 0]
        extracted.confidence_score = sum(valid_confidences) / len(valid_confidences) if valid_confidences else 0.0
        
        return extracted
    
    def process_document(self, doc_id: str, filename: str) -> ExtractedData:
        """Process a single document and extract data"""
        try:
            extracted_data = self.extract_data_from_analysis(doc_id, filename)
            
            # Save to PostgreSQL
            self._save_to_postgresql(extracted_data)
            
            # Save to MongoDB
            self._save_to_mongodb(extracted_data, doc_id)
            
            logger.info(f"✅ Processed document {filename} (ID: {doc_id}) - Confidence: {extracted_data.confidence_score:.2f}")
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
    
    def _save_to_mongodb(self, data: ExtractedData, doc_id: str):
        """Save extracted data to MongoDB"""
        try:
            mongo_document = {
                "postgres_id": data.document_id,
                "doc_id": doc_id,
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
                "extracted_at": data.extracted_at
            }
            
            self.mongo_db.extracted_data.insert_one(mongo_document)
            
        except Exception as e:
            logger.error(f"❌ Failed to save to MongoDB: {e}")
            raise
    
    def get_available_documents(self) -> List[Tuple[str, str]]:
        """Get list of available documents from analysis files"""
        try:
            analysis_files = glob.glob(os.path.join(self.processed_docs_path, "*_analysis.json"))
            documents = []
            
            for file_path in analysis_files:
                filename = os.path.basename(file_path)
                doc_id = filename.replace("_analysis.json", "")
                documents.append((doc_id, f"{doc_id}.txt"))
            
            return documents
            
        except Exception as e:
            logger.error(f"❌ Failed to get available documents: {e}")
            return []
    
    def process_all_documents(self, limit: int = None) -> Dict[str, Any]:
        """Process all available documents"""
        try:
            documents = self.get_available_documents()
            
            if limit:
                documents = documents[:limit]
            
            logger.info(f"🚀 Starting data extraction for {len(documents)} documents...")
            
            processed_count = 0
            failed_count = 0
            total_confidence = 0.0
            
            for doc_id, filename in documents:
                try:
                    # Process document
                    extracted = self.process_document(doc_id, filename)
                    processed_count += 1
                    total_confidence += extracted.confidence_score
                    
                except Exception as e:
                    logger.error(f"❌ Failed to process document {filename}: {e}")
                    failed_count += 1
                
                if processed_count % 50 == 0:
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
            "engine_version": "2.0.0",
            "data_source": "processed_json_files"
        }
        
        # Save report
        report_path = "data_extraction_report_v2.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📋 Extraction report saved to: {report_path}")
        return report

def main():
    """Main extraction function"""
    try:
        engine = DataExtractionEngineV2()
        
        # Connect to databases
        engine.connect_databases()
        
        # Process all documents (remove limit for full extraction)
        results = engine.process_all_documents()
        
        # Generate report
        report = engine.generate_extraction_report(results)
        
        print("\n🎉 Data Extraction Complete!")
        print("=" * 50)
        print(f"✅ Successfully processed: {results['processed_count']} documents")
        print(f"❌ Failed extractions: {results['failed_count']} documents")
        print(f"📊 Success rate: {results['success_rate']}")
        print(f"📈 Average confidence: {results['average_confidence']}")
        print("\n📊 Extraction Features:")
        print("   - Financial data extraction")
        print("   - Date extraction")
        print("   - Company extraction")
        print("   - Document categorization")
        print("   - Transaction classification")
        
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise

if __name__ == "__main__":
    main() 