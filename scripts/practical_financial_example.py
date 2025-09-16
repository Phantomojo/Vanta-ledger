#!/usr/bin/env python3
"""
Practical Example: How Multiple Models Help with Financial Tasks
Real-world scenarios showing the benefits of multiple AI models.
"""
import sys
import asyncio
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

# Add backend to path
backend_path = Path("backend/src")
if backend_path.exists():
    sys.path.insert(0, str(backend_path))

async def example_invoice_processing():
    """Example: Processing a complex invoice with multiple models"""
    logger.info("📄 Example 1: Complex Invoice Processing")
    logger.info("=")
    
    invoice_text = """
    INVOICE #INV-2024-001
    
    From: TechSolutions Inc.
    To: Vanta Ledger Corp.
    
    Services Rendered:
    - Cloud Infrastructure Setup: $2,500
    - Database Migration: $1,800
    - Security Audit: $3,200
    - Training Sessions (2 days): $1,600
    
    Subtotal: $9,100
    Tax (8.5%): $773.50
    Total: $9,873.50
    
    Payment Terms: Net 30
    Due Date: December 15, 2024
    """
    
    logger.info("📋 Invoice Content:")
    logger.info(invoice_text)
    print()
    
    # Simulate different model analyses
    analyses = {
        "GPT-4o-mini (Fast)": {
            "total_amount": 9873.50,
            "vendor": "TechSolutions Inc.",
            "category": "Professional Services",
            "processing_time": "0.5s",
            "cost": "$0.00015"
        },
        "Claude-3-haiku (Accurate)": {
            "total_amount": 9873.50,
            "vendor": "TechSolutions Inc.",
            "category": "IT Services",
            "processing_time": "0.8s",
            "cost": "$0.00025"
        },
        "Gemini-1.5-flash (Efficient)": {
            "total_amount": 9873.50,
            "vendor": "TechSolutions Inc.",
            "category": "Technology Services",
            "processing_time": "0.3s",
            "cost": "$0.000075"
        }
    }
    
    logger.info("🤖 Individual Model Results:")
    for model, result in analyses.items():
        logger.info(f"   {model}:")
        logger.info(f"     Amount: ${result[")
        logger.info(f"     Vendor: {result[")
        logger.info(f"     Category: {result[")
        logger.info(f"     Speed: {result[")
        logger.info(f"     Cost: {result[")
        print()
    
    # Consensus result
    logger.info("🤝 Consensus Result:")
    logger.info("   ✅ Amount: $9,873.50 (All models agree)")
    logger.info("   ✅ Vendor: TechSolutions Inc. (All models agree)")
    logger.info("   📊 Category: Professional Services (Majority consensus)")
    logger.info("   ⚡ Average Speed: 0.53s")
    logger.info("   💰 Total Cost: $0.000475 (Very low)")
    print()

async def example_fraud_detection():
    """Example: Fraud detection using multiple models"""
    logger.info("🔍 Example 2: Fraud Detection")
    logger.info("=")
    
    transactions = [
        {"amount": 5000, "vendor": "Unknown Vendor", "date": "2024-12-01", "type": "suspicious"},
        {"amount": 250, "vendor": "Office Supplies Co", "date": "2024-12-01", "type": "normal"},
        {"amount": 15000, "vendor": "Suspicious Company", "date": "2024-12-01", "type": "suspicious"},
        {"amount": 1200, "vendor": "AWS", "date": "2024-12-01", "type": "normal"}
    ]
    
    logger.info("📊 Transaction Analysis:")
    for tx in transactions:
        status = "🚨" if tx["type"] == "suspicious" else "✅"
        logger.info(f"   {status} ${tx[")
    print()
    
    # Different models detect different patterns
    fraud_analysis = {
        "Claude-3-5-sonnet (Reasoning)": {
            "suspicious_transactions": [0, 2],
            "reasoning": "Large amounts from unknown vendors",
            "confidence": 0.95
        },
        "GPT-4o (Pattern Recognition)": {
            "suspicious_transactions": [0, 2],
            "reasoning": "Unusual vendor names and amounts",
            "confidence": 0.88
        },
        "Mistral-large (Anomaly Detection)": {
            "suspicious_transactions": [0, 2, 3],
            "reasoning": "Amount patterns and vendor analysis",
            "confidence": 0.92
        }
    }
    
    logger.info("🔍 Fraud Detection Results:")
    for model, result in fraud_analysis.items():
        logger.info(f"   {model}:")
        logger.info(f"     Suspicious: Transactions {result[")
        logger.info(f"     Reasoning: {result[")
        logger.info(f"     Confidence: {result[")
        print()
    
    logger.info("🤝 Combined Fraud Detection:")
    logger.info("   🚨 High Risk: Transactions 0, 2 (All models agree)")
    logger.info("   ⚠️ Medium Risk: Transaction 3 (One model flagged)")
    logger.info("   ✅ Low Risk: Transaction 1 (All models clear)")
    print()

async def example_code_generation():
    """Example: Generating financial calculation code"""
    logger.info("💻 Example 3: Code Generation for Financial Calculations")
    logger.info("=")
    
    requirement = "Generate Python code to calculate tax deductions for business expenses"
    
    logger.info(f"📋 Requirement: {requirement}")
    print()
    
    # Different models generate different code approaches
    code_examples = {
        "CodeLlama-70b (Specialized)": {
            "approach": "Comprehensive class-based solution",
            "features": ["OOP", "Error handling", "Documentation"],
            "lines": 45,
            "quality": "Excellent"
        },
        "CodeLlama-34b (Efficient)": {
            "approach": "Functional programming approach",
            "features": ["Pure functions", "Type hints", "Testing"],
            "lines": 32,
            "quality": "Very Good"
        },
        "GPT-4o (Explanatory)": {
            "approach": "Clear, well-documented solution",
            "features": ["Comments", "Examples", "Best practices"],
            "lines": 38,
            "quality": "Excellent"
        }
    }
    
    logger.info("💻 Code Generation Results:")
    for model, result in code_examples.items():
        logger.info(f"   {model}:")
        logger.info(f"     Approach: {result[")
        logger.info(f"     Features: {")
        logger.info(f"     Lines: {result[")
        logger.info(f"     Quality: {result[")
        print()
    
    logger.info("🤝 Combined Code Solution:")
    logger.info("   ✅ Best practices from all models")
    logger.error("   ✅ Comprehensive error handling")
    logger.info("   ✅ Well-documented and tested")
    logger.info("   ✅ Multiple implementation approaches")
    print()

async def example_financial_analysis():
    """Example: Complex financial analysis"""
    logger.info("📊 Example 4: Quarterly Financial Analysis")
    logger.info("=")
    
    financial_data = """
    Q4 2024 Financial Summary:
    
    Revenue: $2,500,000
    Expenses: $1,800,000
    Net Income: $700,000
    
    Key Metrics:
    - Profit Margin: 28%
    - Revenue Growth: 15% vs Q3
    - Expense Ratio: 72%
    - Cash Flow: $650,000
    """
    
    logger.info("📈 Financial Data:")
    logger.info(financial_data)
    print()
    
    # Different models provide different insights
    insights = {
        "Claude-3-5-sonnet (Deep Analysis)": {
            "key_insights": [
                "Strong profit margin indicates good cost control",
                "Revenue growth suggests market expansion",
                "Cash flow is healthy at 93% of net income"
            ],
            "recommendations": [
                "Consider reinvesting excess cash",
                "Monitor expense ratio trends",
                "Plan for continued growth"
            ]
        },
        "GPT-4o (Strategic)": {
            "key_insights": [
                "28% profit margin is above industry average",
                "15% growth rate is sustainable",
                "Expense ratio is well-managed"
            ],
            "recommendations": [
                "Explore new market opportunities",
                "Optimize operational efficiency",
                "Strengthen cash reserves"
            ]
        },
        "Gemini-1.5-pro (Comprehensive)": {
            "key_insights": [
                "Financial health is excellent",
                "Growth trajectory is positive",
                "Risk profile is low"
            ],
            "recommendations": [
                "Maintain current strategies",
                "Invest in technology",
                "Expand team capabilities"
            ]
        }
    }
    
    logger.info("🧠 Analysis Results:")
    for model, result in insights.items():
        logger.info(f"   {model}:")
        logger.info("     Key Insights:")
        for insight in result["key_insights"]:
            logger.info(f"       • {insight}")
        logger.info("     Recommendations:")
        for rec in result["recommendations"]:
            logger.info(f"       • {rec}")
        print()
    
    logger.info("🤝 Combined Analysis:")
    logger.info("   📊 Comprehensive financial health assessment")
    logger.info("   🎯 Strategic recommendations from multiple perspectives")
    logger.info("   🔍 Risk analysis and opportunity identification")
    logger.info("   📈 Growth strategy and operational insights")
    print()

async def main():
    """Main example function"""
    logger.info("🚀 Practical Examples: How Multiple Models Help Vanta Ledger")
    logger.info("=")
    print()
    
    await example_invoice_processing()
    await example_fraud_detection()
    await example_code_generation()
    await example_financial_analysis()
    
    logger.info("🎉 Key Takeaways:")
    logger.info("=")
    logger.info("✅ Multiple models provide redundancy and reliability")
    logger.info("✅ Different models excel at different tasks")
    logger.info("✅ Consensus improves accuracy and confidence")
    logger.info("✅ Cost-effective by using right model for each task")
    logger.info("✅ Faster processing through parallel execution")
    logger.info("✅ Comprehensive analysis from multiple perspectives")
    logger.info("✅ Future-proof system that can easily add new models")

if __name__ == "__main__":
    asyncio.run(main())
