#!/usr/bin/env python3
"""
Vanta Ledger Integration Master
===============================

Master script that orchestrates the complete Vanta Ledger system:
1. Enhanced database setup with all 29 companies
2. Document processing pipeline for all organized data
3. Network analysis of business relationships
4. Comprehensive analytics dashboard generation

Author: Vanta Ledger Team
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import logging

# Import our custom modules
from enhanced_hybrid_database_setup import EnhancedHybridDatabaseManager
from network_analysis_engine import NetworkAnalysisEngine
from document_processing_pipeline import DocumentProcessingPipeline
from analytics_dashboard_engine import AnalyticsDashboardEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vanta_ledger_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VantaLedgerIntegrationMaster:
    """Master integration class for Vanta Ledger system"""
    
    def __init__(self, organized_data_path: str = "/home/phantomojo/vanta_companies_data_improved"):
        self.organized_data_path = organized_data_path
        self.db_manager = None
        self.network_engine = None
        self.document_pipeline = None
        self.analytics_engine = None
        self.integration_results = {}
        
    def setup_database_system(self) -> bool:
        """Step 1: Set up enhanced database system with all 29 companies"""
        try:
            logger.info("🚀 Step 1: Setting up Enhanced Database System...")
            
            # Initialize database manager
            self.db_manager = EnhancedHybridDatabaseManager()
            
            # Set up complete system
            self.db_manager.setup_enhanced_system()
            
            # Store results
            self.integration_results['database_setup'] = {
                'status': 'success',
                'timestamp': datetime.now(),
                'companies_count': 29,
                'message': 'Enhanced database system setup complete'
            }
            
            logger.info("✅ Database system setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database system setup failed: {e}")
            self.integration_results['database_setup'] = {
                'status': 'error',
                'timestamp': datetime.now(),
                'error': str(e)
            }
            return False
    
    def run_network_analysis(self) -> bool:
        """Step 2: Run comprehensive network analysis"""
        try:
            logger.info("🔗 Step 2: Running Network Analysis...")
            
            # Initialize network analysis engine
            self.network_engine = NetworkAnalysisEngine(
                self.db_manager.postgres_engine,
                self.db_manager.mongo_client
            )
            
            # Run complete analysis
            analysis_results = self.network_engine.run_complete_analysis()
            
            # Store results
            self.integration_results['network_analysis'] = {
                'status': 'success',
                'timestamp': datetime.now(),
                'nodes_count': analysis_results.get('centrality_metrics', {}).__len__(),
                'analysis_type': 'comprehensive',
                'message': 'Network analysis completed successfully'
            }
            
            logger.info("✅ Network analysis completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Network analysis failed: {e}")
            self.integration_results['network_analysis'] = {
                'status': 'error',
                'timestamp': datetime.now(),
                'error': str(e)
            }
            return False
    
    def process_documents(self) -> bool:
        """Step 3: Process all organized company documents"""
        try:
            logger.info("📄 Step 3: Processing Company Documents...")
            
            # Initialize document processing pipeline
            self.document_pipeline = DocumentProcessingPipeline(
                self.db_manager.postgres_engine,
                self.db_manager.mongo_client,
                self.organized_data_path
            )
            
            # Run complete document processing
            processing_results = self.document_pipeline.run_complete_processing()
            
            # Store results
            self.integration_results['document_processing'] = {
                'status': 'success',
                'timestamp': datetime.now(),
                'total_documents': processing_results.get('total_documents', 0),
                'processed_documents': processing_results.get('processed_documents', 0),
                'error_documents': processing_results.get('error_documents', 0),
                'success_rate': processing_results.get('success_rate', 0),
                'processing_time_seconds': processing_results.get('processing_time_seconds', 0),
                'message': 'Document processing completed successfully'
            }
            
            logger.info("✅ Document processing completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Document processing failed: {e}")
            self.integration_results['document_processing'] = {
                'status': 'error',
                'timestamp': datetime.now(),
                'error': str(e)
            }
            return False
    
    def generate_analytics(self) -> bool:
        """Step 4: Generate comprehensive analytics dashboard"""
        try:
            logger.info("📊 Step 4: Generating Analytics Dashboard...")
            
            # Initialize analytics engine
            self.analytics_engine = AnalyticsDashboardEngine(
                self.db_manager.postgres_engine,
                self.db_manager.mongo_client
            )
            
            # Generate complete dashboard data
            dashboard_data = self.analytics_engine.generate_dashboard_data()
            
            # Create visualizations
            self.analytics_engine.create_visualizations("analytics_output")
            
            # Store results
            self.integration_results['analytics_generation'] = {
                'status': 'success',
                'timestamp': datetime.now(),
                'dashboard_summary': dashboard_data.get('summary', {}),
                'analytics_sections': list(dashboard_data.get('analytics', {}).keys()),
                'message': 'Analytics dashboard generated successfully'
            }
            
            logger.info("✅ Analytics dashboard generated successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Analytics generation failed: {e}")
            self.integration_results['analytics_generation'] = {
                'status': 'error',
                'timestamp': datetime.now(),
                'error': str(e)
            }
            return False
    
    def generate_integration_report(self) -> Dict[str, Any]:
        """Generate comprehensive integration report"""
        try:
            report = {
                'integration_summary': {
                    'total_steps': 4,
                    'completed_steps': sum(1 for step in self.integration_results.values() if step.get('status') == 'success'),
                    'failed_steps': sum(1 for step in self.integration_results.values() if step.get('status') == 'error'),
                    'overall_status': 'success' if all(step.get('status') == 'success' for step in self.integration_results.values()) else 'partial',
                    'integration_date': datetime.now()
                },
                'step_details': self.integration_results,
                'system_capabilities': {
                    'database': {
                        'companies_supported': 29,
                        'company_types': ['core_family', 'business_partner', 'subsidiary'],
                        'tables': ['companies', 'projects', 'ledger_entries', 'documents', 'company_relationships', 'network_analysis', 'analytics_dashboard']
                    },
                    'document_processing': {
                        'supported_formats': ['PDF', 'DOCX', 'Images', 'Text files'],
                        'ai_capabilities': ['Text extraction', 'Financial data extraction', 'Sentiment analysis', 'Entity recognition'],
                        'categories': ['financial', 'legal', 'tenders', 'projects', 'personal', 'media', 'backups']
                    },
                    'network_analysis': {
                        'metrics': ['Centrality', 'Betweenness', 'Closeness', 'Eigenvector', 'PageRank'],
                        'analysis_types': ['Relationship patterns', 'Financial flows', 'Risk assessment', 'Business insights']
                    },
                    'analytics': {
                        'dashboards': ['Financial', 'Document', 'Network', 'Business Intelligence'],
                        'visualizations': ['Charts', 'Graphs', 'Reports', 'Trends']
                    }
                },
                'next_steps': [
                    'Review analytics dashboard',
                    'Analyze network insights',
                    'Process additional documents as needed',
                    'Set up automated processing schedules',
                    'Configure alerts and notifications'
                ]
            }
            
            # Save report to file
            with open('vanta_ledger_integration_report.json', 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Report generation failed: {e}")
            return {}
    
    def run_complete_integration(self) -> bool:
        """Run complete Vanta Ledger integration"""
        try:
            start_time = datetime.now()
            logger.info("🎯 Starting Complete Vanta Ledger Integration...")
            logger.info("=" * 60)
            
            # Step 1: Database Setup
            if not self.setup_database_system():
                logger.error("❌ Integration failed at database setup step")
                return False
            
            # Step 2: Network Analysis
            if not self.run_network_analysis():
                logger.error("❌ Integration failed at network analysis step")
                return False
            
            # Step 3: Document Processing
            if not self.process_documents():
                logger.error("❌ Integration failed at document processing step")
                return False
            
            # Step 4: Analytics Generation
            if not self.generate_analytics():
                logger.error("❌ Integration failed at analytics generation step")
                return False
            
            # Generate final report
            report = self.generate_integration_report()
            
            end_time = datetime.now()
            integration_time = end_time - start_time
            
            # Print summary
            logger.info("=" * 60)
            logger.info("🎉 Vanta Ledger Integration Complete!")
            logger.info("=" * 60)
            logger.info(f"⏱️  Total Integration Time: {integration_time}")
            logger.info(f"📊 Companies Integrated: 29")
            logger.info(f"📄 Documents Processed: {self.integration_results.get('document_processing', {}).get('processed_documents', 0)}")
            logger.info(f"🔗 Network Analysis: Complete")
            logger.info(f"📈 Analytics Dashboard: Generated")
            logger.info("=" * 60)
            logger.info("📁 Output Files:")
            logger.info("  - vanta_ledger_integration_report.json")
            logger.info("  - analytics_output/ (visualizations)")
            logger.info("  - vanta_ledger_integration.log")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Complete integration failed: {e}")
            return False

def main():
    """Main function to run Vanta Ledger integration"""
    try:
        # Initialize master integration
        master = VantaLedgerIntegrationMaster()
        
        # Run complete integration
        success = master.run_complete_integration()
        
        if success:
            print("\n🎉 Vanta Ledger Integration Successful!")
            print("Your complete business intelligence system is ready.")
            print("\nNext steps:")
            print("1. Review the integration report")
            print("2. Explore the analytics dashboard")
            print("3. Analyze network insights")
            print("4. Process additional documents as needed")
        else:
            print("\n❌ Vanta Ledger Integration Failed!")
            print("Check the logs for detailed error information.")
        
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"Integration failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 