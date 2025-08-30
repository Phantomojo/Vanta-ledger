#!/usr/bin/env python3
"""
Lightweight GitHub Models Service
Provides a safe, dependency-free facade used by routes/github_models.py.
If no token/config is provided, the service remains disabled but imports cleanly.
When enabled, methods perform simple heuristic processing locally without calling external APIs.
"""
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class GitHubModelsService:
    token: Optional[str] = field(default=None)
    default_model: str = field(default="gpt-4o-mini")
    enabled: bool = field(init=False)
    prompts: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self):
        # Read token from env; service considered enabled if token present
        self.token = self.token or os.getenv("GITHUB_MODELS_TOKEN") or os.getenv("GITHUB_TOKEN")
        self.enabled = bool(self.token)
        # Provide a small set of built-in prompt templates (metadata only)
        self.prompts = {
            "financial_document_analyzer": {
                "description": "Analyze financial documents to extract amounts and entities.",
                "model": self.default_model,
                "version": "1.0",
            },
            "expense_categorizer": {
                "description": "Categorize expenses based on description and vendor.",
                "model": self.default_model,
                "version": "1.0",
            },
            "insights_generator": {
                "description": "Generate simple insights from financial data.",
                "model": self.default_model,
                "version": "1.0",
            },
            "report_generator": {
                "description": "Summarize data into a synthetic report.",
                "model": self.default_model,
                "version": "1.0",
            },
            "nl_query": {
                "description": "Answer simple questions about provided context data.",
                "model": self.default_model,
                "version": "1.0",
            },
        }
        logger.info(
            "GitHubModelsService initialized: enabled=%s, model=%s", self.enabled, self.default_model
        )

    # Public helpers used by router
    def get_available_prompts(self) -> List[str]:
        return list(self.prompts.keys())

    def get_prompt_info(self, prompt_name: str) -> Dict[str, Any]:
        return self.prompts.get(prompt_name, {})

    # Heuristic local analyzers — no external calls
    async def analyze_financial_document(self, document_text: str, document_type: str = "invoice") -> Dict[str, Any]:
        if not document_text:
            return {"summary": "Empty document", "entities": {}, "totals": {}}
        amounts = re.findall(r"\$[\d,]+\.?\d*|\b\d+\.?\d*\b", document_text)
        emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", document_text)
        dates = re.findall(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b", document_text)
        vendors = re.findall(r"(?i)(?:from|vendor|supplier|billed\s+to)\s*:\s*([\w .,&-]+)", document_text)
        total_value = None
        for token in amounts[::-1]:  # try last numeric as total
            try:
                total_value = float(str(token).replace("$", "").replace(",", ""))
                break
            except Exception:
                continue
        return {
            "document_type": document_type,
            "entities": {"emails": emails, "dates": dates, "vendors": vendors},
            "totals": {"last_numeric": total_value},
            "amounts_detected": amounts,
        }

    async def categorize_expense(
        self, description: str, amount: Optional[float] = None, vendor: Optional[str] = None, date: Optional[str] = None
    ) -> str:
        text = f"{description} {vendor or ''}".lower()
        if any(k in text for k in ["aws", "azure", "gcp", "hosting", "server", "cloud"]):
            return "Cloud Services"
        if any(k in text for k in ["uber", "taxi", "lyft", "fuel", "gas", "mileage", "transport"]):
            return "Transportation"
        if any(k in text for k in ["coffee", "restaurant", "meal", "cafe", "food"]):
            return "Meals & Entertainment"
        if any(k in text for k in ["office", "stationery", "supplies", "paper", "printer"]):
            return "Office Supplies"
        if any(k in text for k in ["software", "subscription", "license", "saas"]):
            return "Software"
        return "Miscellaneous"

    async def generate_financial_insights(self, financial_data: Dict[str, Any], period: str = "recent", company_size: str = "unknown", industry: str = "general") -> Dict[str, Any]:
        totals = []
        for v in financial_data.values():
            try:
                totals.append(float(v))
            except Exception:
                continue
        total_sum = sum(totals)
        avg = total_sum / len(totals) if totals else 0.0
        return {
            "period": period,
            "company_size": company_size,
            "industry": industry,
            "metrics": {"sum": total_sum, "average": avg, "count": len(totals)},
            "insights": [
                "Keep monitoring cash flow.",
                "Consider optimizing recurring expenses.",
            ],
        }

    async def generate_financial_report(self, financial_data: Dict[str, Any], report_type: str = "quarterly", period: str = "Q1", company_name: str = "Company", context: Optional[str] = None) -> Dict[str, Any]:
        insights = await self.generate_financial_insights(financial_data)
        return {
            "company": company_name,
            "report_type": report_type,
            "period": period,
            "summary": f"Synthetic {report_type} report for {company_name}.",
            "details": insights,
            "context_note": (context[:200] + "...") if context and len(context) > 200 else context,
        }

    async def natural_language_query(self, query: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        # Very naive NLQ: find numbers and keys referenced in query
        q = query.lower()
        matched_keys = [k for k in context_data.keys() if k.lower() in q]
        numbers = re.findall(r"-?\d+\.?\d*", " ".join(str(v) for v in context_data.values()))
        return {
            "query": query,
            "matched_keys": matched_keys,
            "numbers_seen": numbers[:10],
            "answer": f"Found {len(matched_keys)} matching keys and {len(numbers)} numeric values in context.",
        }

    # Placeholder for compatibility with docs; no external HTTP requests are made.
    async def _make_request(self, *args, **kwargs) -> Dict[str, Any]:
        return {"status": "ok", "note": "Local heuristic mode"}


# Export a singleton instance as expected by the router
github_models_service = GitHubModelsService()
