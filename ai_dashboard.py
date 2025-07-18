#!/usr/bin/env python3
"""
Real-time AI Dashboard for Vanta Ledger
=======================================

A live dashboard showing document analysis progress, insights, and alerts.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import requests
from requests.auth import HTTPBasicAuth
from collections import defaultdict, Counter
import statistics

class AIDashboard:
    """Real-time dashboard for document AI analysis"""
    
    def __init__(self, paperless_url: str, username: str, password: str):
        self.paperless_url = paperless_url.rstrip('/')
        self.username = username
        self.password = password
        self.token = None
        self.analysis_history = []
        self.alerts = []
        
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
                return True
            return False
        except Exception:
            return False
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data"""
        if not self.token:
            return {"error": "Not authenticated"}
        
        headers = {'Authorization': f'Token {self.token}'}
        
        try:
            # Get document statistics
            response = requests.get(f"{self.paperless_url}/api/documents/", headers=headers)
            if response.status_code != 200:
                return {"error": "Failed to fetch documents"}
            
            data = response.json()
            total_docs = data.get('count', 0)
            
            # Get recent documents
            recent_response = requests.get(
                f"{self.paperless_url}/api/documents/",
                headers=headers,
                params={'ordering': '-created', 'page_size': 10}
            )
            
            recent_docs = []
            if recent_response.status_code == 200:
                recent_data = recent_response.json()
                recent_docs = recent_data.get('results', [])
            
            # Calculate processing statistics
            processing_stats = self._calculate_processing_stats(recent_docs)
            
            # Generate alerts
            alerts = self._generate_alerts(recent_docs, processing_stats)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'total_documents': total_docs,
                'recent_documents': recent_docs[:5],
                'processing_stats': processing_stats,
                'alerts': alerts,
                'system_health': self._check_system_health()
            }
            
        except Exception as e:
            return {"error": f"Dashboard error: {str(e)}"}
    
    def _calculate_processing_stats(self, recent_docs: List[Dict]) -> Dict[str, Any]:
        """Calculate processing statistics"""
        if not recent_docs:
            return {}
        
        # Document type distribution
        doc_types = Counter()
        for doc in recent_docs:
            doc_type = doc.get('document_type', 'unknown')
            doc_types[doc_type] += 1
        
        # Processing time analysis
        processing_times = []
        for doc in recent_docs:
            created = doc.get('created')
            if created:
                try:
                    created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                    processing_times.append((datetime.now() - created_dt).total_seconds())
                except:
                    pass
        
        avg_processing_time = statistics.mean(processing_times) if processing_times else 0
        
        # File size analysis
        file_sizes = [doc.get('file_size', 0) for doc in recent_docs if doc.get('file_size')]
        avg_file_size = statistics.mean(file_sizes) if file_sizes else 0
        
        return {
            'document_types': dict(doc_types),
            'avg_processing_time_seconds': avg_processing_time,
            'avg_file_size_bytes': avg_file_size,
            'total_processed_today': len(recent_docs)
        }
    
    def _generate_alerts(self, recent_docs: List[Dict], stats: Dict) -> List[Dict]:
        """Generate system alerts"""
        alerts = []
        
        # Check for processing delays
        if stats.get('avg_processing_time_seconds', 0) > 300:  # 5 minutes
            alerts.append({
                'type': 'warning',
                'message': 'Document processing is taking longer than expected',
                'timestamp': datetime.now().isoformat()
            })
        
        # Check for large files
        large_files = [doc for doc in recent_docs if doc.get('file_size', 0) > 10 * 1024 * 1024]  # 10MB
        if large_files:
            alerts.append({
                'type': 'info',
                'message': f'Found {len(large_files)} large files that may need special processing',
                'timestamp': datetime.now().isoformat()
            })
        
        # Check for failed documents
        failed_docs = [doc for doc in recent_docs if doc.get('status') == 'failed']
        if failed_docs:
            alerts.append({
                'type': 'error',
                'message': f'Found {len(failed_docs)} documents that failed processing',
                'timestamp': datetime.now().isoformat()
            })
        
        return alerts
    
    def _check_system_health(self) -> Dict[str, Any]:
        """Check overall system health"""
        try:
            # Check Paperless-ngx API
            response = requests.get(f"{self.paperless_url}/api/", timeout=5)
            api_healthy = response.status_code == 200
            
            # Check disk space (simplified)
            import shutil
            disk_usage = shutil.disk_usage('/')
            disk_free_gb = disk_usage.free / (1024**3)
            
            return {
                'api_healthy': api_healthy,
                'disk_free_gb': disk_free_gb,
                'last_check': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'api_healthy': False,
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
    
    def display_dashboard(self, data: Dict[str, Any]):
        """Display the dashboard in terminal"""
        print("\n" + "="*80)
        print("🤖 VANTA LEDGER - AI DOCUMENT ANALYSIS DASHBOARD")
        print("="*80)
        
        if 'error' in data:
            print(f"❌ Error: {data['error']}")
            return
        
        # System Status
        health = data.get('system_health', {})
        print(f"📊 System Status:")
        print(f"   API Health: {'✅ Healthy' if health.get('api_healthy') else '❌ Unhealthy'}")
        print(f"   Disk Free: {health.get('disk_free_gb', 0):.1f} GB")
        print(f"   Last Check: {health.get('last_check', 'Unknown')}")
        
        # Document Statistics
        print(f"\n📄 Document Statistics:")
        print(f"   Total Documents: {data.get('total_documents', 0):,}")
        print(f"   Processed Today: {data.get('processing_stats', {}).get('total_processed_today', 0)}")
        
        # Document Types
        doc_types = data.get('processing_stats', {}).get('document_types', {})
        if doc_types:
            print(f"\n📁 Document Types (Recent):")
            for doc_type, count in doc_types.items():
                print(f"   {doc_type}: {count}")
        
        # Processing Performance
        stats = data.get('processing_stats', {})
        avg_time = stats.get('avg_processing_time_seconds', 0)
        avg_size = stats.get('avg_file_size_bytes', 0)
        
        print(f"\n⚡ Processing Performance:")
        print(f"   Average Processing Time: {avg_time:.1f} seconds")
        print(f"   Average File Size: {avg_size / 1024 / 1024:.1f} MB")
        
        # Recent Documents
        recent_docs = data.get('recent_documents', [])
        if recent_docs:
            print(f"\n🕒 Recent Documents:")
            for i, doc in enumerate(recent_docs[:5], 1):
                title = doc.get('title', 'Untitled')[:50]
                created = doc.get('created', 'Unknown')
                doc_type = doc.get('document_type', 'unknown')
                print(f"   {i}. {title} ({doc_type}) - {created}")
        
        # Alerts
        alerts = data.get('alerts', [])
        if alerts:
            print(f"\n🚨 Alerts:")
            for alert in alerts:
                icon = "⚠️" if alert['type'] == 'warning' else "❌" if alert['type'] == 'error' else "ℹ️"
                print(f"   {icon} {alert['message']}")
        else:
            print(f"\n✅ No alerts - System running smoothly")
        
        print(f"\n🕐 Last Updated: {data.get('timestamp', 'Unknown')}")
        print("="*80)
    
    async def run_live_dashboard(self, refresh_interval: int = 30):
        """Run live dashboard with auto-refresh"""
        print("🚀 Starting Live AI Dashboard...")
        print("Press Ctrl+C to stop")
        
        if not await self.authenticate():
            print("❌ Authentication failed")
            return
        
        try:
            while True:
                data = self.get_dashboard_data()
                self.display_dashboard(data)
                
                print(f"\n🔄 Refreshing in {refresh_interval} seconds...")
                await asyncio.sleep(refresh_interval)
                
        except KeyboardInterrupt:
            print("\n👋 Dashboard stopped by user")
        except Exception as e:
            print(f"\n❌ Dashboard error: {e}")

async def main():
    """Main function to run the dashboard"""
    dashboard = AIDashboard(
        paperless_url="http://localhost:8000",
        username="Mike",
        password="106730!@#"
    )
    
    await dashboard.run_live_dashboard()

if __name__ == "__main__":
    asyncio.run(main()) 