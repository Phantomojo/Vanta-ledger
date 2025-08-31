#!/usr/bin/env python3
"""
Analytics Dashboard Engine for Vanta Ledger
==========================================

Provides comprehensive analytics and insights across all 29 companies:
- Financial performance metrics
- Document processing analytics
- Network analysis insights
- Business intelligence dashboards
- Risk assessment reports

Author: Vanta Ledger Team
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from sqlalchemy import create_engine, text, func
from pymongo import MongoClient
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AnalyticsDashboardEngine:
    """Comprehensive analytics engine for Vanta Ledger"""
    
    def __init__(self, postgres_engine, mongo_client):
        self.postgres_engine = postgres_engine
        self.mongo_client = mongo_client
        self.mongo_db = mongo_client.vanta_ledger
        self.analytics_data = {}
        
    def get_financial_analytics(self) -> Dict[str, Any]:
        """Get comprehensive financial analytics"""
        try:
            with self.postgres_engine.begin() as conn:
                # Get financial summary
                financial_summary = conn.execute(text("""
                    SELECT 
                        c.name as company_name,
                        c.company_type,
                        COUNT(le.id) as transaction_count,
                        SUM(CASE WHEN le.entry_type = 'income' THEN le.amount ELSE 0 END) as total_income,
                        SUM(CASE WHEN le.entry_type = 'expense' THEN le.amount ELSE 0 END) as total_expenses,
                        SUM(CASE WHEN le.entry_type = 'transfer' THEN le.amount ELSE 0 END) as total_transfers,
                        AVG(le.amount) as avg_transaction_amount,
                        MIN(le.transaction_date) as first_transaction,
                        MAX(le.transaction_date) as last_transaction
                    FROM companies c
                    LEFT JOIN ledger_entries le ON c.id = le.company_id
                    WHERE c.status = 'active'
                    GROUP BY c.id, c.name, c.company_type
                    ORDER BY total_income DESC
                """)).fetchall()
                
                # Get monthly trends
                monthly_trends = conn.execute(text("""
                    SELECT 
                        DATE_TRUNC('month', le.transaction_date) as month,
                        SUM(CASE WHEN le.entry_type = 'income' THEN le.amount ELSE 0 END) as income,
                        SUM(CASE WHEN le.entry_type = 'expense' THEN le.amount ELSE 0 END) as expenses,
                        COUNT(le.id) as transaction_count
                    FROM ledger_entries le
                    WHERE le.transaction_date >= CURRENT_DATE - INTERVAL '12 months'
                    GROUP BY DATE_TRUNC('month', le.transaction_date)
                    ORDER BY month
                """)).fetchall()
                
                # Get top transactions
                top_transactions = conn.execute(text("""
                    SELECT 
                        c.name as company_name,
                        le.entry_type,
                        le.amount,
                        le.description,
                        le.transaction_date
                    FROM ledger_entries le
                    JOIN companies c ON le.company_id = c.id
                    ORDER BY le.amount DESC
                    LIMIT 20
                """)).fetchall()
            
            # Process financial data
            financial_data = {
                'summary': [],
                'monthly_trends': [],
                'top_transactions': [],
                'metrics': {
                    'total_companies': len(financial_summary),
                    'total_transactions': sum(row[2] for row in financial_summary),
                    'total_income': sum(row[3] for row in financial_summary),
                    'total_expenses': sum(row[4] for row in financial_summary),
                    'net_income': sum(row[3] for row in financial_summary) - sum(row[4] for row in financial_summary)
                }
            }
            
            # Process summary data
            for row in financial_summary:
                financial_data['summary'].append({
                    'company_name': row[0],
                    'company_type': row[1],
                    'transaction_count': row[2],
                    'total_income': row[3],
                    'total_expenses': row[4],
                    'total_transfers': row[5],
                    'avg_transaction_amount': row[6],
                    'net_income': row[3] - row[4],
                    'first_transaction': row[7],
                    'last_transaction': row[8]
                })
            
            # Process monthly trends
            for row in monthly_trends:
                financial_data['monthly_trends'].append({
                    'month': row[0].strftime('%Y-%m'),
                    'income': row[1],
                    'expenses': row[2],
                    'transaction_count': row[3],
                    'net_income': row[1] - row[2]
                })
            
            # Process top transactions
            for row in top_transactions:
                financial_data['top_transactions'].append({
                    'company_name': row[0],
                    'entry_type': row[1],
                    'amount': row[2],
                    'description': row[3],
                    'transaction_date': row[4].strftime('%Y-%m-%d')
                })
            
            self.analytics_data['financial'] = financial_data
            logger.info("✅ Financial analytics generated successfully")
            
            return financial_data
            
        except Exception as e:
            logger.error(f"❌ Financial analytics generation failed: {e}")
            return {}
    
    def get_document_analytics(self) -> Dict[str, Any]:
        """Get comprehensive document processing analytics"""
        try:
            with self.postgres_engine.begin() as conn:
                # Get document summary by company
                document_summary = conn.execute(text("""
                    SELECT 
                        c.name as company_name,
                        c.company_type,
                        COUNT(d.id) as total_documents,
                        COUNT(CASE WHEN d.processing_status = 'processed' THEN 1 END) as processed_documents,
                        COUNT(CASE WHEN d.processing_status = 'pending' THEN 1 END) as pending_documents,
                        COUNT(CASE WHEN d.processing_status = 'error' THEN 1 END) as error_documents,
                        SUM(d.file_size) as total_size_bytes
                    FROM companies c
                    LEFT JOIN documents d ON c.id = d.company_id
                    WHERE c.status = 'active'
                    GROUP BY c.id, c.name, c.company_type
                    ORDER BY total_documents DESC
                """)).fetchall()
                
                # Get document types distribution
                document_types = conn.execute(text("""
                    SELECT 
                        document_type,
                        COUNT(*) as count,
                        AVG(file_size) as avg_size
                    FROM documents
                    WHERE processing_status = 'processed'
                    GROUP BY document_type
                    ORDER BY count DESC
                """)).fetchall()
                
                # Get document categories distribution
                document_categories = conn.execute(text("""
                    SELECT 
                        document_category,
                        COUNT(*) as count
                    FROM documents
                    WHERE processing_status = 'processed'
                    GROUP BY document_category
                    ORDER BY count DESC
                """)).fetchall()
                
                # Get processing timeline
                processing_timeline = conn.execute(text("""
                    SELECT 
                        DATE_TRUNC('day', upload_date) as day,
                        COUNT(*) as documents_uploaded,
                        COUNT(CASE WHEN processing_status = 'processed' THEN 1 END) as documents_processed
                    FROM documents
                    WHERE upload_date >= CURRENT_DATE - INTERVAL '30 days'
                    GROUP BY DATE_TRUNC('day', upload_date)
                    ORDER BY day
                """)).fetchall()
            
            # Process document data
            document_data = {
                'summary': [],
                'document_types': [],
                'document_categories': [],
                'processing_timeline': [],
                'metrics': {
                    'total_documents': sum(row[2] for row in document_summary),
                    'processed_documents': sum(row[3] for row in document_summary),
                    'pending_documents': sum(row[4] for row in document_summary),
                    'error_documents': sum(row[5] for row in document_summary),
                    'total_size_gb': sum(row[6] for row in document_summary) / (1024**3),
                    'success_rate': (sum(row[3] for row in document_summary) / sum(row[2] for row in document_summary) * 100) if sum(row[2] for row in document_summary) > 0 else 0
                }
            }
            
            # Process summary data
            for row in document_summary:
                document_data['summary'].append({
                    'company_name': row[0],
                    'company_type': row[1],
                    'total_documents': row[2],
                    'processed_documents': row[3],
                    'pending_documents': row[4],
                    'error_documents': row[5],
                    'total_size_mb': row[6] / (1024**2) if row[6] else 0,
                    'success_rate': (row[3] / row[2] * 100) if row[2] > 0 else 0
                })
            
            # Process document types
            for row in document_types:
                document_data['document_types'].append({
                    'document_type': row[0],
                    'count': row[1],
                    'avg_size_mb': row[2] / (1024**2) if row[2] else 0
                })
            
            # Process document categories
            for row in document_categories:
                document_data['document_categories'].append({
                    'category': row[0],
                    'count': row[1]
                })
            
            # Process timeline
            for row in processing_timeline:
                document_data['processing_timeline'].append({
                    'day': row[0].strftime('%Y-%m-%d'),
                    'documents_uploaded': row[1],
                    'documents_processed': row[2],
                    'processing_rate': (row[2] / row[1] * 100) if row[1] > 0 else 0
                })
            
            self.analytics_data['documents'] = document_data
            logger.info("✅ Document analytics generated successfully")
            
            return document_data
            
        except Exception as e:
            logger.error(f"❌ Document analytics generation failed: {e}")
            return {}
    
    def get_network_analytics(self) -> Dict[str, Any]:
        """Get network analysis insights"""
        try:
            # Get latest network analysis from MongoDB
            network_collection = self.mongo_db.network_analysis
            latest_analysis = network_collection.find_one(
                sort=[('analysis_date', -1)]
            )
            
            if not latest_analysis:
                logger.warning("No network analysis data found")
                return {}
            
            network_data = {
                'network_stats': latest_analysis.get('network_stats', {}),
                'insights': latest_analysis.get('results', {}).get('insights', {}),
                'risk_assessment': latest_analysis.get('results', {}).get('risk_assessment', {}),
                'centrality_metrics': latest_analysis.get('results', {}).get('centrality_metrics', {}),
                'relationship_patterns': latest_analysis.get('results', {}).get('relationship_patterns', {})
            }
            
            # Get company relationship summary from PostgreSQL
            with self.postgres_engine.begin() as conn:
                relationship_summary = conn.execute(text("""
                    SELECT 
                        c.name as company_name,
                        c.company_type,
                        COUNT(cr.id) as total_relationships,
                        COUNT(CASE WHEN cr.relationship_type = 'family_connection' THEN 1 END) as family_connections,
                        COUNT(CASE WHEN cr.relationship_type = 'business_partnership' THEN 1 END) as business_partnerships,
                        COUNT(CASE WHEN cr.relationship_type = 'subsidiary_connection' THEN 1 END) as subsidiary_connections,
                        AVG(cr.relationship_strength) as avg_relationship_strength
                    FROM companies c
                    LEFT JOIN company_relationships cr ON c.id = cr.company_a_id
                    WHERE c.status = 'active'
                    GROUP BY c.id, c.name, c.company_type
                    ORDER BY total_relationships DESC
                """)).fetchall()
            
            # Process relationship data
            relationship_data = []
            for row in relationship_summary:
                relationship_data.append({
                    'company_name': row[0],
                    'company_type': row[1],
                    'total_relationships': row[2],
                    'family_connections': row[3],
                    'business_partnerships': row[4],
                    'subsidiary_connections': row[5],
                    'avg_relationship_strength': row[6]
                })
            
            network_data['relationship_summary'] = relationship_data
            
            self.analytics_data['network'] = network_data
            logger.info("✅ Network analytics generated successfully")
            
            return network_data
            
        except Exception as e:
            logger.error(f"❌ Network analytics generation failed: {e}")
            return {}
    
    def get_business_intelligence(self) -> Dict[str, Any]:
        """Get comprehensive business intelligence insights"""
        try:
            bi_data = {
                'key_metrics': {},
                'trends': {},
                'insights': [],
                'recommendations': [],
                'alerts': []
            }
            
            # Calculate key business metrics
            if 'financial' in self.analytics_data:
                financial = self.analytics_data['financial']
                bi_data['key_metrics']['financial'] = {
                    'total_revenue': financial['metrics']['total_income'],
                    'total_expenses': financial['metrics']['total_expenses'],
                    'net_profit': financial['metrics']['net_income'],
                    'profit_margin': (financial['metrics']['net_income'] / financial['metrics']['total_income'] * 100) if financial['metrics']['total_income'] > 0 else 0,
                    'avg_transaction_value': financial['metrics']['total_income'] / financial['metrics']['total_transactions'] if financial['metrics']['total_transactions'] > 0 else 0
                }
            
            if 'documents' in self.analytics_data:
                documents = self.analytics_data['documents']
                bi_data['key_metrics']['documents'] = {
                    'total_documents': documents['metrics']['total_documents'],
                    'processing_success_rate': documents['metrics']['success_rate'],
                    'total_storage_gb': documents['metrics']['total_size_gb'],
                    'documents_per_company': documents['metrics']['total_documents'] / documents['metrics']['total_companies'] if documents['metrics']['total_companies'] > 0 else 0
                }
            
            # Generate business insights
            insights = []
            
            # Financial insights
            if 'financial' in self.analytics_data:
                financial = self.analytics_data['financial']
                
                # Top performing companies
                top_companies = sorted(financial['summary'], key=lambda x: x['net_income'], reverse=True)[:5]
                insights.append({
                    'type': 'top_performers',
                    'title': 'Top Performing Companies',
                    'description': 'Companies with highest net income',
                    'data': [{'name': c['company_name'], 'net_income': c['net_income']} for c in top_companies]
                })
                
                # Revenue trends
                if financial['monthly_trends']:
                    recent_trend = financial['monthly_trends'][-3:]
                    if len(recent_trend) >= 2:
                        growth_rate = ((recent_trend[-1]['income'] - recent_trend[0]['income']) / recent_trend[0]['income'] * 100) if recent_trend[0]['income'] > 0 else 0
                        insights.append({
                            'type': 'revenue_growth',
                            'title': 'Revenue Growth Trend',
                            'description': f'Revenue growth over last 3 months: {growth_rate:.1f}%',
                            'data': {'growth_rate': growth_rate}
                        })
            
            # Document insights
            if 'documents' in self.analytics_data:
                documents = self.analytics_data['documents']
                
                # Most active companies
                active_companies = sorted(documents['summary'], key=lambda x: x['total_documents'], reverse=True)[:5]
                insights.append({
                    'type': 'most_active',
                    'title': 'Most Active Companies',
                    'description': 'Companies with most documents processed',
                    'data': [{'name': c['company_name'], 'documents': c['total_documents']} for c in active_companies]
                })
            
            bi_data['insights'] = insights
            
            # Generate recommendations
            recommendations = []
            
            # Financial recommendations
            if 'financial' in self.analytics_data:
                financial = self.analytics_data['financial']
                
                # High expense companies
                high_expense_companies = [c for c in financial['summary'] if c['total_expenses'] > c['total_income']]
                if high_expense_companies:
                    recommendations.append({
                        'type': 'cost_optimization',
                        'priority': 'high',
                        'title': 'Cost Optimization Needed',
                        'description': f'{len(high_expense_companies)} companies have expenses exceeding income',
                        'action_items': ['Review expense categories', 'Implement cost controls', 'Optimize operations']
                    })
            
            # Document processing recommendations
            if 'documents' in self.analytics_data:
                documents = self.analytics_data['documents']
                
                if documents['metrics']['success_rate'] < 90:
                    recommendations.append({
                        'type': 'processing_improvement',
                        'priority': 'medium',
                        'title': 'Document Processing Improvement',
                        'description': f'Processing success rate is {documents["metrics"]["success_rate"]:.1f}%',
                        'action_items': ['Review error logs', 'Improve OCR accuracy', 'Update document templates']
                    })
            
            bi_data['recommendations'] = recommendations
            
            # Generate alerts
            alerts = []
            
            # Financial alerts
            if 'financial' in self.analytics_data:
                financial = self.analytics_data['financial']
                
                # Negative cash flow alert
                if financial['metrics']['net_income'] < 0:
                    alerts.append({
                        'type': 'financial_alert',
                        'severity': 'high',
                        'title': 'Negative Cash Flow',
                        'description': 'Overall net income is negative',
                        'timestamp': datetime.now()
                    })
            
            bi_data['alerts'] = alerts
            
            self.analytics_data['business_intelligence'] = bi_data
            logger.info("✅ Business intelligence generated successfully")
            
            return bi_data
            
        except Exception as e:
            logger.error(f"❌ Business intelligence generation failed: {e}")
            return {}
    
    def generate_dashboard_data(self) -> Dict[str, Any]:
        """Generate complete dashboard data"""
        try:
            logger.info("🔍 Generating comprehensive dashboard data...")
            
            # Generate all analytics
            self.get_financial_analytics()
            self.get_document_analytics()
            self.get_network_analytics()
            self.get_business_intelligence()
            
            # Create dashboard summary
            dashboard_data = {
                'generated_at': datetime.now(),
                'analytics': self.analytics_data,
                'summary': {
                    'total_companies': 29,
                    'total_documents': self.analytics_data.get('documents', {}).get('metrics', {}).get('total_documents', 0),
                    'total_transactions': self.analytics_data.get('financial', {}).get('metrics', {}).get('total_transactions', 0),
                    'total_revenue': self.analytics_data.get('financial', {}).get('metrics', {}).get('total_income', 0),
                    'processing_success_rate': self.analytics_data.get('documents', {}).get('metrics', {}).get('success_rate', 0)
                }
            }
            
            # Save dashboard data to database
            with self.postgres_engine.begin() as conn:
                conn.execute(text("""
                    INSERT INTO analytics_dashboard 
                    (dashboard_name, dashboard_type, data_sources, metrics, filters)
                    VALUES (:name, :type, :sources, :metrics, :filters)
                """), {
                    'name': 'Vanta Ledger Comprehensive Dashboard',
                    'type': 'comprehensive',
                    'sources': json.dumps(['financial', 'documents', 'network', 'business_intelligence']),
                    'metrics': json.dumps(dashboard_data['summary']),
                    'filters': json.dumps({'date_range': 'all', 'companies': 'all'})
                })
            
            # Save to MongoDB
            analytics_collection = self.mongo_db.analytics
            analytics_collection.insert_one({
                'dashboard_data': dashboard_data,
                'timestamp': datetime.now()
            })
            
            logger.info("✅ Dashboard data generated and saved successfully")
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"❌ Dashboard data generation failed: {e}")
            raise
    
    def create_visualizations(self, output_path: str = "analytics_visualizations"):
        """Create visualization charts and graphs"""
        try:
            os.makedirs(output_path, exist_ok=True)
            
            # Financial visualizations
            if 'financial' in self.analytics_data:
                financial = self.analytics_data['financial']
                
                # Company revenue comparison
                if financial['summary']:
                    df = pd.DataFrame(financial['summary'])
                    fig = px.bar(df.head(10), x='company_name', y='total_income', 
                               title='Top 10 Companies by Revenue')
                    fig.write_html(f"{output_path}/company_revenue.html")
                
                # Monthly trends
                if financial['monthly_trends']:
                    df = pd.DataFrame(financial['monthly_trends'])
                    fig = px.line(df, x='month', y=['income', 'expenses', 'net_income'],
                                title='Monthly Financial Trends')
                    fig.write_html(f"{output_path}/monthly_trends.html")
            
            # Document visualizations
            if 'documents' in self.analytics_data:
                documents = self.analytics_data['documents']
                
                # Document types distribution
                if documents['document_types']:
                    df = pd.DataFrame(documents['document_types'])
                    fig = px.pie(df, values='count', names='document_type',
                               title='Document Types Distribution')
                    fig.write_html(f"{output_path}/document_types.html")
                
                # Processing success rate by company
                if documents['summary']:
                    df = pd.DataFrame(documents['summary'])
                    fig = px.bar(df, x='company_name', y='success_rate',
                               title='Document Processing Success Rate by Company')
                    fig.write_html(f"{output_path}/processing_success.html")
            
            logger.info(f"✅ Visualizations created in {output_path}")
            
        except Exception as e:
            logger.error(f"❌ Visualization creation failed: {e}")

def main():
    """Main function to run analytics dashboard"""
    try:
        # This would be called from the main application
        # For now, we'll just show the structure
        print("Analytics Dashboard Engine Ready")
        print("Use this class to generate comprehensive business analytics")
        
    except Exception as e:
        logger.error(f"Analytics dashboard failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 