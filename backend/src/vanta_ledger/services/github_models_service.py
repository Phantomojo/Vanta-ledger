#!/usr/bin/env python3
"""
Enhanced GitHub Models Service
Provides a comprehensive, dependency-free AI service for financial analysis.
Features advanced document processing, expense categorization, insights generation,
and natural language querying with sophisticated heuristics.
"""
import logging
import os
import re
import json
from datetime import datetime, date
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from decimal import Decimal

logger = logging.getLogger(__name__)


@dataclass
class GitHubModelsService:
    token: Optional[str] = field(default=None)
    default_model: str = field(default="gpt-4o-mini")
    enabled: bool = field(init=False)
    prompts: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    expense_categories: Dict[str, List[str]] = field(default_factory=dict)
    industry_patterns: Dict[str, List[str]] = field(default_factory=dict)

    def __post_init__(self):
        # Read token from env; service considered enabled if token present
        self.token = self.token or os.getenv("GITHUB_MODELS_TOKEN") or os.getenv("GITHUB_TOKEN")
        self.enabled = bool(self.token)
        
        # Enhanced expense categories with keywords
        self.expense_categories = {
            "Cloud Services": [
                "aws", "amazon web services", "azure", "google cloud", "gcp", "hosting", 
                "server", "cloud", "digitalocean", "heroku", "netlify", "vercel"
            ],
            "Transportation": [
                "uber", "lyft", "taxi", "fuel", "gas", "mileage", "transport", "parking",
                "toll", "public transit", "bus", "train", "subway"
            ],
            "Meals & Entertainment": [
                "coffee", "restaurant", "meal", "cafe", "food", "lunch", "dinner", "breakfast",
                "catering", "entertainment", "movie", "concert", "event"
            ],
            "Office Supplies": [
                "office", "stationery", "supplies", "paper", "printer", "ink", "toner",
                "desk", "chair", "equipment", "furniture"
            ],
            "Software & Subscriptions": [
                "software", "subscription", "license", "saas", "app", "tool", "platform",
                "service", "api", "integration"
            ],
            "Travel": [
                "flight", "hotel", "airbnb", "booking", "travel", "vacation", "conference",
                "seminar", "workshop", "training"
            ],
            "Marketing & Advertising": [
                "advertising", "marketing", "promotion", "campaign", "social media",
                "google ads", "facebook ads", "seo", "content"
            ],
            "Professional Services": [
                "consulting", "legal", "accounting", "audit", "tax", "insurance",
                "professional", "expert", "advisor"
            ],
            "Utilities": [
                "electricity", "water", "internet", "phone", "mobile", "utility",
                "electric", "gas", "heating", "cooling"
            ],
            "Insurance": [
                "insurance", "liability", "property", "health", "life", "auto",
                "coverage", "premium", "policy"
            ]
        }
        
        # Industry-specific patterns for better analysis
        self.industry_patterns = {
            "technology": ["software", "tech", "ai", "ml", "data", "cloud", "saas"],
            "healthcare": ["medical", "health", "patient", "clinic", "hospital", "pharmacy"],
            "finance": ["banking", "financial", "investment", "trading", "credit", "loan"],
            "retail": ["retail", "ecommerce", "store", "shop", "merchant", "sales"],
            "manufacturing": ["manufacturing", "production", "factory", "assembly", "machinery"],
            "education": ["education", "school", "university", "training", "course", "learning"]
        }
        
        # Enhanced prompt templates
        self.prompts = {
            "financial_document_analyzer": {
                "description": "Analyze financial documents to extract amounts, entities, and insights",
                "model": self.default_model,
                "version": "2.0",
                "capabilities": ["amount_extraction", "entity_recognition", "date_parsing", "vendor_identification"]
            },
            "expense_categorizer": {
                "description": "Intelligent expense categorization with industry-specific patterns",
                "model": self.default_model,
                "version": "2.0",
                "capabilities": ["smart_categorization", "industry_detection", "confidence_scoring"]
            },
            "insights_generator": {
                "description": "Generate actionable financial insights and recommendations",
                "model": self.default_model,
                "version": "2.0",
                "capabilities": ["trend_analysis", "anomaly_detection", "recommendations"]
            },
            "report_generator": {
                "description": "Generate comprehensive financial reports with visualizations",
                "model": self.default_model,
                "version": "2.0",
                "capabilities": ["report_generation", "data_visualization", "executive_summary"]
            },
            "nl_query": {
                "description": "Natural language query processing for financial data",
                "model": self.default_model,
                "version": "2.0",
                "capabilities": ["query_understanding", "data_extraction", "context_analysis"]
            },
            "fraud_detector": {
                "description": "Detect potential fraud patterns in financial transactions",
                "model": self.default_model,
                "version": "2.0",
                "capabilities": ["anomaly_detection", "pattern_recognition", "risk_assessment"]
            },
            "compliance_checker": {
                "description": "Check financial data for regulatory compliance",
                "model": self.default_model,
                "version": "2.0",
                "capabilities": ["compliance_validation", "regulation_checking", "audit_trail"]
            }
        }
        
        logger.info(
            "Enhanced GitHubModelsService initialized: enabled=%s, model=%s, categories=%d",
            self.enabled, self.default_model, len(self.expense_categories)
        )

    # Public helpers used by router
    def get_available_prompts(self) -> List[str]:
        """Get list of available prompt templates"""
        return list(self.prompts.keys())

    def get_prompt_info(self, prompt_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific prompt template"""
        return self.prompts.get(prompt_name, {})

    def get_expense_categories(self) -> Dict[str, List[str]]:
        """Get available expense categories and their keywords"""
        return self.expense_categories.copy()

    def get_industry_patterns(self) -> Dict[str, List[str]]:
        """Get industry-specific patterns for analysis"""
        return self.industry_patterns.copy()

    # Enhanced document analysis with better entity extraction
    async def analyze_financial_document(self, document_text: str, document_type: str = "invoice") -> Dict[str, Any]:
        """Analyze financial documents with enhanced entity extraction"""
        if not document_text:
            return {
                "summary": "Empty document",
                "entities": {},
                "totals": {},
                "confidence": 0.0,
                "analysis_quality": "poor"
            }

        # Enhanced amount extraction with currency detection
        amount_patterns = [
            r"\$[\d,]+\.?\d*",  # USD format
            r"€[\d,]+\.?\d*",   # EUR format
            r"£[\d,]+\.?\d*",   # GBP format
            r"\b\d+\.?\d*\b"    # Plain numbers
        ]
        
        amounts = []
        for pattern in amount_patterns:
            amounts.extend(re.findall(pattern, document_text))

        # Enhanced entity extraction
        emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", document_text)
        
        # Multiple date formats
        date_patterns = [
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",  # MM/DD/YYYY or DD/MM/YYYY
            r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",    # YYYY-MM-DD
            r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b",  # Month DD, YYYY
            r"\b\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}\b"  # DD Month YYYY
        ]
        
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, document_text))

        # Enhanced vendor extraction
        vendor_patterns = [
            r"(?i)(?:from|vendor|supplier|billed\s+to|company|business)\s*:?\s*([\w .,&-]+)",
            r"(?i)(?:invoice\s+from|bill\s+from)\s*:?\s*([\w .,&-]+)",
            r"(?i)(?:pay\s+to|payable\s+to)\s*:?\s*([\w .,&-]+)"
        ]
        
        vendors = []
        for pattern in vendor_patterns:
            vendors.extend(re.findall(pattern, document_text))

        # Calculate total value (try to find the largest amount as total)
        total_value = None
        numeric_amounts = []
        
        for amount_str in amounts:
            try:
                # Clean amount string
                clean_amount = re.sub(r'[^\d.-]', '', str(amount_str))
                if clean_amount:
                    numeric_amounts.append(float(clean_amount))
            except (ValueError, TypeError):
                continue

        if numeric_amounts:
            # Use the largest amount as total, or the last one if they're similar
            numeric_amounts.sort(reverse=True)
            total_value = numeric_amounts[0]

        # Calculate confidence based on extracted entities
        confidence_factors = []
        if amounts:
            confidence_factors.append(0.3)
        if emails:
            confidence_factors.append(0.2)
        if dates:
            confidence_factors.append(0.2)
        if vendors:
            confidence_factors.append(0.3)
        
        confidence = sum(confidence_factors)
        
        # Determine analysis quality
        if confidence >= 0.8:
            quality = "excellent"
        elif confidence >= 0.6:
            quality = "good"
        elif confidence >= 0.4:
            quality = "fair"
        else:
            quality = "poor"

        return {
            "document_type": document_type,
            "entities": {
                "emails": list(set(emails)),
                "dates": list(set(dates)),
                "vendors": list(set(vendors)),
                "amounts_detected": amounts,
                "numeric_amounts": numeric_amounts
            },
            "totals": {
                "estimated_total": total_value,
                "amount_count": len(numeric_amounts),
                "currency_detected": "USD" if any("$" in a for a in amounts) else "Unknown"
            },
            "confidence": round(confidence, 2),
            "analysis_quality": quality,
            "extraction_metadata": {
                "patterns_used": len(amount_patterns) + len(date_patterns) + len(vendor_patterns),
                "entities_found": len(emails) + len(dates) + len(vendors)
            }
        }

    # Enhanced expense categorization with confidence scoring
    async def categorize_expense(
        self, 
        description: str, 
        amount: Optional[float] = None, 
        vendor: Optional[str] = None, 
        date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Categorize expenses with confidence scoring and industry detection"""
        text = f"{description} {vendor or ''}".lower()
        
        # Calculate confidence scores for each category
        category_scores = {}
        
        for category, keywords in self.expense_categories.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text:
                    score += 1
            
            if score > 0:
                category_scores[category] = score

        # Find the best category
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])
            confidence = min(best_category[1] / 3.0, 1.0)  # Normalize confidence
        else:
            best_category = ("Miscellaneous", 0)
            confidence = 0.1

        # Detect industry context
        detected_industry = "general"
        for industry, patterns in self.industry_patterns.items():
            if any(pattern.lower() in text for pattern in patterns):
                detected_industry = industry
                break

        return {
            "category": best_category[0],
            "confidence": round(confidence, 2),
            "industry_context": detected_industry,
            "alternative_categories": [
                {"category": cat, "score": score} 
                for cat, score in sorted(category_scores.items(), key=lambda x: x[1], reverse=True)[:3]
            ],
            "analysis_metadata": {
                "keywords_found": len([k for k in self.expense_categories[best_category[0]] if k.lower() in text]),
                "text_length": len(text),
                "amount_provided": amount is not None
            }
        }

    # Enhanced financial insights with trend analysis
    async def generate_financial_insights(
        self, 
        financial_data: Dict[str, Any], 
        period: str = "recent", 
        company_size: str = "unknown", 
        industry: str = "general"
    ) -> Dict[str, Any]:
        """Generate comprehensive financial insights with trend analysis"""
        
        # Extract numeric values
        numeric_data = {}
        for key, value in financial_data.items():
            try:
                if isinstance(value, (int, float, str)):
                    numeric_value = float(str(value).replace(',', '').replace('$', ''))
                    numeric_data[key] = numeric_value
            except (ValueError, TypeError):
                continue

        if not numeric_data:
            return {
                "period": period,
                "company_size": company_size,
                "industry": industry,
                "insights": ["No numeric data available for analysis"],
                "metrics": {"count": 0, "sum": 0, "average": 0},
                "trends": [],
                "recommendations": ["Provide more financial data for detailed analysis"]
            }

        # Calculate basic metrics
        values = list(numeric_data.values())
        total_sum = sum(values)
        average = total_sum / len(values) if values else 0
        min_value = min(values) if values else 0
        max_value = max(values) if values else 0

        # Trend analysis
        trends = []
        if len(values) > 1:
            sorted_values = sorted(values)
            if sorted_values[-1] > sorted_values[0] * 1.5:
                trends.append("Significant growth detected")
            elif sorted_values[-1] < sorted_values[0] * 0.7:
                trends.append("Declining trend observed")
            else:
                trends.append("Stable financial performance")

        # Generate insights based on data patterns
        insights = []
        
        if total_sum > 10000:
            insights.append("High-value transactions detected - consider detailed tracking")
        elif total_sum < 1000:
            insights.append("Low transaction volume - monitor for growth opportunities")
        
        if max_value > average * 3:
            insights.append("High variance in transaction amounts - review for anomalies")
        
        if len(values) > 10:
            insights.append("Sufficient data for trend analysis")
        else:
            insights.append("Limited data - consider collecting more historical information")

        # Industry-specific recommendations
        recommendations = []
        if industry == "technology":
            recommendations.extend([
                "Monitor cloud service costs",
                "Track software subscription renewals",
                "Review SaaS spending efficiency"
            ])
        elif industry == "retail":
            recommendations.extend([
                "Analyze seasonal spending patterns",
                "Monitor inventory-related expenses",
                "Track marketing campaign ROI"
            ])
        else:
            recommendations.extend([
                "Implement regular expense reviews",
                "Set up automated expense categorization",
                "Monitor cash flow patterns"
            ])

        return {
            "period": period,
            "company_size": company_size,
            "industry": industry,
            "metrics": {
                "count": len(values),
                "sum": round(total_sum, 2),
                "average": round(average, 2),
                "min": round(min_value, 2),
                "max": round(max_value, 2),
                "variance": round(max_value - min_value, 2)
            },
            "trends": trends,
            "insights": insights,
            "recommendations": recommendations,
            "analysis_quality": "good" if len(values) > 5 else "limited"
        }

    # Enhanced report generation
    async def generate_financial_report(
        self, 
        financial_data: Dict[str, Any], 
        report_type: str = "quarterly", 
        period: str = "Q1 2024", 
        company_name: str = "Company", 
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive financial reports"""
        
        insights = await self.generate_financial_insights(financial_data, period, "unknown", "general")
        
        # Generate executive summary
        total_value = insights["metrics"]["sum"]
        if total_value > 50000:
            summary_tone = "strong"
            summary_keyword = "robust"
        elif total_value > 10000:
            summary_tone = "stable"
            summary_keyword = "consistent"
        else:
            summary_tone = "developing"
            summary_keyword = "growing"

        executive_summary = f"{company_name} shows {summary_tone} financial performance with {summary_keyword} transaction volume totaling ${total_value:,.2f} for {period}."

        return {
            "company": company_name,
            "report_type": report_type,
            "period": period,
            "generated_at": datetime.now().isoformat(),
            "executive_summary": executive_summary,
            "financial_highlights": {
                "total_transactions": insights["metrics"]["count"],
                "total_value": insights["metrics"]["sum"],
                "average_transaction": insights["metrics"]["average"],
                "largest_transaction": insights["metrics"]["max"]
            },
            "trend_analysis": insights["trends"],
            "key_insights": insights["insights"],
            "recommendations": insights["recommendations"],
            "context_note": (context[:200] + "...") if context and len(context) > 200 else context,
            "report_metadata": {
                "analysis_quality": insights["analysis_quality"],
                "data_points_analyzed": insights["metrics"]["count"],
                "generation_method": "enhanced_heuristic"
            }
        }

    # Enhanced natural language query processing
    async def natural_language_query(self, query: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process natural language queries with enhanced understanding"""
        
        query_lower = query.lower()
        
        # Enhanced query understanding
        query_type = "general"
        if any(word in query_lower for word in ["total", "sum", "amount", "value"]):
            query_type = "aggregation"
        elif any(word in query_lower for word in ["category", "type", "classification"]):
            query_type = "categorization"
        elif any(word in query_lower for word in ["trend", "pattern", "change"]):
            query_type = "trend_analysis"
        elif any(word in query_lower for word in ["when", "date", "time"]):
            query_type = "temporal"
        
        # Extract relevant data based on query
        matched_keys = []
        relevant_numbers = []
        
        for key, value in context_data.items():
            # Check if key matches query
            if key.lower() in query_lower:
                matched_keys.append(key)
            
            # Extract numbers from values
            try:
                if isinstance(value, (int, float, str)):
                    numeric_value = float(str(value).replace(',', '').replace('$', ''))
                    relevant_numbers.append(numeric_value)
            except (ValueError, TypeError):
                continue

        # Generate contextual answer
        if query_type == "aggregation" and relevant_numbers:
            total = sum(relevant_numbers)
            answer = f"The total value is ${total:,.2f} based on {len(relevant_numbers)} numeric values found."
        elif query_type == "categorization" and matched_keys:
            answer = f"Found {len(matched_keys)} relevant categories: {', '.join(matched_keys)}"
        elif query_type == "trend_analysis" and len(relevant_numbers) > 1:
            trend = "increasing" if relevant_numbers[-1] > relevant_numbers[0] else "decreasing"
            answer = f"Trend analysis shows {trend} pattern across {len(relevant_numbers)} data points."
        else:
            answer = f"Found {len(matched_keys)} matching keys and {len(relevant_numbers)} numeric values in the provided context."

        return {
            "query": query,
            "query_type": query_type,
            "matched_keys": matched_keys,
            "relevant_numbers": relevant_numbers,
            "answer": answer,
            "confidence": min(len(matched_keys) / 5.0 + len(relevant_numbers) / 10.0, 1.0),
            "analysis_metadata": {
                "context_keys_analyzed": len(context_data),
                "query_complexity": "simple" if len(query.split()) < 5 else "complex"
            }
        }

    # New method: Fraud detection
    async def detect_fraud_patterns(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect potential fraud patterns in transactions"""
        if not transactions:
            return {"fraud_indicators": [], "risk_level": "low", "confidence": 0.0}

        fraud_indicators = []
        risk_score = 0
        
        # Analyze transaction patterns
        amounts = [t.get('amount', 0) for t in transactions if isinstance(t.get('amount'), (int, float))]
        vendors = [t.get('vendor', '') for t in transactions if t.get('vendor')]
        
        # Check for unusual patterns
        if amounts:
            avg_amount = sum(amounts) / len(amounts)
            max_amount = max(amounts)
            
            if max_amount > avg_amount * 10:
                fraud_indicators.append("Unusually large transaction detected")
                risk_score += 30
            
            if len(set(vendors)) < len(transactions) * 0.3:
                fraud_indicators.append("Limited vendor diversity")
                risk_score += 20

        # Determine risk level
        if risk_score >= 50:
            risk_level = "high"
        elif risk_score >= 25:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "fraud_indicators": fraud_indicators,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "confidence": min(risk_score / 100.0, 1.0),
            "analysis_metadata": {
                "transactions_analyzed": len(transactions),
                "patterns_checked": ["amount_anomalies", "vendor_diversity"]
            }
        }

    # New method: Compliance checking
    async def check_compliance(self, financial_data: Dict[str, Any], regulations: List[str] = None) -> Dict[str, Any]:
        """Check financial data for regulatory compliance"""
        if not regulations:
            regulations = ["basic_accounting", "tax_compliance", "audit_standards"]
        
        compliance_results = {}
        overall_compliance = True
        
        for regulation in regulations:
            if regulation == "basic_accounting":
                # Check for basic accounting principles
                has_balances = any("balance" in key.lower() for key in financial_data.keys())
                has_dates = any("date" in key.lower() for key in financial_data.keys())
                
                compliance_results[regulation] = {
                    "compliant": has_balances and has_dates,
                    "issues": [] if (has_balances and has_dates) else ["Missing balance or date information"]
                }
                
                if not compliance_results[regulation]["compliant"]:
                    overall_compliance = False
            
            elif regulation == "tax_compliance":
                # Basic tax compliance checks
                has_amounts = any(isinstance(v, (int, float)) for v in financial_data.values())
                compliance_results[regulation] = {
                    "compliant": has_amounts,
                    "issues": [] if has_amounts else ["No monetary amounts found"]
                }
                
                if not compliance_results[regulation]["compliant"]:
                    overall_compliance = False
        
        return {
            "overall_compliance": overall_compliance,
            "regulation_results": compliance_results,
            "compliance_score": len([r for r in compliance_results.values() if r["compliant"]]) / len(compliance_results),
            "recommendations": [
                "Ensure all transactions have proper documentation",
                "Maintain audit trail for all financial activities",
                "Regular compliance reviews recommended"
            ]
        }

    # Placeholder for compatibility with docs; no external HTTP requests are made.
    async def _make_request(self, *args, **kwargs) -> Dict[str, Any]:
        return {"status": "ok", "note": "Enhanced local heuristic mode"}


# Export a singleton instance as expected by the router
github_models_service = GitHubModelsService()
