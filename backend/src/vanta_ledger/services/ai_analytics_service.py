import os
#!/usr/bin/env python3
"""
Enhanced AI Analytics Service
Core AI features for predictive analytics and anomaly detection
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

import numpy as np
import pandas as pd
import redis
# from pymongo import MongoClient
from ..database import get_mongo_client
from pymongo.collection import Collection
from pymongo.database import Database

from ..config import settings

logger = logging.getLogger(__name__)


class EnhancedAIAnalyticsService:
    """Enhanced AI analytics service with predictive capabilities"""

    def __init__(self):
        # Database connections
        self.mongo_client = get_mongo_client()
        self.db: Database = self.mongo_client[settings.DATABASE_NAME]
        self.redis_client = redis.Redis.from_url(
            settings.REDIS_URI, decode_responses=True
        )

        # Collections
        self.invoices: Collection = self.db.invoices
        self.bills: Collection = self.db.bills
        self.payments: Collection = self.db.payments
        self.documents: Collection = self.db.documents
        self.journal_entries: Collection = self.db.journal_entries

    async def analyze_financial_trends(
        self, user_id: UUID, period_days: int = 90
    ) -> Dict[str, Any]:
        """Analyze financial trends and patterns"""
        try:
            # Get historical data
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)

            # Collect invoice data
            invoice_data = list(
                self.invoices.find(
                    {"created_at": {"$gte": start_date, "$lte": end_date}}
                )
            )

            # Collect payment data
            payment_data = list(
                self.payments.find(
                    {"payment_date": {"$gte": start_date, "$lte": end_date}}
                )
            )

            # Analyze trends
            trends = await self._analyze_revenue_trends(invoice_data, payment_data)
            patterns = await self._analyze_payment_patterns(payment_data)

            return {
                "success": True,
                "analysis": {
                    "trends": trends,
                    "patterns": patterns,
                    "period": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "days": period_days,
                    },
                },
            }

        except Exception as e:
            logger.error(f"Error analyzing financial trends: {str(e)}")
            raise

    async def predict_financial_metrics(
        self, user_id: UUID, forecast_periods: int = 12
    ) -> Dict[str, Any]:
        """Predict future financial metrics"""
        try:
            # Get historical data for prediction
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=365)  # 1 year of data

            # Collect historical metrics
            historical_data = await self._get_historical_metrics(start_date, end_date)

            # Generate predictions
            revenue_forecast = await self._forecast_revenue(
                historical_data, forecast_periods
            )

            return {
                "success": True,
                "predictions": {
                    "revenue_forecast": revenue_forecast,
                    "forecast_periods": forecast_periods,
                    "confidence_level": 0.85,
                },
            }

        except Exception as e:
            logger.error(f"Error predicting financial metrics: {str(e)}")
            raise

    async def detect_anomalies(
        self, user_id: UUID, data_type: str = "all"
    ) -> Dict[str, Any]:
        """Detect anomalies in financial data and documents"""
        try:
            anomalies = {
                "financial_anomalies": [],
                "document_anomalies": [],
                "payment_anomalies": [],
            }

            if data_type in ["all", "financial"]:
                financial_anomalies = await self._detect_financial_anomalies()
                anomalies["financial_anomalies"] = financial_anomalies

            if data_type in ["all", "documents"]:
                document_anomalies = await self._detect_document_anomalies()
                anomalies["document_anomalies"] = document_anomalies

            if data_type in ["all", "payments"]:
                payment_anomalies = await self._detect_payment_anomalies()
                anomalies["payment_anomalies"] = payment_anomalies

            return {
                "success": True,
                "anomalies": anomalies,
                "detection_timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            raise

    async def generate_financial_insights(self, user_id: UUID) -> Dict[str, Any]:
        """Generate comprehensive financial insights"""
        try:
            # Get current financial state
            current_state = await self._get_current_financial_state()

            # Analyze performance metrics
            performance_metrics = await self._analyze_performance_metrics()

            # Generate recommendations
            recommendations = await self._generate_recommendations(
                current_state, performance_metrics
            )

            return {
                "success": True,
                "insights": {
                    "current_state": current_state,
                    "performance_metrics": performance_metrics,
                    "recommendations": recommendations,
                    "generated_at": datetime.utcnow().isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Error generating financial insights: {str(e)}")
            raise

    async def _analyze_revenue_trends(
        self, invoice_data: List[Dict], payment_data: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze revenue trends"""
        try:
            if not invoice_data:
                return {"message": "No invoice data available for analysis"}

            # Convert to pandas DataFrame for analysis
            df_invoices = pd.DataFrame(invoice_data)
            df_invoices["invoice_date"] = pd.to_datetime(df_invoices["invoice_date"])

            # Monthly revenue aggregation
            monthly_revenue = df_invoices.groupby(
                df_invoices["invoice_date"].dt.to_period("M")
            )["total_amount"].sum()

            # Calculate trend metrics
            if len(monthly_revenue) > 1:
                trend_direction = (
                    "increasing"
                    if monthly_revenue.iloc[-1] > monthly_revenue.iloc[-2]
                    else "decreasing"
                )
                growth_rate = (
                    (monthly_revenue.iloc[-1] - monthly_revenue.iloc[-2])
                    / monthly_revenue.iloc[-2]
                ) * 100
            else:
                trend_direction = "stable"
                growth_rate = 0

            return {
                "monthly_revenue": monthly_revenue.to_dict(),
                "trend_direction": trend_direction,
                "growth_rate_percent": round(growth_rate, 2),
                "average_monthly_revenue": round(monthly_revenue.mean(), 2),
                "revenue_volatility": round(monthly_revenue.std(), 2),
            }

        except Exception as e:
            logger.error(f"Error analyzing revenue trends: {str(e)}")
            return {"error": str(e)}

    async def _analyze_payment_patterns(
        self, payment_data: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze payment patterns"""
        try:
            if not payment_data:
                return {"message": "No payment data available for analysis"}

            df_payments = pd.DataFrame(payment_data)
            df_payments["payment_date"] = pd.to_datetime(df_payments["payment_date"])

            # Payment method analysis
            payment_methods = df_payments["payment_type"].value_counts().to_dict()

            # Monthly payment patterns
            monthly_payments = df_payments.groupby(
                df_payments["payment_date"].dt.to_period("M")
            )["amount"].sum()

            return {
                "payment_methods": payment_methods,
                "monthly_payments": monthly_payments.to_dict(),
                "total_payments": len(payment_data),
                "average_payment_amount": round(df_payments["amount"].mean(), 2),
            }

        except Exception as e:
            logger.error(f"Error analyzing payment patterns: {str(e)}")
            return {"error": str(e)}

    async def _get_historical_metrics(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Get historical financial metrics"""
        try:
            # Get invoices in date range
            invoices = list(
                self.invoices.find(
                    {"invoice_date": {"$gte": start_date, "$lte": end_date}}
                )
            )

            # Get payments in date range
            payments = list(
                self.payments.find(
                    {"payment_date": {"$gte": start_date, "$lte": end_date}}
                )
            )

            # Calculate monthly metrics
            monthly_metrics = {}

            for invoice in invoices:
                month_key = invoice["invoice_date"].strftime("%Y-%m")
                if month_key not in monthly_metrics:
                    monthly_metrics[month_key] = {
                        "revenue": 0,
                        "payments": 0,
                        "invoice_count": 0,
                        "payment_count": 0,
                    }
                monthly_metrics[month_key]["revenue"] += float(invoice["total_amount"])
                monthly_metrics[month_key]["invoice_count"] += 1

            for payment in payments:
                month_key = payment["payment_date"].strftime("%Y-%m")
                if month_key not in monthly_metrics:
                    monthly_metrics[month_key] = {
                        "revenue": 0,
                        "payments": 0,
                        "invoice_count": 0,
                        "payment_count": 0,
                    }
                monthly_metrics[month_key]["payments"] += float(payment["amount"])
                monthly_metrics[month_key]["payment_count"] += 1

            return {
                "monthly_metrics": monthly_metrics,
                "total_revenue": sum(float(inv["total_amount"]) for inv in invoices),
                "total_payments": sum(float(pay["amount"]) for pay in payments),
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Error getting historical metrics: {str(e)}")
            raise

    async def _forecast_revenue(
        self, historical_data: Dict[str, Any], periods: int
    ) -> Dict[str, Any]:
        """Forecast future revenue using simple moving average"""
        try:
            monthly_metrics = historical_data["monthly_metrics"]

            if not monthly_metrics:
                return {"message": "Insufficient data for revenue forecasting"}

            # Extract revenue data
            revenue_data = [metrics["revenue"] for metrics in monthly_metrics.values()]

            if len(revenue_data) < 3:
                return {"message": "Need at least 3 months of data for forecasting"}

            # Simple moving average forecast
            window_size = min(3, len(revenue_data))
            moving_average = sum(revenue_data[-window_size:]) / window_size

            # Generate forecast
            forecast = []
            for i in range(periods):
                forecast.append(
                    round(moving_average * (1 + 0.02 * i), 2)
                )  # 2% growth assumption

            return {
                "forecast_values": forecast,
                "method": "moving_average",
                "window_size": window_size,
                "last_actual_value": revenue_data[-1] if revenue_data else 0,
                "confidence_interval": 0.85,
            }

        except Exception as e:
            logger.error(f"Error forecasting revenue: {str(e)}")
            return {"error": str(e)}

    async def _detect_financial_anomalies(self) -> List[Dict[str, Any]]:
        """Detect financial anomalies"""
        try:
            anomalies = []

            # Get recent invoices
            recent_invoices = list(
                self.invoices.find(
                    {"invoice_date": {"$gte": datetime.utcnow() - timedelta(days=30)}}
                )
            )

            if recent_invoices:
                # Calculate average invoice amount
                amounts = [float(inv["total_amount"]) for inv in recent_invoices]
                avg_amount = np.mean(amounts)
                std_amount = np.std(amounts)

                # Detect outliers (2 standard deviations from mean)
                threshold = avg_amount + (2 * std_amount)

                for invoice in recent_invoices:
                    if float(invoice["total_amount"]) > threshold:
                        anomalies.append(
                            {
                                "type": "high_value_invoice",
                                "severity": "medium",
                                "description": f"Invoice {invoice['invoice_number']} has unusually high value",
                                "value": float(invoice["total_amount"]),
                                "threshold": round(threshold, 2),
                                "date": invoice["invoice_date"].isoformat(),
                                "recommendation": "Review invoice for accuracy and approval",
                            }
                        )

            # Detect overdue invoices
            overdue_invoices = list(
                self.invoices.find(
                    {
                        "due_date": {"$lt": datetime.utcnow()},
                        "status": {"$in": ["sent", "viewed"]},
                    }
                )
            )

            for invoice in overdue_invoices:
                days_overdue = (datetime.utcnow() - invoice["due_date"]).days
                if days_overdue > 30:
                    anomalies.append(
                        {
                            "type": "severely_overdue_invoice",
                            "severity": "high",
                            "description": f"Invoice {invoice['invoice_number']} is {days_overdue} days overdue",
                            "days_overdue": days_overdue,
                            "amount": float(invoice["total_amount"]),
                            "date": invoice["due_date"].isoformat(),
                            "recommendation": "Follow up with customer immediately",
                        }
                    )

            return anomalies

        except Exception as e:
            logger.error(f"Error detecting financial anomalies: {str(e)}")
            return []

    async def _detect_document_anomalies(self) -> List[Dict[str, Any]]:
        """Detect document anomalies"""
        try:
            anomalies = []

            # Get recent documents
            recent_documents = list(
                self.documents.find(
                    {"created_at": {"$gte": datetime.utcnow() - timedelta(days=7)}}
                )
            )

            if recent_documents:
                # Detect unusually large files
                file_sizes = [doc["file_size"] for doc in recent_documents]
                avg_size = np.mean(file_sizes)
                std_size = np.std(file_sizes)

                threshold = avg_size + (2 * std_size)

                for doc in recent_documents:
                    if doc["file_size"] > threshold:
                        anomalies.append(
                            {
                                "type": "large_file",
                                "severity": "low",
                                "description": f"Document {doc['original_filename']} is unusually large",
                                "file_size_mb": round(
                                    doc["file_size"] / (1024 * 1024), 2
                                ),
                                "threshold_mb": round(threshold / (1024 * 1024), 2),
                                "date": doc["created_at"].isoformat(),
                                "recommendation": "Consider file compression or alternative format",
                            }
                        )

            # Detect processing errors
            error_documents = list(
                self.documents.find(
                    {
                        "status": "error",
                        "created_at": {"$gte": datetime.utcnow() - timedelta(days=1)},
                    }
                )
            )

            for doc in error_documents:
                anomalies.append(
                    {
                        "type": "processing_error",
                        "severity": "medium",
                        "description": f"Document {doc['original_filename']} failed to process",
                        "errors": doc.get("processing_errors", []),
                        "date": doc["created_at"].isoformat(),
                        "recommendation": "Review document format and retry processing",
                    }
                )

            return anomalies

        except Exception as e:
            logger.error(f"Error detecting document anomalies: {str(e)}")
            return []

    async def _detect_payment_anomalies(self) -> List[Dict[str, Any]]:
        """Detect payment anomalies"""
        try:
            anomalies = []

            # Get recent payments
            recent_payments = list(
                self.payments.find(
                    {"payment_date": {"$gte": datetime.utcnow() - timedelta(days=30)}}
                )
            )

            if recent_payments:
                # Detect unusual payment amounts
                amounts = [float(pay["amount"]) for pay in recent_payments]
                avg_amount = np.mean(amounts)
                std_amount = np.std(amounts)

                threshold = avg_amount + (2 * std_amount)

                for payment in recent_payments:
                    if float(payment["amount"]) > threshold:
                        anomalies.append(
                            {
                                "type": "high_value_payment",
                                "severity": "medium",
                                "description": f"Payment {payment['payment_number']} has unusually high value",
                                "amount": float(payment["amount"]),
                                "threshold": round(threshold, 2),
                                "date": payment["payment_date"].isoformat(),
                                "recommendation": "Verify payment details and approval",
                            }
                        )

            return anomalies

        except Exception as e:
            logger.error(f"Error detecting payment anomalies: {str(e)}")
            return []

    async def _get_current_financial_state(self) -> Dict[str, Any]:
        """Get current financial state"""
        try:
            # Get current month data
            current_month_start = datetime.utcnow().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )

            # Current month invoices
            current_invoices = list(
                self.invoices.find({"invoice_date": {"$gte": current_month_start}})
            )

            # Current month payments
            current_payments = list(
                self.payments.find({"payment_date": {"$gte": current_month_start}})
            )

            # Calculate metrics
            total_revenue = sum(float(inv["total_amount"]) for inv in current_invoices)
            total_payments = sum(float(pay["amount"]) for pay in current_payments)

            # Outstanding invoices
            outstanding_invoices = list(
                self.invoices.find(
                    {
                        "status": {"$in": ["sent", "viewed"]},
                        "due_date": {"$lt": datetime.utcnow()},
                    }
                )
            )

            outstanding_amount = sum(
                float(inv["balance_due"]) for inv in outstanding_invoices
            )

            return {
                "current_month_revenue": round(total_revenue, 2),
                "current_month_payments": round(total_payments, 2),
                "outstanding_amount": round(outstanding_amount, 2),
                "outstanding_invoices_count": len(outstanding_invoices),
                "current_month_invoices_count": len(current_invoices),
                "current_month_payments_count": len(current_payments),
            }

        except Exception as e:
            logger.error(f"Error getting current financial state: {str(e)}")
            raise

    async def _analyze_performance_metrics(self) -> Dict[str, Any]:
        """Analyze performance metrics"""
        try:
            # Get last 12 months data
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=365)

            invoices = list(
                self.invoices.find(
                    {"invoice_date": {"$gte": start_date, "$lte": end_date}}
                )
            )

            payments = list(
                self.payments.find(
                    {"payment_date": {"$gte": start_date, "$lte": end_date}}
                )
            )

            # Calculate metrics
            total_revenue = sum(float(inv["total_amount"]) for inv in invoices)
            total_payments = sum(float(pay["amount"]) for pay in payments)

            # Payment efficiency
            payment_efficiency = (
                (total_payments / total_revenue * 100) if total_revenue > 0 else 0
            )

            # Average invoice value
            avg_invoice_value = total_revenue / len(invoices) if invoices else 0

            return {
                "annual_revenue": round(total_revenue, 2),
                "annual_payments": round(total_payments, 2),
                "payment_efficiency_percent": round(payment_efficiency, 2),
                "average_invoice_value": round(avg_invoice_value, 2),
                "total_invoices": len(invoices),
                "total_payments": len(payments),
            }

        except Exception as e:
            logger.error(f"Error analyzing performance metrics: {str(e)}")
            raise

    async def _generate_recommendations(
        self, current_state: Dict[str, Any], performance_metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate financial recommendations"""
        try:
            recommendations = []

            # Revenue recommendations
            if (
                current_state["current_month_revenue"]
                < performance_metrics["annual_revenue"] / 12
            ):
                recommendations.append(
                    {
                        "category": "revenue",
                        "priority": "high",
                        "title": "Increase Revenue Generation",
                        "description": "Current month revenue is below monthly average",
                        "action": "Review sales pipeline and marketing strategies",
                        "expected_impact": "Increase monthly revenue by 15-20%",
                    }
                )

            # Payment efficiency recommendations
            if performance_metrics["payment_efficiency_percent"] < 80:
                recommendations.append(
                    {
                        "category": "collections",
                        "priority": "medium",
                        "title": "Improve Payment Collections",
                        "description": f"Payment efficiency is {performance_metrics['payment_efficiency_percent']}%",
                        "action": "Implement automated payment reminders and follow-up procedures",
                        "expected_impact": "Improve payment efficiency to 85%+",
                    }
                )

            # Outstanding invoices recommendations
            if (
                current_state["outstanding_amount"]
                > current_state["current_month_revenue"] * 0.5
            ):
                recommendations.append(
                    {
                        "category": "collections",
                        "priority": "high",
                        "title": "Address Outstanding Invoices",
                        "description": f"Outstanding amount is {current_state['outstanding_amount']}",
                        "action": "Prioritize collection of overdue invoices",
                        "expected_impact": "Reduce outstanding amount by 30%",
                    }
                )

            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []


# Global instance
enhanced_ai_analytics_service = EnhancedAIAnalyticsService()
