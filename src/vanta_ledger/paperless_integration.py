# NOTE: This script is experimental and pending Paperless-ngx integration.
# It is not currently used in production. See documentation for details.
#!/usr/bin/env python3
"""
Paperless-ngx Integration Module

This module handles the integration between Paperless-ngx and Vanta Ledger,
including document import, analysis, and categorization.
"""

import requests
import json
import re
from datetime import datetime, date
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from .database import get_db, Document, Company, DocumentAnalysis
import logging
import os
from .force_scan import ForceScanner, ForceScanResult

logger = logging.getLogger(__name__)

class PaperlessIntegration:
    def __init__(self, base_url: str = "http://localhost:8000", username: str = "Mike", password: str = None):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.token = None
        self.force_scanner = ForceScanner()
        
    def authenticate(self) -> bool:
        """Authenticate with Paperless-ngx API"""
        try:
            auth_url = f"{self.base_url}/api/token/"
            response = self.session.post(auth_url, data={
                'username': self.username,
                'password': self.password
            })
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data.get('token') or token_data.get('access')
                if self.token:
                    self.session.headers.update({
                        'Authorization': f'Token {self.token}'
                    })
                else:
                    raise Exception("No token found in response")
                logger.info("Successfully authenticated with Paperless-ngx")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    def get_documents(self, page: int = 1, page_size: int = 100) -> List[Dict]:
        """Get documents from Paperless-ngx"""
        try:
            url = f"{self.base_url}/api/documents/"
            params = {
                'page': page,
                'page_size': page_size
            }
            
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                return response.json()['results']
            else:
                logger.error(f"Failed to get documents: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting documents: {e}")
            return []
    
    def get_document_details(self, doc_id: int) -> Optional[Dict]:
        """Get detailed information about a specific document"""
        try:
            url = f"{self.base_url}/api/documents/{doc_id}/"
            response = self.session.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get document {doc_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting document {doc_id}: {e}")
            return None
    
    def analyze_document_content(self, ocr_text: str) -> Dict:
        """Analyze document content to extract business-relevant information"""
        analysis = {
            'amounts': [],
            'dates': [],
            'companies': [],
            'addresses': [],
            'confidence_score': 0.0
        }
        
        if not ocr_text:
            return analysis
        
        # Extract amounts (Kenyan Shillings)
        amount_patterns = [
            r'KES\s*([\d,]+(?:\.\d{2})?)',
            r'KSh\s*([\d,]+(?:\.\d{2})?)',
            r'([\d,]+(?:\.\d{2})?)\s*KES',
            r'([\d,]+(?:\.\d{2})?)\s*KSh',
            r'([\d,]+(?:\.\d{2})?)\s*Shillings',
        ]
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, ocr_text, re.IGNORECASE)
            for match in matches:
                amount = float(match.replace(',', ''))
                if amount > 0:
                    analysis['amounts'].append(amount)
        
        # Extract dates
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{1,2}-\d{1,2}-\d{4}',
            r'\d{4}-\d{1,2}-\d{1,2}',
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, ocr_text)
            analysis['dates'].extend(matches)
        
        # Extract company names (common patterns in your documents)
        company_keywords = [
            'LIMITED', 'LTD', 'ENTERPRISES', 'VENTURES', 'CONTRACTORS',
            'SOLUTIONS', 'SUPPLIES', 'SERVICES', 'AGENCIES'
        ]
        
        lines = ocr_text.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.upper() for keyword in company_keywords):
                if len(line) > 5 and len(line) < 100:  # Reasonable company name length
                    analysis['companies'].append(line)
        
        # Calculate confidence score based on extracted data
        confidence_factors = []
        if analysis['amounts']:
            confidence_factors.append(0.3)
        if analysis['dates']:
            confidence_factors.append(0.2)
        if analysis['companies']:
            confidence_factors.append(0.3)
        if len(ocr_text) > 100:
            confidence_factors.append(0.2)
        
        analysis['confidence_score'] = sum(confidence_factors)
        
        return analysis
    
    def categorize_document(self, filename: str, ocr_text: str) -> Dict:
        """Categorize document based on filename and content"""
        filename_lower = filename.lower()
        ocr_lower = ocr_text.lower() if ocr_text else ""
        
        # Document type classification
        doc_type = "Unknown"
        doc_category = "other"
        
        # Statutory documents
        if any(keyword in filename_lower for keyword in ['nca', 'certificate', 'license', 'permit']):
            doc_type = "NCA Certificate"
            doc_category = "statutory"
        elif any(keyword in filename_lower for keyword in ['tax', 'tcc', 'compliance']):
            doc_type = "Tax Compliance Certificate"
            doc_category = "statutory"
        elif any(keyword in filename_lower for keyword in ['agpo', 'supplier']):
            doc_type = "AGPO Certificate"
            doc_category = "statutory"
        elif any(keyword in filename_lower for keyword in ['registration', 'incorporation', 'cr12']):
            doc_type = "Company Registration"
            doc_category = "statutory"
        
        # Financial documents
        elif any(keyword in filename_lower for keyword in ['bank', 'statement', 'account']):
            doc_type = "Bank Statement"
            doc_category = "financial"
        elif any(keyword in filename_lower for keyword in ['audit', 'financial', 'statement']):
            doc_type = "Financial Statement"
            doc_category = "financial"
        elif any(keyword in filename_lower for keyword in ['invoice', 'receipt', 'payment']):
            doc_type = "Invoice/Receipt"
            doc_category = "financial"
        
        # Tender documents
        elif any(keyword in filename_lower for keyword in ['tender', 'bid', 'proposal']):
            doc_type = "Tender Document"
            doc_category = "tender"
        elif any(keyword in filename_lower for keyword in ['contract', 'agreement']):
            doc_type = "Contract"
            doc_category = "contract"
        
        # Equipment and assets
        elif any(keyword in filename_lower for keyword in ['equipment', 'vehicle', 'machinery']):
            doc_type = "Equipment Document"
            doc_category = "assets"
        
        return {
            'doc_type': doc_type,
            'doc_category': doc_category
        }
    
    def import_documents_to_db(self, db: Session) -> Dict:
        """Import all documents from Paperless-ngx to our database"""
        if not self.authenticate():
            return {'success': False, 'error': 'Authentication failed'}
        
        stats = {
            'total_documents': 0,
            'imported': 0,
            'skipped': 0,
            'errors': 0
        }
        
        page = 1
        while True:
            documents = self.get_documents(page=page)
            if not documents:
                break
            
            for doc_data in documents:
                stats['total_documents'] += 1
                
                try:
                    # Check if document already exists
                    existing_doc = db.query(Document).filter(
                        Document.paperless_id == doc_data['id']
                    ).first()
                    
                    if existing_doc:
                        stats['skipped'] += 1
                        continue
                    
                    # Get detailed document information
                    doc_details = self.get_document_details(doc_data['id'])
                    if not doc_details:
                        stats['errors'] += 1
                        continue
                    
                    # Analyze document content
                    ocr_text = doc_details.get('content', '')
                    # If OCR text is empty or low confidence, try force scan
                    if not ocr_text or len(ocr_text.strip()) < 20:
                        file_path = doc_details.get('file_path', None)
                        if file_path and os.path.exists(file_path):
                            force_result = self.force_scanner.scan_file(file_path)
                            ocr_text = force_result.text
                            # Optionally, log or store force_result.confidence and force_result.error
                    analysis = self.analyze_document_content(ocr_text)
                    categorization = self.categorize_document(
                        doc_data.get('title', ''),
                        ocr_text
                    )
                    
                    # Create document record
                    document = Document(
                        paperless_id=doc_data['id'],
                        filename=doc_data.get('title', ''),
                        original_filename=doc_data.get('original_file_name', ''),
                        file_size=doc_data.get('file_size', 0),
                        mime_type=doc_data.get('mime_type', ''),
                        
                        # Paperless-ngx data
                        paperless_title=doc_data.get('title', ''),
                        paperless_correspondent=doc_data.get('correspondent', ''),
                        paperless_tags=doc_data.get('tags', []),
                        paperless_created=datetime.fromisoformat(doc_data['created'].replace('Z', '+00:00')) if doc_data.get('created') else None,
                        paperless_added=datetime.fromisoformat(doc_data['added'].replace('Z', '+00:00')) if doc_data.get('added') else None,
                        paperless_modified=datetime.fromisoformat(doc_data['modified'].replace('Z', '+00:00')) if doc_data.get('modified') else None,
                        
                        # Classification
                        doc_type=categorization['doc_type'],
                        doc_category=categorization['doc_category'],
                        
                        # OCR data
                        ocr_text=ocr_text,
                        ocr_confidence=doc_data.get('archive_serial_number', 0.0),
                        
                        # Business data
                        amount=analysis['amounts'][0] if analysis['amounts'] else None,
                        currency='KES'
                    )
                    
                    db.add(document)
                    db.flush()  # Get the document ID
                    
                    # Create analysis record
                    analysis_record = DocumentAnalysis(
                        document_id=document.id,
                        extracted_amounts=analysis['amounts'],
                        extracted_dates=analysis['dates'],
                        extracted_companies=analysis['companies'],
                        extracted_addresses=analysis['addresses'],
                        confidence_score=analysis['confidence_score'],
                        analysis_method='OCR'
                    )
                    
                    db.add(analysis_record)
                    stats['imported'] += 1
                    
                except Exception as e:
                    logger.error(f"Error importing document {doc_data.get('id')}: {e}")
                    stats['errors'] += 1
            
            page += 1
        
        db.commit()
        return {'success': True, 'stats': stats}

def main():
    """Main function to run the integration"""
    logging.basicConfig(level=logging.INFO)
    
    # Initialize integration
    integration = PaperlessIntegration(
        base_url="http://localhost:8000",
        username="Mike",
        password="106730!@#"  # Your actual password
    )
    
    # Get database session
    db = next(get_db())
    
    try:
        # Import documents
        result = integration.import_documents_to_db(db)
        
        if result['success']:
            stats = result['stats']
            print(f"Import completed successfully!")
            print(f"Total documents: {stats['total_documents']}")
            print(f"Imported: {stats['imported']}")
            print(f"Skipped (already exists): {stats['skipped']}")
            print(f"Errors: {stats['errors']}")
        else:
            print(f"Import failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Integration error: {e}")
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main() 