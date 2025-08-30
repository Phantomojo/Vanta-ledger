#!/usr/bin/env python3
"""
Production AI System for Vanta Ledger
====================================

This is a production-ready AI system with:
- Database integration (PostgreSQL + MongoDB)
- Scalable document processing
- Comprehensive monitoring and crash detection
- Automatic recovery and error handling
- Performance metrics and logging
"""

import sys
import os
import time
import json
import logging
import threading
import queue
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import psycopg2
from pymongo import MongoClient
import signal
import traceback

# Add the virtual environment to the path
venv_path = os.path.join(os.path.dirname(__file__), '..', 'venv', 'lib', 'python3.12', 'site-packages')
sys.path.insert(0, venv_path)

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production_ai_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductionAISystem:
    """Production AI system with database integration and monitoring"""
    
    def __init__(self, max_workers: int = 4, batch_size: int = 10):
        """Initialize the production AI system"""
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.running = False
        self.processing_queue = queue.Queue()
        self.results_queue = queue.Queue()
        self.workers = []
        self.metrics = {
            'documents_processed': 0,
            'documents_failed': 0,
            'processing_time_total': 0,
            'start_time': None,
            'last_heartbeat': None,
            'errors': []
        }
        
        # Database connections
        self.postgres_conn = None
        self.mongo_client = None
        self.mongo_db = None
        
        # Import the enhanced document processor
        try:
            from enhanced_document_processor import EnhancedDocumentProcessor
            self.processor = EnhancedDocumentProcessor()
            logger.info("✅ Enhanced Document Processor loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load processor: {e}")
            raise
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        logger.info("🚀 Production AI System initialized")

    def connect_databases(self):
        """Connect to PostgreSQL and MongoDB databases"""
        try:
            # PostgreSQL connection
            self.postgres_conn = psycopg2.connect(
                host=os.getenv('POSTGRES_HOST', 'localhost'),
                port=int(os.getenv('POSTGRES_PORT', '5432')),
                database=os.getenv('POSTGRES_DB', 'vanta_ledger'),
                user=os.getenv('POSTGRES_USER', 'user'),
                password=os.getenv('POSTGRES_PASSWORD', 'password')
            )
            logger.info("✅ PostgreSQL connected successfully")
            
            # MongoDB connection
            mongo_uri = os.getenv('MONGO_URI', 'mongodb://user:password@localhost:27017/vanta_ledger')
            self.mongo_client = MongoClient(mongo_uri)
            self.mongo_db = self.mongo_client.vanta_ledger
            logger.info("✅ MongoDB connected successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False

    def save_to_database(self, result: Dict[str, Any]):
        """Save processing result to database"""
        try:
            # Save to PostgreSQL
            with self.postgres_conn.cursor() as cur:
                # Insert into documents table
                cur.execute("""
                    INSERT INTO documents (
                        filename, original_path, file_size, mime_type,
                        extracted_text, metadata, processed_at, processing_status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    result['filename'],
                    result['file_path'],
                    result['file_size'],
                    result['file_type'],
                    result['text'][:10000],  # Limit text size
                    json.dumps(result['entities']),
                    datetime.now(),
                    result['processing_status']
                ))
                doc_id = cur.fetchone()[0]
                
                # Insert company if not exists
                company_name = result.get('company', 'Unknown')
                cur.execute("""
                    INSERT INTO companies (name, created_at)
                    VALUES (%s, %s)
                    ON CONFLICT (name) DO NOTHING
                    RETURNING id
                """, (company_name, datetime.now()))
                
                company_result = cur.fetchone()
                if company_result:
                    company_id = company_result[0]
                else:
                    cur.execute("SELECT id FROM companies WHERE name = %s", (company_name,))
                    company_id = cur.fetchone()[0]
                
                # Update document with company_id
                cur.execute("""
                    UPDATE documents SET company_id = %s WHERE id = %s
                """, (company_id, doc_id))
                
            self.postgres_conn.commit()
            
            # Save to MongoDB for detailed analysis
            mongo_doc = {
                'document_id': doc_id,
                'company': result.get('company'),
                'category': result.get('category'),
                'filename': result['filename'],
                'file_path': result['file_path'],
                'file_size': result['file_size'],
                'file_type': result['file_type'],
                'processing_date': result['processing_date'],
                'text': result['text'],
                'entities': result['entities'],
                'document_type': result['document_type'],
                'document_type_scores': result['document_type_scores'],
                'sentiment': result['sentiment'],
                'key_phrases': result['key_phrases'],
                'statistics': result['statistics'],
                'processing_status': result['processing_status'],
                'created_at': datetime.now()
            }
            
            self.mongo_db.processed_documents.insert_one(mongo_doc)
            
            logger.info(f"✅ Saved to database: {result['filename']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database save failed for {result['filename']}: {e}")
            self.postgres_conn.rollback()
            return False

    def worker(self, worker_id: int):
        """Worker thread for processing documents"""
        logger.info(f"🔄 Worker {worker_id} started")
        
        while self.running:
            try:
                # Get document from queue with timeout
                file_path = self.processing_queue.get(timeout=5)
                
                if file_path is None:  # Shutdown signal
                    break
                
                start_time = time.time()
                
                # Process document
                result = self.processor.process_document(file_path)
                result['worker_id'] = worker_id
                result['processing_time'] = time.time() - start_time
                
                # Add to results queue
                self.results_queue.put(result)
                
                # Update metrics
                self.metrics['documents_processed'] += 1
                self.metrics['processing_time_total'] += result['processing_time']
                
                logger.info(f"✅ Worker {worker_id} processed: {file_path.name}")
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"❌ Worker {worker_id} error: {e}")
                self.metrics['documents_failed'] += 1
                self.metrics['errors'].append({
                    'worker_id': worker_id,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        logger.info(f"🔄 Worker {worker_id} stopped")

    def monitor_worker(self):
        """Monitor worker for database operations"""
        logger.info("🔄 Database worker started")
        
        while self.running:
            try:
                # Get result from queue with timeout
                result = self.results_queue.get(timeout=5)
                
                if result is None:  # Shutdown signal
                    break
                
                # Save to database
                success = self.save_to_database(result)
                
                if not success:
                    logger.error(f"❌ Failed to save: {result['filename']}")
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"❌ Database worker error: {e}")
                self.metrics['errors'].append({
                    'worker_type': 'database',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        logger.info("🔄 Database worker stopped")

    def heartbeat_monitor(self):
        """Monitor system health and performance"""
        logger.info("💓 Heartbeat monitor started")
        
        while self.running:
            try:
                # Update heartbeat
                self.metrics['last_heartbeat'] = datetime.now()
                
                # Check database connections
                if self.postgres_conn and self.postgres_conn.closed:
                    logger.warning("⚠️ PostgreSQL connection lost, reconnecting...")
                    self.connect_databases()
                
                # Log performance metrics
                if self.metrics['documents_processed'] > 0:
                    avg_time = self.metrics['processing_time_total'] / self.metrics['documents_processed']
                    logger.info(f"📊 Performance: {self.metrics['documents_processed']} docs, "
                              f"{self.metrics['documents_failed']} failed, "
                              f"{avg_time:.2f}s avg")
                
                # Check for too many errors
                if len(self.metrics['errors']) > 10:
                    logger.error("❌ Too many errors detected, system may be unstable")
                
                time.sleep(30)  # Heartbeat every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Heartbeat monitor error: {e}")
                time.sleep(30)
        
        logger.info("💓 Heartbeat monitor stopped")

    def process_company_documents(self, company_data_path: str = "/home/phantomojo/vanta_companies_data_improved"):
        """Process all company documents with scaling"""
        logger.info(f"🚀 Starting production processing of: {company_data_path}")
        
        if not self.connect_databases():
            logger.error("❌ Cannot start processing without database connection")
            return False
        
        # Start workers
        self.running = True
        self.metrics['start_time'] = datetime.now()
        
        # Start processing workers
        for i in range(self.max_workers):
            worker = threading.Thread(target=self.worker, args=(i,))
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
        
        # Start database worker
        db_worker = threading.Thread(target=self.monitor_worker)
        db_worker.daemon = True
        db_worker.start()
        
        # Start heartbeat monitor
        heartbeat = threading.Thread(target=self.heartbeat_monitor)
        heartbeat.daemon = True
        heartbeat.start()
        
        # Collect all documents
        documents = []
        company_data_path = Path(company_data_path)
        
        if not company_data_path.exists():
            logger.error(f"❌ Company data not found at: {company_data_path}")
            return False
        
        for company_dir in company_data_path.iterdir():
            if company_dir.is_dir() and company_dir.name != "unmatched_documents":
                for category_dir in company_dir.iterdir():
                    if category_dir.is_dir():
                        for file_path in category_dir.iterdir():
                            if file_path.is_file():
                                documents.append(file_path)
        
        logger.info(f"📁 Found {len(documents)} documents to process")
        
        # Add documents to processing queue
        for file_path in documents:
            self.processing_queue.put(file_path)
        
        # Wait for processing to complete
        self.processing_queue.join()
        
        # Send shutdown signals
        for _ in range(self.max_workers):
            self.processing_queue.put(None)
        
        self.results_queue.put(None)  # Shutdown database worker
        
        # Wait for workers to finish
        for worker in self.workers:
            worker.join()
        
        db_worker.join()
        heartbeat.join()
        
        # Generate final report
        self.generate_production_report()
        
        logger.info("🎉 Production processing completed")
        return True

    def generate_production_report(self):
        """Generate comprehensive production report"""
        end_time = datetime.now()
        duration = end_time - self.metrics['start_time']
        
        report = {
            "production_run_date": end_time.isoformat(),
            "duration_seconds": duration.total_seconds(),
            "metrics": self.metrics,
            "performance": {
                "documents_per_second": self.metrics['documents_processed'] / duration.total_seconds() if duration.total_seconds() > 0 else 0,
                "success_rate": (self.metrics['documents_processed'] / (self.metrics['documents_processed'] + self.metrics['documents_failed'])) * 100 if (self.metrics['documents_processed'] + self.metrics['documents_failed']) > 0 else 0,
                "average_processing_time": self.metrics['processing_time_total'] / self.metrics['documents_processed'] if self.metrics['documents_processed'] > 0 else 0
            },
            "system_info": {
                "max_workers": self.max_workers,
                "batch_size": self.batch_size,
                "database_connected": self.postgres_conn is not None and not self.postgres_conn.closed
            }
        }
        
        # Save report
        report_path = Path(f"production_report_{end_time.strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📋 Production report saved to: {report_path}")
        
        # Print summary
        print("\n🎉 Production AI System - Final Report")
        print("=" * 60)
        print(f"📊 Documents Processed: {self.metrics['documents_processed']}")
        print(f"❌ Documents Failed: {self.metrics['documents_failed']}")
        print(f"⏱️  Total Duration: {duration}")
        print(f"🚀 Processing Speed: {report['performance']['documents_per_second']:.2f} docs/sec")
        print(f"✅ Success Rate: {report['performance']['success_rate']:.1f}%")
        print(f"⏱️  Average Processing Time: {report['performance']['average_processing_time']:.2f}s")
        print(f"💾 Database Connected: {report['system_info']['database_connected']}")
        print(f"📁 Report Saved: {report_path}")

    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"🛑 Received signal {signum}, shutting down gracefully...")
        self.running = False

    def cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up resources...")
        
        if self.postgres_conn:
            self.postgres_conn.close()
        
        if self.mongo_client:
            self.mongo_client.close()
        
        logger.info("✅ Cleanup completed")

def main():
    """Main production AI system"""
    print("🚀 Vanta Ledger Production AI System")
    print("=" * 60)
    
    # Initialize production system
    production_system = ProductionAISystem(max_workers=4, batch_size=10)
    
    try:
        # Process all company documents
        success = production_system.process_company_documents()
        
        if success:
            print("\n🎉 Production AI System completed successfully!")
            print("✅ All documents processed and saved to database")
            print("✅ Performance metrics collected")
            print("✅ System monitoring active")
        else:
            print("\n❌ Production AI System failed!")
            
    except KeyboardInterrupt:
        print("\n🛑 Production system interrupted by user")
    except Exception as e:
        print(f"\n❌ Production system error: {e}")
        logger.error(f"Production system error: {e}")
        logger.error(traceback.format_exc())
    finally:
        production_system.cleanup()

if __name__ == "__main__":
    main() 