"""
Agent Manager Module

Manages the lifecycle and coordination of all AI agents in the Vanta Ledger system.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Type

from .base_agent import BaseAgent, AgentType, AgentResult
from .communication import AgentCommunication, AgentMessage, MessageType

logger = logging.getLogger(__name__)


class AgentManager:
    """
    Manages the lifecycle and coordination of all AI agents.
    
    This class provides centralized management of agent creation, execution,
    monitoring, and communication.
    """

    def __init__(self):
        """Initialize the agent manager."""
        self._agents: Dict[str, BaseAgent] = {}
        self._agent_types: Dict[str, Type[BaseAgent]] = {}
        self._communication = AgentCommunication()
        self._running = False
        self._task_queue: asyncio.Queue = asyncio.Queue()
        
        logger.info("Initialized Agent Manager")

    async def register_agent_type(self, agent_type: AgentType, agent_class: Type[BaseAgent]) -> None:
        """
        Register an agent type with its implementation class.
        
        Args:
            agent_type: Type of agent to register
            agent_class: Class implementing the agent
        """
        self._agent_types[agent_type.value] = agent_class
        logger.info(f"Registered agent type: {agent_type.value}")

    async def create_agent(
        self,
        agent_type: AgentType,
        agent_id: Optional[str] = None,
        name: Optional[str] = None,
        **kwargs
    ) -> BaseAgent:
        """
        Create a new agent instance.
        
        Args:
            agent_type: Type of agent to create
            agent_id: Optional agent ID
            name: Optional agent name
            **kwargs: Additional arguments for agent initialization
            
        Returns:
            Created agent instance
            
        Raises:
            ValueError: If agent type is not registered
        """
        if agent_type.value not in self._agent_types:
            raise ValueError(f"Agent type '{agent_type.value}' not registered")
            
        agent_class = self._agent_types[agent_type.value]
        agent = agent_class(
            agent_id=agent_id,
            agent_type=agent_type,
            name=name or f"{agent_type.value.title()} Agent",
            **kwargs
        )
        
        self._agents[agent.agent_id] = agent
        await self._communication.register_agent(agent.agent_id, agent)
        
        logger.info(f"Created agent: {agent.name} (ID: {agent.agent_id})")
        return agent

    async def start_agent(self, agent_id: str) -> AgentResult:
        """
        Start a specific agent.
        
        Args:
            agent_id: ID of the agent to start
            
        Returns:
            AgentResult indicating success/failure
        """
        if agent_id not in self._agents:
            return AgentResult(
                success=False,
                message=f"Agent {agent_id} not found",
                errors=[f"Agent {agent_id} not found"]
            )
            
        agent = self._agents[agent_id]
        result = await agent.start()
        
        if result.success:
            logger.info(f"Started agent: {agent.name}")
        else:
            logger.error(f"Failed to start agent {agent.name}: {result.message}")
            
        return result

    async def stop_agent(self, agent_id: str) -> AgentResult:
        """
        Stop a specific agent.
        
        Args:
            agent_id: ID of the agent to stop
            
        Returns:
            AgentResult indicating success/failure
        """
        if agent_id not in self._agents:
            return AgentResult(
                success=False,
                message=f"Agent {agent_id} not found",
                errors=[f"Agent {agent_id} not found"]
            )
            
        agent = self._agents[agent_id]
        result = await agent.stop()
        
        if result.success:
            logger.info(f"Stopped agent: {agent.name}")
        else:
            logger.error(f"Failed to stop agent {agent.name}: {result.message}")
            
        return result

    async def execute_agent(
        self,
        agent_id: str,
        context: Dict[str, Any]
    ) -> AgentResult:
        """
        Execute a specific agent with given context.
        
        Args:
            agent_id: ID of the agent to execute
            context: Context data for execution
            
        Returns:
            AgentResult from agent execution
        """
        if agent_id not in self._agents:
            return AgentResult(
                success=False,
                message=f"Agent {agent_id} not found",
                errors=[f"Agent {agent_id} not found"]
            )
            
        agent = self._agents[agent_id]
        result = await agent._execute_with_timing(context)
        
        logger.info(f"Executed agent {agent.name}: {result.success}")
        return result

    async def start_all_agents(self) -> List[AgentResult]:
        """
        Start all registered agents.
        
        Returns:
            List of AgentResult for each agent
        """
        results = []
        for agent_id in self._agents:
            result = await self.start_agent(agent_id)
            results.append(result)
            
        logger.info(f"Started {len(results)} agents")
        return results

    async def stop_all_agents(self) -> List[AgentResult]:
        """
        Stop all registered agents.
        
        Returns:
            List of AgentResult for each agent
        """
        results = []
        for agent_id in self._agents:
            result = await self.stop_agent(agent_id)
            results.append(result)
            
        logger.info(f"Stopped {len(results)} agents")
        return results

    async def start_manager(self) -> None:
        """Start the agent manager and communication system."""
        if self._running:
            logger.warning("Agent manager already running")
            return
            
        self._running = True
        
        # Start communication system
        await self._communication.start_message_processor()
        
        # Start all agents
        await self.start_all_agents()
        
        logger.info("Started Agent Manager")

    async def stop_manager(self) -> None:
        """Stop the agent manager and all agents."""
        if not self._running:
            logger.warning("Agent manager not running")
            return
            
        self._running = False
        
        # Stop all agents
        await self.stop_all_agents()
        
        # Stop communication system
        await self._communication.stop_message_processor()
        
        logger.info("Stopped Agent Manager")

    async def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Agent status dictionary or None if not found
        """
        if agent_id not in self._agents:
            return None
            
        agent = self._agents[agent_id]
        return await agent.get_status()

    async def get_all_agent_statuses(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all agents.
        
        Returns:
            Dictionary mapping agent IDs to their status
        """
        statuses = {}
        for agent_id, agent in self._agents.items():
            statuses[agent_id] = await agent.get_status()
        return statuses

    async def broadcast_message(
        self,
        from_agent: str,
        message_type: MessageType,
        content: Dict[str, Any]
    ) -> AgentMessage:
        """
        Broadcast a message to all agents.
        
        Args:
            from_agent: Source agent ID
            message_type: Type of message
            content: Message content
            
        Returns:
            The broadcast message
        """
        return await self._communication.broadcast_alert(
            from_agent=from_agent,
            alert_type=message_type.value,
            alert_data=content
        )

    async def send_message(
        self,
        from_agent: str,
        to_agent: str,
        message_type: MessageType,
        content: Dict[str, Any]
    ) -> AgentMessage:
        """
        Send a message from one agent to another.
        
        Args:
            from_agent: Source agent ID
            to_agent: Target agent ID
            message_type: Type of message
            content: Message content
            
        Returns:
            The sent message
        """
        return await self._communication.send_message(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            content=content
        )

    async def get_manager_status(self) -> Dict[str, Any]:
        """
        Get overall manager status.
        
        Returns:
            Dictionary containing manager status information
        """
        agent_statuses = await self.get_all_agent_statuses()
        comm_status = await self._communication.get_system_status()
        
        return {
            "running": self._running,
            "total_agents": len(self._agents),
            "agent_types": list(self._agent_types.keys()),
            "agents": agent_statuses,
            "communication": comm_status
        }

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Agent instance or None if not found
        """
        return self._agents.get(agent_id)

    def list_agents(self) -> List[Dict[str, Any]]:
        """
        List all registered agents.
        
        Returns:
            List of agent information dictionaries
        """
        agents = []
        for agent_id, agent in self._agents.items():
            agents.append({
                "agent_id": agent_id,
                "name": agent.name,
                "type": agent.agent_type.value,
                "status": agent.status.value
            })
        return agents

    def __str__(self) -> str:
        """String representation of the agent manager."""
        return f"AgentManager(agents={len(self._agents)}, running={self._running})"
