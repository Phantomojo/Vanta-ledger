#!/usr/bin/env python3
"""
Demonstration of System Analysis Service Usage
Shows how to integrate the service into applications
"""

import asyncio
import json
from datetime import datetime
from src.vanta_ledger.services.system_analysis_service import SystemAnalysisService


class SystemMonitor:
    """Example system monitoring application using the System Analysis Service"""
    
    def __init__(self):
        self.analysis_service = SystemAnalysisService()
        self.monitoring_active = False
    
    async def start_monitoring(self, interval_seconds: int = 60):
        """Start continuous system monitoring"""
        if not self.analysis_service.enabled:
            print("⚠️  AI features not available - running basic monitoring only")
        
        self.monitoring_active = True
        print(f"🚀 Starting system monitoring (interval: {interval_seconds}s)")
        
        while self.monitoring_active:
            try:
                await self._run_monitoring_cycle()
                await asyncio.sleep(interval_seconds)
            except KeyboardInterrupt:
                print("\n🛑 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                await asyncio.sleep(10)  # Wait before retrying
    
    async def _run_monitoring_cycle(self):
        """Run one monitoring cycle"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n📊 Monitoring Cycle - {timestamp}")
        print("-" * 40)
        
        # Collect basic metrics
        metrics = self.analysis_service._collect_system_metrics()
        
        # Display key metrics
        print(f"💻 CPU Usage: {metrics['cpu_percent']:.1f}%")
        print(f"🧠 Memory Usage: {metrics['memory_percent']:.1f}%")
        print(f"💾 Available Memory: {metrics['memory_available_gb']:.1f} GB")
        print(f"💿 Disk Usage: {metrics['disk_percent']:.1f}%")
        print(f"🌐 Network Sent: {metrics['network_bytes_sent'] / (1024**2):.1f} MB")
        print(f"🌐 Network Received: {metrics['network_bytes_recv'] / (1024**2):.1f} MB")
        
        # Check for critical thresholds
        alerts = self._check_thresholds(metrics)
        if alerts:
            print("\n🚨 ALERTS:")
            for alert in alerts:
                print(f"   ⚠️  {alert}")
        
        # Try AI analysis if available
        if self.analysis_service.enabled:
            print("\n🤖 Running AI analysis...")
            try:
                analysis = await self.analysis_service.analyze_system_health(include_logs=False)
                if "system_status" in analysis:
                    print(f"   Status: {analysis['system_status']}")
                if "recommendations" in analysis:
                    print(f"   Recommendations: {len(analysis['recommendations'])} items")
            except Exception as e:
                print(f"   ❌ AI analysis failed: {e}")
        
        print("-" * 40)
    
    def _check_thresholds(self, metrics: dict) -> list:
        """Check metrics against critical thresholds"""
        alerts = []
        
        if metrics['cpu_percent'] > 80:
            alerts.append(f"High CPU usage: {metrics['cpu_percent']:.1f}%")
        
        if metrics['memory_percent'] > 90:
            alerts.append(f"Critical memory usage: {metrics['memory_percent']:.1f}%")
        
        if metrics['disk_percent'] > 85:
            alerts.append(f"High disk usage: {metrics['disk_percent']:.1f}%")
        
        if metrics['memory_available_gb'] < 1.0:
            alerts.append(f"Low available memory: {metrics['memory_available_gb']:.1f} GB")
        
        return alerts
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        print("🛑 Monitoring stopped")


async def main():
    """Main demonstration function"""
    print("🔍 System Analysis Service Demonstration")
    print("=" * 50)
    
    # Create monitoring instance
    monitor = SystemMonitor()
    
    # Show service status
    print(f"🔧 AI Features Available: {monitor.analysis_service.enabled}")
    print(f"📁 Log Directory: {monitor.analysis_service.log_dir}")
    print()
    
    # Run a single monitoring cycle
    print("📊 Running Single Monitoring Cycle...")
    await monitor._run_monitoring_cycle()
    
    print("\n" + "=" * 50)
    print("🎯 Demonstration Complete!")
    print("\n💡 Usage Examples:")
    print("   • Continuous monitoring: await monitor.start_monitoring(30)")
    print("   • Single analysis: await monitor.analysis_service.analyze_system_health()")
    print("   • Code review: await monitor.analysis_service.analyze_code_quality('file.py')")
    print("   • Project analysis: await monitor.analysis_service.analyze_project_codebase()")
    
    # Ask if user wants to start continuous monitoring
    try:
        response = input("\n🚀 Start continuous monitoring? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            print("\n🔄 Starting continuous monitoring (Press Ctrl+C to stop)...")
            await monitor.start_monitoring(30)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demonstration interrupted")
