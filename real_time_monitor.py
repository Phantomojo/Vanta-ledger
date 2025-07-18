#!/usr/bin/env python3
"""
Real-Time Monitoring System for Vanta Ledger
============================================

Comprehensive monitoring of Paperless-ngx processing, AI system status,
and system resources while allowing continued development.
"""

import asyncio
import json
import time
import psutil
import requests
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import threading
import queue
import os

@dataclass
class SystemMetrics:
    """System performance metrics"""
    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    disk_usage_percent: float
    disk_free_gb: float
    network_io: Dict[str, float]
    timestamp: datetime

@dataclass
class PaperlessMetrics:
    """Paperless-ngx processing metrics"""
    total_documents: int
    documents_processed_today: int
    processing_rate: float  # docs per hour
    current_status: str
    last_processed: Optional[datetime]
    errors_count: int
    duplicates_count: int
    timestamp: datetime

@dataclass
class AIMetrics:
    """AI system metrics"""
    ollama_running: bool
    llama2_available: bool
    model_loaded: bool
    response_time: float
    memory_usage_gb: float
    timestamp: datetime

class RealTimeMonitor:
    """Real-time monitoring system"""
    
    def __init__(self, paperless_url: str = "http://localhost:8000", 
                 ollama_url: str = "http://localhost:11434"):
        self.paperless_url = paperless_url
        self.ollama_url = ollama_url
        self.metrics_queue = queue.Queue()
        self.running = False
        self.monitoring_thread = None
        
    def start_monitoring(self):
        """Start the monitoring system in background"""
        self.running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        print("🔍 Real-time monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring system"""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        print("🛑 Real-time monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Collect all metrics
                system_metrics = self._get_system_metrics()
                paperless_metrics = self._get_paperless_metrics()
                ai_metrics = self._get_ai_metrics()
                
                # Store in queue for display
                self.metrics_queue.put({
                    'system': system_metrics,
                    'paperless': paperless_metrics,
                    'ai': ai_metrics,
                    'timestamp': datetime.now()
                })
                
                time.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                print(f"⚠️ Monitoring error: {e}")
                time.sleep(30)  # Wait longer on error
    
    def _get_system_metrics(self) -> SystemMetrics:
        """Get system performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_available_gb=memory.available / (1024**3),
                disk_usage_percent=disk.percent,
                disk_free_gb=disk.free / (1024**3),
                network_io={
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv
                },
                timestamp=datetime.now()
            )
        except Exception as e:
            print(f"Error getting system metrics: {e}")
            return SystemMetrics(0, 0, 0, 0, 0, {}, datetime.now())
    
    def _get_paperless_metrics(self) -> PaperlessMetrics:
        """Get Paperless-ngx processing metrics"""
        try:
            # Check if Paperless is running
            response = requests.get(f"{self.paperless_url}/api/", timeout=5)
            if response.status_code != 200:
                return PaperlessMetrics(0, 0, 0, "unavailable", None, 0, 0, datetime.now())
            
            # Get document count
            docs_response = requests.get(f"{self.paperless_url}/api/documents/", timeout=5)
            total_docs = 0
            if docs_response.status_code == 200:
                data = docs_response.json()
                total_docs = data.get('count', 0)
            
            # Get recent documents for processing rate
            recent_response = requests.get(
                f"{self.paperless_url}/api/documents/",
                params={'ordering': '-created', 'page_size': 50},
                timeout=5
            )
            
            docs_processed_today = 0
            processing_rate = 0
            last_processed = None
            errors_count = 0
            duplicates_count = 0
            
            if recent_response.status_code == 200:
                recent_docs = recent_response.json().get('results', [])
                today = datetime.now().date()
                
                for doc in recent_docs:
                    created = doc.get('created')
                    if created:
                        try:
                            doc_date = datetime.fromisoformat(created.replace('Z', '+00:00')).date()
                            if doc_date == today:
                                docs_processed_today += 1
                        except:
                            pass
                
                # Calculate processing rate (docs per hour)
                if recent_docs:
                    first_doc_time = recent_docs[0].get('created')
                    if first_doc_time:
                        try:
                            first_dt = datetime.fromisoformat(first_doc_time.replace('Z', '+00:00'))
                            hours_elapsed = (datetime.now() - first_dt).total_seconds() / 3600
                            if hours_elapsed > 0:
                                processing_rate = len(recent_docs) / hours_elapsed
                        except:
                            pass
            
            return PaperlessMetrics(
                total_documents=total_docs,
                documents_processed_today=docs_processed_today,
                processing_rate=processing_rate,
                current_status="processing" if processing_rate > 0 else "idle",
                last_processed=last_processed,
                errors_count=errors_count,
                duplicates_count=duplicates_count,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            print(f"Error getting Paperless metrics: {e}")
            return PaperlessMetrics(0, 0, 0, "error", None, 0, 0, datetime.now())
    
    def _get_ai_metrics(self) -> AIMetrics:
        """Get AI system metrics"""
        try:
            # Check Ollama
            ollama_running = False
            try:
                response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
                ollama_running = response.status_code == 200
            except:
                pass
            
            # Check Llama2
            llama2_available = False
            model_loaded = False
            response_time = 0
            memory_usage_gb = 0
            
            if ollama_running:
                try:
                    # Test Llama2 response time
                    start_time = time.time()
                    test_response = requests.post(
                        f"{self.ollama_url}/api/generate",
                        json={
                            "model": "llama2",
                            "prompt": "test",
                            "stream": False
                        },
                        timeout=10
                    )
                    response_time = time.time() - start_time
                    llama2_available = test_response.status_code == 200
                    model_loaded = llama2_available
                except:
                    pass
                
                # Get Ollama memory usage
                try:
                    ollama_process = None
                    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                        if 'ollama' in proc.info['name'].lower():
                            ollama_process = proc
                            break
                    
                    if ollama_process:
                        memory_usage_gb = ollama_process.info['memory_info'].rss / (1024**3)
                except:
                    pass
            
            return AIMetrics(
                ollama_running=ollama_running,
                llama2_available=llama2_available,
                model_loaded=model_loaded,
                response_time=response_time,
                memory_usage_gb=memory_usage_gb,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            print(f"Error getting AI metrics: {e}")
            return AIMetrics(False, False, False, 0, 0, datetime.now())
    
    def get_latest_metrics(self) -> Optional[Dict[str, Any]]:
        """Get the latest metrics"""
        try:
            return self.metrics_queue.get_nowait()
        except queue.Empty:
            return None
    
    def display_dashboard(self, metrics: Dict[str, Any]):
        """Display the monitoring dashboard"""
        if not metrics:
            return
        
        # Clear screen (works on most terminals)
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("\n" + "="*100)
        print("🤖 VANTA LEDGER - REAL-TIME MONITORING DASHBOARD")
        print("="*100)
        print(f"📅 Last Updated: {metrics['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # System Metrics
        system = metrics['system']
        print("💻 SYSTEM RESOURCES:")
        print(f"   CPU Usage: {system.cpu_percent:5.1f}%")
        print(f"   Memory: {system.memory_percent:5.1f}% ({system.memory_available_gb:.1f} GB available)")
        print(f"   Disk: {system.disk_usage_percent:5.1f}% ({system.disk_free_gb:.1f} GB free)")
        print()
        
        # Paperless Metrics
        paperless = metrics['paperless']
        print("📄 PAPERLESS-NGX PROCESSING:")
        print(f"   Total Documents: {paperless.total_documents:,}")
        print(f"   Processed Today: {paperless.documents_processed_today}")
        print(f"   Processing Rate: {paperless.processing_rate:.1f} docs/hour")
        print(f"   Status: {paperless.current_status.upper()}")
        if paperless.errors_count > 0:
            print(f"   ⚠️  Errors: {paperless.errors_count}")
        if paperless.duplicates_count > 0:
            print(f"   🔄 Duplicates: {paperless.duplicates_count}")
        print()
        
        # AI Metrics
        ai = metrics['ai']
        print("🤖 AI SYSTEM STATUS:")
        print(f"   Ollama: {'✅ Running' if ai.ollama_running else '❌ Stopped'}")
        print(f"   Llama2: {'✅ Available' if ai.llama2_available else '❌ Unavailable'}")
        print(f"   Model Loaded: {'✅ Yes' if ai.model_loaded else '❌ No'}")
        if ai.response_time > 0:
            print(f"   Response Time: {ai.response_time:.2f}s")
        if ai.memory_usage_gb > 0:
            print(f"   Memory Usage: {ai.memory_usage_gb:.1f} GB")
        print()
        
        # Recommendations
        print("💡 RECOMMENDATIONS:")
        if system.cpu_percent > 80:
            print("   ⚠️  High CPU usage - consider reducing concurrent tasks")
        if system.memory_percent > 85:
            print("   ⚠️  High memory usage - monitor for potential issues")
        if paperless.processing_rate < 10 and paperless.total_documents > 100:
            print("   📊 Paperless processing slowly - this is normal for large batches")
        if not ai.ollama_running:
            print("   🤖 Ollama not running - AI features unavailable")
        if ai.response_time > 5:
            print("   ⏱️  Slow AI response - model may be under heavy load")
        
        print("\n" + "="*100)
        print("💡 Press Ctrl+C to stop monitoring")
        print("="*100)

async def run_monitoring_dashboard(refresh_interval: int = 10):
    """Run the monitoring dashboard"""
    monitor = RealTimeMonitor()
    
    try:
        print("🚀 Starting Vanta Ledger monitoring dashboard...")
        monitor.start_monitoring()
        
        while True:
            metrics = monitor.get_latest_metrics()
            if metrics:
                monitor.display_dashboard(metrics)
            
            await asyncio.sleep(refresh_interval)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping monitoring...")
        monitor.stop_monitoring()
        print("✅ Monitoring stopped")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Vanta Ledger Real-Time Monitor')
    parser.add_argument('--refresh', type=int, default=10, 
                       help='Refresh interval in seconds (default: 10)')
    
    args = parser.parse_args()
    
    print("🤖 Vanta Ledger Real-Time Monitoring System")
    print("="*50)
    print("This will monitor:")
    print("  • System resources (CPU, Memory, Disk)")
    print("  • Paperless-ngx processing status")
    print("  • AI system (Ollama + Llama2) status")
    print("  • Processing recommendations")
    print()
    
    asyncio.run(run_monitoring_dashboard(args.refresh))

if __name__ == "__main__":
    main() 