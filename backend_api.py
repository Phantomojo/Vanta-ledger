#!/usr/bin/env python3
"""
Vanta Ledger Backend API
Connects React web dashboard with Paperless-ngx data and AI insights
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json
import os
from datetime import datetime, timedelta
import sqlite3
from typing import Dict, List, Any
import asyncio
import threading
import time

# Import the integration module
from integrate_backend_data import DataIntegrator, PaperlessIntegration, DatabaseManager, AIProcessor

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configuration
PAPERLESS_URL = "http://localhost:8000"
PAPERLESS_USERNAME = "Mike"
PAPERLESS_PASSWORD = "106730!@#"
DATABASE_PATH = "vanta_ledger.db"

# Initialize integration components
paperless_api = PaperlessIntegration(PAPERLESS_URL, PAPERLESS_USERNAME, PAPERLESS_PASSWORD)
db = DatabaseManager(DATABASE_PATH)
ai_processor = AIProcessor()
integrator = DataIntegrator(PAPERLESS_URL, PAPERLESS_USERNAME, PAPERLESS_PASSWORD, DATABASE_PATH)

# Start data synchronization
integrator.start_sync()

# Mock data for development (when Paperless-ngx is not running)
MOCK_DATA = {
    'documents': [
        {
            'id': 1,
            'title': 'Invoice #INV-2024-001',
            'document_type': 'invoice',
            'created': '2024-07-14T10:30:00Z',
            'amount': 12450.00,
            'vendor': 'Construction Co. Ltd',
            'status': 'processed',
            'ai_analyzed': True
        },
        {
            'id': 2,
            'title': 'Contract #CTR-2024-089',
            'document_type': 'contract',
            'created': '2024-07-14T09:15:00Z',
            'amount': 250000.00,
            'vendor': 'Skyline Developers',
            'status': 'pending_review',
            'ai_analyzed': True,
            'risk_score': 0.87
        }
    ],
    'projects': [
        {'name': 'Skyline Tower', 'status': 'Active', 'docs': 847, 'value': 2400000},
        {'name': 'Riverside Plaza', 'status': 'Planning', 'docs': 234, 'value': 1800000},
        {'name': 'Tech Campus', 'status': 'Completed', 'docs': 1156, 'value': 3200000},
        {'name': 'Green Heights', 'status': 'Active', 'docs': 432, 'value': 1100000},
        {'name': 'Metro Station', 'status': 'On Hold', 'docs': 89, 'value': 850000},
        {'name': 'Shopping Mall', 'status': 'Active', 'docs': 567, 'value': 1900000}
    ],
    'analytics': {
        'total_documents': 3150,
        'ai_processed': 2847,
        'active_projects': 12,
        'pending_review': 89,
        'processing_today': 47,
        'processing_week': 312,
        'processing_month': 1247,
        'ai_accuracy': 94.2,
        'processing_speed': 2.3,
        'success_rate': 98.7
    }
}

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check Paperless-ngx connection
        paperless_connected = paperless_api.get_documents(limit=1) is not None
        
        # Check database connection
        db_connected = True
        try:
            db.get_latest_analytics()
        except:
            db_connected = False
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'paperless_connected': paperless_connected,
            'database_connected': db_connected,
            'integration_running': integrator.is_running
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Get dashboard data"""
    try:
        # Try to get real data from integration
        dashboard_data = integrator.get_dashboard_data()
        
        if dashboard_data and dashboard_data.get('analytics'):
            # Use real data
            return jsonify({
                'analytics': dashboard_data['analytics'],
                'recent_activity': dashboard_data.get('recent_activity', [])
            })
        else:
            # Use mock data as fallback
            return jsonify({
                'analytics': MOCK_DATA['analytics'],
                'recent_activity': [
                    {
                        'id': 1,
                        'type': 'document_processed',
                        'title': 'Invoice #INV-2024-001 processed',
                        'timestamp': '2 minutes ago',
                        'status': 'AI Analyzed'
                    },
                    {
                        'id': 2,
                        'type': 'project_updated',
                        'title': 'Project "Skyline Tower" updated',
                        'timestamp': '15 minutes ago',
                        'status': 'Updated'
                    },
                    {
                        'id': 3,
                        'type': 'ai_analysis',
                        'title': 'Contract analysis completed',
                        'timestamp': '1 hour ago',
                        'status': 'Risk Detected'
                    }
                ]
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """Get documents list"""
    try:
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Try to get real documents from integration
        dashboard_data = integrator.get_dashboard_data()
        
        if dashboard_data and dashboard_data.get('documents'):
            documents = dashboard_data['documents']
            return jsonify({
                'documents': documents[offset:offset+limit],
                'total': len(documents),
                'limit': limit,
                'offset': offset
            })
        else:
            # Use mock data
            return jsonify({
                'documents': MOCK_DATA['documents'],
                'total': len(MOCK_DATA['documents']),
                'limit': limit,
                'offset': offset
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Get projects list"""
    try:
        # Try to get real projects from integration
        dashboard_data = integrator.get_dashboard_data()
        
        if dashboard_data and dashboard_data.get('projects'):
            return jsonify({'projects': dashboard_data['projects']})
        else:
            # Use mock data
            return jsonify({'projects': MOCK_DATA['projects']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data"""
    try:
        # Try to get real analytics from integration
        dashboard_data = integrator.get_dashboard_data()
        
        if dashboard_data and dashboard_data.get('analytics'):
            return jsonify({'analytics': dashboard_data['analytics']})
        else:
            # Use mock data
            return jsonify({'analytics': MOCK_DATA['analytics']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai-insights', methods=['GET'])
def get_ai_insights():
    """Get AI insights"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        # Try to get real insights from database
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, document_id, insight_type, insight_data, risk_score, created_at
                FROM ai_insights
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            insights = []
            for row in cursor.fetchall():
                insights.append({
                    'id': row[0],
                    'document_id': row[1],
                    'insight_type': row[2],
                    'insight_data': json.loads(row[3]),
                    'risk_score': row[4],
                    'created_at': row[5]
                })
            conn.close()
            
            if insights:
                return jsonify({'insights': insights})
        except:
            pass
        
        # Use mock data as fallback
        mock_insights = [
            {
                'id': 1,
                'document_id': 2,
                'insight_type': 'risk_analysis',
                'insight_data': {
                    'risk_level': 'high',
                    'risk_factors': ['payment_terms', 'penalty_clauses'],
                    'recommendations': ['Review payment terms', 'Negotiate penalties']
                },
                'risk_score': 0.87,
                'created_at': '2024-07-14T09:15:00Z'
            },
            {
                'id': 2,
                'document_id': 1,
                'insight_type': 'financial_analysis',
                'insight_data': {
                    'amount': 12450.00,
                    'currency': 'USD',
                    'payment_status': 'pending',
                    'due_date': '2024-08-14'
                },
                'risk_score': 0.25,
                'created_at': '2024-07-14T10:30:00Z'
            }
        ]
        return jsonify({'insights': mock_insights})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents/<int:doc_id>', methods=['GET'])
def get_document(doc_id):
    """Get specific document"""
    try:
        # Try to get from Paperless-ngx
        try:
            doc_data = paperless_api.get_document(doc_id)
            if doc_data:
                return jsonify(doc_data)
        except:
            pass
        
        # Return mock data
        return jsonify(MOCK_DATA['documents'][0])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync', methods=['POST'])
def trigger_sync():
    """Trigger manual data synchronization"""
    try:
        integrator.sync_all_data()
        return jsonify({
            'status': 'success',
            'message': 'Data synchronization completed',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    try:
        return jsonify({
            'paperless_connected': paperless_api.get_documents(limit=1) is not None,
            'database_connected': True,
            'integration_running': integrator.is_running,
            'last_sync': integrator.paperless.last_sync,
            'sync_interval': integrator.sync_interval,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Vanta Ledger Backend API...")
    print(f"📊 Paperless-ngx URL: {PAPERLESS_URL}")
    print(f"💾 Database: {DATABASE_PATH}")
    print("🌐 API will be available at: http://localhost:5000")
    print("🔄 Data integration is running in background...")
    
    app.run(host='0.0.0.0', port=5000, debug=True) 