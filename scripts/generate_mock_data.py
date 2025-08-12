#!/usr/bin/env python3
"""
Vanta Ledger - Mock Data Generator
Generates realistic construction industry data for development and testing
"""

import sqlite3
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

DATABASE_PATH = "vanta_ledger.db"

class MockDataGenerator:
    def __init__(self):
        self.db_path = DATABASE_PATH
        
    def generate_documents(self, count: int = 100) -> List[Dict[str, Any]]:
        """Generate mock document data"""
        document_types = ['invoice', 'contract', 'proposal', 'report', 'permit', 'receipt']
        vendors = [
            'Skyline Construction Ltd', 'Riverside Builders Inc', 'Metro Developers Corp',
            'Green Heights Contractors', 'Tech Campus Builders', 'Urban Construction LLC',
            'Premier Steel Works', 'Elite Electrical Services', 'Quality Plumbing Co',
            'Advanced HVAC Systems', 'Landscape Solutions Ltd', 'Security Systems Pro'
        ]
        
        projects = [
            {'name': 'Skyline Tower', 'code': 'SKL-001', 'value': 2400000},
            {'name': 'Riverside Plaza', 'code': 'RIV-002', 'value': 1800000},
            {'name': 'Tech Campus', 'code': 'TEC-003', 'value': 3200000},
            {'name': 'Green Heights', 'code': 'GRN-004', 'value': 1100000},
            {'name': 'Metro Station', 'code': 'MET-005', 'value': 850000},
            {'name': 'Shopping Mall', 'code': 'URB-006', 'value': 1900000}
        ]
        
        documents = []
        for i in range(count):
            doc_type = random.choice(document_types)
            vendor = random.choice(vendors)
            project = random.choice(projects)
            
            # Generate realistic amounts based on document type
            if doc_type == 'invoice':
                amount = random.uniform(5000, 50000)
            elif doc_type == 'contract':
                amount = random.uniform(50000, 500000)
            elif doc_type == 'proposal':
                amount = random.uniform(10000, 100000)
            else:
                amount = random.uniform(1000, 10000)
            
            # Generate creation date (within last 6 months)
            days_ago = random.randint(0, 180)
            created_date = datetime.now() - timedelta(days=days_ago)
            
            # Generate risk score based on amount and type
            base_risk = min(amount / 100000, 0.8)  # Higher amounts = higher risk
            if doc_type in ['contract', 'proposal']:
                base_risk += 0.1
            risk_score = min(1.0, base_risk + random.uniform(-0.1, 0.1))
            
            document = {
                'id': i + 1,
                'title': f"{doc_type.title()} #{str(i+1).zfill(3)} - {project['name']}",
                'document_type': doc_type,
                'created': created_date.isoformat(),
                'amount': round(amount, 2),
                'vendor': vendor,
                'status': random.choice(['processed', 'pending_review', 'approved']),
                'ai_analyzed': True,
                'risk_score': round(risk_score, 2),
                'project_code': project['code'],
                'project_name': project['name']
            }
            
            documents.append(document)
        
        return documents
    
    def generate_ai_insights(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate AI insights for documents"""
        insights = []
        insight_id = 1
        
        for doc in documents:
            # Risk analysis insight
            risk_level = 'high' if doc['risk_score'] > 0.7 else 'medium' if doc['risk_score'] > 0.4 else 'low'
            risk_factors = []
            
            if doc['amount'] > 100000:
                risk_factors.append('high_value')
            if doc['document_type'] == 'contract':
                risk_factors.append('contract_terms')
            if doc['risk_score'] > 0.5:
                risk_factors.append('payment_terms')
            
            insights.append({
                'id': insight_id,
                'document_id': doc['id'],
                'insight_type': 'risk_analysis',
                'insight_data': {
                    'risk_level': risk_level,
                    'risk_factors': risk_factors,
                    'recommendations': [
                        'Review payment terms' if 'payment_terms' in risk_factors else 'Standard processing',
                        'Monitor closely' if risk_level == 'high' else 'Regular review'
                    ]
                },
                'risk_score': doc['risk_score'],
                'created_at': doc['created']
            })
            insight_id += 1
            
            # Financial analysis insight
            payment_status = random.choice(['pending', 'paid', 'overdue'])
            due_date = datetime.fromisoformat(doc['created']) + timedelta(days=random.randint(30, 90))
            
            insights.append({
                'id': insight_id,
                'document_id': doc['id'],
                'insight_type': 'financial_analysis',
                'insight_data': {
                    'amount': doc['amount'],
                    'currency': 'USD',
                    'payment_status': payment_status,
                    'due_date': due_date.strftime('%Y-%m-%d'),
                    'vendor': doc['vendor'],
                    'project_code': doc['project_code']
                },
                'risk_score': doc['risk_score'],
                'created_at': doc['created']
            })
            insight_id += 1
        
        return insights
    
    def generate_projects(self) -> List[Dict[str, Any]]:
        """Generate project data"""
        projects = [
            {
                'name': 'Skyline Tower',
                'status': 'Active',
                'docs': 847,
                'value': 2400000,
                'progress': 65,
                'start_date': '2024-01-15',
                'end_date': '2024-12-31'
            },
            {
                'name': 'Riverside Plaza',
                'status': 'Planning',
                'docs': 234,
                'value': 1800000,
                'progress': 15,
                'start_date': '2024-03-01',
                'end_date': '2025-06-30'
            },
            {
                'name': 'Tech Campus',
                'status': 'Completed',
                'docs': 1156,
                'value': 3200000,
                'progress': 100,
                'start_date': '2023-06-01',
                'end_date': '2024-05-31'
            },
            {
                'name': 'Green Heights',
                'status': 'Active',
                'docs': 432,
                'value': 1100000,
                'progress': 45,
                'start_date': '2024-02-01',
                'end_date': '2024-11-30'
            },
            {
                'name': 'Metro Station',
                'status': 'On Hold',
                'docs': 89,
                'value': 850000,
                'progress': 25,
                'start_date': '2024-04-01',
                'end_date': '2025-03-31'
            },
            {
                'name': 'Shopping Mall',
                'status': 'Active',
                'docs': 567,
                'value': 1900000,
                'progress': 78,
                'start_date': '2024-01-01',
                'end_date': '2024-10-31'
            }
        ]
        
        return projects
    
    def generate_analytics(self, document_count: int) -> Dict[str, Any]:
        """Generate analytics data"""
        return {
            'total_documents': document_count,
            'ai_processed': int(document_count * 0.95),
            'active_projects': 6,
            'pending_review': random.randint(50, 150),
            'processing_today': random.randint(20, 80),
            'processing_week': random.randint(200, 400),
            'processing_month': random.randint(800, 1500),
            'ai_accuracy': round(random.uniform(92, 98), 1),
            'processing_speed': round(random.uniform(1.5, 3.5), 1),
            'success_rate': round(random.uniform(96, 99), 1)
        }
    
    def populate_database(self, document_count: int = 100):
        """Populate database with mock data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        print("🗄️ Generating and populating database with mock data...")
        
        # Clear existing data
        cursor.execute("DELETE FROM ai_insights")
        cursor.execute("DELETE FROM analytics")
        cursor.execute("DELETE FROM projects")
        
        # Generate documents
        documents = self.generate_documents(document_count)
        print(f"📄 Generated {len(documents)} documents")
        
        # Generate AI insights
        insights = self.generate_ai_insights(documents)
        print(f"🤖 Generated {len(insights)} AI insights")
        
        # Insert AI insights
        for insight in insights:
            cursor.execute('''
                INSERT INTO ai_insights (document_id, insight_type, insight_data, risk_score, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                insight['document_id'],
                insight['insight_type'],
                json.dumps(insight['insight_data']),
                insight['risk_score'],
                insight['created_at']
            ))
        
        # Generate and insert analytics
        analytics = self.generate_analytics(document_count)
        for metric_name, metric_value in analytics.items():
            cursor.execute('''
                INSERT INTO analytics (metric_name, metric_value, timestamp)
                VALUES (?, ?, ?)
            ''', (metric_name, metric_value, datetime.now().isoformat()))
        
        # Generate and insert projects
        projects = self.generate_projects()
        for project in projects:
            cursor.execute('''
                INSERT INTO projects (name, status, document_count, total_value, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                project['name'],
                project['status'],
                project['docs'],
                project['value'],
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        
        print("✅ Database populated successfully!")
        print(f"📊 Summary:")
        print(f"   - Documents: {len(documents)}")
        print(f"   - AI Insights: {len(insights)}")
        print(f"   - Projects: {len(projects)}")
        print(f"   - Analytics: {len(analytics)} metrics")
        
        return documents, insights, projects, analytics

if __name__ == '__main__':
    generator = MockDataGenerator()
    documents, insights, projects, analytics = generator.populate_database(100)
    
    print("\n🎉 Mock data generation complete!")
    print("🌐 Your Vanta Ledger dashboard is now ready with realistic data!") 