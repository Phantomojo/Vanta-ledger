#!/usr/bin/env python3
"""
Phase 2 AI Agents Test Script

Comprehensive testing of all Phase 2 AI agents:
- Compliance Monitoring Agent
- Financial Forecasting Agent
- Fraud Detection Agent
- Automated Reporting Agent
"""

import sys
import os
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to Python path
backend_path = Path("backend/src")
if backend_path.exists():
    sys.path.insert(0, str(backend_path))

from vanta_ledger.agents.agent_manager import AgentManager
from vanta_ledger.agents.base_agent import AgentType
from vanta_ledger.services.github_models_service import GitHubModelsService
from vanta_ledger.services.multi_github_models_service import MultiGitHubModelsService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Phase2AIAgentsTester:
    """Comprehensive tester for Phase 2 AI agents."""
    
    def __init__(self):
        self.agent_manager = AgentManager()
        self.github_models = GitHubModelsService()
        self.multi_github_models = MultiGitHubModelsService()
        self.test_results = {}
        
    async def setup(self):
        """Setup test environment."""
        print("🔧 Setting up Phase 2 AI Agents test environment...")
        
        # Check GitHub Models service
        if not self.github_models.enabled:
            print("⚠️ GitHub Models service not enabled. Some tests may fail.")
        
        # Check Multi-GitHub Models service
        multi_status = await self.multi_github_models.get_model_status()
        if not multi_status["service_enabled"]:
            print("⚠️ Multi-GitHub Models service not enabled. Some tests may fail.")
        
        print("✅ Test environment setup complete")
    
    async def test_compliance_agent(self):
        """Test Compliance Monitoring Agent."""
        print("\n🧪 Testing Compliance Monitoring Agent...")
        
        try:
            # Create compliance agent
            compliance_agent = await self.agent_manager.create_agent(
                agent_type=AgentType.COMPLIANCE,
                company_id="test_company_001",
                name="Test Compliance Agent"
            )
            
            # Test data
            test_transactions = [
                {"id": "tx1", "amount": 15000, "type": "payment", "customer_id": "cust1"},
                {"id": "tx2", "amount": 4500, "type": "payment", "customer_id": "cust1"},
                {"id": "tx3", "amount": 4800, "type": "payment", "customer_id": "cust1"},
            ]
            
            test_documents = [
                {"id": "doc1", "type": "invoice", "amount": 5000, "created_at": datetime.utcnow() - timedelta(days=400)},
                {"id": "doc2", "type": "receipt", "amount": 1000, "created_at": datetime.utcnow() - timedelta(days=10)},
            ]
            
            # Execute compliance monitoring
            context = {
                "transactions": test_transactions,
                "documents": test_documents
            }
            
            result = await compliance_agent.execute(context)
            
            if result.success:
                print(f"✅ Compliance monitoring executed successfully")
                print(f"   - New alerts: {result.data.get('new_alerts', 0)}")
                print(f"   - Total alerts: {result.data.get('total_alerts', 0)}")
                
                # Test analysis
                analysis_result = await compliance_agent.analyze(test_transactions)
                print(f"   - Analysis confidence: {analysis_result.confidence}")
                print(f"   - Risk score: {analysis_result.risk_score}")
                
                # Get summary
                summary = await compliance_agent.get_compliance_summary()
                print(f"   - Active alerts: {summary.get('active_alerts', 0)}")
                
                self.test_results["compliance_agent"] = "PASS"
            else:
                print(f"❌ Compliance monitoring failed: {result.message}")
                self.test_results["compliance_agent"] = "FAIL"
                
        except Exception as e:
            print(f"❌ Compliance agent test failed: {e}")
            self.test_results["compliance_agent"] = "ERROR"
    
    async def test_forecasting_agent(self):
        """Test Financial Forecasting Agent."""
        print("\n🧪 Testing Financial Forecasting Agent...")
        
        try:
            # Create forecasting agent
            forecasting_agent = await self.agent_manager.create_agent(
                agent_type=AgentType.FORECASTING,
                company_id="test_company_001",
                name="Test Forecasting Agent"
            )
            
            # Test historical data
            historical_data = [
                {"revenue": 50000, "expenses": 30000, "month": "2024-01"},
                {"revenue": 55000, "expenses": 32000, "month": "2024-02"},
                {"revenue": 60000, "expenses": 35000, "month": "2024-03"},
                {"revenue": 65000, "expenses": 38000, "month": "2024-04"},
                {"revenue": 70000, "expenses": 40000, "month": "2024-05"},
                {"revenue": 75000, "expenses": 42000, "month": "2024-06"},
            ]
            
            # Execute forecasting
            context = {
                "historical_data": historical_data,
                "forecast_periods": 3
            }
            
            result = await forecasting_agent.execute(context)
            
            if result.success:
                print(f"✅ Financial forecasting executed successfully")
                print(f"   - Revenue forecast: {result.data.get('revenue_forecast', {}).get('predicted_value', 0):,.2f}")
                print(f"   - Expense forecast: {result.data.get('expense_forecast', {}).get('predicted_value', 0):,.2f}")
                print(f"   - Cash flow forecast: {result.data.get('cash_flow_forecast', {}).get('predicted_value', 0):,.2f}")
                print(f"   - Trends analyzed: {len(result.data.get('trends', []))}")
                
                # Test analysis
                analysis_result = await forecasting_agent.analyze(historical_data)
                print(f"   - Analysis confidence: {analysis_result.confidence}")
                print(f"   - Risk score: {analysis_result.risk_score}")
                
                # Get summary
                summary = await forecasting_agent.get_forecast_summary()
                print(f"   - Total forecasts: {summary.get('total_forecasts', 0)}")
                print(f"   - Total trends: {summary.get('total_trends', 0)}")
                
                self.test_results["forecasting_agent"] = "PASS"
            else:
                print(f"❌ Financial forecasting failed: {result.message}")
                self.test_results["forecasting_agent"] = "FAIL"
                
        except Exception as e:
            print(f"❌ Forecasting agent test failed: {e}")
            self.test_results["forecasting_agent"] = "ERROR"
    
    async def test_fraud_detection_agent(self):
        """Test Fraud Detection Agent."""
        print("\n🧪 Testing Fraud Detection Agent...")
        
        try:
            # Create fraud detection agent
            fraud_agent = await self.agent_manager.create_agent(
                agent_type=AgentType.FRAUD_DETECTION,
                company_id="test_company_001",
                name="Test Fraud Detection Agent"
            )
            
            # Test data with suspicious patterns
            test_transactions = [
                {"id": "tx1", "amount": 12000, "type": "payment", "customer_id": "cust1"},
                {"id": "tx2", "amount": 4800, "type": "payment", "customer_id": "cust1"},
                {"id": "tx3", "amount": 4900, "type": "payment", "customer_id": "cust1"},
                {"id": "tx4", "amount": 4700, "type": "payment", "customer_id": "cust1"},
                {"id": "tx5", "amount": 4600, "type": "payment", "customer_id": "cust1"},
            ]
            
            # Execute fraud detection
            context = {
                "transactions": test_transactions
            }
            
            result = await fraud_agent.execute(context)
            
            if result.success:
                print(f"✅ Fraud detection executed successfully")
                print(f"   - Fraud results: {len(result.data.get('fraud_results', []))}")
                print(f"   - New alerts: {result.data.get('new_alerts', 0)}")
                print(f"   - Total alerts: {result.data.get('total_alerts', 0)}")
                
                # Test analysis
                analysis_result = await fraud_agent.analyze(test_transactions)
                print(f"   - Analysis confidence: {analysis_result.confidence}")
                print(f"   - Risk score: {analysis_result.risk_score}")
                
                # Get summary
                summary = await fraud_agent.get_fraud_summary()
                print(f"   - Active alerts: {summary.get('active_alerts', 0)}")
                
                self.test_results["fraud_detection_agent"] = "PASS"
            else:
                print(f"❌ Fraud detection failed: {result.message}")
                self.test_results["fraud_detection_agent"] = "FAIL"
                
        except Exception as e:
            print(f"❌ Fraud detection agent test failed: {e}")
            self.test_results["fraud_detection_agent"] = "ERROR"
    
    async def test_reporting_agent(self):
        """Test Automated Reporting Agent."""
        print("\n🧪 Testing Automated Reporting Agent...")
        
        try:
            # Create reporting agent
            reporting_agent = await self.agent_manager.create_agent(
                agent_type=AgentType.REPORTING,
                company_id="test_company_001",
                name="Test Reporting Agent"
            )
            
            # Test data
            test_transactions = [
                {"id": "tx1", "amount": 50000, "type": "revenue", "customer_id": "cust1"},
                {"id": "tx2", "amount": 30000, "type": "expense", "customer_id": "cust1"},
                {"id": "tx3", "amount": 60000, "type": "revenue", "customer_id": "cust2"},
                {"id": "tx4", "amount": 40000, "type": "expense", "customer_id": "cust2"},
            ]
            
            test_compliance_alerts = [
                {"severity": "medium", "type": "large_transaction"},
                {"severity": "low", "type": "document_retention"},
            ]
            
            test_fraud_alerts = [
                {"severity": "high", "type": "structuring_suspicion"},
            ]
            
            # Execute reporting
            context = {
                "report_type": "financial",
                "period_start": datetime.utcnow() - timedelta(days=30),
                "period_end": datetime.utcnow(),
                "transactions": test_transactions,
                "compliance_alerts": test_compliance_alerts,
                "fraud_alerts": test_fraud_alerts
            }
            
            result = await reporting_agent.execute(context)
            
            if result.success:
                print(f"✅ Automated reporting executed successfully")
                print(f"   - Report title: {result.data.get('report', {}).get('title', 'N/A')}")
                print(f"   - Report type: {result.data.get('report', {}).get('report_type', 'N/A')}")
                print(f"   - Total reports: {result.data.get('total_reports', 0)}")
                
                # Test analysis
                analysis_result = await reporting_agent.analyze(test_transactions)
                print(f"   - Analysis confidence: {analysis_result.confidence}")
                print(f"   - Risk score: {analysis_result.risk_score}")
                
                # Get summary
                summary = await reporting_agent.get_report_summary()
                print(f"   - Total reports: {summary.get('total_reports', 0)}")
                print(f"   - Active schedules: {summary.get('active_schedules', 0)}")
                
                # Test scheduling
                schedule = await reporting_agent.schedule_report(
                    report_type="financial",
                    frequency="monthly",
                    recipients=["admin@company.com"]
                )
                print(f"   - Scheduled report: {schedule.report_type} ({schedule.frequency})")
                
                self.test_results["reporting_agent"] = "PASS"
            else:
                print(f"❌ Automated reporting failed: {result.message}")
                self.test_results["reporting_agent"] = "FAIL"
                
        except Exception as e:
            print(f"❌ Reporting agent test failed: {e}")
            self.test_results["reporting_agent"] = "ERROR"
    
    async def test_agent_coordination(self):
        """Test agent coordination and communication."""
        print("\n🧪 Testing Agent Coordination...")
        
        try:
            # Create multiple agents
            agents = []
            agent_types = [
                AgentType.COMPLIANCE,
                AgentType.FORECASTING,
                AgentType.FRAUD_DETECTION,
                AgentType.REPORTING
            ]
            
            for agent_type in agent_types:
                agent = await self.agent_manager.create_agent(
                    agent_type=agent_type,
                    company_id="test_company_001",
                    name=f"Test {agent_type.value.title()} Agent"
                )
                agents.append(agent)
            
            # Test agent manager status
            manager_status = await self.agent_manager.get_manager_status()
            print(f"✅ Agent manager status:")
            print(f"   - Running: {manager_status.get('running', False)}")
            print(f"   - Total agents: {manager_status.get('total_agents', 0)}")
            print(f"   - Agent types: {manager_status.get('agent_types', [])}")
            
            # Test agent listing
            agent_list = self.agent_manager.list_agents()
            print(f"   - Registered agents: {len(agent_list)}")
            for agent_info in agent_list:
                print(f"     * {agent_info['name']} ({agent_info['type']}) - {agent_info['status']}")
            
            # Test agent communication
            if len(agents) >= 2:
                message = await self.agent_manager.send_message(
                    from_agent=agents[0].agent_id,
                    to_agent=agents[1].agent_id,
                    message_type="request",
                    content={"message": "Test coordination message"}
                )
                print(f"   - Message sent: {message.message_id}")
            
            self.test_results["agent_coordination"] = "PASS"
            
        except Exception as e:
            print(f"❌ Agent coordination test failed: {e}")
            self.test_results["agent_coordination"] = "ERROR"
    
    async def test_multi_github_models_integration(self):
        """Test Multi-GitHub Models integration with agents."""
        print("\n🧪 Testing Multi-GitHub Models Integration...")
        
        try:
            # Test multi-GitHub models service
            status = await self.multi_github_models.get_model_status()
            print(f"✅ Multi-GitHub Models status:")
            print(f"   - Service enabled: {status.get('service_enabled', False)}")
            print(f"   - Total models: {status.get('total_models', 0)}")
            print(f"   - Active models: {status.get('active_models', 0)}")
            
            # Test multi-model analysis
            test_text = "Analyze this financial data for potential issues: Revenue $100,000, Expenses $80,000, Large transaction $15,000"
            
            analysis_result = await self.multi_github_models.analyze_with_multiple_models(
                text=test_text,
                task_type="financial"
            )
            
            print(f"   - Analysis task type: {analysis_result.get('task_type', 'N/A')}")
            print(f"   - Models used: {len(analysis_result.get('models_used', []))}")
            print(f"   - Successful models: {analysis_result.get('successful_models', 0)}")
            print(f"   - Failed models: {analysis_result.get('failed_models', 0)}")
            
            if analysis_result.get('combined_response'):
                print(f"   - Combined response length: {len(analysis_result['combined_response'])} characters")
            
            self.test_results["multi_github_models"] = "PASS"
            
        except Exception as e:
            print(f"❌ Multi-GitHub Models integration test failed: {e}")
            self.test_results["multi_github_models"] = "ERROR"
    
    async def run_all_tests(self):
        """Run all Phase 2 AI agent tests."""
        print("🚀 Starting Phase 2 AI Agents Comprehensive Testing")
        print("=" * 60)
        
        await self.setup()
        
        # Run individual agent tests
        await self.test_compliance_agent()
        await self.test_forecasting_agent()
        await self.test_fraud_detection_agent()
        await self.test_reporting_agent()
        
        # Run integration tests
        await self.test_agent_coordination()
        await self.test_multi_github_models_integration()
        
        # Print results summary
        await self.print_results_summary()
    
    async def print_results_summary(self):
        """Print test results summary."""
        print("\n" + "=" * 60)
        print("📊 Phase 2 AI Agents Test Results Summary")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result == "PASS")
        failed_tests = sum(1 for result in self.test_results.values() if result == "FAIL")
        error_tests = sum(1 for result in self.test_results.values() if result == "ERROR")
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Errors: {error_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
        
        print("\nDetailed Results:")
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result == "PASS" else "❌" if result == "FAIL" else "⚠️"
            print(f"  {status_icon} {test_name}: {result}")
        
        if passed_tests == total_tests:
            print("\n🎉 All Phase 2 AI Agents tests passed! Phase 2.1 is ready for production.")
        else:
            print(f"\n⚠️ {failed_tests + error_tests} tests need attention before Phase 2.1 is complete.")


async def main():
    """Main test execution."""
    tester = Phase2AIAgentsTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
