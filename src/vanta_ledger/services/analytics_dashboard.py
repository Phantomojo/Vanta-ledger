#!/usr/bin/env python3
"""
Analytics Dashboard Service for Vanta Ledger
===========================================

This service provides comprehensive analytics, visualizations, and real-time insights
for the Vanta Ledger system, including financial trends, compliance metrics, and business intelligence.
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
import logging

logger = logging.getLogger(__name__)

class AnalyticsDashboard:
    """Comprehensive analytics dashboard service"""
    
    def __init__(self):
        """Initialize the analytics dashboard"""
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        logger.info("🚀 Analytics Dashboard initialized")

    async def get_dashboard_overview(self, mongo_client, postgres_conn) -> Dict[str, Any]:
        """Get comprehensive dashboard overview"""
        try:
            # Get data from both databases
            mongo_data = await self._get_mongo_analytics(mongo_client)
            postgres_data = await self._get_postgres_analytics(postgres_conn)
            
            # Combine and structure data
            overview = {
                "timestamp": datetime.now().isoformat(),
                "system_health": await self._get_system_health(mongo_client, postgres_conn),
                "financial_metrics": self._combine_financial_data(mongo_data, postgres_data),
                "compliance_metrics": self._get_compliance_metrics(mongo_data),
                "processing_metrics": self._get_processing_metrics(mongo_data),
                "trends": await self._get_trends(mongo_data),
                "alerts": await self._get_alerts(mongo_data),
                "top_performers": self._get_top_performers(mongo_data),
                "risk_analysis": self._get_risk_analysis(mongo_data)
            }
            
            logger.info("✅ Dashboard overview generated")
            return overview
            
        except Exception as e:
            logger.error(f"❌ Dashboard overview generation failed: {e}")
            return {"error": "An internal error has occurred."}

    async def _get_mongo_analytics(self, mongo_client) -> Dict[str, Any]:
        """Get analytics data from MongoDB"""
        try:
            db = mongo_client.vanta_ledger
            
            # Get processed documents
            documents = list(db.processed_documents.find({}))
            
            # Get AI reports
            ai_reports = list(db.ai_reports.find({}))
            
            # Get system analytics
            system_analytics = list(db.system_analytics.find({}))
            
            return {
                "documents": documents,
                "ai_reports": ai_reports,
                "system_analytics": system_analytics,
                "total_documents": len(documents),
                "total_companies": len(set(doc.get('company') for doc in documents if doc.get('company')))
            }
            
        except Exception as e:
            logger.error(f"❌ MongoDB analytics failed: {e}")
            return {"error": str(e)}

    async def _get_postgres_analytics(self, postgres_conn) -> Dict[str, Any]:
        """Get analytics data from PostgreSQL"""
        try:
            cursor = postgres_conn.cursor()
            
            # Get financial transactions
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_transactions,
                    SUM(amount) as total_amount,
                    AVG(amount) as avg_amount,
                    MIN(amount) as min_amount,
                    MAX(amount) as max_amount
                FROM financial_transactions
            """)
            
            financial_data = cursor.fetchone()
            
            # Get companies
            cursor.execute("SELECT COUNT(*) FROM companies")
            company_count = cursor.fetchone()[0]
            
            # Get documents
            cursor.execute("SELECT COUNT(*) FROM documents")
            document_count = cursor.fetchone()[0]
            
            cursor.close()
            
            return {
                "financial_transactions": {
                    "total": financial_data[0] if financial_data[0] else 0,
                    "total_amount": float(financial_data[1]) if financial_data[1] else 0,
                    "avg_amount": float(financial_data[2]) if financial_data[2] else 0,
                    "min_amount": float(financial_data[3]) if financial_data[3] else 0,
                    "max_amount": float(financial_data[4]) if financial_data[4] else 0
                },
                "company_count": company_count,
                "document_count": document_count
            }
            
        except Exception as e:
            logger.error(f"❌ PostgreSQL analytics failed: {e}")
            return {"error": str(e)}

    async def _get_system_health(self, mongo_client, postgres_conn) -> Dict[str, Any]:
        """Get system health metrics"""
        try:
            # Check database connections
            mongo_health = "healthy"
            postgres_health = "healthy"
            
            try:
                mongo_client.admin.command('ping')
            except:
                mongo_health = "unhealthy"
            
            try:
                postgres_conn.cursor().execute("SELECT 1")
            except:
                postgres_health = "unhealthy"
            
            # Get processing statistics
            db = mongo_client.vanta_ledger
            total_docs = db.processed_documents.count_documents({})
            success_docs = db.processed_documents.count_documents({"processing_status": "success"})
            
            success_rate = (success_docs / total_docs * 100) if total_docs > 0 else 0
            
            return {
                "overall_status": "healthy" if mongo_health == "healthy" and postgres_health == "healthy" else "degraded",
                "mongodb": mongo_health,
                "postgresql": postgres_health,
                "processing_success_rate": round(success_rate, 2),
                "total_documents_processed": total_docs,
                "successful_documents": success_docs,
                "failed_documents": total_docs - success_docs
            }
            
        except Exception as e:
            logger.error(f"❌ System health check failed: {e}")
            return {"error": str(e)}

    def _combine_financial_data(self, mongo_data: Dict[str, Any], postgres_data: Dict[str, Any]) -> Dict[str, Any]:
        """Combine financial data from both databases"""
        try:
            # Extract amounts from MongoDB documents
            mongo_amounts = []
            for doc in mongo_data.get('documents', []):
                amounts = doc.get('entities', {}).get('amounts', [])
                for amt in amounts:
                    try:
                        mongo_amounts.append(float(str(amt).replace(',', '')))
                    except:
                        pass
            
            # Combine with PostgreSQL data
            postgres_amounts = postgres_data.get('financial_transactions', {})
            
            total_mongo_amount = sum(mongo_amounts)
            total_postgres_amount = postgres_amounts.get('total_amount', 0)
            
            return {
                "total_financial_value": total_mongo_amount + total_postgres_amount,
                "mongo_amounts": {
                    "total": total_mongo_amount,
                    "count": len(mongo_amounts),
                    "average": total_mongo_amount / len(mongo_amounts) if mongo_amounts else 0
                },
                "postgres_amounts": postgres_amounts,
                "currency": "KSH",
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Financial data combination failed: {e}")
            return {"error": str(e)}

    def _get_compliance_metrics(self, mongo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get compliance metrics from documents"""
        try:
            documents = mongo_data.get('documents', [])
            
            # Count compliance-related entities
            tax_numbers = []
            compliance_issues = []
            certificates = []
            
            for doc in documents:
                entities = doc.get('entities', {})
                tax_numbers.extend(entities.get('tax_numbers', []))
                compliance_issues.extend(entities.get('compliance_issues', []))
                certificates.extend(entities.get('certificates', []))
            
            # Calculate compliance scores
            total_docs = len(documents)
            docs_with_tax = len([doc for doc in documents if doc.get('entities', {}).get('tax_numbers')])
            docs_with_issues = len([doc for doc in documents if doc.get('entities', {}).get('compliance_issues')])
            
            compliance_score = ((docs_with_tax / total_docs) * 100) if total_docs > 0 else 0
            risk_score = ((docs_with_issues / total_docs) * 100) if total_docs > 0 else 0
            
            return {
                "compliance_score": round(compliance_score, 2),
                "risk_score": round(risk_score, 2),
                "total_tax_numbers": len(set(tax_numbers)),
                "total_compliance_issues": len(set(compliance_issues)),
                "total_certificates": len(set(certificates)),
                "documents_with_tax_info": docs_with_tax,
                "documents_with_issues": docs_with_issues,
                "compliance_status": "COMPLIANT" if compliance_score > 80 and risk_score < 20 else "NON_COMPLIANT"
            }
            
        except Exception as e:
            logger.error(f"❌ Compliance metrics failed: {e}")
            return {"error": str(e)}

    def _get_processing_metrics(self, mongo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get document processing metrics"""
        try:
            documents = mongo_data.get('documents', [])
            
            # Processing status counts
            status_counts = Counter(doc.get('processing_status', 'unknown') for doc in documents)
            
            # Document type distribution
            doc_types = Counter(doc.get('document_type', 'unknown') for doc in documents)
            
            # Company distribution
            companies = Counter(doc.get('company', 'unknown') for doc in documents)
            
            # Processing time analysis
            processing_times = []
            for doc in documents:
                if doc.get('processing_time'):
                    processing_times.append(doc['processing_time'])
            
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
            
            return {
                "total_documents": len(documents),
                "processing_status": dict(status_counts),
                "document_types": dict(doc_types),
                "companies": dict(companies),
                "average_processing_time": round(avg_processing_time, 2),
                "success_rate": (status_counts.get('success', 0) / len(documents) * 100) if documents else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Processing metrics failed: {e}")
            return {"error": str(e)}

    async def _get_trends(self, mongo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get trends and patterns in the data"""
        try:
            documents = mongo_data.get('documents', [])
            
            # Date-based trends
            date_counts = defaultdict(int)
            amount_trends = defaultdict(list)
            
            for doc in documents:
                # Extract date
                processing_date = doc.get('processing_date', '')
                if processing_date:
                    date_key = processing_date[:10]  # YYYY-MM-DD
                    date_counts[date_key] += 1
                
                # Extract amounts
                amounts = doc.get('entities', {}).get('amounts', [])
                for amt in amounts:
                    try:
                        amount_val = float(str(amt).replace(',', ''))
                        if processing_date:
                            amount_trends[processing_date[:10]].append(amount_val)
                    except:
                        pass
            
            # Calculate trends
            sorted_dates = sorted(date_counts.keys())
            document_trend = [date_counts[date] for date in sorted_dates[-7:]]  # Last 7 days
            
            amount_trend = []
            for date in sorted_dates[-7:]:
                daily_amounts = amount_trends.get(date, [])
                amount_trend.append(sum(daily_amounts))
            
            return {
                "document_trend": document_trend,
                "amount_trend": amount_trend,
                "trend_dates": sorted_dates[-7:],
                "growth_rate": self._calculate_growth_rate(document_trend),
                "amount_growth_rate": self._calculate_growth_rate(amount_trend)
            }
            
        except Exception as e:
            logger.error(f"❌ Trends analysis failed: {e}")
            return {"error": str(e)}

    def _calculate_growth_rate(self, values: List[float]) -> float:
        """Calculate growth rate from a list of values"""
        if len(values) < 2:
            return 0.0
        
        first_value = values[0] if values[0] != 0 else 1
        last_value = values[-1]
        
        return ((last_value - first_value) / first_value) * 100

    async def _get_alerts(self, mongo_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get system alerts and notifications"""
        try:
            alerts = []
            documents = mongo_data.get('documents', [])
            
            # Check for high-risk documents
            high_risk_docs = [doc for doc in documents if doc.get('entities', {}).get('compliance_issues')]
            if high_risk_docs:
                alerts.append({
                    "type": "compliance_risk",
                    "severity": "high",
                    "message": f"{len(high_risk_docs)} documents have compliance issues",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Check for large financial amounts
            large_amounts = []
            for doc in documents:
                amounts = doc.get('entities', {}).get('amounts', [])
                for amt in amounts:
                    try:
                        if float(str(amt).replace(',', '')) > 10000000:  # 10M KSH
                            large_amounts.append(amt)
                    except:
                        pass
            
            if large_amounts:
                alerts.append({
                    "type": "large_transaction",
                    "severity": "medium",
                    "message": f"{len(large_amounts)} transactions exceed 10M KSH",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Check for processing failures
            failed_docs = [doc for doc in documents if doc.get('processing_status') == 'failed']
            if failed_docs:
                alerts.append({
                    "type": "processing_failure",
                    "severity": "medium",
                    "message": f"{len(failed_docs)} documents failed to process",
                    "timestamp": datetime.now().isoformat()
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"❌ Alerts generation failed: {e}")
            return [{"error": str(e)}]

    def _get_top_performers(self, mongo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get top performing companies and metrics"""
        try:
            documents = mongo_data.get('documents', [])
            
            # Company performance analysis
            company_metrics = defaultdict(lambda: {
                'documents': 0,
                'total_amount': 0,
                'avg_amount': 0,
                'compliance_score': 0
            })
            
            for doc in documents:
                company = doc.get('company', 'Unknown')
                metrics = company_metrics[company]
                
                metrics['documents'] += 1
                
                # Calculate amounts
                amounts = doc.get('entities', {}).get('amounts', [])
                for amt in amounts:
                    try:
                        metrics['total_amount'] += float(str(amt).replace(',', ''))
                    except:
                        pass
                
                # Calculate compliance
                if doc.get('entities', {}).get('tax_numbers'):
                    metrics['compliance_score'] += 1
            
            # Calculate averages and sort
            for company, metrics in company_metrics.items():
                if metrics['documents'] > 0:
                    metrics['avg_amount'] = metrics['total_amount'] / metrics['documents']
                    metrics['compliance_score'] = (metrics['compliance_score'] / metrics['documents']) * 100
            
            # Sort by different criteria
            top_by_documents = sorted(company_metrics.items(), key=lambda x: x[1]['documents'], reverse=True)[:5]
            top_by_amount = sorted(company_metrics.items(), key=lambda x: x[1]['total_amount'], reverse=True)[:5]
            top_by_compliance = sorted(company_metrics.items(), key=lambda x: x[1]['compliance_score'], reverse=True)[:5]
            
            return {
                "top_by_documents": [{"company": k, "metrics": v} for k, v in top_by_documents],
                "top_by_amount": [{"company": k, "metrics": v} for k, v in top_by_amount],
                "top_by_compliance": [{"company": k, "metrics": v} for k, v in top_by_compliance]
            }
            
        except Exception as e:
            logger.error(f"❌ Top performers analysis failed: {e}")
            return {"error": str(e)}

    def _get_risk_analysis(self, mongo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive risk analysis"""
        try:
            documents = mongo_data.get('documents', [])
            
            # Risk categorization
            high_risk = []
            medium_risk = []
            low_risk = []
            
            for doc in documents:
                entities = doc.get('entities', {})
                
                # Risk assessment logic
                risk_score = 0
                
                # High risk indicators
                if entities.get('compliance_issues'):
                    risk_score += 3
                if entities.get('tax_numbers') and not entities.get('compliance_issues'):
                    risk_score -= 1
                
                # Amount-based risk
                amounts = entities.get('amounts', [])
                for amt in amounts:
                    try:
                        amount_val = float(str(amt).replace(',', ''))
                        if amount_val > 10000000:  # 10M KSH
                            risk_score += 2
                        elif amount_val > 1000000:  # 1M KSH
                            risk_score += 1
                    except:
                        pass
                
                # Categorize by risk score
                if risk_score >= 3:
                    high_risk.append(doc)
                elif risk_score >= 1:
                    medium_risk.append(doc)
                else:
                    low_risk.append(doc)
            
            return {
                "high_risk_documents": len(high_risk),
                "medium_risk_documents": len(medium_risk),
                "low_risk_documents": len(low_risk),
                "overall_risk_level": "HIGH" if len(high_risk) > len(documents) * 0.1 else "MEDIUM" if len(medium_risk) > len(documents) * 0.2 else "LOW",
                "risk_distribution": {
                    "high": len(high_risk),
                    "medium": len(medium_risk),
                    "low": len(low_risk)
                },
                "risk_percentage": {
                    "high": (len(high_risk) / len(documents) * 100) if documents else 0,
                    "medium": (len(medium_risk) / len(documents) * 100) if documents else 0,
                    "low": (len(low_risk) / len(documents) * 100) if documents else 0
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Risk analysis failed: {e}")
            return {"error": str(e)}

    async def get_company_dashboard(self, company_id: str, mongo_client, postgres_conn) -> Dict[str, Any]:
        """Get company-specific dashboard"""
        try:
            db = mongo_client.vanta_ledger
            
            # Get company documents
            documents = list(db.processed_documents.find({"company": company_id}))
            
            if not documents:
                return {"error": "No documents found for company"}
            
            # Get company-specific analytics
            company_analytics = {
                "company_id": company_id,
                "timestamp": datetime.now().isoformat(),
                "document_count": len(documents),
                "financial_summary": self._get_company_financial_summary(documents),
                "compliance_status": self._get_company_compliance_status(documents),
                "processing_status": self._get_company_processing_status(documents),
                "risk_assessment": self._get_company_risk_assessment(documents),
                "recent_activity": self._get_company_recent_activity(documents)
            }
            
            logger.info(f"✅ Company dashboard generated for {company_id}")
            return company_analytics
            
        except Exception as e:
            logger.error(f"❌ Company dashboard generation failed: {e}", exc_info=True)
            return {"error": "An internal error occurred while generating the company dashboard."}

    def _get_company_financial_summary(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get company financial summary"""
        total_amount = 0
        amounts = []
        
        for doc in documents:
            doc_amounts = doc.get('entities', {}).get('amounts', [])
            for amt in doc_amounts:
                try:
                    amount_val = float(str(amt).replace(',', ''))
                    total_amount += amount_val
                    amounts.append(amount_val)
                except:
                    pass
        
        return {
            "total_value": total_amount,
            "transaction_count": len(amounts),
            "average_transaction": total_amount / len(amounts) if amounts else 0,
            "largest_transaction": max(amounts) if amounts else 0,
            "smallest_transaction": min(amounts) if amounts else 0
        }

    def _get_company_compliance_status(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get company compliance status"""
        tax_numbers = []
        compliance_issues = []
        
        for doc in documents:
            entities = doc.get('entities', {})
            tax_numbers.extend(entities.get('tax_numbers', []))
            compliance_issues.extend(entities.get('compliance_issues', []))
        
        total_docs = len(documents)
        docs_with_tax = len([doc for doc in documents if doc.get('entities', {}).get('tax_numbers')])
        
        return {
            "compliance_score": (docs_with_tax / total_docs * 100) if total_docs > 0 else 0,
            "tax_numbers_found": len(set(tax_numbers)),
            "compliance_issues": len(set(compliance_issues)),
            "status": "COMPLIANT" if not compliance_issues else "NON_COMPLIANT"
        }

    def _get_company_processing_status(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get company processing status"""
        status_counts = Counter(doc.get('processing_status', 'unknown') for doc in documents)
        doc_types = Counter(doc.get('document_type', 'unknown') for doc in documents)
        
        return {
            "processing_status": dict(status_counts),
            "document_types": dict(doc_types),
            "success_rate": (status_counts.get('success', 0) / len(documents) * 100) if documents else 0
        }

    def _get_company_risk_assessment(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get company risk assessment"""
        high_risk = 0
        medium_risk = 0
        low_risk = 0
        
        for doc in documents:
            entities = doc.get('entities', {})
            
            if entities.get('compliance_issues'):
                high_risk += 1
            elif any(float(str(amt).replace(',', '')) > 1000000 for amt in entities.get('amounts', [])):
                medium_risk += 1
            else:
                low_risk += 1
        
        return {
            "high_risk_documents": high_risk,
            "medium_risk_documents": medium_risk,
            "low_risk_documents": low_risk,
            "overall_risk_level": "HIGH" if high_risk > 0 else "MEDIUM" if medium_risk > 0 else "LOW"
        }

    def _get_company_recent_activity(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get company recent activity"""
        # Sort by processing date and get recent documents
        sorted_docs = sorted(documents, key=lambda x: x.get('processing_date', ''), reverse=True)
        
        recent_activity = []
        for doc in sorted_docs[:10]:  # Last 10 documents
            recent_activity.append({
                "filename": doc.get('filename'),
                "document_type": doc.get('document_type'),
                "processing_date": doc.get('processing_date'),
                "processing_status": doc.get('processing_status'),
                "total_amount": sum(float(str(amt).replace(',', '')) for amt in doc.get('entities', {}).get('amounts', []))
            })
        
        return recent_activity

# Global instance
analytics_dashboard = AnalyticsDashboard() 