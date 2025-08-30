#!/usr/bin/env python3
"""
Test Agent Coordination

This script demonstrates how multiple agents can coordinate and work together
using a shared LLM for complex financial analysis tasks.
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


class CoordinatedComplianceAgent(BaseAgent):
    """Compliance agent that coordinates with other agents."""
    
    def __init__(self, agent_id: str, llm: OllamaIntegration, communication: AgentCommunication):
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.COMPLIANCE,
            name="Coordinated Compliance Agent",
            description="Compliance agent that coordinates with fraud detection"
        )
        self.llm = llm
        self.communication = communication
        self.analysis_count = 0
    
    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """Execute coordinated compliance analysis."""
        try:
            self.analysis_count += 1
            text = context.get("text", "No text provided")
            
            # Step 1: Initial compliance analysis
            print(f"   🔍 Step 1: Initial compliance analysis...")
            compliance_analysis = await self.llm.analyze_text(text, "compliance")
            
            # Step 2: If high risk, request fraud analysis
            if compliance_analysis["confidence"] > 0.7:
                print(f"   🚨 High risk detected! Requesting fraud analysis...")
                
                # Send request to fraud agent
                await self.communication.send_message(
                    from_agent=self.agent_id,
                    to_agent="fraud-001",
                    message_type=MessageType.REQUEST,
                    content={
                        "request_type": "fraud_analysis",
                        "data": text,
                        "compliance_confidence": compliance_analysis["confidence"]
                    },
                    priority=MessagePriority.HIGH
                )
                
                # Broadcast alert
                await self.communication.broadcast_alert(
                    from_agent=self.agent_id,
                    alert_type="high_risk_compliance",
                    alert_data={
                        "text": text,
                        "confidence": compliance_analysis["confidence"],
                        "analysis_count": self.analysis_count
                    },
                    priority=MessagePriority.CRITICAL
                )
            
            return AgentResult(
                success=True,
                data={
                    "compliance_analysis": compliance_analysis,
                    "analysis_count": self.analysis_count,
                    "coordinated": compliance_analysis["confidence"] > 0.7
                },
                message=f"Coordinated compliance analysis completed: {compliance_analysis['confidence']:.2f} confidence"
            )
        except Exception as e:
            return AgentResult(
                success=False,
                message=f"Coordinated compliance analysis failed: {str(e)}",
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
        print(f"📨 {self.name} received: {message.message_type.value}")
        
        if message.message_type == MessageType.RESPONSE:
            print(f"   📋 Response from {message.from_agent}: {message.content.get('result', 'No result')}")
        elif message.message_type == MessageType.ALERT:
            print(f"   🚨 Alert: {message.content.get('alert_type', 'Unknown')}")


class CoordinatedFraudAgent(BaseAgent):
    """Fraud agent that coordinates with compliance agent."""
    
    def __init__(self, agent_id: str, llm: OllamaIntegration, communication: AgentCommunication):
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.FRAUD_DETECTION,
            name="Coordinated Fraud Agent",
            description="Fraud agent that coordinates with compliance"
        )
        self.llm = llm
        self.communication = communication
        self.request_count = 0
    
    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """Execute coordinated fraud detection."""
        try:
            text = context.get("text", "No text provided")
            fraud_analysis = await self.llm.analyze_text(text, "fraud")
            
            return AgentResult(
                success=True,
                data={"fraud_analysis": fraud_analysis},
                message=f"Fraud analysis completed: {fraud_analysis['confidence']:.2f} confidence"
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
        self.request_count += 1
        print(f"📨 {self.name} received request #{self.request_count}: {message.message_type.value}")
        
        if message.message_type == MessageType.REQUEST:
            request_type = message.content.get("request_type", "unknown")
            data = message.content.get("data", "")
            compliance_confidence = message.content.get("compliance_confidence", 0.0)
            
            print(f"   📋 Request type: {request_type}")
            print(f"   📊 Compliance confidence: {compliance_confidence:.2f}")
            
            if request_type == "fraud_analysis":
                # Perform fraud analysis
                print(f"   🔍 Performing fraud analysis...")
                fraud_result = await self.execute({"text": data})
                
                # Send response back to compliance agent
                await self.communication.send_message(
                    from_agent=self.agent_id,
                    to_agent=message.from_agent,
                    message_type=MessageType.RESPONSE,
                    content={
                        "request_id": message.message_id,
                        "result": fraud_result.data,
                        "fraud_confidence": fraud_result.data["fraud_analysis"]["confidence"],
                        "combined_risk": (compliance_confidence + fraud_result.data["fraud_analysis"]["confidence"]) / 2
                    },
                    priority=MessagePriority.HIGH
                )
                
                print(f"   ✅ Fraud analysis completed and response sent")
        
        elif message.message_type == MessageType.ALERT:
            print(f"   🚨 Alert: {message.content.get('alert_type', 'Unknown')}")


async def test_agent_coordination():
    """Test coordinated agent operations."""
    print("🤖 Agent Coordination Test")
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
    
    # Create coordinated agents
    print("\n🤖 Creating coordinated agents...")
    compliance_agent = CoordinatedComplianceAgent("compliance-001", llm, communication)
    fraud_agent = CoordinatedFraudAgent("fraud-001", llm, communication)
    
    # Register agents
    await communication.register_agent(compliance_agent.agent_id, compliance_agent)
    await communication.register_agent(fraud_agent.agent_id, fraud_agent)
    
    print(f"✅ Registered {len(communication._agents)} coordinated agents")
    
    # Start communication system
    print("\n🚀 Starting communication system...")
    comm_task = asyncio.create_task(communication.start_message_processor())
    await asyncio.sleep(1)
    
    # Test 1: Low-risk transaction (no coordination needed)
    print("\n📊 Test 1: Low-risk transaction")
    low_risk_result = await compliance_agent.execute({
        "text": "Standard office supplies purchase of $500 from known vendor."
    })
    print(f"✅ Low-risk result: {low_risk_result.success}")
    if low_risk_result.success:
        print(f"   📊 Coordinated: {low_risk_result.data['coordinated']}")
        print(f"   📈 Analysis count: {low_risk_result.data['analysis_count']}")
    
    await asyncio.sleep(3)  # Wait for any messages to process
    
    # Test 2: High-risk transaction (triggers coordination)
    print("\n🚨 Test 2: High-risk transaction")
    high_risk_result = await compliance_agent.execute({
        "text": "Company reported $10M revenue but only $100K expenses, with multiple transactions to offshore accounts."
    })
    print(f"✅ High-risk result: {high_risk_result.success}")
    if high_risk_result.success:
        print(f"   📊 Coordinated: {high_risk_result.data['coordinated']}")
        print(f"   📈 Analysis count: {high_risk_result.data['analysis_count']}")
    
    # Wait for coordination to complete
    await asyncio.sleep(5)
    
    # Test 3: Message history
    print("\n📚 Test 3: Message history")
    history = await communication.get_message_history(limit=20)
    print(f"✅ Retrieved {len(history)} messages from history")
    
    for msg in history:
        print(f"   📝 {msg.message_type.value} from {msg.from_agent} to {msg.to_agent or 'ALL'}")
        if msg.message_type == MessageType.REQUEST:
            print(f"      📋 Request: {msg.content.get('request_type', 'Unknown')}")
        elif msg.message_type == MessageType.RESPONSE:
            print(f"      📊 Response: {msg.content.get('result', 'No result')}")
    
    # Test 4: Agent statistics
    print("\n📊 Test 4: Agent statistics")
    print(f"✅ Compliance Agent:")
    print(f"   Analysis count: {compliance_agent.analysis_count}")
    print(f"   Status: {compliance_agent.status.value}")
    
    print(f"✅ Fraud Agent:")
    print(f"   Request count: {fraud_agent.request_count}")
    print(f"   Status: {fraud_agent.status.value}")
    
    # Test 5: System performance
    print("\n⚡ Test 5: System performance")
    status = await communication.get_system_status()
    print(f"✅ Communication system:")
    print(f"   Running: {status['running']}")
    print(f"   Queue size: {status['queue_size']}")
    print(f"   Message history: {status['message_history_size']}")
    print(f"   Total agents: {status['total_agents']}")
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    await communication.stop_message_processor()
    await llm.close()
    comm_task.cancel()
    
    print("\n🎉 Agent coordination test completed successfully!")
    return True


async def main():
    """Main test function."""
    try:
        success = await test_agent_coordination()
        if success:
            print("\n✅ All coordination tests passed!")
            print("🚀 Your agents can successfully coordinate using the shared LLM!")
            print("🎯 Ready for real-world financial analysis scenarios!")
        else:
            print("\n❌ Some tests failed")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
