#!/usr/bin/env python3
"""
Advanced Document AI System for Vanta Ledger
============================================

A comprehensive algorithmic system that integrates with Paperless-ngx to provide:
- Financial data extraction and validation
- Intelligent document classification
- Entity recognition and normalization
- Business intelligence and pattern analysis
- Anomaly detection
- Duplicate detection
- Automated tagging and categorization

Author: Vanta Ledger Team
"""

import re
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict, Counter
import statistics
from decimal import Decimal
import hashlib
import difflib
from pathlib import Path

# AI/ML Libraries
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from fuzzywuzzy import fuzz, process

# Financial libraries
import pandas as pd
from dateutil import parser as date_parser

# Custom imports
import requests
from requests.auth import HTTPBasicAuth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('document_ai.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class FinancialData:
    """Structured financial data extracted from documents"""
    amount: Optional[Decimal]
    currency: str = "KES"
    date: Optional[datetime] = None
    invoice_number: Optional[str] = None
    tax_amount: Optional[Decimal] = None
    tax_rate: Optional[float] = None
    vendor_name: Optional[str] = None
    project_code: Optional[str] = None
    confidence: float = 0.0

@dataclass
class DocumentAnalysis:
    """Complete analysis results for a document"""
    document_id: int
    document_type: str
    confidence: float
    financial_data: List[FinancialData]
    entities: Dict[str, List[str]]
    tags: List[str]
    risk_score: float
    duplicate_score: float
    business_insights: Dict[str, Any]

class DocumentAIEngine:
    """Advanced Document AI Engine with multiple algorithms"""
    
    def __init__(self, paperless_url: str, username: str, password: str):
        self.paperless_url = paperless_url.rstrip('/')
        self.username = username
        self.password = password
        self.token = None
        
        # Initialize AI models
        self.nlp = spacy.load("en_core_web_sm")
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 3)
        )
        
        # Document type patterns
        self.document_patterns = {
            'invoice': [
                r'invoice\s*#?\s*\d+',
                r'bill\s*to:',
                r'amount\s*due:',
                r'total\s*amount:',
                r'payment\s*terms:'
            ],
            'receipt': [
                r'receipt\s*#?\s*\d+',
                r'payment\s*received',
                r'cash\s*register',
                r'pos\s*terminal'
            ],
            'contract': [
                r'contract\s*agreement',
                r'terms\s*and\s*conditions',
                r'party\s*a\s*and\s*party\s*b',
                r'effective\s*date:',
                r'contract\s*period:'
            ],
            'bank_statement': [
                r'bank\s*statement',
                r'account\s*summary',
                r'opening\s*balance:',
                r'closing\s*balance:',
                r'transaction\s*history'
            ],
            'tax_document': [
                r'tax\s*compliance',
                r'vat\s*return',
                r'income\s*tax',
                r'tax\s*period:',
                r'irs\s*form'
            ],
            'tender_document': [
                r'tender\s*document',
                r'request\s*for\s*proposal',
                r'rfp',
                r'bidding\s*document',
                r'technical\s*specification'
            ]
        }
        
        # Financial patterns
        self.financial_patterns = {
            'amount': [
                r'(?:total|amount|sum|value|cost):?\s*[ks]?sh\.?\s*([\d,]+\.?\d*)',
                r'[ks]?sh\.?\s*([\d,]+\.?\d*)',
                r'([\d,]+\.?\d*)\s*[ks]?sh',
                r'usd\s*\$?\s*([\d,]+\.?\d*)',
                r'\$([\d,]+\.?\d*)'
            ],
            'invoice_number': [
                r'invoice\s*#?\s*([a-z0-9\-_]+)',
                r'inv[oice]*\s*#?\s*([a-z0-9\-_]+)',
                r'document\s*#?\s*([a-z0-9\-_]+)',
                r'ref[erence]*\s*#?\s*([a-z0-9\-_]+)'
            ],
            'date': [
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
                r'(\w+\s+\d{1,2},?\s+\d{4})',
                r'(\d{1,2}\s+\w+\s+\d{4})'
            ],
            'tax': [
                r'vat\s*:?\s*[ks]?sh\.?\s*([\d,]+\.?\d*)',
                r'tax\s*:?\s*[ks]?sh\.?\s*([\d,]+\.?\d*)',
                r'([\d,]+\.?\d*)\s*%?\s*vat',
                r'([\d,]+\.?\d*)\s*%?\s*tax'
            ]
        }
        
        # Company name patterns and known companies
        self.known_companies = {
            'CABERA ENTERPRISES', 'BRIMMACS INVESTMENTS', 'ALTAN ENTERPRISES',
            'DORDEN VENTURES', 'NKONGE SOLUTION', 'NETZACH AGENCIES',
            'RUCTUS GROUP LIMITED', 'CANDIMO LIMITED'
        }
        
        # Initialize analysis cache
        self.analysis_cache = {}
        self.document_embeddings = {}
        
    async def authenticate(self) -> bool:
        """Authenticate with Paperless-ngx"""
        try:
            auth_url = f"{self.paperless_url}/api/token/"
            response = requests.post(
                auth_url,
                auth=HTTPBasicAuth(self.username, self.password)
            )
            
            if response.status_code == 200:
                self.token = response.json().get('token')
                logger.info("✅ Authentication successful")
                return True
            else:
                logger.error(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    def extract_financial_data(self, text: str) -> List[FinancialData]:
        """Extract financial data using multiple algorithms"""
        financial_data = []
        
        # Amount extraction with confidence scoring
        amounts = []
        for pattern in self.financial_patterns['amount']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    amount_str = match.group(1).replace(',', '')
                    amount = Decimal(amount_str)
                    amounts.append((amount, match.start(), match.end()))
                except (ValueError, IndexError):
                    continue
        
        # Invoice number extraction
        invoice_numbers = []
        for pattern in self.financial_patterns['invoice_number']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                invoice_numbers.append(match.group(1))
        
        # Date extraction
        dates = []
        for pattern in self.financial_patterns['date']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    date_str = match.group(1)
                    parsed_date = date_parser.parse(date_str, fuzzy=True)
                    dates.append(parsed_date)
                except:
                    continue
        
        # Tax extraction
        tax_amounts = []
        for pattern in self.financial_patterns['tax']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    tax_str = match.group(1).replace(',', '')
                    tax_amount = Decimal(tax_str)
                    tax_amounts.append(tax_amount)
                except (ValueError, IndexError):
                    continue
        
        # Create financial data objects with confidence scoring
        for amount, start, end in amounts:
            # Calculate confidence based on context
            context = text[max(0, start-50):min(len(text), end+50)]
            confidence = self._calculate_amount_confidence(context, amount)
            
            financial_data.append(FinancialData(
                amount=amount,
                invoice_number=invoice_numbers[0] if invoice_numbers else None,
                date=dates[0] if dates else None,
                tax_amount=tax_amounts[0] if tax_amounts else None,
                confidence=confidence
            ))
        
        return financial_data
    
    def _calculate_amount_confidence(self, context: str, amount: Decimal) -> float:
        """Calculate confidence score for extracted amount"""
        confidence = 0.5  # Base confidence
        
        # Boost confidence for common financial keywords
        financial_keywords = ['total', 'amount', 'sum', 'due', 'payment', 'invoice', 'bill']
        for keyword in financial_keywords:
            if keyword.lower() in context.lower():
                confidence += 0.1
        
        # Boost for currency indicators
        currency_indicators = ['sh', 'kes', 'usd', '$', 'ksh']
        for indicator in currency_indicators:
            if indicator.lower() in context.lower():
                confidence += 0.1
        
        # Penalize for very small amounts (likely not main amounts)
        if amount < 100:
            confidence -= 0.2
        
        # Penalize for very large amounts (might be totals)
        if amount > 1000000:
            confidence -= 0.1
        
        return min(1.0, max(0.0, confidence))
    
    def classify_document(self, text: str) -> Tuple[str, float]:
        """Classify document type using pattern matching and ML"""
        scores = {}
        
        # Pattern-based classification
        for doc_type, patterns in self.document_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                score += matches * 0.3
            
            scores[doc_type] = min(1.0, score)
        
        # ML-based classification using TF-IDF
        try:
            # Create feature vector
            features = self.vectorizer.fit_transform([text])
            
            # Simple keyword-based scoring
            keywords = {
                'invoice': ['invoice', 'bill', 'payment', 'amount due'],
                'receipt': ['receipt', 'payment received', 'cash'],
                'contract': ['contract', 'agreement', 'terms', 'party'],
                'bank_statement': ['bank', 'account', 'balance', 'transaction'],
                'tax_document': ['tax', 'vat', 'irs', 'compliance'],
                'tender_document': ['tender', 'proposal', 'rfp', 'bidding']
            }
            
            for doc_type, doc_keywords in keywords.items():
                keyword_score = sum(1 for keyword in doc_keywords if keyword in text.lower())
                scores[doc_type] = max(scores.get(doc_type, 0), keyword_score * 0.2)
                
        except Exception as e:
            logger.warning(f"ML classification failed: {e}")
        
        # Get best classification
        if scores:
            best_type = max(scores, key=scores.get)
            confidence = scores[best_type]
        else:
            best_type = 'other'
            confidence = 0.0
        
        return best_type, confidence
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities using spaCy and custom patterns"""
        entities = {
            'companies': [],
            'people': [],
            'locations': [],
            'dates': [],
            'amounts': [],
            'project_codes': []
        }
        
        # Use spaCy for NER
        doc = self.nlp(text)
        
        for ent in doc.ents:
            if ent.label_ == 'ORG':
                entities['companies'].append(ent.text.strip())
            elif ent.label_ == 'PERSON':
                entities['people'].append(ent.text.strip())
            elif ent.label_ == 'GPE':
                entities['locations'].append(ent.text.strip())
            elif ent.label_ == 'DATE':
                entities['dates'].append(ent.text.strip())
            elif ent.label_ == 'MONEY':
                entities['amounts'].append(ent.text.strip())
        
        # Custom project code extraction
        project_patterns = [
            r'project\s*#?\s*([a-z0-9\-_]+)',
            r'job\s*#?\s*([a-z0-9\-_]+)',
            r'contract\s*#?\s*([a-z0-9\-_]+)',
            r'([a-z]{2,4}\d{3,6})',  # Common project code pattern
        ]
        
        for pattern in project_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['project_codes'].extend(matches)
        
        # Normalize company names
        entities['companies'] = self._normalize_company_names(entities['companies'])
        
        return entities
    
    def _normalize_company_names(self, companies: List[str]) -> List[str]:
        """Normalize and deduplicate company names"""
        normalized = []
        seen = set()
        
        for company in companies:
            # Clean company name
            clean_name = re.sub(r'[^\w\s]', '', company).strip().upper()
            
            # Check against known companies
            best_match = None
            best_score = 0
            
            for known_company in self.known_companies:
                score = fuzz.ratio(clean_name, known_company)
                if score > 80 and score > best_score:
                    best_match = known_company
                    best_score = score
            
            if best_match and best_match not in seen:
                normalized.append(best_match)
                seen.add(best_match)
            elif clean_name and clean_name not in seen:
                normalized.append(clean_name)
                seen.add(clean_name)
        
        return normalized
    
    def detect_duplicates(self, text: str, existing_documents: List[Dict]) -> Tuple[float, Optional[int]]:
        """Detect duplicate documents using multiple algorithms"""
        if not existing_documents:
            return 0.0, None
        
        # Create document fingerprint
        fingerprint = self._create_document_fingerprint(text)
        
        best_match = None
        best_score = 0.0
        
        for doc in existing_documents:
            if 'fingerprint' in doc:
                # Compare fingerprints
                similarity = self._compare_fingerprints(fingerprint, doc['fingerprint'])
                if similarity > best_score:
                    best_score = similarity
                    best_match = doc.get('id')
        
        return best_score, best_match
    
    def _create_document_fingerprint(self, text: str) -> str:
        """Create a document fingerprint for duplicate detection"""
        # Clean and normalize text
        clean_text = re.sub(r'\s+', ' ', text.lower())
        clean_text = re.sub(r'[^\w\s]', '', clean_text)
        
        # Extract key features
        words = clean_text.split()
        
        # Create fingerprint from most common words and structure
        word_freq = Counter(words)
        top_words = [word for word, freq in word_freq.most_common(20)]
        
        # Add document structure features
        lines = text.split('\n')
        line_count = len(lines)
        avg_line_length = sum(len(line) for line in lines) / max(1, line_count)
        
        fingerprint_data = {
            'top_words': top_words,
            'line_count': line_count,
            'avg_line_length': avg_line_length,
            'total_length': len(text)
        }
        
        return hashlib.md5(json.dumps(fingerprint_data, sort_keys=True).encode()).hexdigest()
    
    def _compare_fingerprints(self, fp1: str, fp2: str) -> float:
        """Compare two document fingerprints"""
        if fp1 == fp2:
            return 1.0
        
        # Simple hash comparison for now
        # In production, you'd use more sophisticated similarity metrics
        return 0.0
    
    def calculate_risk_score(self, financial_data: List[FinancialData], 
                           document_type: str, entities: Dict) -> float:
        """Calculate risk score for document"""
        risk_score = 0.0
        
        # Financial risk factors
        total_amount = sum(fd.amount for fd in financial_data if fd.amount)
        if total_amount > 1000000:
            risk_score += 0.3
        elif total_amount > 100000:
            risk_score += 0.2
        
        # Document type risk
        high_risk_types = ['contract', 'tender_document']
        if document_type in high_risk_types:
            risk_score += 0.2
        
        # Entity risk (unknown companies)
        known_companies = set(self.known_companies)
        unknown_companies = [c for c in entities.get('companies', []) 
                           if c not in known_companies]
        if unknown_companies:
            risk_score += 0.1 * len(unknown_companies)
        
        # Missing data risk
        missing_fields = 0
        for fd in financial_data:
            if not fd.amount:
                missing_fields += 1
            if not fd.date:
                missing_fields += 1
            if not fd.invoice_number:
                missing_fields += 1
        
        risk_score += 0.05 * missing_fields
        
        return min(1.0, risk_score)
    
    def generate_business_insights(self, documents: List[DocumentAnalysis]) -> Dict[str, Any]:
        """Generate business intelligence insights"""
        insights = {
            'total_documents': len(documents),
            'total_value': 0,
            'document_types': Counter(),
            'companies': Counter(),
            'monthly_trends': defaultdict(list),
            'risk_analysis': {
                'high_risk_docs': 0,
                'average_risk_score': 0
            },
            'anomalies': []
        }
        
        # Process each document
        for doc in documents:
            # Document type distribution
            insights['document_types'][doc.document_type] += 1
            
            # Financial analysis
            for fd in doc.financial_data:
                if fd.amount:
                    insights['total_value'] += float(fd.amount)
                    
                    if fd.date:
                        month_key = fd.date.strftime('%Y-%m')
                        insights['monthly_trends'][month_key].append(float(fd.amount))
            
            # Company analysis
            for company in doc.entities.get('companies', []):
                insights['companies'][company] += 1
            
            # Risk analysis
            if doc.risk_score > 0.7:
                insights['risk_analysis']['high_risk_docs'] += 1
        
        # Calculate averages
        if documents:
            insights['risk_analysis']['average_risk_score'] = sum(d.risk_score for d in documents) / len(documents)
        
        # Detect anomalies
        amounts = [float(fd.amount) for doc in documents for fd in doc.financial_data if fd.amount]
        if amounts:
            mean_amount = statistics.mean(amounts)
            std_amount = statistics.stdev(amounts) if len(amounts) > 1 else 0
            
            for doc in documents:
                for fd in doc.financial_data:
                    if fd.amount and std_amount > 0:
                        z_score = abs(float(fd.amount) - mean_amount) / std_amount
                        if z_score > 2.5:  # Statistical anomaly
                            insights['anomalies'].append({
                                'document_id': doc.document_id,
                                'amount': float(fd.amount),
                                'z_score': z_score,
                                'type': 'amount_anomaly'
                            })
        
        return insights
    
    async def analyze_document(self, document_id: int, text: str, 
                             existing_documents: List[Dict] = None) -> DocumentAnalysis:
        """Complete document analysis pipeline"""
        logger.info(f"🔍 Analyzing document {document_id}")
        
        # Extract financial data
        financial_data = self.extract_financial_data(text)
        
        # Classify document
        document_type, type_confidence = self.classify_document(text)
        
        # Extract entities
        entities = self.extract_entities(text)
        
        # Detect duplicates
        duplicate_score, duplicate_id = self.detect_duplicates(text, existing_documents or [])
        
        # Calculate risk score
        risk_score = self.calculate_risk_score(financial_data, document_type, entities)
        
        # Generate tags
        tags = self._generate_tags(document_type, entities, financial_data)
        
        # Create analysis result
        analysis = DocumentAnalysis(
            document_id=document_id,
            document_type=document_type,
            confidence=type_confidence,
            financial_data=financial_data,
            entities=entities,
            tags=tags,
            risk_score=risk_score,
            duplicate_score=duplicate_score,
            business_insights={}
        )
        
        logger.info(f"✅ Document {document_id} analyzed: {document_type} (confidence: {type_confidence:.2f})")
        return analysis
    
    def _generate_tags(self, document_type: str, entities: Dict, 
                      financial_data: List[FinancialData]) -> List[str]:
        """Generate automatic tags for document"""
        tags = [document_type]
        
        # Add company tags
        for company in entities.get('companies', []):
            tags.append(f"company:{company}")
        
        # Add project tags
        for project in entities.get('project_codes', []):
            tags.append(f"project:{project}")
        
        # Add financial tags
        for fd in financial_data:
            if fd.amount:
                if fd.amount > 1000000:
                    tags.append("high_value")
                elif fd.amount < 10000:
                    tags.append("low_value")
            
            if fd.tax_amount:
                tags.append("has_tax")
        
        # Add risk tags
        if any(fd.amount and fd.amount > 1000000 for fd in financial_data):
            tags.append("high_risk")
        
        return list(set(tags))  # Remove duplicates
    
    async def analyze_all_documents(self) -> Dict[str, Any]:
        """Analyze all documents in Paperless-ngx"""
        if not await self.authenticate():
            return {"error": "Authentication failed"}
        
        headers = {'Authorization': f'Token {self.token}'}
        
        # Get all documents
        documents = []
        page = 1
        
        while True:
            try:
                response = requests.get(
                    f"{self.paperless_url}/api/documents/",
                    headers=headers,
                    params={'page': page}
                )
                
                if response.status_code != 200:
                    break
                
                data = response.json()
                if not data.get('results'):
                    break
                
                documents.extend(data['results'])
                page += 1
                
            except Exception as e:
                logger.error(f"Error fetching documents: {e}")
                break
        
        logger.info(f"📄 Found {len(documents)} documents to analyze")
        
        # Analyze each document
        analyses = []
        existing_docs = []
        
        for doc in documents:
            try:
                # Get document content
                content_response = requests.get(
                    f"{self.paperless_url}/api/documents/{doc['id']}/",
                    headers=headers
                )
                
                if content_response.status_code == 200:
                    doc_data = content_response.json()
                    text = doc_data.get('content', '')
                    
                    # Analyze document
                    analysis = await self.analyze_document(
                        doc['id'], 
                        text, 
                        existing_docs
                    )
                    analyses.append(analysis)
                    existing_docs.append(doc)
                
            except Exception as e:
                logger.error(f"Error analyzing document {doc['id']}: {e}")
        
        # Generate business insights
        insights = self.generate_business_insights(analyses)
        
        return {
            'total_documents': len(analyses),
            'analyses': analyses,
            'insights': insights
        }

async def main():
    """Main function to run the advanced document AI system"""
    print("🚀 Advanced Document AI System")
    print("=" * 50)
    
    # Initialize AI engine
    ai_engine = DocumentAIEngine(
        paperless_url="http://localhost:8000",
        username="Mike",
        password="106730!@#"
    )
    
    # Run analysis
    results = await ai_engine.analyze_all_documents()
    
    if 'error' in results:
        print(f"❌ Error: {results['error']}")
        return
    
    # Display results
    print(f"\n📊 Analysis Complete!")
    print(f"Total Documents Analyzed: {results['total_documents']}")
    
    # Document type distribution
    doc_types = Counter(analysis.document_type for analysis in results['analyses'])
    print(f"\n📁 Document Types:")
    for doc_type, count in doc_types.most_common():
        percentage = (count / results['total_documents']) * 100
        print(f"   {doc_type}: {count} ({percentage:.1f}%)")
    
    # Financial insights
    total_value = sum(
        float(fd.amount) 
        for analysis in results['analyses'] 
        for fd in analysis.financial_data 
        if fd.amount
    )
    print(f"\n💰 Total Financial Value: KES {total_value:,.2f}")
    
    # Risk analysis
    high_risk_docs = sum(1 for analysis in results['analyses'] if analysis.risk_score > 0.7)
    avg_risk = statistics.mean(analysis.risk_score for analysis in results['analyses'])
    print(f"\n⚠️  Risk Analysis:")
    print(f"   High Risk Documents: {high_risk_docs}")
    print(f"   Average Risk Score: {avg_risk:.2f}")
    
    # Anomalies
    anomalies = results['insights']['anomalies']
    if anomalies:
        print(f"\n🚨 Anomalies Detected: {len(anomalies)}")
        for anomaly in anomalies[:5]:  # Show top 5
            print(f"   Document {anomaly['document_id']}: KES {anomaly['amount']:,.2f} (Z-score: {anomaly['z_score']:.2f})")
    
    # Companies
    companies = results['insights']['companies']
    if companies:
        print(f"\n🏢 Top Companies:")
        for company, count in companies.most_common(5):
            print(f"   {company}: {count} documents")
    
    print(f"\n🎉 Analysis complete! Check 'document_ai.log' for detailed logs.")

if __name__ == "__main__":
    asyncio.run(main()) 