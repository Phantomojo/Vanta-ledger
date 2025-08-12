#!/usr/bin/env python3
"""
AI Analytics API Routes
Advanced AI features including predictive analytics and anomaly detection
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from ..auth import User, get_current_user
from ..services.ai_analytics_service import enhanced_ai_analytics_service
from ..utils.validation import input_validator

router = APIRouter(prefix="/api/v2/ai-analytics", tags=["AI Analytics"])

# ============================================================================
# FINANCIAL TREND ANALYSIS
# ============================================================================


@router.get("/trends/financial")
async def analyze_financial_trends(
    period_days: int = Query(90, ge=30, le=365, description="Analysis period in days"),
    current_user: User = Depends(get_current_user),
):
    """Analyze financial trends and patterns"""
    try:
        analysis = await enhanced_ai_analytics_service.analyze_financial_trends(
            current_user.id, period_days
        )
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze financial trends: {str(e)}",
        )


# ============================================================================
# PREDICTIVE ANALYTICS
# ============================================================================


@router.get("/predictions/financial")
async def predict_financial_metrics(
    forecast_periods: int = Query(
        12, ge=1, le=24, description="Number of periods to forecast"
    ),
    current_user: User = Depends(get_current_user),
):
    """Predict future financial metrics"""
    try:
        predictions = await enhanced_ai_analytics_service.predict_financial_metrics(
            current_user.id, forecast_periods
        )
        return predictions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to predict financial metrics: {str(e)}",
        )


# ============================================================================
# ANOMALY DETECTION
# ============================================================================


@router.get("/anomalies")
async def detect_anomalies(
    data_type: str = Query(
        "all",
        description="Type of data to analyze: all, financial, documents, payments",
    ),
    current_user: User = Depends(get_current_user),
):
    """Detect anomalies in financial data and documents"""
    try:
        anomalies = await enhanced_ai_analytics_service.detect_anomalies(
            current_user.id, data_type
        )
        return anomalies
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect anomalies: {str(e)}",
        )


@router.get("/anomalies/financial")
async def detect_financial_anomalies(current_user: User = Depends(get_current_user)):
    """Detect financial anomalies specifically"""
    try:
        anomalies = await enhanced_ai_analytics_service.detect_anomalies(
            current_user.id, "financial"
        )
        return anomalies
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect financial anomalies: {str(e)}",
        )


@router.get("/anomalies/documents")
async def detect_document_anomalies(current_user: User = Depends(get_current_user)):
    """Detect document anomalies specifically"""
    try:
        anomalies = await enhanced_ai_analytics_service.detect_anomalies(
            current_user.id, "documents"
        )
        return anomalies
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect document anomalies: {str(e)}",
        )


# ============================================================================
# FINANCIAL INSIGHTS
# ============================================================================


@router.get("/insights/financial")
async def generate_financial_insights(current_user: User = Depends(get_current_user)):
    """Generate comprehensive financial insights"""
    try:
        insights = await enhanced_ai_analytics_service.generate_financial_insights(
            current_user.id
        )
        return insights
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate financial insights: {str(e)}",
        )


# ============================================================================
# ANALYTICS DASHBOARD
# ============================================================================


@router.get("/dashboard/overview")
async def get_analytics_dashboard(current_user: User = Depends(get_current_user)):
    """Get comprehensive analytics dashboard data"""
    try:
        # Get all analytics data
        trends = await enhanced_ai_analytics_service.analyze_financial_trends(
            current_user.id, 90
        )
        predictions = await enhanced_ai_analytics_service.predict_financial_metrics(
            current_user.id, 6
        )
        anomalies = await enhanced_ai_analytics_service.detect_anomalies(
            current_user.id, "all"
        )
        insights = await enhanced_ai_analytics_service.generate_financial_insights(
            current_user.id
        )

        return {
            "success": True,
            "dashboard": {
                "trends": trends.get("analysis", {}),
                "predictions": predictions.get("predictions", {}),
                "anomalies": anomalies.get("anomalies", {}),
                "insights": insights.get("insights", {}),
                "generated_at": datetime.utcnow().isoformat(),
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate dashboard: {str(e)}",
        )


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================


@router.get("/health")
async def ai_analytics_health():
    """Check AI analytics service health"""
    return {
        "success": True,
        "service": "ai_analytics",
        "status": "healthy",
        "features": [
            "financial_trend_analysis",
            "predictive_analytics",
            "anomaly_detection",
            "financial_insights",
        ],
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/cache/clear")
async def clear_ai_cache(current_user: User = Depends(get_current_user)):
    """Clear AI analytics cache"""
    try:
        # Clear Redis cache for AI analytics
        cache_keys = enhanced_ai_analytics_service.redis_client.keys("ai_analytics:*")
        if cache_keys:
            enhanced_ai_analytics_service.redis_client.delete(*cache_keys)

        return {
            "success": True,
            "message": "AI analytics cache cleared successfully",
            "cleared_keys": len(cache_keys),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}",
        )
