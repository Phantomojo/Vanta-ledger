import os
"""
Base Agent Module

Provides the foundational classes for all AI agents in the Vanta Ledger system.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AgentStatus(str, Enum):
    """Agent status enumeration."""
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    STOPPED = "stopped"


class AgentType(str, Enum):
    """Agent type enumeration."""
    COMPLIANCE = "compliance"
    FRAUD_DETECTION = "fraud_detection"
    FORECASTING = "forecasting"
    REPORTING = "reporting"


class AgentResult(BaseModel):
    """Result from agent execution."""
    success: bool = Field(..., description="Whether the operation was successful")
    data: Optional[Dict[str, Any]] = Field(None, description="Result data")
    message: str = Field(..., description="Result message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Execution timestamp")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    errors: Optional[List[str]] = Field(None, description="List of errors if any")


class AnalysisResult(BaseModel):
    """Result from agent analysis."""
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    insights: List[str] = Field(default_factory=list, description="Key insights")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    risk_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Risk assessment score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class BaseAgent(ABC):
    """
    Base class for all AI agents in the Vanta Ledger system.
    
    This class provides the foundation for intelligent financial automation,
    including compliance monitoring, fraud detection, forecasting, and reporting.
    """

    def __init__(
        self,
        agent_id: Optional[str] = None,
        agent_type: AgentType = AgentType.COMPLIANCE,
        name: str = "Base Agent",
        description: str = "Base AI agent for financial automation"
    ):
        """
        Initialize the base agent.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_type: Type of agent (compliance, fraud_detection, etc.)
            name: Human-readable name for the agent
            description: Description of the agent's purpose
        """
        self.agent_id = agent_id or str(uuid4())
        self.agent_type = agent_type
        self.name = name
        self.description = description
        self.status = AgentStatus.IDLE
        self.last_run: Optional[datetime] = None
        self.created_at = datetime.utcnow()
        self.metrics: Dict[str, Any] = {}
        
        logger.info(f"Initialized {self.name} (ID: {self.agent_id})")

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Execute the main agent logic.
        
        Args:
            context: Context data for the execution
            
        Returns:
            AgentResult containing the execution results
        """
        pass

    @abstractmethod
    async def analyze(self, data: Any) -> AnalysisResult:
        """
        Analyze data using AI capabilities.
        
        Args:
            data: Data to analyze
            
        Returns:
            AnalysisResult containing analysis insights
        """
        pass

    async def start(self) -> AgentResult:
        """
        Start the agent.
        
        Returns:
            AgentResult indicating success/failure
        """
        try:
            self.status = AgentStatus.RUNNING
            logger.info(f"Started {self.name} (ID: {self.agent_id})")
            return AgentResult(
                success=True,
                message=f"{self.name} started successfully",
                data={"status": self.status.value}
            )
        except Exception as e:
            self.status = AgentStatus.ERROR
            logger.error(f"Failed to start {self.name}: {e}")
            return AgentResult(
                success=False,
                message=f"Failed to start {self.name}: {str(e)}",
                errors=[str(e)]
            )

    async def stop(self) -> AgentResult:
        """
        Stop the agent.
        
        Returns:
            AgentResult indicating success/failure
        """
        try:
            self.status = AgentStatus.STOPPED
            logger.info(f"Stopped {self.name} (ID: {self.agent_id})")
            return AgentResult(
                success=True,
                message=f"{self.name} stopped successfully",
                data={"status": self.status.value}
            )
        except Exception as e:
            logger.error(f"Failed to stop {self.name}: {e}")
            return AgentResult(
                success=False,
                message=f"Failed to stop {self.name}: {str(e)}",
                errors=[str(e)]
            )

    async def get_status(self) -> Dict[str, Any]:
        """
        Get current agent status and metrics.
        
        Returns:
            Dictionary containing agent status information
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "name": self.name,
            "status": self.status.value,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "created_at": self.created_at.isoformat(),
            "metrics": self.metrics
        }

    def update_metrics(self, metric_name: str, value: Any) -> None:
        """
        Update agent metrics.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
        """
        self.metrics[metric_name] = value
        logger.debug(f"Updated metric {metric_name} for {self.name}: {value}")

    async def _execute_with_timing(self, context: Dict[str, Any]) -> AgentResult:
        """
        Execute agent logic with timing information.
        
        Args:
            context: Context data for execution
            
        Returns:
            AgentResult with timing information
        """
        start_time = datetime.utcnow()
        try:
            result = await self.execute(context)
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            result.execution_time = execution_time
            self.last_run = datetime.utcnow()
            self.update_metrics("last_execution_time", execution_time)
            self.update_metrics("total_executions", self.metrics.get("total_executions", 0) + 1)
            return result
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Error in {self.name} execution: {e}")
            return AgentResult(
                success=False,
                message=f"Error in {self.name} execution: {str(e)}",
                execution_time=execution_time,
                errors=[str(e)]
            )

    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.name} ({self.agent_type.value}) - {self.status.value}"

    def __repr__(self) -> str:
        """Detailed string representation of the agent."""
        return f"<{self.__class__.__name__}(id={self.agent_id}, type={self.agent_type.value}, status={self.status.value})>"
