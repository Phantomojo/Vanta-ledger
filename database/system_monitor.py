#!/usr/bin/env python3
"""
System Monitor for Vanta Ledger AI System
========================================

This module provides comprehensive monitoring, crash detection,
and automatic recovery for the production AI system.
"""

import os
import time
import json
import logging
import threading
import subprocess
import psutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import signal
import smtplib
from email.mime.text import MIMEText
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemMonitor:
    """Comprehensive system monitor with crash detection and recovery"""
    
    def __init__(self, check_interval: int = 60, max_restarts: int = 3):
        """Initialize the system monitor"""
        self.check_interval = check_interval
        self.max_restarts = max_restarts
        self.running = False
        self.restart_count = 0
        self.last_check = None
        self.system_health = {
            'cpu_usage': 0,
            'memory_usage': 0,
            'disk_usage': 0,
            'ai_process_running': False,
            'database_connected': False,
            'last_heartbeat': None,
            'errors': [],
            'restarts': 0
        }
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        logger.info("🚀 System Monitor initialized")

    def check_system_health(self):
        """Check overall system health"""
        try:
            # CPU usage
            self.system_health['cpu_usage'] = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.system_health['memory_usage'] = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.system_health['disk_usage'] = (disk.used / disk.total) * 100
            
            # Check if AI process is running
            self.system_health['ai_process_running'] = self.check_ai_process()
            
            # Check database connectivity
            self.system_health['database_connected'] = self.check_database_connection()
            
            # Update timestamp
            self.system_health['last_heartbeat'] = datetime.now()
            
            logger.info(f"💓 System Health: CPU {self.system_health['cpu_usage']}%, "
                       f"Memory {self.system_health['memory_usage']}%, "
                       f"Disk {self.system_health['disk_usage']:.1f}%, "
                       f"AI Process: {self.system_health['ai_process_running']}, "
                       f"DB: {self.system_health['database_connected']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ System health check failed: {e}")
            self.system_health['errors'].append({
                'type': 'health_check',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            return False

    def check_ai_process(self):
        """Check if the AI processing system is running"""
        try:
            # Check for production_ai_system.py process
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'production_ai_system.py' in ' '.join(proc.info['cmdline'] or []):
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Check for log file activity
            log_file = Path('production_ai_system.log')
            if log_file.exists():
                # Check if log file was modified in last 5 minutes
                if time.time() - log_file.stat().st_mtime < 300:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ AI process check failed: {e}")
            return False

    def check_database_connection(self):
        """Check database connectivity"""
        try:
            import psycopg2
            from pymongo import MongoClient
            
            # Test PostgreSQL
            postgres_conn = psycopg2.connect(
                host=os.getenv('POSTGRES_HOST', 'localhost'),
                port=int(os.getenv('POSTGRES_PORT', '5432')),
                database=os.getenv('POSTGRES_DB', 'vanta_ledger'),
                user=os.getenv('POSTGRES_USER', 'user'),
                password=os.getenv('POSTGRES_PASSWORD', 'password'),
                connect_timeout=5
            )
            postgres_conn.close()
            
            # Test MongoDB
            mongo_uri = os.getenv('MONGO_URI', 'mongodb://user:password@localhost:27017/vanta_ledger')
            mongo_client = MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=5000
            )
            mongo_client.admin.command('ping')
            mongo_client.close()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Database connection check failed: {e}")
            return False

    def check_crash_conditions(self):
        """Check for crash conditions"""
        crash_conditions = []
        
        # High CPU usage
        if self.system_health['cpu_usage'] > 90:
            crash_conditions.append(f"High CPU usage: {self.system_health['cpu_usage']}%")
        
        # High memory usage
        if self.system_health['memory_usage'] > 95:
            crash_conditions.append(f"High memory usage: {self.system_health['memory_usage']}%")
        
        # High disk usage
        if self.system_health['disk_usage'] > 95:
            crash_conditions.append(f"High disk usage: {self.system_health['disk_usage']:.1f}%")
        
        # AI process not running
        if not self.system_health['ai_process_running']:
            crash_conditions.append("AI process not running")
        
        # Database not connected
        if not self.system_health['database_connected']:
            crash_conditions.append("Database not connected")
        
        # Too many errors
        if len(self.system_health['errors']) > 10:
            crash_conditions.append(f"Too many errors: {len(self.system_health['errors'])}")
        
        return crash_conditions

    def restart_ai_system(self):
        """Restart the AI system"""
        try:
            logger.warning("🔄 Restarting AI system...")
            
            # Kill existing AI processes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'production_ai_system.py' in ' '.join(proc.info['cmdline'] or []):
                        logger.info(f"🛑 Killing AI process: {proc.info['pid']}")
                        proc.terminate()
                        proc.wait(timeout=10)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                    continue
            
            # Wait a moment
            time.sleep(5)
            
            # Start new AI system
            ai_script = Path('production_ai_system.py')
            if ai_script.exists():
                logger.info("🚀 Starting new AI system...")
                subprocess.Popen([
                    sys.executable, 'production_ai_system.py'
                ], cwd=os.getcwd())
                
                self.restart_count += 1
                self.system_health['restarts'] = self.restart_count
                
                logger.info(f"✅ AI system restarted (attempt {self.restart_count})")
                return True
            else:
                logger.error("❌ AI system script not found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to restart AI system: {e}")
            return False

    def send_alert(self, message: str, alert_type: str = "warning"):
        """Send alert notification"""
        try:
            # Create alert file
            alert_file = Path(f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            alert_data = {
                'timestamp': datetime.now().isoformat(),
                'type': alert_type,
                'message': message,
                'system_health': self.system_health
            }
            
            with open(alert_file, 'w') as f:
                json.dump(alert_data, f, indent=2)
            
            logger.warning(f"🚨 Alert created: {alert_file}")
            
            # Print alert to console
            print(f"\n🚨 SYSTEM ALERT: {alert_type.upper()}")
            print(f"📝 Message: {message}")
            print(f"📁 Alert saved: {alert_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to send alert: {e}")

    def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("🔄 Starting system monitoring loop...")
        
        while self.running:
            try:
                # Check system health
                health_ok = self.check_system_health()
                
                if not health_ok:
                    self.send_alert("System health check failed", "error")
                
                # Check for crash conditions
                crash_conditions = self.check_crash_conditions()
                
                if crash_conditions:
                    alert_message = f"Crash conditions detected: {', '.join(crash_conditions)}"
                    self.send_alert(alert_message, "critical")
                    
                    # Attempt restart if conditions are severe
                    if (not self.system_health['ai_process_running'] or 
                        not self.system_health['database_connected']) and \
                        self.restart_count < self.max_restarts:
                        
                        logger.warning("🔄 Attempting system restart...")
                        if self.restart_ai_system():
                            self.send_alert("System restarted successfully", "info")
                        else:
                            self.send_alert("System restart failed", "critical")
                    elif self.restart_count >= self.max_restarts:
                        self.send_alert("Maximum restart attempts reached", "critical")
                        break
                
                # Check for performance issues
                if self.system_health['cpu_usage'] > 80:
                    self.send_alert(f"High CPU usage: {self.system_health['cpu_usage']}%", "warning")
                
                if self.system_health['memory_usage'] > 85:
                    self.send_alert(f"High memory usage: {self.system_health['memory_usage']}%", "warning")
                
                # Save system health snapshot
                self.save_health_snapshot()
                
                # Wait for next check
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"❌ Monitoring loop error: {e}")
                self.system_health['errors'].append({
                    'type': 'monitoring_loop',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                time.sleep(self.check_interval)

    def save_health_snapshot(self):
        """Save system health snapshot"""
        try:
            snapshot_file = Path(f"health_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            
            snapshot_data = {
                'timestamp': datetime.now().isoformat(),
                'system_health': self.system_health,
                'restart_count': self.restart_count
            }
            
            with open(snapshot_file, 'w') as f:
                json.dump(snapshot_data, f, indent=2)
            
            # Keep only last 10 snapshots
            snapshots = sorted(Path('.').glob('health_snapshot_*.json'))
            if len(snapshots) > 10:
                for old_snapshot in snapshots[:-10]:
                    old_snapshot.unlink()
                    
        except Exception as e:
            logger.error(f"❌ Failed to save health snapshot: {e}")

    def generate_monitoring_report(self):
        """Generate comprehensive monitoring report"""
        try:
            report = {
                'monitoring_session': {
                    'start_time': self.last_check.isoformat() if self.last_check else None,
                    'end_time': datetime.now().isoformat(),
                    'total_checks': 0,  # Would need to track this
                    'restarts_performed': self.restart_count
                },
                'system_health_summary': {
                    'average_cpu': 0,  # Would need to track averages
                    'average_memory': 0,
                    'average_disk': 0,
                    'total_errors': len(self.system_health['errors'])
                },
                'current_status': self.system_health,
                'recommendations': self.generate_recommendations()
            }
            
            report_file = Path(f"monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"📋 Monitoring report saved: {report_file}")
            return report_file
            
        except Exception as e:
            logger.error(f"❌ Failed to generate monitoring report: {e}")
            return None

    def generate_recommendations(self):
        """Generate system recommendations"""
        recommendations = []
        
        if self.system_health['cpu_usage'] > 80:
            recommendations.append("Consider reducing AI worker threads or upgrading CPU")
        
        if self.system_health['memory_usage'] > 85:
            recommendations.append("Consider reducing batch size or adding more RAM")
        
        if self.system_health['disk_usage'] > 90:
            recommendations.append("Consider cleaning up old logs and reports")
        
        if self.restart_count > 0:
            recommendations.append("System has been restarted - monitor for stability")
        
        if len(self.system_health['errors']) > 5:
            recommendations.append("High error rate - review system logs for issues")
        
        return recommendations

    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"🛑 Received signal {signum}, shutting down monitor...")
        self.running = False

    def start_monitoring(self):
        """Start the monitoring system"""
        logger.info("🚀 Starting system monitoring...")
        self.running = True
        self.last_check = datetime.now()
        
        # Start monitoring in a separate thread
        monitor_thread = threading.Thread(target=self.monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        try:
            # Keep main thread alive
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Monitoring interrupted by user")
        finally:
            self.running = False
            monitor_thread.join()
            
            # Generate final report
            self.generate_monitoring_report()
            
            logger.info("✅ System monitoring stopped")

def main():
    """Main monitoring system"""
    print("🚀 Vanta Ledger System Monitor")
    print("=" * 50)
    
    # Initialize monitor
    monitor = SystemMonitor(check_interval=60, max_restarts=3)
    
    try:
        # Start monitoring
        monitor.start_monitoring()
        
    except Exception as e:
        print(f"❌ Monitoring system error: {e}")
        logger.error(f"Monitoring system error: {e}")

if __name__ == "__main__":
    main() 