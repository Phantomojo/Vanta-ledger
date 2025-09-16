#!/usr/bin/env python3
"""
Automated Reporting Agent

Generates scheduled reports, custom reports, and executive summaries.
Provides automated reporting capabilities for financial data and business insights.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel

from .base_agent import BaseAgent, AgentType, AgentResult, AnalysisResult
from ..services.github_models_service import GitHubModelsService
from ..services.multi_github_models_service import MultiGitHubModelsService

logger = logging.getLogger(__name__)


class Report(BaseModel):
    """Report definition."""
    report_id: str
    company_id: str
    report_type: str  # financial, compliance, executive, custom
    title: str
    content: str
    period_start: datetime
    period_end: datetime
    generated_at: datetime
    status: str = "generated"  # generated, delivered, archived


class ReportSchedule(BaseModel):
    """Report schedule."""
    schedule_id: str
    company_id: str
    report_type: str
    frequency: str  # daily, weekly, monthly, quarterly
    recipients: List[str]
    enabled: bool = True
    last_generated: Optional[datetime] = None


class AutomatedReportingAgent(BaseAgent):
    """AI-powered automated reporting agent."""

    def __init__(
        self,
        agent_id: Optional[str] = None,
        agent_type: AgentType = AgentType.REPORTING,
        name: str = "Automated Reporting Agent",
        description: str = "AI agent for automated report generation",
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
        self.reports: List[Report] = []
        self.schedules: List[ReportSchedule] = []
        
        logger.info(f"Initialized Automated Reporting Agent for company {company_id}")

    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """Execute automated reporting."""
        try:
            report_type = context.get("report_type", "financial")
            period_start = context.get("period_start", datetime.utcnow() - timedelta(days=30))
            period_end = context.get("period_end", datetime.utcnow())
            
            # Generate report
            report = await self._generate_report(report_type, period_start, period_end, context)
            self.reports.append(report)
            
            return AgentResult(
                success=True,
                message=f"Report generated successfully: {report.title}",
                data={
                    "report": report.dict(),
                    "total_reports": len(self.reports)
                }
            )
            
        except Exception as e:
            logger.error(f"Automated reporting failed: {e}")
            return AgentResult(
                success=False,
                message=f"Automated reporting failed: {str(e)}",
                errors=[str(e)]
            )

    async def analyze(self, data: Any) -> AnalysisResult:
        """Analyze data for reporting insights."""
        try:
            analysis_prompt = f"Analyze this data for reporting insights: {data}"
            
            ai_analysis = await self.multi_github_models.analyze_with_multiple_models(
                text=analysis_prompt,
                task_type="financial"
            )
            
            insights = [f"AI Analysis: {ai_analysis.get('combined_response', 'No AI analysis available')}"]
            recommendations = ["Generate comprehensive reports", "Include key metrics", "Add visualizations"]
            
            return AnalysisResult(
                confidence=0.8,
                insights=insights,
                recommendations=recommendations,
                risk_score=0.1,  # Low risk for reporting
                metadata={"ai_models_used": ai_analysis.get("models_used", [])}
            )
            
        except Exception as e:
            logger.error(f"Reporting analysis failed: {e}")
            return AnalysisResult(
                confidence=0.0,
                insights=[f"Analysis failed: {str(e)}"],
                recommendations=["Review system configuration"],
                risk_score=0.5
            )

    async def _generate_report(
        self,
        report_type: str,
        period_start: datetime,
        period_end: datetime,
        context: Dict[str, Any]
    ) -> Report:
        """Generate a report based on type and period."""
        try:
            if report_type == "financial":
                content = await self._generate_financial_report(period_start, period_end, context)
                title = f"Financial Report - {period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}"
            elif report_type == "compliance":
                content = await self._generate_compliance_report(period_start, period_end, context)
                title = f"Compliance Report - {period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}"
            elif report_type == "executive":
                content = await self._generate_executive_summary(period_start, period_end, context)
                title = f"Executive Summary - {period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}"
            else:
                content = await self._generate_custom_report(report_type, period_start, period_end, context)
                title = f"Custom Report - {report_type} - {period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}"
            
            return Report(
                report_id=str(uuid4()),
                company_id=self.company_id,
                report_type=report_type,
                title=title,
                content=content,
                period_start=period_start,
                period_end=period_end,
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return Report(
                report_id=str(uuid4()),
                company_id=self.company_id,
                report_type=report_type,
                title=f"Error Report - {report_type}",
                content=f"Error generating report: {str(e)}",
                period_start=period_start,
                period_end=period_end,
                generated_at=datetime.utcnow()
            )

    async def _generate_financial_report(
        self,
        period_start: datetime,
        period_end: datetime,
        context: Dict[str, Any]
    ) -> str:
        """Generate financial report."""
        try:
            # Get financial data from context
            transactions = context.get("transactions", [])
            revenue = sum(t.get("amount", 0) for t in transactions if t.get("type") == "revenue")
            expenses = sum(t.get("amount", 0) for t in transactions if t.get("type") == "expense")
            profit = revenue - expenses
            
            # Use AI to enhance the report
            ai_prompt = f"""
            Generate a financial report summary for the period {period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}:
            
            Revenue: ${revenue:,.2f}
            Expenses: ${expenses:,.2f}
            Profit: ${profit:,.2f}
            
            Please provide:
            1. Executive summary
            2. Key financial metrics
            3. Trend analysis
            4. Recommendations
            """
            
            ai_response = await self.multi_github_models.analyze_with_multiple_models(
                text=ai_prompt,
                task_type="financial"
            )
            
            ai_summary = ai_response.get("combined_response", "AI analysis unavailable")
            
            report_content = f"""
# Financial Report
**Period**: {period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}

## Financial Summary
- **Total Revenue**: ${revenue:,.2f}
- **Total Expenses**: ${expenses:,.2f}
- **Net Profit**: ${profit:,.2f}
- **Profit Margin**: {(profit/revenue*100):.1f}% if revenue > 0 else 0%

## Transaction Summary
- **Total Transactions**: {len(transactions)}
- **Revenue Transactions**: {len([t for t in transactions if t.get('type') == 'revenue'])}
- **Expense Transactions**: {len([t for t in transactions if t.get('type') == 'expense'])}

## AI Analysis
{ai_summary}

## Recommendations
1. Monitor revenue trends closely
2. Optimize expense management
3. Maintain healthy profit margins
4. Review transaction patterns regularly
            """
            
            return report_content
            
        except Exception as e:
            logger.error(f"Financial report generation failed: {e}")
            return f"Error generating financial report: {str(e)}"

    async def _generate_compliance_report(
        self,
        period_start: datetime,
        period_end: datetime,
        context: Dict[str, Any]
    ) -> str:
        """Generate compliance report."""
        try:
            # Get compliance data from context
            compliance_alerts = context.get("compliance_alerts", [])
            fraud_alerts = context.get("fraud_alerts", [])
            
            total_alerts = len(compliance_alerts) + len(fraud_alerts)
            critical_alerts = len([a for a in compliance_alerts + fraud_alerts if a.get("severity") == "critical"])
            
            report_content = f"""
# Compliance Report
**Period**: {period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}

## Compliance Summary
- **Total Alerts**: {total_alerts}
- **Critical Alerts**: {critical_alerts}
- **Compliance Score**: {max(100 - total_alerts * 5, 0)}%

## Compliance Alerts
- **Total**: {len(compliance_alerts)}
- **Critical**: {len([a for a in compliance_alerts if a.get('severity') == 'critical'])}
- **High**: {len([a for a in compliance_alerts if a.get('severity') == 'high'])}
- **Medium**: {len([a for a in compliance_alerts if a.get('severity') == 'medium'])}
- **Low**: {len([a for a in compliance_alerts if a.get('severity') == 'low'])}

## Fraud Alerts
- **Total**: {len(fraud_alerts)}
- **Critical**: {len([a for a in fraud_alerts if a.get('severity') == 'critical'])}
- **High**: {len([a for a in fraud_alerts if a.get('severity') == 'high'])}
- **Medium**: {len([a for a in fraud_alerts if a.get('severity') == 'medium'])}
- **Low**: {len([a for a in fraud_alerts if a.get('severity') == 'low'])}

## Recommendations
1. Address critical alerts immediately
2. Review compliance procedures
3. Implement additional controls
4. Schedule compliance training
            """
            
            return report_content
            
        except Exception as e:
            logger.error(f"Compliance report generation failed: {e}")
            return f"Error generating compliance report: {str(e)}"

    async def _generate_executive_summary(
        self,
        period_start: datetime,
        period_end: datetime,
        context: Dict[str, Any]
    ) -> str:
        """Generate executive summary."""
        try:
            # Get key metrics from context
            transactions = context.get("transactions", [])
            revenue = sum(t.get("amount", 0) for t in transactions if t.get("type") == "revenue")
            expenses = sum(t.get("amount", 0) for t in transactions if t.get("type") == "expense")
            profit = revenue - expenses
            
            compliance_alerts = context.get("compliance_alerts", [])
            fraud_alerts = context.get("fraud_alerts", [])
            
            # Use AI to generate executive insights
            ai_prompt = f"""
            Generate an executive summary for the period {period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}:
            
            Key Metrics:
            - Revenue: ${revenue:,.2f}
            - Expenses: ${expenses:,.2f}
            - Profit: ${profit:,.2f}
            - Compliance Alerts: {len(compliance_alerts)}
            - Fraud Alerts: {len(fraud_alerts)}
            
            Please provide:
            1. Executive overview
            2. Key achievements
            3. Areas of concern
            4. Strategic recommendations
            """
            
            ai_response = await self.multi_github_models.analyze_with_multiple_models(
                text=ai_prompt,
                task_type="financial"
            )
            
            ai_summary = ai_response.get("combined_response", "AI analysis unavailable")
            
            report_content = f"""
# Executive Summary
**Period**: {period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}

## Key Metrics
- **Revenue**: ${revenue:,.2f}
- **Expenses**: ${expenses:,.2f}
- **Profit**: ${profit:,.2f}
- **Profit Margin**: {(profit/revenue*100):.1f}% if revenue > 0 else 0%
- **Compliance Score**: {max(100 - len(compliance_alerts) * 5, 0)}%
- **Risk Level**: {"High" if len(fraud_alerts) > 5 else "Medium" if len(fraud_alerts) > 2 else "Low"}

## AI Executive Analysis
{ai_summary}

## Key Highlights
1. Financial performance overview
2. Compliance status
3. Risk assessment
4. Strategic insights

## Action Items
1. Review financial performance
2. Address compliance issues
3. Monitor risk indicators
4. Plan strategic initiatives
            """
            
            return report_content
            
        except Exception as e:
            logger.error(f"Executive summary generation failed: {e}")
            return f"Error generating executive summary: {str(e)}"

    async def _generate_custom_report(
        self,
        report_type: str,
        period_start: datetime,
        period_end: datetime,
        context: Dict[str, Any]
    ) -> str:
        """Generate custom report."""
        try:
            # Use AI to generate custom report based on type
            ai_prompt = f"""
            Generate a custom {report_type} report for the period {period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}.
            
            Context data: {context}
            
            Please provide a comprehensive {report_type} report with:
            1. Overview and objectives
            2. Key findings and metrics
            3. Analysis and insights
            4. Recommendations and next steps
            """
            
            ai_response = await self.multi_github_models.analyze_with_multiple_models(
                text=ai_prompt,
                task_type="financial"
            )
            
            ai_content = ai_response.get("combined_response", "AI analysis unavailable")
            
            report_content = f"""
# Custom Report: {report_type.title()}
**Period**: {period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}

## Report Overview
This is a custom {report_type} report generated for the specified period.

## AI-Generated Content
{ai_content}

## Report Metadata
- **Report Type**: {report_type}
- **Generated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
- **Company ID**: {self.company_id}
            """
            
            return report_content
            
        except Exception as e:
            logger.error(f"Custom report generation failed: {e}")
            return f"Error generating custom report: {str(e)}"

    async def schedule_report(
        self,
        report_type: str,
        frequency: str,
        recipients: List[str]
    ) -> ReportSchedule:
        """Schedule a recurring report."""
        schedule = ReportSchedule(
            schedule_id=str(uuid4()),
            company_id=self.company_id,
            report_type=report_type,
            frequency=frequency,
            recipients=recipients
        )
        
        self.schedules.append(schedule)
        logger.info(f"Scheduled {frequency} {report_type} report for company {self.company_id}")
        
        return schedule

    async def get_report_summary(self) -> Dict[str, Any]:
        """Get reporting summary."""
        return {
            "agent_id": self.agent_id,
            "company_id": self.company_id,
            "total_reports": len(self.reports),
            "active_schedules": len([s for s in self.schedules if s.enabled]),
            "status": self.status.value
        }

    async def get_recent_reports(self, limit: int = 10) -> List[Report]:
        """Get recent reports."""
        return sorted(
            self.reports,
            key=lambda x: x.generated_at,
            reverse=True
        )[:limit]

    async def get_schedules(self) -> List[ReportSchedule]:
        """Get all report schedules."""
        return self.schedules
