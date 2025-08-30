"""
Agent Communication Module

Handles inter-agent communication and coordination in the Vanta Ledger system.
"""

import asyncio
import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import uuid4

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """Message type enumeration."""
    ALERT = "alert"
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    STATUS_UPDATE = "status_update"


class MessagePriority(str, Enum):
    """Message priority enumeration."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class AgentMessage(BaseModel):
    """Message structure for inter-agent communication."""
    message_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique message identifier")
    from_agent: str = Field(..., description="Source agent ID")
    to_agent: Optional[str] = Field(None, description="Target agent ID (None for broadcast)")
    message_type: MessageType = Field(..., description="Type of message")
    priority: MessagePriority = Field(default=MessagePriority.NORMAL, description="Message priority")
    content: Dict[str, Any] = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AgentCommunication:
    """
    Handles inter-agent communication and coordination.
    
    This class provides a messaging system for agents to communicate with each other,
    share information, and coordinate their activities.
    """

    def __init__(self):
        """Initialize the agent communication system."""
        self._agents: Dict[str, Any] = {}
        self._message_handlers: Dict[str, List[Callable]] = {}
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._message_history: List[AgentMessage] = []
        self._max_history = 1000
        
        logger.info("Initialized Agent Communication System")

    async def register_agent(self, agent_id: str, agent: Any) -> None:
        """
        Register an agent with the communication system.
        
        Args:
            agent_id: Unique identifier for the agent
            agent: Agent instance
        """
        self._agents[agent_id] = agent
        self._message_handlers[agent_id] = []
        logger.info(f"Registered agent: {agent_id}")

    async def unregister_agent(self, agent_id: str) -> None:
        """
        Unregister an agent from the communication system.
        
        Args:
            agent_id: Unique identifier for the agent
        """
        if agent_id in self._agents:
            del self._agents[agent_id]
            del self._message_handlers[agent_id]
            logger.info(f"Unregistered agent: {agent_id}")

    async def send_message(
        self,
        from_agent: str,
        to_agent: str,
        message_type: MessageType,
        content: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentMessage:
        """
        Send a message from one agent to another.
        
        Args:
            from_agent: Source agent ID
            to_agent: Target agent ID
            message_type: Type of message
            content: Message content
            priority: Message priority
            metadata: Additional metadata
            
        Returns:
            The created message
        """
        message = AgentMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            priority=priority,
            content=content,
            metadata=metadata or {}
        )
        
        await self._message_queue.put(message)
        self._add_to_history(message)
        logger.debug(f"Queued message from {from_agent} to {to_agent}: {message_type.value}")
        
        return message

    async def broadcast_alert(
        self,
        from_agent: str,
        alert_type: str,
        alert_data: Dict[str, Any],
        priority: MessagePriority = MessagePriority.HIGH
    ) -> AgentMessage:
        """
        Broadcast an alert to all registered agents.
        
        Args:
            from_agent: Source agent ID
            alert_type: Type of alert
            alert_data: Alert data
            priority: Alert priority
            
        Returns:
            The broadcast message
        """
        content = {
            "alert_type": alert_type,
            "alert_data": alert_data,
            "broadcast": True
        }
        
        message = AgentMessage(
            from_agent=from_agent,
            to_agent=None,  # None indicates broadcast
            message_type=MessageType.BROADCAST,
            priority=priority,
            content=content
        )
        
        await self._message_queue.put(message)
        self._add_to_history(message)
        logger.info(f"Broadcast alert from {from_agent}: {alert_type}")
        
        return message

    async def start_message_processor(self) -> None:
        """Start the message processing loop."""
        if self._running:
            logger.warning("Message processor already running")
            return
            
        self._running = True
        logger.info("Started message processor")
        
        try:
            while self._running:
                try:
                    message = await asyncio.wait_for(self._message_queue.get(), timeout=1.0)
                    await self._process_message(message)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
        except Exception as e:
            logger.error(f"Message processor error: {e}")
        finally:
            self._running = False
            logger.info("Stopped message processor")

    async def stop_message_processor(self) -> None:
        """Stop the message processing loop."""
        self._running = False
        logger.info("Stopping message processor")

    async def _process_message(self, message: AgentMessage) -> None:
        """
        Process a single message.
        
        Args:
            message: Message to process
        """
        try:
            if message.to_agent is None:
                # Broadcast message
                await self._handle_broadcast(message)
            else:
                # Direct message
                await self._handle_direct_message(message)
        except Exception as e:
            logger.error(f"Error processing message {message.message_id}: {e}")

    async def _handle_direct_message(self, message: AgentMessage) -> None:
        """
        Handle a direct message to a specific agent.
        
        Args:
            message: Message to handle
        """
        if message.to_agent not in self._agents:
            logger.warning(f"Target agent {message.to_agent} not found for message {message.message_id}")
            return
            
        agent = self._agents[message.to_agent]
        if hasattr(agent, 'handle_message'):
            try:
                await agent.handle_message(message)
                logger.debug(f"Delivered message {message.message_id} to {message.to_agent}")
            except Exception as e:
                logger.error(f"Error handling message in agent {message.to_agent}: {e}")

    async def _handle_broadcast(self, message: AgentMessage) -> None:
        """
        Handle a broadcast message to all agents.
        
        Args:
            message: Broadcast message to handle
        """
        for agent_id, agent in self._agents.items():
            if agent_id != message.from_agent:  # Don't send back to sender
                if hasattr(agent, 'handle_message'):
                    try:
                        await agent.handle_message(message)
                        logger.debug(f"Broadcast message {message.message_id} delivered to {agent_id}")
                    except Exception as e:
                        logger.error(f"Error handling broadcast in agent {agent_id}: {e}")

    def _add_to_history(self, message: AgentMessage) -> None:
        """
        Add message to history, maintaining size limit.
        
        Args:
            message: Message to add to history
        """
        self._message_history.append(message)
        if len(self._message_history) > self._max_history:
            self._message_history.pop(0)

    async def get_message_history(
        self,
        agent_id: Optional[str] = None,
        message_type: Optional[MessageType] = None,
        limit: int = 100
    ) -> List[AgentMessage]:
        """
        Get message history with optional filtering.
        
        Args:
            agent_id: Filter by agent ID
            message_type: Filter by message type
            limit: Maximum number of messages to return
            
        Returns:
            List of filtered messages
        """
        filtered_messages = self._message_history
        
        if agent_id:
            filtered_messages = [
                msg for msg in filtered_messages
                if msg.from_agent == agent_id or msg.to_agent == agent_id
            ]
            
        if message_type:
            filtered_messages = [
                msg for msg in filtered_messages
                if msg.message_type == message_type
            ]
            
        return filtered_messages[-limit:]

    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get communication system status.
        
        Returns:
            Dictionary containing system status
        """
        return {
            "running": self._running,
            "registered_agents": list(self._agents.keys()),
            "queue_size": self._message_queue.qsize(),
            "message_history_size": len(self._message_history),
            "total_agents": len(self._agents)
        }

    def __str__(self) -> str:
        """String representation of the communication system."""
        return f"AgentCommunication(agents={len(self._agents)}, running={self._running})"
