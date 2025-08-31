#!/usr/bin/env python3
"""
Compliance Monitoring Agent

Monitors regulatory compliance, generates alerts, and provides automated compliance reporting.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from decimal import Decimal
from uuid import uuid4

from pydantic import BaseModel

from .base_agent import BaseAgent, AgentType, AgentResult, AnalysisResult
from ..services.github_models_service import GitHubModelsService
from ..services.multi_github_models_service import MultiGitHubModelsService

logger = logging.getLogger(__name__)


class ComplianceAlert(BaseModel):
    """Compliance alert."""
    alert_id: str
    rule_id: str
    company_id: str
    severity: str
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    status: str = "active"


class ComplianceMonitoringAgent(BaseAgent):
    """AI-powered compliance monitoring agent."""

    def __init__(
        self,
        agent_id: Optional[str] = None,
        agent_type: AgentType = AgentType.COMPLIANCE,
        name: str = "Compliance Monitoring Agent",
        description: str = "AI agent for regulatory compliance monitoring",
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
        self.active_alerts: List[ComplianceAlert] = []
        
        logger.info(f"Initialized Compliance Monitoring Agent for company {company_id}")

    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """Execute compliance monitoring."""
        try:
            transactions = context.get("transactions", [])
            documents = context.get("documents", [])
            
            # Perform compliance checks
            violations = await self._check_compliance(transactions, documents)
            
            # Generate alerts
            new_alerts = await self._generate_alerts(violations)
            self.active_alerts.extend(new_alerts)
            
            return AgentResult(
                success=True,
                message=f"Compliance monitoring completed - {len(new_alerts)} new alerts",
                data={
                    "violations": violations,
                    "new_alerts": len(new_alerts),
                    "total_alerts": len(self.active_alerts)
                }
            )
            
        except Exception as e:
            logger.error(f"Compliance monitoring failed: {e}")
            return AgentResult(
                success=False,
                message=f"Compliance monitoring failed: {str(e)}",
                errors=[str(e)]
            )

    async def analyze(self, data: Any) -> AnalysisResult:
        """Analyze data for compliance issues using AI."""
        try:
            analysis_prompt = f"Analyze this financial data for compliance issues: {data}"
            
            ai_analysis = await self.multi_github_models.analyze_with_multiple_models(
                text=analysis_prompt,
                task_type="financial"
            )
            
            violations = await self._identify_violations(data)
            risk_score = min(len(violations) * 0.2, 1.0)
            
            insights = [f"AI Analysis: {ai_analysis.get('combined_response', 'No AI analysis available')}"]
            recommendations = ["Review compliance violations", "Implement additional controls"] if violations else ["Maintain current practices"]
            
            return AnalysisResult(
                confidence=0.85,
                insights=insights,
                recommendations=recommendations,
                risk_score=risk_score,
                metadata={"violations": violations}
            )
            
        except Exception as e:
            logger.error(f"Compliance analysis failed: {e}")
            return AnalysisResult(
                confidence=0.0,
                insights=[f"Analysis failed: {str(e)}"],
                recommendations=["Review system configuration"],
                risk_score=1.0
            )

    async def _check_compliance(self, transactions: List[Dict], documents: List[Dict]) -> List[Dict]:
        """Check compliance rules."""
        violations = []
        
        # Check large transactions
        for transaction in transactions:
            amount = Decimal(str(transaction.get("amount", 0)))
            if amount > 10000:
                violations.append({
                    "type": "large_transaction",
                    "transaction_id": transaction.get("id"),
                    "amount": float(amount),
                    "severity": "medium"
                })
        
        # Check document retention
        for document in documents:
            if document.get("type") in ["invoice", "receipt"]:
                created_at = document.get("created_at", datetime.utcnow())
                age_days = (datetime.utcnow() - created_at).days
                if age_days > 365:
                    violations.append({
                        "type": "document_retention",
                        "document_id": document.get("id"),
                        "age_days": age_days,
                        "severity": "low"
                    })
        
        return violations

    async def _generate_alerts(self, violations: List[Dict]) -> List[ComplianceAlert]:
        """Generate compliance alerts."""
        alerts = []
        
        for violation in violations:
            alert = ComplianceAlert(
                alert_id=str(uuid4()),
                rule_id=violation["type"],
                company_id=self.company_id,
                severity=violation["severity"],
                message=f"Compliance violation: {violation['type']}",
                details=violation,
                timestamp=datetime.utcnow()
            )
            alerts.append(alert)
        
        return alerts

    async def _identify_violations(self, data: Any) -> List[Dict]:
        """Identify compliance violations in data."""
        # Simple violation detection
        violations = []
        
        if isinstance(data, dict):
            if data.get("amount", 0) > 10000:
                violations.append({"type": "large_amount", "details": data})
        
        return violations

    async def get_compliance_summary(self) -> Dict[str, Any]:
        """Get compliance summary."""
        return {
            "agent_id": self.agent_id,
            "company_id": self.company_id,
            "active_alerts": len(self.active_alerts),
            "status": self.status.value
        }

    async def get_active_alerts(self) -> List[ComplianceAlert]:
        """Get active alerts."""
        return [alert for alert in self.active_alerts if alert.status == "active"]
