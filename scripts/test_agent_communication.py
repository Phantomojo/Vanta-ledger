#!/usr/bin/env python3
"""
Test Agent Communication System

This script tests the agent communication system with multiple agents
sharing a single LLM (CodeLlama:7b).
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any

# Add the backend src to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend" / "src"))

from vanta_ledger.agents.base_agent import BaseAgent, AgentType, AgentResult, AnalysisResult
from vanta_ledger.agents.communication import AgentCommunication, MessageType, MessagePriority, AgentMessage
from vanta_ledger.agents.ollama_integration import OllamaConfig, OllamaIntegration


class TestComplianceAgent(BaseAgent):
    """Test compliance agent for communication testing."""
    
    def __init__(self, agent_id: str, llm: OllamaIntegration):
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.COMPLIANCE,
            name="Test Compliance Agent",
            description="Test agent for compliance monitoring"
        )
        self.llm = llm
        self.message_count = 0
    
    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """Execute compliance analysis."""
        try:
            text = context.get("text", "No text provided")
            analysis = await self.llm.analyze_text(text, "compliance")
            
            return AgentResult(
                success=True,
                data={"analysis": analysis},
                message=f"Compliance analysis completed: {analysis['confidence']:.2f} confidence"
            )
        except Exception as e:
            return AgentResult(
                success=False,
                message=f"Compliance analysis failed: {str(e)}",
                errors=[str(e)]
            )
    
    async def analyze(self, data: Any) -> AnalysisResult:
        """Analyze data for compliance issues."""
        try:
            if isinstance(data, str):
                analysis = await self.llm.analyze_text(data, "compliance")
                return AnalysisResult(
                    confidence=analysis["confidence"],
                    insights=[analysis["result"]],
                    recommendations=["Review compliance policies"],
                    risk_score=1.0 - analysis["confidence"]
                )
            else:
                return AnalysisResult(
                    confidence=0.5,
                    insights=["Data format not supported"],
                    recommendations=["Provide text data for analysis"]
                )
        except Exception as e:
            return AnalysisResult(
                confidence=0.0,
                insights=[f"Analysis error: {str(e)}"],
                recommendations=["Check data format and try again"]
            )
    
    async def handle_message(self, message: AgentMessage) -> None:
        """Handle incoming messages."""
        self.message_count += 1
        print(f"📨 {self.name} received message #{self.message_count}: {message.message_type.value}")
        
        if message.message_type == MessageType.ALERT:
            print(f"   🚨 Alert from {message.from_agent}: {message.content.get('alert_type', 'Unknown')}")
        elif message.message_type == MessageType.REQUEST:
            print(f"   📋 Request from {message.from_agent}: {message.content.get('request_type', 'Unknown')}")


class TestFraudAgent(BaseAgent):
    """Test fraud detection agent for communication testing."""
    
    def __init__(self, agent_id: str, llm: OllamaIntegration):
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.FRAUD_DETECTION,
            name="Test Fraud Agent",
            description="Test agent for fraud detection"
        )
        self.llm = llm
        self.message_count = 0
    
    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """Execute fraud detection analysis."""
        try:
            text = context.get("text", "No text provided")
            analysis = await self.llm.analyze_text(text, "fraud")
            
            return AgentResult(
                success=True,
                data={"analysis": analysis},
                message=f"Fraud analysis completed: {analysis['confidence']:.2f} confidence"
            )
        except Exception as e:
            return AgentResult(
                success=False,
                message=f"Fraud analysis failed: {str(e)}",
                errors=[str(e)]
            )
    
    async def analyze(self, data: Any) -> AnalysisResult:
        """Analyze data for fraud indicators."""
        try:
            if isinstance(data, str):
                analysis = await self.llm.analyze_text(data, "fraud")
                return AnalysisResult(
                    confidence=analysis["confidence"],
                    insights=[analysis["result"]],
                    recommendations=["Investigate suspicious patterns"],
                    risk_score=analysis["confidence"]
                )
            else:
                return AnalysisResult(
                    confidence=0.5,
                    insights=["Data format not supported"],
                    recommendations=["Provide text data for analysis"]
                )
        except Exception as e:
            return AnalysisResult(
                confidence=0.0,
                insights=[f"Analysis error: {str(e)}"],
                recommendations=["Check data format and try again"]
            )
    
    async def handle_message(self, message: AgentMessage) -> None:
        """Handle incoming messages."""
        self.message_count += 1
        print(f"📨 {self.name} received message #{self.message_count}: {message.message_type.value}")
        
        if message.message_type == MessageType.ALERT:
            print(f"   🚨 Alert from {message.from_agent}: {message.content.get('alert_type', 'Unknown')}")
        elif message.message_type == MessageType.REQUEST:
            print(f"   📋 Request from {message.from_agent}: {message.content.get('request_type', 'Unknown')}")


async def test_agent_communication():
    """Test the agent communication system."""
    print("🤖 Agent Communication System Test")
    print("=" * 50)
    
    # Initialize Ollama
    print("🔧 Initializing Ollama integration...")
    config = OllamaConfig(
        model_name="codellama:7b",
        max_tokens=256,
        temperature=0.7,
        timeout=60
    )
    
    llm = OllamaIntegration(config)
    connected = await llm.check_connection()
    if not connected:
        print("❌ Failed to connect to Ollama")
        return False
    
    print("✅ Ollama connected successfully!")
    
    # Create communication system
    print("\n📡 Creating agent communication system...")
    communication = AgentCommunication()
    
    # Create test agents
    print("\n🤖 Creating test agents...")
    compliance_agent = TestComplianceAgent("compliance-001", llm)
    fraud_agent = TestFraudAgent("fraud-001", llm)
    
    # Register agents with communication system
    await communication.register_agent(compliance_agent.agent_id, compliance_agent)
    await communication.register_agent(fraud_agent.agent_id, fraud_agent)
    
    print(f"✅ Registered {len(communication._agents)} agents")
    
    # Start communication system
    print("\n🚀 Starting communication system...")
    comm_task = asyncio.create_task(communication.start_message_processor())
    
    # Wait a moment for system to start
    await asyncio.sleep(1)
    
    # Test 1: Direct messaging between agents
    print("\n📨 Test 1: Direct messaging between agents")
    message = await communication.send_message(
        from_agent=compliance_agent.agent_id,
        to_agent=fraud_agent.agent_id,
        message_type=MessageType.REQUEST,
        content={"request_type": "fraud_check", "data": "Check this transaction for fraud"},
        priority=MessagePriority.HIGH
    )
    print(f"✅ Sent message: {message.message_id}")
    
    # Wait for message processing
    await asyncio.sleep(2)
    
    # Test 2: Broadcast alert
    print("\n📢 Test 2: Broadcast alert to all agents")
    alert = await communication.broadcast_alert(
        from_agent=compliance_agent.agent_id,
        alert_type="high_risk_transaction",
        alert_data={"transaction_id": "TX123", "risk_level": "high"},
        priority=MessagePriority.CRITICAL
    )
    print(f"✅ Broadcast alert: {alert.message_id}")
    
    # Wait for alert processing
    await asyncio.sleep(2)
    
    # Test 3: Agent execution with LLM
    print("\n🧠 Test 3: Agent execution with shared LLM")
    
    # Compliance agent execution
    print("   🔍 Running compliance analysis...")
    compliance_result = await compliance_agent.execute({
        "text": "Company reported $1M revenue but only $100K expenses, which seems unusual."
    })
    print(f"   ✅ Compliance result: {compliance_result.success}")
    if compliance_result.success:
        print(f"   📊 Analysis: {compliance_result.message}")
    
    # Fraud agent execution
    print("   🔍 Running fraud analysis...")
    fraud_result = await fraud_agent.execute({
        "text": "Multiple transactions to unknown vendors with round amounts."
    })
    print(f"   ✅ Fraud result: {fraud_result.success}")
    if fraud_result.success:
        print(f"   📊 Analysis: {fraud_result.message}")
    
    # Test 4: Message history
    print("\n📚 Test 4: Message history")
    history = await communication.get_message_history(limit=10)
    print(f"✅ Retrieved {len(history)} messages from history")
    
    for msg in history:
        print(f"   📝 {msg.message_type.value} from {msg.from_agent} to {msg.to_agent or 'ALL'}")
    
    # Test 5: System status
    print("\n📊 Test 5: System status")
    status = await communication.get_system_status()
    print(f"✅ Communication system status:")
    print(f"   Running: {status['running']}")
    print(f"   Registered agents: {status['registered_agents']}")
    print(f"   Queue size: {status['queue_size']}")
    print(f"   Message history: {status['message_history_size']}")
    
    # Test 6: Agent status
    print("\n🤖 Test 6: Agent status")
    compliance_status = await compliance_agent.get_status()
    fraud_status = await fraud_agent.get_status()
    
    print(f"✅ Compliance Agent: {compliance_status['status']}, Messages: {compliance_agent.message_count}")
    print(f"✅ Fraud Agent: {fraud_status['status']}, Messages: {fraud_agent.message_count}")
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    await communication.stop_message_processor()
    await llm.close()
    # Ensure clean shutdown of the background task
    try:
        await comm_task
    except asyncio.CancelledError:
        pass
    
    print("\n🎉 Agent communication test completed successfully!")
    return True


async def main():
    """Main test function."""
    try:
        success = await test_agent_communication()
        if success:
            print("\n✅ All communication tests passed!")
            print("🚀 Your single LLM can successfully power multiple agents!")
        else:
            print("\n❌ Some tests failed")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
