#!/usr/bin/env python3
"""
Paperless-ngx Failed Document Management Script
Handles duplicates, OCR failures, and other processing issues
"""

import requests
import json
import os
from datetime import datetime
import argparse

class PaperlessManager:
    def __init__(self, base_url="http://localhost:8000", username="Mike", password=None):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.token = None
        self.session = requests.Session()
        
    def authenticate(self):
        """Authenticate with Paperless-ngx"""
        if not self.password:
            self.password = input(f"Enter password for user {self.username}: ")
        
        auth_url = f"{self.base_url}/api/token/"
        response = self.session.post(auth_url, data={
            'username': self.username,
            'password': self.password
        })
        
        if response.status_code == 200:
            self.token = response.json()['token']
            self.session.headers.update({'Authorization': f'Token {self.token}'})
            print("✅ Authentication successful")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
    
    def get_documents(self, query=None, limit=100):
        """Get documents from Paperless-ngx"""
        url = f"{self.base_url}/api/documents/"
        params = {'page_size': limit}
        if query:
            params['query'] = query
        
        response = self.session.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get documents: {response.status_code}")
            return None
    
    def get_failed_documents(self):
        """Get documents that failed processing"""
        return self.get_documents("is:failed")
    
    def get_duplicate_documents(self):
        """Get documents that are duplicates"""
        return self.get_documents("is:duplicate")
    
    def get_document_details(self, doc_id):
        """Get detailed information about a specific document"""
        url = f"{self.base_url}/api/documents/{doc_id}/"
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get document {doc_id}: {response.status_code}")
            return None
    
    def delete_document(self, doc_id):
        """Delete a document"""
        url = f"{self.base_url}/api/documents/{doc_id}/"
        response = self.session.delete(url)
        if response.status_code == 204:
            print(f"✅ Deleted document {doc_id}")
            return True
        else:
            print(f"❌ Failed to delete document {doc_id}: {response.status_code}")
            return False
    
    def retry_processing(self, doc_id):
        """Retry processing a failed document"""
        url = f"{self.base_url}/api/documents/{doc_id}/retry/"
        response = self.session.post(url)
        if response.status_code == 200:
            print(f"✅ Retry initiated for document {doc_id}")
            return True
        else:
            print(f"❌ Failed to retry document {doc_id}: {response.status_code}")
            return False
    
    def analyze_failures(self):
        """Analyze and categorize failures, including password-protected docs"""
        print("🔍 Analyzing document processing failures...")
        
        # Get failed documents
        failed_docs = self.get_failed_documents()
        if not failed_docs:
            print("✅ No failed documents found")
            return
        
        print(f"\n📊 Found {failed_docs['count']} failed documents")
        
        # Categorize failures
        categories = {
            'duplicates': [],
            'ocr_failures': [],
            'parsing_failures': [],
            'password_protected': [],
            'other': []
        }
        
        for doc in failed_docs['results']:
            doc_id = doc['id']
            title = doc['title']
            created = doc['created']
            
            # Get detailed info
            details = self.get_document_details(doc_id)
            if not details:
                continue
            details_str = str(details).lower()
            # Categorize based on error messages or status
            if 'duplicate' in title.lower() or 'duplicate' in details_str:
                categories['duplicates'].append({
                    'id': doc_id,
                    'title': title,
                    'created': created,
                    'details': details
                })
            elif 'password' in details_str and 'protect' in details_str:
                categories['password_protected'].append({
                    'id': doc_id,
                    'title': title,
                    'created': created,
                    'details': details
                })
            elif 'ocr' in details_str or 'tesseract' in details_str:
                categories['ocr_failures'].append({
                    'id': doc_id,
                    'title': title,
                    'created': created,
                    'details': details
                })
            elif 'parse' in details_str or 'convert' in details_str:
                categories['parsing_failures'].append({
                    'id': doc_id,
                    'title': title,
                    'created': created,
                    'details': details
                })
            else:
                categories['other'].append({
                    'id': doc_id,
                    'title': title,
                    'created': created,
                    'details': details
                })
        
        # Display analysis
        print("\n📋 Failure Analysis:")
        for category, docs in categories.items():
            if docs:
                print(f"\n🔸 {category.replace('_', ' ').title()} ({len(docs)} documents):")
                for doc in docs[:5]:  # Show first 5
                    print(f"   - ID {doc['id']}: {doc['title']} ({doc['created'][:10]})")
                if len(docs) > 5:
                    print(f"   ... and {len(docs) - 5} more")
        
        return categories

    def handle_duplicates(self, auto_delete=False):
        """Handle duplicate documents"""
        print("🔄 Handling duplicate documents...")
        
        duplicates = self.get_duplicate_documents()
        if not duplicates or duplicates['count'] == 0:
            print("✅ No duplicate documents found")
            return
        
        print(f"\n📊 Found {duplicates['count']} duplicate documents")
        
        if auto_delete:
            print("🗑️  Auto-deleting duplicates...")
            for doc in duplicates['results']:
                self.delete_document(doc['id'])
        else:
            print("\n📋 Duplicate documents:")
            for doc in duplicates['results']:
                print(f"   - ID {doc['id']}: {doc['title']} ({doc['created'][:10]})")
            
            choice = input("\n❓ Delete all duplicates? (y/N): ").lower()
            if choice == 'y':
                for doc in duplicates['results']:
                    self.delete_document(doc['id'])
    
    def retry_failed_processing(self, auto_retry=False):
        """Retry processing for failed documents, skipping duplicates and password-protected"""
        print("🔄 Retrying failed document processing...")
        
        failed_docs = self.get_failed_documents()
        if not failed_docs or failed_docs['count'] == 0:
            print("✅ No failed documents to retry")
            return
        
        print(f"\n📊 Found {failed_docs['count']} failed documents")
        
        # Analyze to get categories
        categories = self.analyze_failures()
        skip_ids = set()
        if categories:
            for doc in categories.get('duplicates', []):
                skip_ids.add(doc['id'])
            for doc in categories.get('password_protected', []):
                skip_ids.add(doc['id'])
        
        if auto_retry:
            print("🔄 Auto-retrying all non-duplicate, non-password-protected failed documents...")
            retried = 0
            for doc in failed_docs['results']:
                if doc['id'] in skip_ids:
                    continue
                if self.retry_processing(doc['id']):
                    retried += 1
            print(f"✅ Retried {retried} documents (skipped {len(skip_ids)})")
        else:
            print("\n📋 Failed documents (excluding duplicates and password-protected):")
            for doc in failed_docs['results']:
                if doc['id'] in skip_ids:
                    continue
                print(f"   - ID {doc['id']}: {doc['title']} ({doc['created'][:10]})")
            choice = input("\n❓ Retry processing for all listed failed documents? (y/N): ").lower()
            if choice == 'y':
                for doc in failed_docs['results']:
                    if doc['id'] in skip_ids:
                        continue
                    self.retry_processing(doc['id'])
        # Manual review note
        if categories and categories.get('password_protected'):
            print("\n🔒 Password-protected documents detected. These are excluded from retry and require manual password entry later.")
            for doc in categories['password_protected']:
                print(f"   - ID {doc['id']}: {doc['title']} ({doc['created'][:10]}) [PASSWORD PROTECTED]")
        print("\n📝 For persistent failures, see the generated report for manual review and tagging.")

    def generate_report(self):
        """Generate a comprehensive failure report, including password-protected docs"""
        print("📊 Generating failure report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'failed_documents': self.get_failed_documents(),
            'duplicate_documents': self.get_duplicate_documents(),
            'analysis': self.analyze_failures()
        }
        
        # Save report
        filename = f"paperless_failure_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📄 Report saved to: {filename}")
        print("🔒 Password-protected documents are listed separately for manual follow-up.")
        return report

def main():
    parser = argparse.ArgumentParser(description='Manage Paperless-ngx failed documents')
    parser.add_argument('--url', default='http://localhost:8000', help='Paperless-ngx URL')
    parser.add_argument('--username', default='Mike', help='Username')
    parser.add_argument('--password', help='Password (will prompt if not provided)')
    parser.add_argument('--action', choices=['analyze', 'duplicates', 'retry', 'report', 'all'], 
                       default='analyze', help='Action to perform')
    parser.add_argument('--auto', action='store_true', help='Auto-confirm actions')
    
    args = parser.parse_args()
    
    manager = PaperlessManager(args.url, args.username, args.password)
    
    if not manager.authenticate():
        return
    
    if args.action == 'analyze':
        manager.analyze_failures()
    elif args.action == 'duplicates':
        manager.handle_duplicates(auto_delete=args.auto)
    elif args.action == 'retry':
        manager.retry_failed_processing(auto_retry=args.auto)
    elif args.action == 'report':
        manager.generate_report()
    elif args.action == 'all':
        print("🔄 Running comprehensive failure management...")
        manager.analyze_failures()
        manager.handle_duplicates(auto_delete=args.auto)
        manager.retry_failed_processing(auto_retry=args.auto)
        manager.generate_report()

if __name__ == "__main__":
    main() 