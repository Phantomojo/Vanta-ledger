#!/usr/bin/env python3
"""
Enhanced GitHub Models Test Suite
Comprehensive testing of all enhanced GitHub Models capabilities
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'src'))

from vanta_ledger.services.github_models_service import github_models_service


class EnhancedGitHubModelsTester:
    """Comprehensive tester for enhanced GitHub Models capabilities"""
    
    def __init__(self):
        self.service = github_models_service
        self.test_results = []
        
    async def test_service_initialization(self) -> Dict[str, Any]:
        """Test service initialization and basic capabilities"""
        print("🔧 Testing Service Initialization...")
        
        result = {
            "test": "service_initialization",
            "enabled": self.service.enabled,
            "default_model": self.service.default_model,
            "available_prompts": len(self.service.get_available_prompts()),
            "expense_categories": len(self.service.get_expense_categories()),
            "industry_patterns": len(self.service.get_industry_patterns()),
            "success": True
        }
        
        print(f"✅ Service enabled: {result['enabled']}")
        print(f"✅ Default model: {result['default_model']}")
        print(f"✅ Available prompts: {result['available_prompts']}")
        print(f"✅ Expense categories: {result['expense_categories']}")
        print(f"✅ Industry patterns: {result['industry_patterns']}")
        
        return result
    
    async def test_enhanced_document_analysis(self) -> Dict[str, Any]:
        """Test enhanced document analysis capabilities"""
        print("\n📄 Testing Enhanced Document Analysis...")
        
        test_documents = [
            {
                "text": """
                INVOICE
                From: TechCorp Solutions
                Date: 2024-01-15
                Amount: $1,250.00
                Contact: billing@techcorp.com
                
                Services: Cloud hosting and software licenses
                Due Date: 2024-02-15
                """,
                "type": "invoice"
            },
            {
                "text": """
                RECEIPT
                Vendor: Coffee Shop Express
                Date: 01/20/2024
                Items: Coffee $4.50, Sandwich $12.99
                Total: $17.49
                Payment: Credit Card
                """,
                "type": "receipt"
            }
        ]
        
        results = []
        for i, doc in enumerate(test_documents):
            try:
                analysis = await self.service.analyze_financial_document(
                    document_text=doc["text"],
                    document_type=doc["type"]
                )
                
                results.append({
                    "document": i + 1,
                    "type": doc["type"],
                    "confidence": analysis.get("confidence", 0.0),
                    "quality": analysis.get("analysis_quality", "unknown"),
                    "entities_found": analysis.get("extraction_metadata", {}).get("entities_found", 0),
                    "amounts_detected": len(analysis.get("entities", {}).get("amounts_detected", [])),
                    "success": True
                })
                
                print(f"✅ Document {i+1} ({doc['type']}): Confidence {analysis.get('confidence', 0.0):.2f}, Quality: {analysis.get('analysis_quality', 'unknown')}")
                
            except Exception as e:
                results.append({
                    "document": i + 1,
                    "type": doc["type"],
                    "error": str(e),
                    "success": False
                })
                print(f"❌ Document {i+1} failed: {e}")
        
        return {
            "test": "enhanced_document_analysis",
            "results": results,
            "success": all(r["success"] for r in results)
        }
    
    async def test_enhanced_expense_categorization(self) -> Dict[str, Any]:
        """Test enhanced expense categorization with confidence scoring"""
        print("\n🏷️ Testing Enhanced Expense Categorization...")
        
        test_expenses = [
            {
                "description": "AWS Cloud Services",
                "amount": 150.00,
                "vendor": "Amazon Web Services"
            },
            {
                "description": "Uber ride to office",
                "amount": 25.50,
                "vendor": "Uber"
            },
            {
                "description": "Office supplies and printer ink",
                "amount": 89.99,
                "vendor": "Office Depot"
            },
            {
                "description": "Software subscription for project management",
                "amount": 299.00,
                "vendor": "Atlassian"
            }
        ]
        
        results = []
        for i, expense in enumerate(test_expenses):
            try:
                categorization = await self.service.categorize_expense(
                    description=expense["description"],
                    amount=expense["amount"],
                    vendor=expense["vendor"]
                )
                
                results.append({
                    "expense": i + 1,
                    "description": expense["description"],
                    "category": categorization.get("category", "Unknown"),
                    "confidence": categorization.get("confidence", 0.0),
                    "industry_context": categorization.get("industry_context", "general"),
                    "success": True
                })
                
                print(f"✅ Expense {i+1}: {categorization.get('category', 'Unknown')} (Confidence: {categorization.get('confidence', 0.0):.2f})")
                
            except Exception as e:
                results.append({
                    "expense": i + 1,
                    "description": expense["description"],
                    "error": str(e),
                    "success": False
                })
                print(f"❌ Expense {i+1} failed: {e}")
        
        return {
            "test": "enhanced_expense_categorization",
            "results": results,
            "success": all(r["success"] for r in results)
        }
    
    async def test_enhanced_financial_insights(self) -> Dict[str, Any]:
        """Test enhanced financial insights generation"""
        print("\n💡 Testing Enhanced Financial Insights...")
        
        test_data = {
            "Q1_revenue": 50000,
            "Q2_revenue": 55000,
            "Q3_revenue": 52000,
            "Q4_revenue": 60000,
            "cloud_costs": 15000,
            "marketing_expenses": 8000,
            "office_rent": 12000,
            "software_licenses": 5000
        }
        
        try:
            insights = await self.service.generate_financial_insights(
                financial_data=test_data,
                period="Q1-Q4 2024",
                company_size="medium",
                industry="technology"
            )
            
            result = {
                "test": "enhanced_financial_insights",
                "metrics_count": insights.get("metrics", {}).get("count", 0),
                "trends_detected": len(insights.get("trends", [])),
                "insights_generated": len(insights.get("insights", [])),
                "recommendations": len(insights.get("recommendations", [])),
                "analysis_quality": insights.get("analysis_quality", "unknown"),
                "success": True
            }
            
            print(f"✅ Metrics analyzed: {result['metrics_count']}")
            print(f"✅ Trends detected: {result['trends_detected']}")
            print(f"✅ Insights generated: {result['insights_generated']}")
            print(f"✅ Recommendations: {result['recommendations']}")
            print(f"✅ Analysis quality: {result['analysis_quality']}")
            
            return result
            
        except Exception as e:
            return {
                "test": "enhanced_financial_insights",
                "error": str(e),
                "success": False
            }
    
    async def test_enhanced_report_generation(self) -> Dict[str, Any]:
        """Test enhanced financial report generation"""
        print("\n📊 Testing Enhanced Report Generation...")
        
        test_data = {
            "revenue": 217000,
            "expenses": 40000,
            "profit": 177000,
            "cash_flow": 150000
        }
        
        try:
            report = await self.service.generate_financial_report(
                financial_data=test_data,
                report_type="annual",
                period="2024",
                company_name="TechStart Inc.",
                context="Technology startup with strong growth"
            )
            
            result = {
                "test": "enhanced_report_generation",
                "report_type": report.get("report_type"),
                "company": report.get("company"),
                "has_executive_summary": bool(report.get("executive_summary")),
                "has_financial_highlights": bool(report.get("financial_highlights")),
                "has_trend_analysis": bool(report.get("trend_analysis")),
                "has_recommendations": bool(report.get("recommendations")),
                "generation_method": report.get("report_metadata", {}).get("generation_method"),
                "success": True
            }
            
            print(f"✅ Report type: {result['report_type']}")
            print(f"✅ Company: {result['company']}")
            print(f"✅ Executive summary: {result['has_executive_summary']}")
            print(f"✅ Financial highlights: {result['has_financial_highlights']}")
            print(f"✅ Trend analysis: {result['has_trend_analysis']}")
            print(f"✅ Recommendations: {result['has_recommendations']}")
            
            return result
            
        except Exception as e:
            return {
                "test": "enhanced_report_generation",
                "error": str(e),
                "success": False
            }
    
    async def test_enhanced_natural_language_query(self) -> Dict[str, Any]:
        """Test enhanced natural language query processing"""
        print("\n🔍 Testing Enhanced Natural Language Query...")
        
        test_queries = [
            "What is the total revenue?",
            "Show me all expenses by category",
            "What are the trends in our financial data?",
            "When were the largest transactions made?"
        ]
        
        context_data = {
            "revenue": 50000,
            "expenses": 15000,
            "profit": 35000,
            "cloud_costs": 5000,
            "marketing": 3000,
            "office": 7000
        }
        
        results = []
        for i, query in enumerate(test_queries):
            try:
                response = await self.service.natural_language_query(
                    query=query,
                    context_data=context_data
                )
                
                results.append({
                    "query": i + 1,
                    "query_text": query,
                    "query_type": response.get("query_type", "general"),
                    "confidence": response.get("confidence", 0.0),
                    "matched_keys": len(response.get("matched_keys", [])),
                    "relevant_numbers": len(response.get("relevant_numbers", [])),
                    "success": True
                })
                
                print(f"✅ Query {i+1}: Type={response.get('query_type', 'general')}, Confidence={response.get('confidence', 0.0):.2f}")
                
            except Exception as e:
                results.append({
                    "query": i + 1,
                    "query_text": query,
                    "error": str(e),
                    "success": False
                })
                print(f"❌ Query {i+1} failed: {e}")
        
        return {
            "test": "enhanced_natural_language_query",
            "results": results,
            "success": all(r["success"] for r in results)
        }
    
    async def test_fraud_detection(self) -> Dict[str, Any]:
        """Test fraud detection capabilities"""
        print("\n🚨 Testing Fraud Detection...")
        
        test_transactions = [
            {"amount": 100, "vendor": "Office Supplies Inc."},
            {"amount": 150, "vendor": "Cloud Services Ltd."},
            {"amount": 2000, "vendor": "Office Supplies Inc."},  # Suspicious large amount
            {"amount": 75, "vendor": "Office Supplies Inc."},   # Same vendor multiple times
            {"amount": 300, "vendor": "Office Supplies Inc."},
            {"amount": 50000, "vendor": "Unknown Vendor"}       # Very large amount
        ]
        
        try:
            fraud_analysis = await self.service.detect_fraud_patterns(
                transactions=test_transactions
            )
            
            result = {
                "test": "fraud_detection",
                "risk_level": fraud_analysis.get("risk_level", "unknown"),
                "risk_score": fraud_analysis.get("risk_score", 0),
                "confidence": fraud_analysis.get("confidence", 0.0),
                "fraud_indicators": len(fraud_analysis.get("fraud_indicators", [])),
                "transactions_analyzed": fraud_analysis.get("analysis_metadata", {}).get("transactions_analyzed", 0),
                "success": True
            }
            
            print(f"✅ Risk level: {result['risk_level']}")
            print(f"✅ Risk score: {result['risk_score']}")
            print(f"✅ Confidence: {result['confidence']:.2f}")
            print(f"✅ Fraud indicators: {result['fraud_indicators']}")
            print(f"✅ Transactions analyzed: {result['transactions_analyzed']}")
            
            return result
            
        except Exception as e:
            return {
                "test": "fraud_detection",
                "error": str(e),
                "success": False
            }
    
    async def test_compliance_checking(self) -> Dict[str, Any]:
        """Test compliance checking capabilities"""
        print("\n📋 Testing Compliance Checking...")
        
        test_financial_data = {
            "balance_sheet": 100000,
            "income_statement": 50000,
            "transaction_date": "2024-01-15",
            "account_balance": 25000,
            "tax_amount": 5000
        }
        
        try:
            compliance_analysis = await self.service.check_compliance(
                financial_data=test_financial_data,
                regulations=["basic_accounting", "tax_compliance", "audit_standards"]
            )
            
            result = {
                "test": "compliance_checking",
                "overall_compliance": compliance_analysis.get("overall_compliance", False),
                "compliance_score": compliance_analysis.get("compliance_score", 0.0),
                "regulations_checked": len(compliance_analysis.get("regulation_results", {})),
                "recommendations": len(compliance_analysis.get("recommendations", [])),
                "success": True
            }
            
            print(f"✅ Overall compliance: {result['overall_compliance']}")
            print(f"✅ Compliance score: {result['compliance_score']:.2f}")
            print(f"✅ Regulations checked: {result['regulations_checked']}")
            print(f"✅ Recommendations: {result['recommendations']}")
            
            return result
            
        except Exception as e:
            return {
                "test": "compliance_checking",
                "error": str(e),
                "success": False
            }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all enhanced GitHub Models tests"""
        print("🚀 Starting Enhanced GitHub Models Test Suite")
        print("=" * 60)
        
        tests = [
            self.test_service_initialization,
            self.test_enhanced_document_analysis,
            self.test_enhanced_expense_categorization,
            self.test_enhanced_financial_insights,
            self.test_enhanced_report_generation,
            self.test_enhanced_natural_language_query,
            self.test_fraud_detection,
            self.test_compliance_checking
        ]
        
        results = []
        for test in tests:
            try:
                result = await test()
                results.append(result)
                self.test_results.append(result)
            except Exception as e:
                error_result = {
                    "test": test.__name__,
                    "error": str(e),
                    "success": False
                }
                results.append(error_result)
                self.test_results.append(error_result)
                print(f"❌ Test {test.__name__} failed: {e}")
        
        # Generate summary
        successful_tests = [r for r in results if r.get("success", False)]
        failed_tests = [r for r in results if not r.get("success", False)]
        
        summary = {
            "total_tests": len(results),
            "successful_tests": len(successful_tests),
            "failed_tests": len(failed_tests),
            "success_rate": len(successful_tests) / len(results) if results else 0,
            "test_results": results,
            "timestamp": datetime.now().isoformat()
        }
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Successful: {summary['successful_tests']}/{summary['total_tests']}")
        print(f"❌ Failed: {summary['failed_tests']}/{summary['total_tests']}")
        print(f"📈 Success Rate: {summary['success_rate']:.1%}")
        
        if failed_tests:
            print("\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"   - {test.get('test', 'Unknown')}: {test.get('error', 'Unknown error')}")
        
        return summary


async def main():
    """Main test runner"""
    tester = EnhancedGitHubModelsTester()
    summary = await tester.run_all_tests()
    
    # Save results to file
    output_file = "enhanced_github_models_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n💾 Test results saved to: {output_file}")
    
    # Return exit code based on success rate
    if summary["success_rate"] >= 0.8:
        print("🎉 Enhanced GitHub Models test suite completed successfully!")
        return 0
    else:
        print("⚠️ Some tests failed. Please review the results.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
