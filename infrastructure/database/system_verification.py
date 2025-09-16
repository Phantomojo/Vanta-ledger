#!/usr/bin/env python3
"""
Vanta Ledger System Verification & Cleanup
==========================================

This script performs comprehensive verification of the entire system
and performs cleanup operations.

Author: Vanta Ledger Team
"""

import os
import json
import requests
import subprocess
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemVerifier:
    """Comprehensive system verification and cleanup"""
    
    def __init__(self):
        self.verification_results = {}
        
    def check_docker_containers(self) -> Dict[str, Any]:
        """Check Docker container status"""
        try:
            result = subprocess.run(
                ["docker-compose", "-f", "docker-compose-hybrid.yml", "ps", "--format", "json"],
                capture_output=True, text=True, check=True
            )
            
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    containers.append(json.loads(line))
            
            healthy_count = sum(1 for c in containers if c.get('State') == 'running')
            total_count = len(containers)
            
            status = {
                "total_containers": total_count,
                "healthy_containers": healthy_count,
                "all_healthy": healthy_count == total_count,
                "containers": containers
            }
            
            logger.info(f"✅ Docker containers: {healthy_count}/{total_count} healthy")
            return status
            
        except Exception as e:
            logger.error(f"❌ Docker container check failed: {e}")
            return {"error": str(e)}
    
    def check_database_connections(self) -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            # Test PostgreSQL connection
            postgres_result = subprocess.run(
                ["docker", "exec", "vanta_ledger_postgresql", "psql", "-U", "vanta_user", "-d", "vanta_ledger", "-c", "SELECT COUNT(*) FROM documents;"],
                capture_output=True, text=True
            )
            
            # Test MongoDB connection
            mongo_result = subprocess.run(
                ["docker", "exec", "vanta_ledger_mongodb", "mongosh", "--eval", "db.documents.countDocuments()"],
                capture_output=True, text=True
            )
            
            status = {
                "postgresql": {
                    "connected": postgres_result.returncode == 0,
                    "document_count": postgres_result.stdout.strip() if postgres_result.returncode == 0 else "N/A"
                },
                "mongodb": {
                    "connected": mongo_result.returncode == 0,
                    "document_count": mongo_result.stdout.strip() if mongo_result.returncode == 0 else "N/A"
                }
            }
            
            logger.info(f"✅ PostgreSQL: {'Connected' if status['postgresql']['connected'] else 'Failed'}")
            logger.info(f"✅ MongoDB: {'Connected' if status['mongodb']['connected'] else 'Failed'}")
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Database connection check failed: {e}")
            return {"error": str(e)}
    
    def check_api_endpoints(self) -> Dict[str, Any]:
        """Check API endpoint health"""
        try:
            endpoints = {
                "health": "http://localhost:8500/health",
                "docs": "http://localhost:8500/docs"
            }
            
            results = {}
            for name, url in endpoints.items():
                try:
                    response = requests.get(url, timeout=5)
                    results[name] = {
                        "status_code": response.status_code,
                        "accessible": response.status_code == 200,
                        "response_time": response.elapsed.total_seconds()
                    }
                except Exception as e:
                    results[name] = {
                        "status_code": None,
                        "accessible": False,
                        "error": str(e)
                    }
            
            logger.info(f"✅ API endpoints: {sum(1 for r in results.values() if r.get('accessible', False))}/{len(results)} accessible")
            return results
            
        except Exception as e:
            logger.error(f"❌ API endpoint check failed: {e}")
            return {"error": str(e)}
    
    def check_migration_data(self) -> Dict[str, Any]:
        """Verify migration data integrity"""
        try:
            # Check migration summary
            summary_path = "../data/processed_documents/migration_summary.json"
            if os.path.exists(summary_path):
                with open(summary_path, 'r') as f:
                    summary = json.load(f)
                
                status = {
                    "migration_summary_exists": True,
                    "total_migrated": summary.get("migrated_documents", 0),
                    "success_rate": summary.get("success_rate", "0%"),
                    "migration_date": summary.get("migration_date", "Unknown")
                }
            else:
                status = {
                    "migration_summary_exists": False,
                    "total_migrated": 0,
                    "success_rate": "0%",
                    "migration_date": "Unknown"
                }
            
            logger.info(f"✅ Migration data: {status['total_migrated']} documents migrated ({status['success_rate']})")
            return status
            
        except Exception as e:
            logger.error(f"❌ Migration data check failed: {e}")
            return {"error": str(e)}
    
    def perform_cleanup(self) -> Dict[str, Any]:
        """Perform system cleanup operations"""
        try:
            cleanup_results = {}
            
            # Clean up old log files
            log_files = []
            for root, dirs, files in os.walk("."):
                for file in files:
                    if file.endswith(".log") and os.path.getsize(os.path.join(root, file)) > 10 * 1024 * 1024:  # 10MB
                        log_files.append(os.path.join(root, file))
            
            if log_files:
                for log_file in log_files:
                    try:
                        os.remove(log_file)
                        logger.info(f"🗑️ Cleaned up large log file: {log_file}")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to clean up log file {log_file}: {e}")
            
            cleanup_results["log_files_cleaned"] = len(log_files)
            
            # Clean up temporary files
            temp_files = []
            for root, dirs, files in os.walk("."):
                for file in files:
                    if file.endswith((".tmp", ".temp", ".cache")):
                        temp_files.append(os.path.join(root, file))
            
            if temp_files:
                for temp_file in temp_files:
                    try:
                        os.remove(temp_file)
                        logger.info(f"🗑️ Cleaned up temp file: {temp_file}")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to clean up temp file {temp_file}: {e}")
            
            cleanup_results["temp_files_cleaned"] = len(temp_files)
            
            # Check disk usage
            disk_usage = subprocess.run(
                ["df", "-h", "."],
                capture_output=True, text=True
            )
            
            if disk_usage.returncode == 0:
                lines = disk_usage.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) >= 5:
                        cleanup_results["disk_usage"] = {
                            "total": parts[1],
                            "used": parts[2],
                            "available": parts[3],
                            "usage_percent": parts[4]
                        }
            
            logger.info(f"✅ Cleanup completed: {cleanup_results.get('log_files_cleaned', 0)} log files, {cleanup_results.get('temp_files_cleaned', 0)} temp files")
            return cleanup_results
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            return {"error": str(e)}
    
    def generate_verification_report(self) -> Dict[str, Any]:
        """Generate comprehensive verification report"""
        try:
            report = {
                "verification_date": datetime.now(timezone.utc).isoformat(),
                "docker_containers": self.check_docker_containers(),
                "database_connections": self.check_database_connections(),
                "api_endpoints": self.check_api_endpoints(),
                "migration_data": self.check_migration_data(),
                "cleanup_results": self.perform_cleanup()
            }
            
            # Calculate overall system health
            health_indicators = []
            
            # Docker health
            if report["docker_containers"].get("all_healthy", False):
                health_indicators.append("docker")
            
            # Database health
            db_connections = report["database_connections"]
            if not db_connections.get("error") and db_connections.get("postgresql", {}).get("connected") and db_connections.get("mongodb", {}).get("connected"):
                health_indicators.append("databases")
            
            # API health
            api_endpoints = report["api_endpoints"]
            if not api_endpoints.get("error") and api_endpoints.get("health", {}).get("accessible"):
                health_indicators.append("api")
            
            # Migration health
            migration_data = report["migration_data"]
            if migration_data.get("migration_summary_exists") and migration_data.get("total_migrated", 0) > 0:
                health_indicators.append("migration")
            
            report["system_health"] = {
                "overall_status": "healthy" if len(health_indicators) >= 4 else "degraded" if len(health_indicators) >= 2 else "unhealthy",
                "healthy_components": health_indicators,
                "health_score": len(health_indicators) / 4 * 100
            }
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Verification report generation failed: {e}")
            return {"error": str(e)}
    
    def save_report(self, report: Dict[str, Any]):
        """Save verification report to file"""
        try:
            report_path = "system_verification_report.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"📋 Verification report saved to: {report_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save verification report: {e}")

def main():
    """Main verification function"""
    try:
        verifier = SystemVerifier()
        
        logger.info("\n🔍 Vanta Ledger System Verification & Cleanup")
        logger.info("=")
        
        # Generate comprehensive report
        report = verifier.generate_verification_report()
        
        # Save report
        verifier.save_report(report)
        
        # Display summary
        health = report.get("system_health", {})
        logger.info(f"\n📊 System Health Summary:")
        logger.info(f"   Overall Status: {health.get(").upper()}")
        logger.info(f"   Health Score: {health.get(")
        logger.info(f"   Healthy Components: {")
        
        # Docker status
        docker = report.get("docker_containers", {})
        logger.info(f"\n🐳 Docker Status:")
        logger.info(f"   Containers: {docker.get(")
        
        # Database status
        db = report.get("database_connections", {})
        logger.info(f"\n🗄️ Database Status:")
        logger.info(f"   PostgreSQL: {") else '❌ Failed'}")
        logger.info(f"   MongoDB: {") else '❌ Failed'}")
        
        # API status
        api = report.get("api_endpoints", {})
        logger.info(f"\n🌐 API Status:")
        logger.info(f"   Health Endpoint: {") else '❌ Failed'}")
        logger.info(f"   Documentation: {") else '❌ Failed'}")
        
        # Migration status
        migration = report.get("migration_data", {})
        logger.info(f"\n📊 Migration Status:")
        logger.info(f"   Documents Migrated: {migration.get(")
        logger.info(f"   Success Rate: {migration.get(")}")
        
        # Cleanup results
        cleanup = report.get("cleanup_results", {})
        logger.info(f"\n🧹 Cleanup Results:")
        logger.info(f"   Log Files Cleaned: {cleanup.get(")
        logger.info(f"   Temp Files Cleaned: {cleanup.get(")
        
        if health.get("overall_status") == "healthy":
            logger.info(f"\n🎉 SYSTEM VERIFICATION COMPLETE - ALL SYSTEMS OPERATIONAL!")
        else:
            logger.info(f"\n⚠️ SYSTEM VERIFICATION COMPLETE - SOME ISSUES DETECTED")
        
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        raise

if __name__ == "__main__":
    main() 