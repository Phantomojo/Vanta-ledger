#!/usr/bin/env python3
"""
Demonstration of System Analysis Service Usage
Shows how to integrate the service into applications
"""

import asyncio
import json
from datetime import datetime
from src.vanta_ledger.services.system_analysis_service import SystemAnalysisService
import logging
logger = logging.getLogger(__name__)


class SystemMonitor:
    """Example system monitoring application using the System Analysis Service"""
    
    def __init__(self):
        self.analysis_service = SystemAnalysisService()
        self.monitoring_active = False
    
    async def start_monitoring(self, interval_seconds: int = 60):
        """Start continuous system monitoring"""
        if not self.analysis_service.enabled:
            logger.info("⚠️  AI features not available - running basic monitoring only")
        
        self.monitoring_active = True
        logger.info(f"🚀 Starting system monitoring (interval: {interval_seconds}s)")
        
        while self.monitoring_active:
            try:
                await self._run_monitoring_cycle()
                await asyncio.sleep(interval_seconds)
            except KeyboardInterrupt:
                logger.info("\n🛑 Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                await asyncio.sleep(10)  # Wait before retrying
    
    async def _run_monitoring_cycle(self):
        """Run one monitoring cycle"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"\n📊 Monitoring Cycle - {timestamp}")
        logger.info("-")
        
        # Collect basic metrics
        metrics = self.analysis_service._collect_system_metrics()
        
        # Display key metrics
        logger.info(f"💻 CPU Usage: {metrics[")
        logger.info(f"🧠 Memory Usage: {metrics[")
        logger.info(f"💾 Available Memory: {metrics[")
        logger.info(f"💿 Disk Usage: {metrics[")
        logger.info(f"🌐 Network Sent: {metrics[")
        logger.info(f"🌐 Network Received: {metrics[")
        
        # Check for critical thresholds
        alerts = self._check_thresholds(metrics)
        if alerts:
            logger.info("\n🚨 ALERTS:")
            for alert in alerts:
                logger.info(f"   ⚠️  {alert}")
        
        # Try AI analysis if available
        if self.analysis_service.enabled:
            logger.info("\n🤖 Running AI analysis...")
            try:
                analysis = await self.analysis_service.analyze_system_health(include_logs=False)
                if "system_status" in analysis:
                    logger.info(f"   Status: {analysis[")
                if "recommendations" in analysis:
                    logger.info(f"   Recommendations: {len(analysis[")
            except Exception as e:
                logger.error(f"   ❌ AI analysis failed: {e}")
        
        logger.info("-")
    
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
        logger.info("🛑 Monitoring stopped")


async def main():
    """Main demonstration function"""
    logger.info("🔍 System Analysis Service Demonstration")
    logger.info("=")
    
    # Create monitoring instance
    monitor = SystemMonitor()
    
    # Show service status
    logger.info(f"🔧 AI Features Available: {monitor.analysis_service.enabled}")
    logger.info(f"📁 Log Directory: {monitor.analysis_service.log_dir}")
    print()
    
    # Run a single monitoring cycle
    logger.info("📊 Running Single Monitoring Cycle...")
    await monitor._run_monitoring_cycle()
    
    logger.info("\n")
    logger.info("🎯 Demonstration Complete!")
    logger.info("\n💡 Usage Examples:")
    logger.info("   • Continuous monitoring: await monitor.start_monitoring(30)")
    logger.info("   • Single analysis: await monitor.analysis_service.analyze_system_health()")
    logger.info("   • Code review: await monitor.analysis_service.analyze_code_quality(")")
    logger.info("   • Project analysis: await monitor.analysis_service.analyze_project_codebase()")
    
    # Ask if user wants to start continuous monitoring
    try:
        response = input("\n🚀 Start continuous monitoring? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            logger.info("\n🔄 Starting continuous monitoring (Press Ctrl+C to stop)...")
            await monitor.start_monitoring(30)
    except KeyboardInterrupt:
        logger.info("\n👋 Goodbye!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n👋 Demonstration interrupted")
