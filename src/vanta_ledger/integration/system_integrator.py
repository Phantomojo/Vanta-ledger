#!/usr/bin/env python3
"""
System Integrator
Unified interface for all Vanta Ledger enhanced features
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from uuid import UUID

from ..services.enhanced_document_service import enhanced_document_service
from ..services.financial_service import financial_service
from ..services.ai_analytics_service import enhanced_ai_analytics_service
from ..optimizations.performance_optimizer import performance_optimizer
from ..models.document_models import EnhancedDocument, DocumentType, DocumentStatus
from ..models.financial_models import ChartOfAccounts, Invoice, Customer, AccountType

logger = logging.getLogger(__name__)

class VantaLedgerSystemIntegrator:
    """Main system integrator for Vanta Ledger enhanced features"""
    
    def __init__(self):
        self.document_service = enhanced_document_service
        self.financial_service = financial_service
        self.ai_analytics_service = enhanced_ai_analytics_service
        self.performance_optimizer = performance_optimizer
        
        # Initialize system
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize the integrated system"""
        try:
            # Optimize database queries
            self.performance_optimizer.optimize_database_queries()
            
            # Optimize memory usage
            self.performance_optimizer.optimize_memory_usage()
            
            # Optimize connection pools
            self.performance_optimizer.connection_pool_optimizer()
            
            logger.info("Vanta Ledger System Integrator initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing system integrator: {str(e)}")
    
    async def get_system_overview(self, user_id: UUID) -> Dict[str, Any]:
        """Get comprehensive system overview"""
        try:
            # Get document statistics
            doc_stats = self.document_service.get_document_statistics(user_id)
            
            # Get financial statistics
            financial_stats = self.financial_service.get_financial_statistics(user_id)
            
            # Get AI insights
            ai_insights = await self.ai_analytics_service.generate_financial_insights(user_id)
            
            # Get performance metrics
            performance_metrics = self.performance_optimizer.performance_monitor()
            
            return {
                "success": True,
                "system_overview": {
                    "documents": doc_stats,
                    "financial": financial_stats,
                    "ai_insights": ai_insights.get("insights", {}),
                    "performance": performance_metrics,
                    "generated_at": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting system overview: {str(e)}")
            raise
    
    async def process_document_with_financial_integration(self, document_data: Dict[str, Any], user_id: UUID) -> Dict[str, Any]:
        """Process document with financial data extraction and integration"""
        try:
            # Create enhanced document
            document = self.document_service.create_document(document_data, user_id)
            
            # Extract financial data from document
            financial_data = await self._extract_financial_data_from_document(document)
            
            # Create financial records if applicable
            financial_records = {}
            if financial_data.get("is_invoice"):
                invoice = await self._create_invoice_from_document(document, financial_data, user_id)
                financial_records["invoice"] = invoice
            
            if financial_data.get("is_receipt"):
                journal_entry = await self._create_journal_entry_from_document(document, financial_data, user_id)
                financial_records["journal_entry"] = journal_entry
            
            # Update document with financial metadata
            self._update_document_with_financial_metadata(document, financial_data)
            
            return {
                "success": True,
                "document": document.dict(),
                "financial_records": financial_records,
                "extracted_data": financial_data,
                "message": "Document processed with financial integration"
            }
            
        except Exception as e:
            logger.error(f"Error processing document with financial integration: {str(e)}")
            raise
    
    async def _extract_financial_data_from_document(self, document: EnhancedDocument) -> Dict[str, Any]:
        """Extract financial data from document content"""
        try:
            extracted_data = {
                "is_invoice": False,
                "is_receipt": False,
                "amount": None,
                "currency": "KES",
                "date": None,
                "vendor": None,
                "customer": None,
                "line_items": []
            }
            
            # Analyze document content for financial data
            if document.extracted_text:
                text = document.extracted_text.lower()
                
                # Check if it's an invoice
                if any(keyword in text for keyword in ["invoice", "bill", "amount due", "total"]):
                    extracted_data["is_invoice"] = True
                
                # Check if it's a receipt
                if any(keyword in text for keyword in ["receipt", "payment", "paid", "amount paid"]):
                    extracted_data["is_receipt"] = True
                
                # Extract amount (simplified)
                import re
                amount_pattern = r'[\$]?[\d,]+\.?\d*'
                amounts = re.findall(amount_pattern, document.extracted_text)
                if amounts:
                    # Get the largest amount (likely the total)
                    amounts = [float(amt.replace('$', '').replace(',', '')) for amt in amounts]
                    extracted_data["amount"] = max(amounts)
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error extracting financial data: {str(e)}")
            return {"is_invoice": False, "is_receipt": False}
    
    async def _create_invoice_from_document(self, document: EnhancedDocument, financial_data: Dict[str, Any], user_id: UUID) -> Optional[Dict[str, Any]]:
        """Create invoice from document data"""
        try:
            if not financial_data.get("is_invoice") or not financial_data.get("amount"):
                return None
            
            # Create customer if needed
            customer_data = {
                "customer_code": f"CUST-{document.id}",
                "customer_name": financial_data.get("customer", "Unknown Customer"),
                "created_by": user_id
            }
            
            customer = self.financial_service.create_customer(customer_data, user_id)
            
            # Create invoice
            invoice_data = {
                "invoice_number": f"INV-{document.id}",
                "customer_id": str(customer.id),
                "invoice_date": document.created_at.isoformat(),
                "due_date": (document.created_at + timedelta(days=30)).isoformat(),
                "lines": [
                    {
                        "item_description": document.metadata.title or "Document Processing",
                        "quantity": "1.00",
                        "unit_price": str(financial_data["amount"]),
                        "tax_rate": "0.00"
                    }
                ]
            }
            
            invoice = self.financial_service.create_invoice(invoice_data, user_id)
            
            return invoice.dict()
            
        except Exception as e:
            logger.error(f"Error creating invoice from document: {str(e)}")
            return None
    
    async def _create_journal_entry_from_document(self, document: EnhancedDocument, financial_data: Dict[str, Any], user_id: UUID) -> Optional[Dict[str, Any]]:
        """Create journal entry from document data"""
        try:
            if not financial_data.get("is_receipt") or not financial_data.get("amount"):
                return None
            
            # Get cash account
            cash_accounts = self.financial_service.get_accounts(AccountType.ASSET)
            cash_account = next((acc for acc in cash_accounts if "cash" in acc.account_name.lower()), None)
            
            if not cash_account:
                return None
            
            # Create journal entry
            entry_data = {
                "entry_number": f"JE-{document.id}",
                "entry_date": document.created_at.isoformat(),
                "description": f"Receipt from {document.original_filename}",
                "lines": [
                    {
                        "account_id": str(cash_account.id),
                        "description": "Cash receipt",
                        "debit_amount": str(financial_data["amount"]),
                        "credit_amount": "0.00"
                    },
                    {
                        "account_id": str(cash_account.id),  # Placeholder for revenue account
                        "description": "Revenue",
                        "debit_amount": "0.00",
                        "credit_amount": str(financial_data["amount"])
                    }
                ]
            }
            
            journal_entry = self.financial_service.create_journal_entry(entry_data, user_id)
            
            return journal_entry.dict()
            
        except Exception as e:
            logger.error(f"Error creating journal entry from document: {str(e)}")
            return None
    
    def _update_document_with_financial_metadata(self, document: EnhancedDocument, financial_data: Dict[str, Any]):
        """Update document with extracted financial metadata"""
        try:
            # Add financial tags
            if financial_data.get("is_invoice"):
                # Find or create invoice tag
                invoice_tags = self.document_service.get_tags()
                invoice_tag = next((tag for tag in invoice_tags if "invoice" in tag.name.lower()), None)
                
                if invoice_tag:
                    document.add_tag(invoice_tag.id)
            
            if financial_data.get("is_receipt"):
                # Find or create receipt tag
                receipt_tags = self.document_service.get_tags()
                receipt_tag = next((tag for tag in receipt_tags if "receipt" in tag.name.lower()), None)
                
                if receipt_tag:
                    document.add_tag(receipt_tag.id)
            
            # Add financial metadata
            if financial_data.get("amount"):
                document.metadata.custom_fields["extracted_amount"] = financial_data["amount"]
                document.metadata.custom_fields["extracted_currency"] = financial_data["currency"]
            
            # Update document in database
            self.document_service.documents.update_one(
                {"_id": str(document.id)},
                {"$set": {
                    "metadata": document.metadata.dict(),
                    "modified_at": datetime.utcnow()
                }}
            )
            
        except Exception as e:
            logger.error(f"Error updating document with financial metadata: {str(e)}")
    
    async def get_financial_dashboard(self, user_id: UUID) -> Dict[str, Any]:
        """Get comprehensive financial dashboard"""
        try:
            # Get financial trends
            trends = await self.ai_analytics_service.analyze_financial_trends(user_id, 90)
            
            # Get predictions
            predictions = await self.ai_analytics_service.predict_financial_metrics(user_id, 6)
            
            # Get anomalies
            anomalies = await self.ai_analytics_service.detect_anomalies(user_id, "financial")
            
            # Get insights
            insights = await self.ai_analytics_service.generate_financial_insights(user_id)
            
            return {
                "success": True,
                "financial_dashboard": {
                    "trends": trends.get("analysis", {}),
                    "predictions": predictions.get("predictions", {}),
                    "anomalies": anomalies.get("anomalies", {}),
                    "insights": insights.get("insights", {}),
                    "generated_at": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting financial dashboard: {str(e)}")
            raise
    
    async def get_document_analytics(self, user_id: UUID) -> Dict[str, Any]:
        """Get document analytics with AI insights"""
        try:
            # Get document statistics
            doc_stats = self.document_service.get_document_statistics(user_id)
            
            # Get document anomalies
            doc_anomalies = await self.ai_analytics_service.detect_anomalies(user_id, "documents")
            
            # Get document processing insights
            processing_insights = await self._analyze_document_processing(user_id)
            
            return {
                "success": True,
                "document_analytics": {
                    "statistics": doc_stats,
                    "anomalies": doc_anomalies.get("anomalies", {}),
                    "processing_insights": processing_insights,
                    "generated_at": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting document analytics: {str(e)}")
            raise
    
    async def _analyze_document_processing(self, user_id: UUID) -> Dict[str, Any]:
        """Analyze document processing patterns"""
        try:
            # Get recent documents
            recent_documents = list(self.document_service.documents.find({
                "created_by": str(user_id),
                "created_at": {"$gte": datetime.utcnow() - timedelta(days=30)}
            }))
            
            # Analyze processing times
            processing_times = []
            for doc in recent_documents:
                if doc.get("processing_started_at") and doc.get("processing_completed_at"):
                    start_time = doc["processing_started_at"]
                    end_time = doc["processing_completed_at"]
                    if isinstance(start_time, str):
                        start_time = datetime.fromisoformat(start_time)
                    if isinstance(end_time, str):
                        end_time = datetime.fromisoformat(end_time)
                    processing_time = (end_time - start_time).total_seconds()
                    processing_times.append(processing_time)
            
            # Calculate statistics
            if processing_times:
                avg_processing_time = sum(processing_times) / len(processing_times)
                max_processing_time = max(processing_times)
                min_processing_time = min(processing_times)
            else:
                avg_processing_time = max_processing_time = min_processing_time = 0
            
            # Analyze document types
            doc_types = {}
            for doc in recent_documents:
                doc_type = doc.get("metadata", {}).get("document_type", "unknown")
                doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            
            return {
                "processing_performance": {
                    "average_processing_time_seconds": round(avg_processing_time, 2),
                    "max_processing_time_seconds": round(max_processing_time, 2),
                    "min_processing_time_seconds": round(min_processing_time, 2),
                    "total_documents_processed": len(recent_documents)
                },
                "document_type_distribution": doc_types,
                "processing_success_rate": self._calculate_processing_success_rate(recent_documents)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing document processing: {str(e)}")
            return {}
    
    def _calculate_processing_success_rate(self, documents: List[Dict[str, Any]]) -> float:
        """Calculate document processing success rate"""
        try:
            if not documents:
                return 0.0
            
            successful = sum(1 for doc in documents if doc.get("status") == "processed")
            return round((successful / len(documents)) * 100, 2)
            
        except Exception as e:
            logger.error(f"Error calculating processing success rate: {str(e)}")
            return 0.0
    
    async def run_system_optimization(self) -> Dict[str, Any]:
        """Run comprehensive system optimization"""
        try:
            optimization_results = {
                "database_optimization": {},
                "memory_optimization": {},
                "cache_optimization": {},
                "performance_metrics": {}
            }
            
            # Database optimization
            self.performance_optimizer.optimize_database_queries()
            optimization_results["database_optimization"]["status"] = "completed"
            
            # Memory optimization
            self.performance_optimizer.optimize_memory_usage()
            optimization_results["memory_optimization"]["status"] = "completed"
            
            # Cache warmup
            warmup_functions = [
                lambda: self.document_service.get_document_statistics(UUID(1)), # Placeholder for a valid UUID
                lambda: self.financial_service.get_financial_statistics(UUID(1)) # Placeholder for a valid UUID
            ]
            self.performance_optimizer.cache_warmup(warmup_functions)
            optimization_results["cache_optimization"]["status"] = "completed"
            
            # Performance monitoring
            performance_metrics = self.performance_optimizer.performance_monitor()
            optimization_results["performance_metrics"] = performance_metrics
            
            return {
                "success": True,
                "optimization_results": optimization_results,
                "completed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error running system optimization: {str(e)}")
            raise
    
    async def export_system_report(self, user_id: UUID) -> Dict[str, Any]:
        """Export comprehensive system report"""
        try:
            # Gather all system data
            system_overview = await self.get_system_overview(user_id)
            financial_dashboard = await self.get_financial_dashboard(user_id)
            document_analytics = await self.get_document_analytics(user_id)
            
            # Compile comprehensive report
            report = {
                "report_metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "user_id": str(user_id),
                    "report_type": "comprehensive_system_report"
                },
                "system_overview": system_overview.get("system_overview", {}),
                "financial_dashboard": financial_dashboard.get("financial_dashboard", {}),
                "document_analytics": document_analytics.get("document_analytics", {}),
                "performance_metrics": self.performance_optimizer.performance_monitor(),
                "recommendations": await self._generate_system_recommendations(user_id)
            }
            
            return {
                "success": True,
                "report": report,
                "export_format": "json",
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error exporting system report: {str(e)}")
            raise
    
    async def _generate_system_recommendations(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Generate system recommendations based on current state"""
        try:
            recommendations = []
            
            # Get system data
            doc_stats = self.document_service.get_document_statistics(user_id)
            financial_stats = self.financial_service.get_financial_statistics(user_id)
            performance_metrics = self.performance_optimizer.performance_monitor()
            
            # Document recommendations
            if doc_stats.get("total_documents", 0) > 1000:
                recommendations.append({
                    "category": "documents",
                    "priority": "medium",
                    "title": "Consider Document Archiving",
                    "description": "Large number of documents detected. Consider implementing archiving policies.",
                    "action": "Review and implement document retention policies"
                })
            
            # Financial recommendations
            if financial_stats.get("total_invoices", 0) > 100:
                recommendations.append({
                    "category": "financial",
                    "priority": "high",
                    "title": "Implement Automated Invoicing",
                    "description": "High volume of invoices detected. Consider automation.",
                    "action": "Set up automated invoice processing workflows"
                })
            
            # Performance recommendations
            if performance_metrics.get("system", {}).get("memory_percent", 0) > 80:
                recommendations.append({
                    "category": "performance",
                    "priority": "high",
                    "title": "System Memory Optimization",
                    "description": "High memory usage detected. Consider optimization.",
                    "action": "Review memory usage and implement optimizations"
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating system recommendations: {str(e)}")
            return []

# Global instance
vanta_ledger_integrator = VantaLedgerSystemIntegrator() 