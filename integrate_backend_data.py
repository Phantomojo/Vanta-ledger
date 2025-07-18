#!/usr/bin/env python3
"""
Vanta Ledger Backend Integration Script
Connects all data sources and provides real-time synchronization for the web dashboard
"""

import os
import sys
import json
import sqlite3
import requests
import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Document:
    id: int
    title: str
    document_type: str
    created: str
    amount: float
    vendor: str
    status: str
    ai_analyzed: bool
    risk_score: Optional[float] = None
    project_id: Optional[int] = None

@dataclass
class Project:
    id: int
    name: str
    status: str
    docs: int
    value: float
    created_at: str

@dataclass
class AIInsight:
    id: int
    document_id: int
    insight_type: str
    insight_data: Dict[str, Any]
    risk_score: float
    created_at: str

class PaperlessIntegration:
    """Integration with Paperless-ngx document management system"""
    
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.last_sync = None
    
    def get_documents(self, limit: int = 100, offset: int = 0) -> List[Document]:
        """Get documents from Paperless-ngx"""
        try:
            url = f"{self.base_url}/api/documents/"
            params = {
                'limit': limit,
                'offset': offset,
                'ordering': '-created'
            }
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            documents = []
            for doc in data.get('results', []):
                # Extract amount from document content or tags
                amount = self._extract_amount(doc)
                vendor = self._extract_vendor(doc)
                doc_type = self._classify_document(doc)
                
                documents.append(Document(
                    id=doc['id'],
                    title=doc.get('title', 'Untitled'),
                    document_type=doc_type,
                    created=doc.get('created', ''),
                    amount=amount,
                    vendor=vendor,
                    status='processed' if doc.get('archive_serial_number') else 'pending',
                    ai_analyzed=True,  # Paperless-ngx has OCR
                    risk_score=self._calculate_risk_score(doc)
                ))
            
            return documents
        except Exception as e:
            logger.error(f"Error fetching documents from Paperless: {e}")
            return []
    
    def get_document(self, doc_id: int) -> Dict[str, Any]:
        """Get specific document by ID"""
        try:
            url = f"{self.base_url}/api/documents/{doc_id}/"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching document {doc_id}: {e}")
            return {}
    
    def _extract_amount(self, doc: Dict) -> float:
        """Extract monetary amount from document"""
        try:
            # Check tags for amount
            tags = doc.get('tags', [])
            for tag in tags:
                if 'amount' in tag.lower() or 'value' in tag.lower():
                    # Try to extract number from tag
                    import re
                    numbers = re.findall(r'\d+\.?\d*', tag)
                    if numbers:
                        return float(numbers[0])
            
            # Check document content (if available)
            content = doc.get('content', '')
            if content:
                import re
                # Look for currency patterns
                currency_patterns = [
                    r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                    r'USD\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                    r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*USD'
                ]
                for pattern in currency_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        return float(matches[0].replace(',', ''))
            
            return 0.0
        except:
            return 0.0
    
    def _extract_vendor(self, doc: Dict) -> str:
        """Extract vendor/supplier from document"""
        try:
            # Check correspondent
            correspondent = doc.get('correspondent', {})
            if correspondent:
                return correspondent.get('name', 'Unknown')
            
            # Check tags
            tags = doc.get('tags', [])
            for tag in tags:
                if any(word in tag.lower() for word in ['vendor', 'supplier', 'company', 'ltd', 'inc']):
                    return tag
            
            return 'Unknown Vendor'
        except:
            return 'Unknown Vendor'
    
    def _classify_document(self, doc: Dict) -> str:
        """Classify document type"""
        try:
            title = doc.get('title', '').lower()
            tags = [tag.lower() for tag in doc.get('tags', [])]
            
            if any(word in title for word in ['invoice', 'bill']):
                return 'invoice'
            elif any(word in title for word in ['contract', 'agreement']):
                return 'contract'
            elif any(word in title for word in ['receipt', 'payment']):
                return 'receipt'
            elif any(word in title for word in ['proposal', 'quote']):
                return 'proposal'
            else:
                return 'document'
        except:
            return 'document'
    
    def _calculate_risk_score(self, doc: Dict) -> float:
        """Calculate risk score for document"""
        try:
            score = 0.0
            
            # Check for high-value documents
            amount = self._extract_amount(doc)
            if amount > 100000:
                score += 0.3
            elif amount > 50000:
                score += 0.2
            elif amount > 10000:
                score += 0.1
            
            # Check document type
            doc_type = self._classify_document(doc)
            if doc_type == 'contract':
                score += 0.4
            elif doc_type == 'invoice':
                score += 0.2
            
            # Check tags for risk indicators
            tags = [tag.lower() for tag in doc.get('tags', [])]
            risk_keywords = ['urgent', 'critical', 'legal', 'compliance', 'penalty']
            for keyword in risk_keywords:
                if any(keyword in tag for tag in tags):
                    score += 0.2
            
            return min(score, 1.0)
        except:
            return 0.0

class DatabaseManager:
    """Manages local SQLite database for analytics and insights"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                status TEXT NOT NULL,
                document_count INTEGER DEFAULT 0,
                total_value REAL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create ai_insights table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                insight_type TEXT NOT NULL,
                insight_data TEXT NOT NULL,
                risk_score REAL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create documents table for caching
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                document_type TEXT NOT NULL,
                created TEXT NOT NULL,
                amount REAL DEFAULT 0,
                vendor TEXT NOT NULL,
                status TEXT NOT NULL,
                ai_analyzed BOOLEAN DEFAULT FALSE,
                risk_score REAL DEFAULT 0,
                project_id INTEGER,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def update_analytics(self, analytics_data: Dict[str, float]):
        """Update analytics metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for metric_name, value in analytics_data.items():
            cursor.execute('''
                INSERT INTO analytics (metric_name, metric_value)
                VALUES (?, ?)
            ''', (metric_name, value))
        
        conn.commit()
        conn.close()
    
    def get_latest_analytics(self) -> Dict[str, float]:
        """Get latest analytics values"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT metric_name, metric_value 
            FROM analytics 
            WHERE id IN (
                SELECT MAX(id) 
                FROM analytics 
                GROUP BY metric_name
            )
        ''')
        
        analytics = {}
        for row in cursor.fetchall():
            analytics[row[0]] = row[1]
        
        conn.close()
        return analytics
    
    def cache_documents(self, documents: List[Document]):
        """Cache documents in local database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for doc in documents:
            cursor.execute('''
                INSERT OR REPLACE INTO documents 
                (id, title, document_type, created, amount, vendor, status, ai_analyzed, risk_score, project_id, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                doc.id, doc.title, doc.document_type, doc.created, doc.amount,
                doc.vendor, doc.status, doc.ai_analyzed, doc.risk_score,
                doc.project_id, datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    def get_cached_documents(self, limit: int = 100) -> List[Document]:
        """Get cached documents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, document_type, created, amount, vendor, status, ai_analyzed, risk_score, project_id
            FROM documents
            ORDER BY last_updated DESC
            LIMIT ?
        ''', (limit,))
        
        documents = []
        for row in cursor.fetchall():
            documents.append(Document(
                id=row[0], title=row[1], document_type=row[2], created=row[3],
                amount=row[4], vendor=row[5], status=row[6], ai_analyzed=row[7],
                risk_score=row[8], project_id=row[9]
            ))
        
        conn.close()
        return documents

class AIProcessor:
    """Process documents and generate AI insights"""
    
    def __init__(self):
        self.insight_types = ['risk_analysis', 'financial_analysis', 'compliance_check', 'vendor_analysis']
    
    def analyze_document(self, document: Document) -> List[AIInsight]:
        """Analyze a document and generate insights"""
        insights = []
        
        # Risk analysis
        risk_insight = self._analyze_risk(document)
        if risk_insight:
            insights.append(risk_insight)
        
        # Financial analysis
        financial_insight = self._analyze_financial(document)
        if financial_insight:
            insights.append(financial_insight)
        
        # Compliance check
        compliance_insight = self._analyze_compliance(document)
        if compliance_insight:
            insights.append(compliance_insight)
        
        return insights
    
    def _analyze_risk(self, document: Document) -> Optional[AIInsight]:
        """Analyze document for risks"""
        risk_factors = []
        risk_score = document.risk_score or 0.0
        
        if document.amount > 100000:
            risk_factors.append('high_value')
            risk_score += 0.2
        
        if document.document_type == 'contract':
            risk_factors.append('contract_terms')
            risk_score += 0.3
        
        if document.vendor.lower() in ['unknown', 'unknown vendor']:
            risk_factors.append('unknown_vendor')
            risk_score += 0.2
        
        if risk_factors:
            return AIInsight(
                id=len(risk_factors),  # Simple ID generation
                document_id=document.id,
                insight_type='risk_analysis',
                insight_data={
                    'risk_level': 'high' if risk_score > 0.7 else 'medium' if risk_score > 0.4 else 'low',
                    'risk_factors': risk_factors,
                    'recommendations': self._get_risk_recommendations(risk_factors)
                },
                risk_score=min(risk_score, 1.0),
                created_at=datetime.now().isoformat()
            )
        return None
    
    def _analyze_financial(self, document: Document) -> Optional[AIInsight]:
        """Analyze document for financial insights"""
        if document.amount > 0:
            return AIInsight(
                id=document.id + 1000,  # Offset for financial insights
                document_id=document.id,
                insight_type='financial_analysis',
                insight_data={
                    'amount': document.amount,
                    'currency': 'USD',
                    'payment_status': document.status,
                    'vendor_category': self._categorize_vendor(document.vendor),
                    'budget_impact': 'high' if document.amount > 50000 else 'medium' if document.amount > 10000 else 'low'
                },
                risk_score=0.1,  # Low risk for financial analysis
                created_at=datetime.now().isoformat()
            )
        return None
    
    def _analyze_compliance(self, document: Document) -> Optional[AIInsight]:
        """Analyze document for compliance issues"""
        compliance_issues = []
        
        if document.document_type == 'contract' and document.amount > 100000:
            compliance_issues.append('large_contract_review_required')
        
        if document.vendor.lower() in ['unknown', 'unknown vendor']:
            compliance_issues.append('vendor_verification_required')
        
        if compliance_issues:
            return AIInsight(
                id=document.id + 2000,  # Offset for compliance insights
                document_id=document.id,
                insight_type='compliance_check',
                insight_data={
                    'compliance_status': 'requires_review' if compliance_issues else 'compliant',
                    'issues': compliance_issues,
                    'required_actions': self._get_compliance_actions(compliance_issues)
                },
                risk_score=0.5 if compliance_issues else 0.1,
                created_at=datetime.now().isoformat()
            )
        return None
    
    def _get_risk_recommendations(self, risk_factors: List[str]) -> List[str]:
        """Get recommendations based on risk factors"""
        recommendations = []
        
        if 'high_value' in risk_factors:
            recommendations.append('Review payment terms and conditions')
        
        if 'contract_terms' in risk_factors:
            recommendations.append('Legal review recommended')
        
        if 'unknown_vendor' in risk_factors:
            recommendations.append('Verify vendor credentials')
        
        return recommendations
    
    def _categorize_vendor(self, vendor: str) -> str:
        """Categorize vendor type"""
        vendor_lower = vendor.lower()
        
        if any(word in vendor_lower for word in ['construction', 'build', 'contractor']):
            return 'construction'
        elif any(word in vendor_lower for word in ['tech', 'software', 'it']):
            return 'technology'
        elif any(word in vendor_lower for word in ['legal', 'law', 'attorney']):
            return 'legal'
        else:
            return 'general'
    
    def _get_compliance_actions(self, issues: List[str]) -> List[str]:
        """Get required compliance actions"""
        actions = []
        
        if 'large_contract_review_required' in issues:
            actions.append('Schedule legal review')
        
        if 'vendor_verification_required' in issues:
            actions.append('Verify vendor documentation')
        
        return actions

class DataIntegrator:
    """Main integration class that coordinates all data sources"""
    
    def __init__(self, paperless_url: str, paperless_username: str, paperless_password: str, db_path: str):
        self.paperless = PaperlessIntegration(paperless_url, paperless_username, paperless_password)
        self.database = DatabaseManager(db_path)
        self.ai_processor = AIProcessor()
        self.sync_interval = 300  # 5 minutes
        self.is_running = False
    
    def start_sync(self):
        """Start continuous data synchronization"""
        self.is_running = True
        logger.info("Starting data synchronization...")
        
        # Initial sync
        self.sync_all_data()
        
        # Start background sync thread
        sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        sync_thread.start()
    
    def stop_sync(self):
        """Stop data synchronization"""
        self.is_running = False
        logger.info("Stopping data synchronization...")
    
    def _sync_loop(self):
        """Background sync loop"""
        while self.is_running:
            try:
                time.sleep(self.sync_interval)
                if self.is_running:
                    self.sync_all_data()
            except Exception as e:
                logger.error(f"Error in sync loop: {e}")
    
    def sync_all_data(self):
        """Synchronize all data sources"""
        try:
            logger.info("Starting data sync...")
            
            # Get documents from Paperless-ngx
            documents = self.paperless.get_documents(limit=1000)
            logger.info(f"Retrieved {len(documents)} documents from Paperless-ngx")
            
            # Cache documents
            self.database.cache_documents(documents)
            
            # Generate AI insights
            all_insights = []
            for doc in documents:
                insights = self.ai_processor.analyze_document(doc)
                all_insights.extend(insights)
            
            logger.info(f"Generated {len(all_insights)} AI insights")
            
            # Calculate analytics
            analytics = self._calculate_analytics(documents)
            self.database.update_analytics(analytics)
            
            # Update projects
            projects = self._extract_projects(documents)
            self._update_projects(projects)
            
            logger.info("Data sync completed successfully")
            
        except Exception as e:
            logger.error(f"Error during data sync: {e}")
    
    def _calculate_analytics(self, documents: List[Document]) -> Dict[str, float]:
        """Calculate analytics metrics"""
        total_docs = len(documents)
        ai_processed = sum(1 for doc in documents if doc.ai_analyzed)
        total_value = sum(doc.amount for doc in documents)
        pending_review = sum(1 for doc in documents if doc.status == 'pending')
        
        # Calculate processing metrics
        today = datetime.now().date()
        processing_today = sum(1 for doc in documents 
                             if datetime.fromisoformat(doc.created.replace('Z', '+00:00')).date() == today)
        
        week_ago = today - timedelta(days=7)
        processing_week = sum(1 for doc in documents 
                            if datetime.fromisoformat(doc.created.replace('Z', '+00:00')).date() >= week_ago)
        
        month_ago = today - timedelta(days=30)
        processing_month = sum(1 for doc in documents 
                             if datetime.fromisoformat(doc.created.replace('Z', '+00:00')).date() >= month_ago)
        
        return {
            'total_documents': total_docs,
            'ai_processed': ai_processed,
            'active_projects': len(set(doc.project_id for doc in documents if doc.project_id)),
            'pending_review': pending_review,
            'processing_today': processing_today,
            'processing_week': processing_week,
            'processing_month': processing_month,
            'ai_accuracy': 94.2,  # Mock value
            'processing_speed': 2.3,  # Mock value
            'success_rate': 98.7,  # Mock value
            'total_value': total_value
        }
    
    def _extract_projects(self, documents: List[Document]) -> List[Project]:
        """Extract projects from documents"""
        projects = {}
        
        for doc in documents:
            # Simple project extraction based on vendor and document type
            if doc.document_type in ['contract', 'proposal'] and doc.amount > 10000:
                project_key = f"{doc.vendor}_{doc.document_type}"
                
                if project_key not in projects:
                    projects[project_key] = Project(
                        id=len(projects) + 1,
                        name=f"{doc.vendor} Project",
                        status='Active',
                        docs=0,
                        value=0,
                        created_at=doc.created
                    )
                
                projects[project_key].docs += 1
                projects[project_key].value += doc.amount
        
        return list(projects.values())
    
    def _update_projects(self, projects: List[Project]):
        """Update projects in database"""
        conn = sqlite3.connect(self.database.db_path)
        cursor = conn.cursor()
        
        # Clear existing projects
        cursor.execute('DELETE FROM projects')
        
        # Insert new projects
        for project in projects:
            cursor.execute('''
                INSERT INTO projects (id, name, status, document_count, total_value, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (project.id, project.name, project.status, project.docs, project.value, project.created_at))
        
        conn.commit()
        conn.close()
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get complete dashboard data"""
        try:
            # Get analytics
            analytics = self.database.get_latest_analytics()
            
            # Get recent documents
            documents = self.database.get_cached_documents(limit=20)
            
            # Get projects
            conn = sqlite3.connect(self.database.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, status, document_count, total_value, created_at FROM projects')
            projects = []
            for row in cursor.fetchall():
                projects.append(Project(
                    id=row[0], name=row[1], status=row[2], docs=row[3], value=row[4], created_at=row[5]
                ))
            conn.close()
            
            # Generate recent activity
            recent_activity = self._generate_recent_activity(documents)
            
            return {
                'analytics': analytics,
                'recent_activity': recent_activity,
                'documents': [asdict(doc) for doc in documents],
                'projects': [asdict(project) for project in projects]
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {}
    
    def _generate_recent_activity(self, documents: List[Document]) -> List[Dict[str, Any]]:
        """Generate recent activity feed"""
        activities = []
        
        for doc in documents[:10]:  # Last 10 documents
            activity_type = 'document_processed' if doc.status == 'processed' else 'document_pending'
            status = 'AI Analyzed' if doc.ai_analyzed else 'Pending Analysis'
            
            activities.append({
                'id': doc.id,
                'type': activity_type,
                'title': f"{doc.document_type.title()} from {doc.vendor}",
                'timestamp': doc.created,
                'status': status
            })
        
        return activities

def main():
    """Main function to run the integration"""
    # Configuration
    PAPERLESS_URL = "http://localhost:8000"
    PAPERLESS_USERNAME = "Mike"
    PAPERLESS_PASSWORD = "106730!@#"
    DATABASE_PATH = "vanta_ledger_integrated.db"
    
    # Create integrator
    integrator = DataIntegrator(PAPERLESS_URL, PAPERLESS_USERNAME, PAPERLESS_PASSWORD, DATABASE_PATH)
    
    try:
        # Start sync
        integrator.start_sync()
        
        # Keep running
        while True:
            time.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        integrator.stop_sync()

if __name__ == "__main__":
    main() 