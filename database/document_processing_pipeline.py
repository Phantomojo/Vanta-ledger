#!/usr/bin/env python3
"""
Document Processing Pipeline for Vanta Ledger
============================================

Processes all organized company documents and extracts structured data for:
- Financial statements and invoices
- Legal documents and contracts
- Tender documents and bids
- Project documents and methodologies
- Personal documents and CVs

Author: Vanta Ledger Team
"""

import os
import sys
import json
import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from pathlib import Path
import mimetypes
import shutil

# Database imports
from sqlalchemy import create_engine, text
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

# Document processing imports
import PyPDF2
import docx
import pandas as pd
import numpy as np
from PIL import Image
import pytesseract
import fitz  # PyMuPDF

# AI/ML imports for text analysis
import spacy
from transformers import pipeline
import openai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DocumentProcessingPipeline:
    """Comprehensive document processing pipeline for Vanta Ledger"""
    
    def __init__(self, postgres_engine, mongo_client, organized_data_path):
        self.postgres_engine = postgres_engine
        self.mongo_client = mongo_client
        self.mongo_db = mongo_client.vanta_ledger
        self.organized_data_path = Path(organized_data_path)
        self.processed_count = 0
        self.error_count = 0
        
        # Initialize AI models
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("✅ spaCy NLP model loaded successfully")
        except Exception as e:
            logger.warning(f"⚠️  spaCy model not available: {e}")
            self.nlp = None
            
        try:
            self.sentiment_analyzer = pipeline("sentiment-analysis")
            self.text_classifier = pipeline("text-classification")
            logger.info("✅ Transformers models loaded successfully")
        except Exception as e:
            logger.warning(f"⚠️  Transformers models not available: {e}")
            self.sentiment_analyzer = None
            self.text_classifier = None
        
        # Document type patterns
        self.document_patterns = {
            'financial': [
                r'financial.*statement', r'audit.*report', r'income.*statement',
                r'balance.*sheet', r'cash.*flow', r'invoice', r'receipt',
                r'bank.*statement', r'credit.*line', r'equity.*statement'
            ],
            'legal': [
                r'contract', r'agreement', r'permit', r'license', r'certificate',
                r'incorporation', r'tax.*compliance', r'vat.*certificate',
                r'affidavit', r'power.*of.*attorney', r'lease.*agreement'
            ],
            'tenders': [
                r'tender', r'bid', r'proposal', r'quotation', r'rfp',
                r'request.*for.*proposal', r'expression.*of.*interest',
                r'pre.*qualification', r'technical.*proposal'
            ],
            'projects': [
                r'project', r'methodology', r'workplan', r'technical.*specification',
                r'design.*document', r'construction.*plan', r'engineering.*drawing',
                r'site.*plan', r'progress.*report'
            ],
            'personal': [
                r'cv', r'resume', r'curriculum.*vitae', r'id.*card', r'passport',
                r'national.*id', r'personal.*information', r'employee.*record'
            ],
            'media': [
                r'\.jpg$', r'\.jpeg$', r'\.png$', r'\.gif$', r'\.bmp$',
                r'photograph', r'image', r'picture', r'photo'
            ],
            'backups': [
                r'\.zip$', r'\.rar$', r'\.7z$', r'backup', r'archive',
                r'compressed', r'packaged'
            ]
        }
        
        # Financial extraction patterns
        self.financial_patterns = {
            'amounts': [
                r'KES\s*([\d,]+\.?\d*)',
                r'USD\s*([\d,]+\.?\d*)',
                r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:KES|USD)?',
                r'Total[:\s]*([\d,]+\.?\d*)',
                r'Amount[:\s]*([\d,]+\.?\d*)'
            ],
            'dates': [
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'(\d{4}-\d{2}-\d{2})',
                r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}'
            ],
            'companies': [
                r'([A-Z][A-Z\s&]+(?:LIMITED|LTD|LLC|INC|CORP))',
                r'([A-Z][A-Z\s]+(?:ENTERPRISES|VENTURES|SOLUTIONS|AGENCIES))'
            ]
        }
    
    def get_company_id_by_name(self, company_name: str) -> Optional[int]:
        """Get company ID from database by name"""
        try:
            with self.postgres_engine.begin() as conn:
                result = conn.execute(text("""
                    SELECT id FROM companies 
                    WHERE name ILIKE :name OR name ILIKE :name_clean
                """), {
                    'name': f'%{company_name}%',
                    'name_clean': company_name.replace('_', ' ').replace('-', ' ')
                }).fetchone()
                
                return result[0] if result else None
                
        except Exception as e:
            logger.error(f"Error getting company ID for {company_name}: {e}")
            return None
    
    def extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        try:
            text = ""
            
            # Try PyMuPDF first (better for complex PDFs)
            try:
                doc = fitz.open(file_path)
                for page in doc:
                    text += page.get_text()
                doc.close()
            except:
                # Fallback to PyPDF2
                try:
                    with open(file_path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        for page in pdf_reader.pages:
                            text += page.extract_text()
                except:
                    text = f"[PDF file: {file_path.name} - text extraction failed]"
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {e}")
            return ""
    
    def extract_text_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file"""
        try:
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
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from image {file_path}: {e}")
            return f"[Image file: {file_path.name} - OCR failed]"
    
    def extract_text_from_file(self, file_path: Path) -> str:
        """Extract text from any supported file type"""
        try:
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            if mime_type == 'application/pdf':
                return self.extract_text_from_pdf(file_path)
            elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                return self.extract_text_from_docx(file_path)
            elif mime_type and mime_type.startswith('image/'):
                return self.extract_text_from_image(file_path)
            else:
                # Try to read as text file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return f.read().strip()
                except:
                    return ""
                    
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return ""
    
    def classify_document_type(self, filename: str, text: str) -> str:
        """Classify document type based on filename and content"""
        try:
            # Check filename patterns first
            filename_lower = filename.lower()
            text_lower = text.lower()
            
            for doc_type, patterns in self.document_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, filename_lower, re.IGNORECASE) or \
                       re.search(pattern, text_lower, re.IGNORECASE):
                        return doc_type
            
            # Default to documents if no specific type found
            return 'documents'
            
        except Exception as e:
            logger.error(f"Error classifying document type: {e}")
            return 'documents'
    
    def extract_financial_data(self, text: str) -> Dict[str, Any]:
        """Extract financial data from document text"""
        try:
            financial_data = {
                'amounts': [],
                'dates': [],
                'companies': [],
                'total_amount': None,
                'currency': 'KES',
                'document_type': 'unknown'
            }
            
            # Extract amounts
            for pattern in self.financial_patterns['amounts']:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    try:
                        # Clean and convert amount
                        amount_str = match.replace(',', '')
                        amount = float(amount_str)
                        financial_data['amounts'].append(amount)
                    except:
                        continue
            
            # Extract dates
            for pattern in self.financial_patterns['dates']:
                matches = re.findall(pattern, text, re.IGNORECASE)
                financial_data['dates'].extend(matches)
            
            # Extract company names
            for pattern in self.financial_patterns['companies']:
                matches = re.findall(pattern, text, re.IGNORECASE)
                financial_data['companies'].extend(matches)
            
            # Calculate total amount
            if financial_data['amounts']:
                financial_data['total_amount'] = sum(financial_data['amounts'])
            
            # Determine document type
            if any(word in text.lower() for word in ['invoice', 'bill', 'receipt']):
                financial_data['document_type'] = 'invoice'
            elif any(word in text.lower() for word in ['statement', 'balance', 'financial']):
                financial_data['document_type'] = 'financial_statement'
            elif any(word in text.lower() for word in ['contract', 'agreement']):
                financial_data['document_type'] = 'contract'
            
            return financial_data
            
        except Exception as e:
            logger.error(f"Error extracting financial data: {e}")
            return {}
    
    def analyze_document_content(self, text: str) -> Dict[str, Any]:
        """Analyze document content using AI/ML"""
        try:
            analysis = {
                'sentiment': 'neutral',
                'confidence': 0.0,
                'key_entities': [],
                'summary': '',
                'risk_score': 0.0,
                'tags': []
            }
            
            if not text.strip():
                return analysis
            
            # Sentiment analysis
            try:
                sentiment_result = self.sentiment_analyzer(text[:512])[0]
                analysis['sentiment'] = sentiment_result['label']
                analysis['confidence'] = sentiment_result['score']
            except:
                pass
            
            # Named entity recognition
            try:
                doc = self.nlp(text[:1000])
                entities = []
                for ent in doc.ents:
                    entities.append({
                        'text': ent.text,
                        'label': ent.label_,
                        'start': ent.start_char,
                        'end': ent.end_char
                    })
                analysis['key_entities'] = entities
            except:
                pass
            
            # Risk assessment based on keywords
            risk_keywords = ['default', 'late', 'overdue', 'penalty', 'breach', 'termination']
            risk_count = sum(1 for keyword in risk_keywords if keyword in text.lower())
            analysis['risk_score'] = min(risk_count / len(risk_keywords), 1.0)
            
            # Generate tags
            tags = []
            if any(word in text.lower() for word in ['urgent', 'immediate', 'asap']):
                tags.append('urgent')
            if any(word in text.lower() for word in ['confidential', 'private', 'secret']):
                tags.append('confidential')
            if any(word in text.lower() for word in ['approved', 'authorized', 'signed']):
                tags.append('approved')
            
            analysis['tags'] = tags
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing document content: {e}")
            return {}
    
    def process_single_document(self, file_path: Path, company_name: str, category: str) -> Dict[str, Any]:
        """Process a single document and extract all relevant data"""
        try:
            # Get company ID
            company_id = self.get_company_id_by_name(company_name)
            if not company_id:
                logger.warning(f"Company not found in database: {company_name}")
                return {}
            
            # Extract text
            text = self.extract_text_from_file(file_path)
            
            # Classify document type
            doc_type = self.classify_document_type(file_path.name, text)
            
            # Extract financial data
            financial_data = self.extract_financial_data(text)
            
            # Analyze content
            content_analysis = self.analyze_document_content(text)
            
            # Generate document hash
            file_hash = hashlib.md5(file_path.read_bytes()).hexdigest()
            
            # Prepare document data
            document_data = {
                'filename': file_path.name,
                'original_path': str(file_path),
                'file_size': file_path.stat().st_size,
                'mime_type': mimetypes.guess_type(str(file_path))[0],
                'company_id': company_id,
                'company_name': company_name,
                'category': category,
                'document_type': doc_type,
                'extracted_text': text,
                'financial_data': financial_data,
                'content_analysis': content_analysis,
                'file_hash': file_hash,
                'processing_date': datetime.now(),
                'status': 'processed'
            }
            
            return document_data
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {e}")
            return {}
    
    def save_document_to_database(self, document_data: Dict[str, Any]) -> bool:
        """Save processed document to both PostgreSQL and MongoDB"""
        try:
            # Save metadata to PostgreSQL
            with self.postgres_engine.begin() as conn:
                result = conn.execute(text("""
                    INSERT INTO documents 
                    (company_id, document_type, document_category, filename, original_path, 
                     file_size, mime_type, processing_status, extracted_data, ai_analysis)
                    VALUES (:company_id, :doc_type, :category, :filename, :original_path,
                           :file_size, :mime_type, :status, :extracted_data, :ai_analysis)
                    RETURNING id
                """), {
                    'company_id': document_data['company_id'],
                    'doc_type': document_data['document_type'],
                    'category': document_data['category'],
                    'filename': document_data['filename'],
                    'original_path': document_data['original_path'],
                    'file_size': document_data['file_size'],
                    'mime_type': document_data['mime_type'],
                    'status': document_data['status'],
                    'extracted_data': json.dumps(document_data['financial_data']),
                    'ai_analysis': json.dumps(document_data['content_analysis'])
                })
                
                document_id = result.fetchone()[0]
            
            # Save full document to MongoDB
            documents_collection = self.mongo_db.documents
            mongo_doc = {
                'postgres_id': document_id,
                'company_id': document_data['company_id'],
                'company_name': document_data['company_name'],
                'filename': document_data['filename'],
                'original_path': document_data['original_path'],
                'category': document_data['category'],
                'document_type': document_data['document_type'],
                'extracted_text': document_data['extracted_text'],
                'financial_data': document_data['financial_data'],
                'content_analysis': document_data['content_analysis'],
                'file_hash': document_data['file_hash'],
                'processing_date': document_data['processing_date'],
                'status': document_data['status']
            }
            
            documents_collection.insert_one(mongo_doc)
            
            # Update PostgreSQL with MongoDB document ID
            with self.postgres_engine.begin() as conn:
                conn.execute(text("""
                    UPDATE documents 
                    SET mongo_document_id = :mongo_id 
                    WHERE id = :postgres_id
                """), {
                    'mongo_id': str(mongo_doc['_id']),
                    'postgres_id': document_id
                })
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving document to database: {e}")
            return False
    
    def process_company_documents(self, company_path: Path) -> Dict[str, int]:
        """Process all documents for a single company"""
        try:
            company_name = company_path.name.replace('_', ' ').replace('-', ' ')
            stats = {'processed': 0, 'errors': 0, 'total': 0}
            
            logger.info(f"Processing documents for company: {company_name}")
            
            # Process each category
            for category_path in company_path.iterdir():
                if category_path.is_dir():
                    category = category_path.name
                    logger.info(f"  Processing category: {category}")
                    
                    # Process each file in the category
                    for file_path in category_path.iterdir():
                        if file_path.is_file():
                            stats['total'] += 1
                            
                            try:
                                # Process document
                                document_data = self.process_single_document(file_path, company_name, category)
                                
                                if document_data:
                                    # Save to database
                                    if self.save_document_to_database(document_data):
                                        stats['processed'] += 1
                                        self.processed_count += 1
                                    else:
                                        stats['errors'] += 1
                                        self.error_count += 1
                                else:
                                    stats['errors'] += 1
                                    self.error_count += 1
                                    
                            except Exception as e:
                                logger.error(f"Error processing {file_path}: {e}")
                                stats['errors'] += 1
                                self.error_count += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error processing company documents for {company_path}: {e}")
            return {'processed': 0, 'errors': 0, 'total': 0}
    
    def run_complete_processing(self) -> Dict[str, Any]:
        """Run complete document processing pipeline"""
        try:
            logger.info("🚀 Starting complete document processing pipeline...")
            
            start_time = datetime.now()
            total_stats = {'processed': 0, 'errors': 0, 'total': 0, 'companies': 0}
            
            # Process each company
            for company_path in self.organized_data_path.iterdir():
                if company_path.is_dir() and not company_path.name.startswith('.'):
                    company_stats = self.process_company_documents(company_path)
                    
                    total_stats['processed'] += company_stats['processed']
                    total_stats['errors'] += company_stats['errors']
                    total_stats['total'] += company_stats['total']
                    total_stats['companies'] += 1
                    
                    logger.info(f"Company {company_path.name}: {company_stats['processed']} processed, {company_stats['errors']} errors")
            
            end_time = datetime.now()
            processing_time = end_time - start_time
            
            # Generate summary
            summary = {
                'processing_date': start_time,
                'processing_time_seconds': processing_time.total_seconds(),
                'total_companies': total_stats['companies'],
                'total_documents': total_stats['total'],
                'processed_documents': total_stats['processed'],
                'error_documents': total_stats['errors'],
                'success_rate': (total_stats['processed'] / total_stats['total'] * 100) if total_stats['total'] > 0 else 0
            }
            
            # Save processing summary to MongoDB
            processing_collection = self.mongo_db.document_processing
            processing_collection.insert_one({
                'summary': summary,
                'timestamp': datetime.now()
            })
            
            logger.info("✅ Document processing pipeline completed")
            logger.info(f"📊 Summary: {summary['processed_documents']} documents processed, {summary['error_documents']} errors")
            logger.info(f"⏱️  Processing time: {processing_time}")
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Complete document processing failed: {e}")
            raise

def main():
    """Main function to run document processing"""
    try:
        # This would be called from the main application
        # For now, we'll just show the structure
        print("Document Processing Pipeline Ready")
        print("Use this class to process all organized company documents")
        
    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 