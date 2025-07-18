#!/usr/bin/env python3
"""
Simple Paperless-ngx Integration (No Database Required)

This script connects to Paperless-ngx and shows document statistics
without requiring database setup.
"""

import requests
import json
import re
from datetime import datetime
from collections import defaultdict

class SimplePaperlessIntegration:
    def __init__(self, base_url="http://localhost:8000", username="Mike", password="106730!@#"):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.token = None
        
    def authenticate(self):
        """Authenticate with Paperless-ngx"""
        try:
            auth_url = f"{self.base_url}/api/token/"
            response = self.session.post(auth_url, data={
                'username': self.username,
                'password': self.password
            })
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data.get('token')
                if self.token:
                    self.session.headers.update({
                        'Authorization': f'Token {self.token}'
                    })
                    print("✅ Authentication successful!")
                    return True
                else:
                    print("❌ No token in response")
                    return False
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def get_all_documents(self):
        """Get all documents from Paperless-ngx"""
        documents = []
        page = 1
        
        while True:
            try:
                url = f"{self.base_url}/api/documents/"
                params = {
                    'page': page,
                    'page_size': 100
                }
                
                response = self.session.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])
                    
                    if not results:
                        break
                    
                    documents.extend(results)
                    print(f"📄 Retrieved page {page}: {len(results)} documents")
                    page += 1
                else:
                    print(f"❌ Failed to get page {page}: {response.status_code}")
                    break
                    
            except Exception as e:
                print(f"❌ Error getting page {page}: {e}")
                break
        
        return documents
    
    def analyze_documents(self, documents):
        """Analyze documents and provide statistics"""
        print(f"\n📊 Document Analysis")
        print("=" * 50)
        
        # Basic stats
        total_docs = len(documents)
        print(f"Total Documents: {total_docs}")
        
        # Document types by filename
        doc_types = defaultdict(int)
        companies = defaultdict(int)
        amounts = []
        
        for doc in documents:
            filename = doc.get('title', '').lower()
            
            # Categorize by filename
            if any(keyword in filename for keyword in ['nca', 'certificate', 'license']):
                doc_types['NCA Certificate'] += 1
            elif any(keyword in filename for keyword in ['tax', 'tcc', 'compliance']):
                doc_types['Tax Compliance'] += 1
            elif any(keyword in filename for keyword in ['bank', 'statement', 'account']):
                doc_types['Bank Statement'] += 1
            elif any(keyword in filename for keyword in ['audit', 'financial']):
                doc_types['Financial Statement'] += 1
            elif any(keyword in filename for keyword in ['tender', 'bid']):
                doc_types['Tender Document'] += 1
            elif any(keyword in filename for keyword in ['contract', 'agreement']):
                doc_types['Contract'] += 1
            else:
                doc_types['Other'] += 1
            
            # Extract company names
            if 'masterbuild' in filename:
                companies['MASTERBUILD LIMITED'] += 1
            elif 'brimmacs' in filename:
                companies['BRIMMACS INVESTMENTS'] += 1
            elif 'cabera' in filename:
                companies['CABERA ENTERPRISES'] += 1
            elif 'altan' in filename:
                companies['ALTAN ENTERPRISES'] += 1
            elif 'dorden' in filename:
                companies['DORDEN VENTURES'] += 1
            elif 'nkonge' in filename:
                companies['NKONGE SOLUTION'] += 1
            elif 'netzach' in filename:
                companies['NETZACH AGENCIES'] += 1
            elif 'zerubbabel' in filename:
                companies['ZERUBBABEL TAILOR WORKS'] += 1
        
        # Print results
        print(f"\n📁 Document Types:")
        for doc_type, count in sorted(doc_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_docs) * 100
            print(f"   {doc_type}: {count} ({percentage:.1f}%)")
        
        print(f"\n🏢 Companies Identified:")
        for company, count in sorted(companies.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_docs) * 100
            print(f"   {company}: {count} documents ({percentage:.1f}%)")
        
        # Recent documents
        print(f"\n📅 Recent Documents:")
        recent_docs = sorted(documents, key=lambda x: x.get('added', ''), reverse=True)[:5]
        for doc in recent_docs:
            added_date = doc.get('added', 'Unknown')
            print(f"   {doc.get('title', 'No title')} - {added_date}")
        
        return {
            'total_documents': total_docs,
            'document_types': dict(doc_types),
            'companies': dict(companies)
        }

def main():
    """Main function"""
    print("🚀 Simple Paperless-ngx Integration")
    print("=" * 50)
    
    # Initialize integration
    integration = SimplePaperlessIntegration()
    
    # Authenticate
    if not integration.authenticate():
        print("❌ Failed to authenticate")
        return
    
    # Get documents
    print("\n📄 Retrieving documents...")
    documents = integration.get_all_documents()
    
    if not documents:
        print("❌ No documents found")
        return
    
    # Analyze documents
    stats = integration.analyze_documents(documents)
    
    print(f"\n🎉 Analysis complete!")
    print(f"Ready to import {stats['total_documents']} documents to database.")

if __name__ == "__main__":
    main() 