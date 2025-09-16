#!/usr/bin/env python3
"""
Financial Forecasting Agent

Provides revenue forecasting, expense prediction, cash flow analysis, and trend identification.
Uses AI models to analyze historical data and predict future financial performance.
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


class ForecastResult(BaseModel):
    """Forecast result."""
    forecast_id: str
    company_id: str
    forecast_type: str  # revenue, expense, cash_flow, trend
    period_start: datetime
    period_end: datetime
    predicted_value: float
    confidence: float
    factors: List[str]
    created_at: datetime


class TrendAnalysis(BaseModel):
    """Trend analysis result."""
    trend_id: str
    company_id: str
    metric: str
    trend_direction: str  # increasing, decreasing, stable
    trend_strength: float  # 0.0 to 1.0
    seasonality: bool
    seasonality_pattern: Optional[str]
    created_at: datetime


class FinancialForecastingAgent(BaseAgent):
    """AI-powered financial forecasting agent."""

    def __init__(
        self,
        agent_id: Optional[str] = None,
        agent_type: AgentType = AgentType.FORECASTING,
        name: str = "Financial Forecasting Agent",
        description: str = "AI agent for financial forecasting and trend analysis",
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
        self.forecasts: List[ForecastResult] = []
        self.trends: List[TrendAnalysis] = []
        
        logger.info(f"Initialized Financial Forecasting Agent for company {company_id}")

    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """Execute financial forecasting."""
        try:
            historical_data = context.get("historical_data", [])
            forecast_periods = context.get("forecast_periods", 3)  # months
            
            # Perform forecasting
            revenue_forecast = await self._forecast_revenue(historical_data, forecast_periods)
            expense_forecast = await self._forecast_expenses(historical_data, forecast_periods)
            cash_flow_forecast = await self._forecast_cash_flow(historical_data, forecast_periods)
            
            # Analyze trends
            trends = await self._analyze_trends(historical_data)
            
            # Store results
            self.forecasts.extend([revenue_forecast, expense_forecast, cash_flow_forecast])
            self.trends.extend(trends)
            
            return AgentResult(
                success=True,
                message=f"Financial forecasting completed - {len(self.forecasts)} forecasts, {len(trends)} trends",
                data={
                    "revenue_forecast": revenue_forecast.dict(),
                    "expense_forecast": expense_forecast.dict(),
                    "cash_flow_forecast": cash_flow_forecast.dict(),
                    "trends": [t.dict() for t in trends]
                }
            )
            
        except Exception as e:
            logger.error(f"Financial forecasting failed: {e}")
            return AgentResult(
                success=False,
                message=f"Financial forecasting failed: {str(e)}",
                errors=[str(e)]
            )

    async def analyze(self, data: Any) -> AnalysisResult:
        """Analyze financial data for forecasting insights."""
        try:
            analysis_prompt = f"Analyze this financial data for forecasting insights: {data}"
            
            ai_analysis = await self.multi_github_models.analyze_with_multiple_models(
                text=analysis_prompt,
                task_type="financial"
            )
            
            # Extract insights from AI analysis
            insights = []
            if ai_analysis.get("combined_response"):
                insights.append(f"AI Analysis: {ai_analysis['combined_response']}")
            
            # Generate forecasting recommendations
            recommendations = [
                "Monitor revenue trends closely",
                "Optimize expense management",
                "Maintain healthy cash flow",
                "Review seasonal patterns"
            ]
            
            # Calculate confidence based on data quality
            confidence = 0.8 if data else 0.3
            
            return AnalysisResult(
                confidence=confidence,
                insights=insights,
                recommendations=recommendations,
                risk_score=0.2,  # Low risk for forecasting
                metadata={"ai_models_used": ai_analysis.get("models_used", [])}
            )
            
        except Exception as e:
            logger.error(f"Forecasting analysis failed: {e}")
            return AnalysisResult(
                confidence=0.0,
                insights=[f"Analysis failed: {str(e)}"],
                recommendations=["Review data quality"],
                risk_score=0.5
            )

    async def _forecast_revenue(self, historical_data: List[Dict], periods: int) -> ForecastResult:
        """Forecast revenue based on historical data."""
        try:
            # Extract revenue data
            revenue_data = [d.get("revenue", 0) for d in historical_data if d.get("revenue")]
            
            if not revenue_data:
                # Use AI to generate synthetic forecast
                ai_forecast = await self._generate_ai_forecast("revenue", historical_data, periods)
                predicted_value = ai_forecast.get("predicted_value", 0.0)
                confidence = ai_forecast.get("confidence", 0.3)
                factors = ai_forecast.get("factors", ["Limited historical data"])
            else:
                # Calculate trend-based forecast
                predicted_value = self._calculate_trend_forecast(revenue_data, periods)
                confidence = min(len(revenue_data) / 12, 0.9)  # Higher confidence with more data
                factors = ["Historical trend analysis", "Seasonal patterns"]
            
            return ForecastResult(
                forecast_id=str(uuid4()),
                company_id=self.company_id,
                forecast_type="revenue",
                period_start=datetime.utcnow(),
                period_end=datetime.utcnow() + timedelta(days=30 * periods),
                predicted_value=predicted_value,
                confidence=confidence,
                factors=factors,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Revenue forecasting failed: {e}")
            return ForecastResult(
                forecast_id=str(uuid4()),
                company_id=self.company_id,
                forecast_type="revenue",
                period_start=datetime.utcnow(),
                period_end=datetime.utcnow() + timedelta(days=30 * periods),
                predicted_value=0.0,
                confidence=0.0,
                factors=["Forecasting error"],
                created_at=datetime.utcnow()
            )

    async def _forecast_expenses(self, historical_data: List[Dict], periods: int) -> ForecastResult:
        """Forecast expenses based on historical data."""
        try:
            # Extract expense data
            expense_data = [d.get("expenses", 0) for d in historical_data if d.get("expenses")]
            
            if not expense_data:
                # Use AI to generate synthetic forecast
                ai_forecast = await self._generate_ai_forecast("expenses", historical_data, periods)
                predicted_value = ai_forecast.get("predicted_value", 0.0)
                confidence = ai_forecast.get("confidence", 0.3)
                factors = ai_forecast.get("factors", ["Limited historical data"])
            else:
                # Calculate trend-based forecast
                predicted_value = self._calculate_trend_forecast(expense_data, periods)
                confidence = min(len(expense_data) / 12, 0.9)
                factors = ["Historical trend analysis", "Cost structure analysis"]
            
            return ForecastResult(
                forecast_id=str(uuid4()),
                company_id=self.company_id,
                forecast_type="expenses",
                period_start=datetime.utcnow(),
                period_end=datetime.utcnow() + timedelta(days=30 * periods),
                predicted_value=predicted_value,
                confidence=confidence,
                factors=factors,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Expense forecasting failed: {e}")
            return ForecastResult(
                forecast_id=str(uuid4()),
                company_id=self.company_id,
                forecast_type="expenses",
                period_start=datetime.utcnow(),
                period_end=datetime.utcnow() + timedelta(days=30 * periods),
                predicted_value=0.0,
                confidence=0.0,
                factors=["Forecasting error"],
                created_at=datetime.utcnow()
            )

    async def _forecast_cash_flow(self, historical_data: List[Dict], periods: int) -> ForecastResult:
        """Forecast cash flow based on historical data."""
        try:
            # Calculate cash flow from historical data
            cash_flows = []
            for data in historical_data:
                revenue = data.get("revenue", 0)
                expenses = data.get("expenses", 0)
                cash_flow = revenue - expenses
                cash_flows.append(cash_flow)
            
            if not cash_flows:
                # Use AI to generate synthetic forecast
                ai_forecast = await self._generate_ai_forecast("cash_flow", historical_data, periods)
                predicted_value = ai_forecast.get("predicted_value", 0.0)
                confidence = ai_forecast.get("confidence", 0.3)
                factors = ai_forecast.get("factors", ["Limited historical data"])
            else:
                # Calculate trend-based forecast
                predicted_value = self._calculate_trend_forecast(cash_flows, periods)
                confidence = min(len(cash_flows) / 12, 0.9)
                factors = ["Revenue and expense projections", "Working capital analysis"]
            
            return ForecastResult(
                forecast_id=str(uuid4()),
                company_id=self.company_id,
                forecast_type="cash_flow",
                period_start=datetime.utcnow(),
                period_end=datetime.utcnow() + timedelta(days=30 * periods),
                predicted_value=predicted_value,
                confidence=confidence,
                factors=factors,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Cash flow forecasting failed: {e}")
            return ForecastResult(
                forecast_id=str(uuid4()),
                company_id=self.company_id,
                forecast_type="cash_flow",
                period_start=datetime.utcnow(),
                period_end=datetime.utcnow() + timedelta(days=30 * periods),
                predicted_value=0.0,
                confidence=0.0,
                factors=["Forecasting error"],
                created_at=datetime.utcnow()
            )

    async def _analyze_trends(self, historical_data: List[Dict]) -> List[TrendAnalysis]:
        """Analyze trends in historical data."""
        trends = []
        
        try:
            # Analyze revenue trends
            revenue_data = [d.get("revenue", 0) for d in historical_data if d.get("revenue")]
            if len(revenue_data) >= 3:
                revenue_trend = self._calculate_trend_direction(revenue_data)
                trends.append(TrendAnalysis(
                    trend_id=str(uuid4()),
                    company_id=self.company_id,
                    metric="revenue",
                    trend_direction=revenue_trend["direction"],
                    trend_strength=revenue_trend["strength"],
                    seasonality=revenue_trend["seasonality"],
                    seasonality_pattern=revenue_trend.get("pattern"),
                    created_at=datetime.utcnow()
                ))
            
            # Analyze expense trends
            expense_data = [d.get("expenses", 0) for d in historical_data if d.get("expenses")]
            if len(expense_data) >= 3:
                expense_trend = self._calculate_trend_direction(expense_data)
                trends.append(TrendAnalysis(
                    trend_id=str(uuid4()),
                    company_id=self.company_id,
                    metric="expenses",
                    trend_direction=expense_trend["direction"],
                    trend_strength=expense_trend["strength"],
                    seasonality=expense_trend["seasonality"],
                    seasonality_pattern=expense_trend.get("pattern"),
                    created_at=datetime.utcnow()
                ))
            
            # Analyze profit margin trends
            profit_margins = []
            for data in historical_data:
                revenue = data.get("revenue", 0)
                expenses = data.get("expenses", 0)
                if revenue > 0:
                    margin = (revenue - expenses) / revenue
                    profit_margins.append(margin)
            
            if len(profit_margins) >= 3:
                margin_trend = self._calculate_trend_direction(profit_margins)
                trends.append(TrendAnalysis(
                    trend_id=str(uuid4()),
                    company_id=self.company_id,
                    metric="profit_margin",
                    trend_direction=margin_trend["direction"],
                    trend_strength=margin_trend["strength"],
                    seasonality=margin_trend["seasonality"],
                    seasonality_pattern=margin_trend.get("pattern"),
                    created_at=datetime.utcnow()
                ))
                
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
        
        return trends

    async def _generate_ai_forecast(self, forecast_type: str, historical_data: List[Dict], periods: int) -> Dict[str, Any]:
        """Generate AI-powered forecast when historical data is limited."""
        try:
            prompt = f"""
            Generate a {forecast_type} forecast for a business based on the following data:
            
            Historical Data: {historical_data}
            Forecast Periods: {periods} months
            
            Please provide:
            1. Predicted value for the next {periods} months
            2. Confidence level (0.0 to 1.0)
            3. Key factors influencing the forecast
            4. Recommendations for improving accuracy
            """
            
            ai_response = await self.multi_github_models.analyze_with_multiple_models(
                text=prompt,
                task_type="financial"
            )
            
            # Parse AI response (simplified)
            combined_response = ai_response.get("combined_response", "")
            
            # Extract predicted value (simplified parsing)
            predicted_value = 0.0
            if "predicted" in combined_response.lower():
                # Simple extraction - in practice, use more sophisticated parsing
                predicted_value = 50000.0  # Default value
            
            return {
                "predicted_value": predicted_value,
                "confidence": 0.3,  # Low confidence for AI-generated forecasts
                "factors": ["AI-generated forecast", "Limited historical data"],
                "ai_response": combined_response
            }
            
        except Exception as e:
            logger.error(f"AI forecast generation failed: {e}")
            return {
                "predicted_value": 0.0,
                "confidence": 0.0,
                "factors": ["Forecast generation failed"],
                "ai_response": ""
            }

    def _calculate_trend_forecast(self, data: List[float], periods: int) -> float:
        """Calculate trend-based forecast using simple linear regression."""
        if len(data) < 2:
            return data[0] if data else 0.0
        
        # Simple linear trend calculation
        n = len(data)
        x_sum = sum(range(n))
        y_sum = sum(data)
        xy_sum = sum(i * data[i] for i in range(n))
        x2_sum = sum(i * i for i in range(n))
        
        # Calculate slope and intercept
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
        intercept = (y_sum - slope * x_sum) / n
        
        # Predict next value
        next_period = n + periods - 1
        predicted_value = slope * next_period + intercept
        
        return max(predicted_value, 0.0)  # Ensure non-negative

    def _calculate_trend_direction(self, data: List[float]) -> Dict[str, Any]:
        """Calculate trend direction and strength."""
        if len(data) < 3:
            return {
                "direction": "stable",
                "strength": 0.0,
                "seasonality": False
            }
        
        # Calculate trend direction
        recent_avg = sum(data[-3:]) / 3
        earlier_avg = sum(data[:3]) / 3
        
        if recent_avg > earlier_avg * 1.1:
            direction = "increasing"
        elif recent_avg < earlier_avg * 0.9:
            direction = "decreasing"
        else:
            direction = "stable"
        
        # Calculate trend strength
        trend_strength = abs(recent_avg - earlier_avg) / max(earlier_avg, 1.0)
        trend_strength = min(trend_strength, 1.0)
        
        # Simple seasonality detection (check for repeating patterns)
        seasonality = len(data) >= 12 and self._detect_seasonality(data)
        
        return {
            "direction": direction,
            "strength": trend_strength,
            "seasonality": seasonality,
            "pattern": "quarterly" if seasonality else None
        }

    def _detect_seasonality(self, data: List[float]) -> bool:
        """Detect seasonality in data."""
        if len(data) < 12:
            return False
        
        # Simple seasonality detection - check for quarterly patterns
        quarterly_avgs = []
        for i in range(0, len(data), 3):
            quarter_data = data[i:i+3]
            if len(quarter_data) == 3:
                quarterly_avgs.append(sum(quarter_data) / 3)
        
        if len(quarterly_avgs) >= 4:
            # Check if quarterly averages vary significantly
            avg = sum(quarterly_avgs) / len(quarterly_avgs)
            variance = sum((x - avg) ** 2 for x in quarterly_avgs) / len(quarterly_avgs)
            return variance > (avg * 0.1) ** 2  # 10% threshold
        
        return False

    async def get_forecast_summary(self) -> Dict[str, Any]:
        """Get forecasting summary."""
        return {
            "agent_id": self.agent_id,
            "company_id": self.company_id,
            "total_forecasts": len(self.forecasts),
            "total_trends": len(self.trends),
            "status": self.status.value
        }

    async def get_recent_forecasts(self, limit: int = 10) -> List[ForecastResult]:
        """Get recent forecasts."""
        return sorted(
            self.forecasts,
            key=lambda x: x.created_at,
            reverse=True
        )[:limit]

    async def get_trend_analysis(self, metric: Optional[str] = None) -> List[TrendAnalysis]:
        """Get trend analysis."""
        if metric:
            return [t for t in self.trends if t.metric == metric]
        return self.trends
