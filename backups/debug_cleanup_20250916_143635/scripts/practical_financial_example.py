#!/usr/bin/env python3
"""
Practical Example: How Multiple Models Help with Financial Tasks
Real-world scenarios showing the benefits of multiple AI models.
"""
import sys
import asyncio
from pathlib import Path

# Add backend to path
backend_path = Path("backend/src")
if backend_path.exists():
    sys.path.insert(0, str(backend_path))

async def example_invoice_processing():
    """Example: Processing a complex invoice with multiple models"""
    print("📄 Example 1: Complex Invoice Processing")
    print("=" * 50)
    
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
    
    print("📋 Invoice Content:")
    print(invoice_text)
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
    
    print("🤖 Individual Model Results:")
    for model, result in analyses.items():
        print(f"   {model}:")
        print(f"     Amount: ${result['total_amount']}")
        print(f"     Vendor: {result['vendor']}")
        print(f"     Category: {result['category']}")
        print(f"     Speed: {result['processing_time']}")
        print(f"     Cost: {result['cost']}")
        print()
    
    # Consensus result
    print("🤝 Consensus Result:")
    print("   ✅ Amount: $9,873.50 (All models agree)")
    print("   ✅ Vendor: TechSolutions Inc. (All models agree)")
    print("   📊 Category: Professional Services (Majority consensus)")
    print("   ⚡ Average Speed: 0.53s")
    print("   💰 Total Cost: $0.000475 (Very low)")
    print()

async def example_fraud_detection():
    """Example: Fraud detection using multiple models"""
    print("🔍 Example 2: Fraud Detection")
    print("=" * 50)
    
    transactions = [
        {"amount": 5000, "vendor": "Unknown Vendor", "date": "2024-12-01", "type": "suspicious"},
        {"amount": 250, "vendor": "Office Supplies Co", "date": "2024-12-01", "type": "normal"},
        {"amount": 15000, "vendor": "Suspicious Company", "date": "2024-12-01", "type": "suspicious"},
        {"amount": 1200, "vendor": "AWS", "date": "2024-12-01", "type": "normal"}
    ]
    
    print("📊 Transaction Analysis:")
    for tx in transactions:
        status = "🚨" if tx["type"] == "suspicious" else "✅"
        print(f"   {status} ${tx['amount']} - {tx['vendor']}")
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
    
    print("🔍 Fraud Detection Results:")
    for model, result in fraud_analysis.items():
        print(f"   {model}:")
        print(f"     Suspicious: Transactions {result['suspicious_transactions']}")
        print(f"     Reasoning: {result['reasoning']}")
        print(f"     Confidence: {result['confidence']}")
        print()
    
    print("🤝 Combined Fraud Detection:")
    print("   🚨 High Risk: Transactions 0, 2 (All models agree)")
    print("   ⚠️ Medium Risk: Transaction 3 (One model flagged)")
    print("   ✅ Low Risk: Transaction 1 (All models clear)")
    print()

async def example_code_generation():
    """Example: Generating financial calculation code"""
    print("💻 Example 3: Code Generation for Financial Calculations")
    print("=" * 50)
    
    requirement = "Generate Python code to calculate tax deductions for business expenses"
    
    print(f"📋 Requirement: {requirement}")
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
    
    print("💻 Code Generation Results:")
    for model, result in code_examples.items():
        print(f"   {model}:")
        print(f"     Approach: {result['approach']}")
        print(f"     Features: {', '.join(result['features'])}")
        print(f"     Lines: {result['lines']}")
        print(f"     Quality: {result['quality']}")
        print()
    
    print("🤝 Combined Code Solution:")
    print("   ✅ Best practices from all models")
    print("   ✅ Comprehensive error handling")
    print("   ✅ Well-documented and tested")
    print("   ✅ Multiple implementation approaches")
    print()

async def example_financial_analysis():
    """Example: Complex financial analysis"""
    print("📊 Example 4: Quarterly Financial Analysis")
    print("=" * 50)
    
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
    
    print("📈 Financial Data:")
    print(financial_data)
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
    
    print("🧠 Analysis Results:")
    for model, result in insights.items():
        print(f"   {model}:")
        print("     Key Insights:")
        for insight in result["key_insights"]:
            print(f"       • {insight}")
        print("     Recommendations:")
        for rec in result["recommendations"]:
            print(f"       • {rec}")
        print()
    
    print("🤝 Combined Analysis:")
    print("   📊 Comprehensive financial health assessment")
    print("   🎯 Strategic recommendations from multiple perspectives")
    print("   🔍 Risk analysis and opportunity identification")
    print("   📈 Growth strategy and operational insights")
    print()

async def main():
    """Main example function"""
    print("🚀 Practical Examples: How Multiple Models Help Vanta Ledger")
    print("=" * 70)
    print()
    
    await example_invoice_processing()
    await example_fraud_detection()
    await example_code_generation()
    await example_financial_analysis()
    
    print("🎉 Key Takeaways:")
    print("=" * 30)
    print("✅ Multiple models provide redundancy and reliability")
    print("✅ Different models excel at different tasks")
    print("✅ Consensus improves accuracy and confidence")
    print("✅ Cost-effective by using right model for each task")
    print("✅ Faster processing through parallel execution")
    print("✅ Comprehensive analysis from multiple perspectives")
    print("✅ Future-proof system that can easily add new models")

if __name__ == "__main__":
    asyncio.run(main())
