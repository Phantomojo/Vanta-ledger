#!/usr/bin/env python3
"""
Fraud Detection Agent

Detects suspicious patterns, anomalies, and potential fraud using AI models.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from decimal import Decimal
from uuid import uuid4

from pydantic import BaseModel

from .base_agent import BaseAgent, AgentType, AgentResult, AnalysisResult
from ..services.github_models_service import GitHubModelsService
from ..services.multi_github_models_service import MultiGitHubModelsService

logger = logging.getLogger(__name__)


class FraudAlert(BaseModel):
    """Fraud alert."""
    alert_id: str
    company_id: str
    fraud_type: str
    severity: str
    confidence: float
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    status: str = "active"


class FraudDetectionAgent(BaseAgent):
    """AI-powered fraud detection agent."""

    def __init__(
        self,
        agent_id: Optional[str] = None,
        agent_type: AgentType = AgentType.FRAUD_DETECTION,
        name: str = "Fraud Detection Agent",
        description: str = "AI agent for fraud detection",
        company_id: Optional[str] = None
    ):
        super().__init__(
            agent_id=agent_id,
            agent_type=agent_type,
            name=name,
            description=description
        )
        
        self.company_id = company_id
        self.github_models = GitHubModelsService()
        self.multi_github_models = MultiGitHubModelsService()
        self.fraud_alerts: List[FraudAlert] = []
        
        # Detection thresholds
        self.thresholds = {
            "large_transaction": 10000.0,
            "structuring_limit": 5000.0,
            "unusual_frequency": 10
        }
        
        logger.info(f"Initialized Fraud Detection Agent for company {company_id}")

    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """Execute fraud detection."""
        try:
            transactions = context.get("transactions", [])
            
            # Detect fraud
            fraud_results = await self._detect_fraud(transactions)
            
            # Generate alerts
            new_alerts = await self._generate_alerts(fraud_results)
            self.fraud_alerts.extend(new_alerts)
            
            return AgentResult(
                success=True,
                message=f"Fraud detection completed - {len(new_alerts)} alerts",
                data={
                    "fraud_results": fraud_results,
                    "new_alerts": len(new_alerts),
                    "total_alerts": len(self.fraud_alerts)
                }
            )
            
        except Exception as e:
            logger.error(f"Fraud detection failed: {e}")
            return AgentResult(
                success=False,
                message=f"Fraud detection failed: {str(e)}",
                errors=[str(e)]
            )

    async def analyze(self, data: Any) -> AnalysisResult:
        """Analyze data for fraud indicators using AI."""
        try:
            analysis_prompt = f"Analyze this financial data for fraud indicators: {data}"
            
            ai_analysis = await self.multi_github_models.analyze_with_multiple_models(
                text=analysis_prompt,
                task_type="financial"
            )
            
            fraud_indicators = await self._identify_indicators(data)
            risk_score = min(len(fraud_indicators) * 0.3, 1.0)
            
            insights = [f"AI Analysis: {ai_analysis.get('combined_response', 'No AI analysis available')}"]
            recommendations = ["Investigate suspicious transactions"] if fraud_indicators else ["Continue monitoring"]
            
            return AnalysisResult(
                confidence=0.85,
                insights=insights,
                recommendations=recommendations,
                risk_score=risk_score,
                metadata={"fraud_indicators": fraud_indicators}
            )
            
        except Exception as e:
            logger.error(f"Fraud analysis failed: {e}")
            return AnalysisResult(
                confidence=0.0,
                insights=[f"Analysis failed: {str(e)}"],
                recommendations=["Review system configuration"],
                risk_score=1.0
            )

    async def _detect_fraud(self, transactions: List[Dict]) -> List[Dict]:
        """Detect fraud in transactions."""
        fraud_indicators = []
        
        for transaction in transactions:
            amount = Decimal(str(transaction.get("amount", 0)))
            
            # Check for large transactions
            if amount > self.thresholds["large_transaction"]:
                fraud_indicators.append({
                    "transaction_id": transaction.get("id"),
                    "type": "large_transaction",
                    "amount": float(amount),
                    "risk_score": 0.7
                })
            
            # Check for structuring (just under limit)
            if amount > self.thresholds["structuring_limit"] * 0.9 and amount < self.thresholds["structuring_limit"]:
                fraud_indicators.append({
                    "transaction_id": transaction.get("id"),
                    "type": "structuring_suspicion",
                    "amount": float(amount),
                    "risk_score": 0.8
                })
        
        return fraud_indicators

    async def _generate_alerts(self, fraud_results: List[Dict]) -> List[FraudAlert]:
        """Generate fraud alerts."""
        alerts = []
        
        for result in fraud_results:
            alert = FraudAlert(
                alert_id=str(uuid4()),
                company_id=self.company_id,
                fraud_type=result["type"],
                severity=self._get_severity(result["risk_score"]),
                confidence=result["risk_score"],
                message=f"Fraud detected: {result['type']}",
                details=result,
                timestamp=datetime.utcnow()
            )
            alerts.append(alert)
        
        return alerts

    async def _identify_indicators(self, data: Any) -> List[Dict]:
        """Identify fraud indicators in data."""
        indicators = []
        
        if isinstance(data, dict):
            amount = data.get("amount", 0)
            if amount > self.thresholds["large_transaction"]:
                indicators.append({"type": "large_amount", "details": data})
        
        return indicators

    def _get_severity(self, risk_score: float) -> str:
        """Convert risk score to severity."""
        if risk_score >= 0.8:
            return "critical"
        elif risk_score >= 0.6:
            return "high"
        elif risk_score >= 0.4:
            return "medium"
        else:
            return "low"

    async def get_fraud_summary(self) -> Dict[str, Any]:
        """Get fraud detection summary."""
        return {
            "agent_id": self.agent_id,
            "company_id": self.company_id,
            "active_alerts": len([a for a in self.fraud_alerts if a.status == "active"]),
            "status": self.status.value
        }

    async def get_active_alerts(self) -> List[FraudAlert]:
        """Get active fraud alerts."""
        return [alert for alert in self.fraud_alerts if alert.status == "active"]
