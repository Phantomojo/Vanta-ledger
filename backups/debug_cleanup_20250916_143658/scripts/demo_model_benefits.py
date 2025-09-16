#!/usr/bin/env python3
"""
Demo: How Multiple Models Help Vanta Ledger
Shows the benefits of using multiple AI models for better accuracy and reliability.
"""
import sys
import asyncio
from pathlib import Path

# Add backend to path
backend_path = Path("backend/src")
if backend_path.exists():
    sys.path.insert(0, str(backend_path))

async def demo_accuracy_improvement():
    """Demo how multiple models improve accuracy"""
    print("🎯 Accuracy Improvement Demo")
    print("=" * 50)
    
    # Simulate different model responses for the same financial document
    document = "Invoice for $1,250 from ABC Consulting for Q4 2024 services"
    
    print(f"📄 Document: {document}")
    print()
    
    # Simulate responses from different models
    model_responses = {
        "GPT-4o-mini": {
            "amount": 1250,
            "vendor": "ABC Consulting",
            "category": "Professional Services",
            "confidence": 0.85
        },
        "Claude-3-haiku": {
            "amount": 1250,
            "vendor": "ABC Consulting", 
            "category": "Consulting",
            "confidence": 0.92
        },
        "Gemini-1.5-flash": {
            "amount": 1250,
            "vendor": "ABC Consulting",
            "category": "Professional Services",
            "confidence": 0.78
        }
    }
    
    print("📊 Individual Model Responses:")
    for model, response in model_responses.items():
        print(f"   {model}:")
        print(f"     Amount: ${response['amount']}")
        print(f"     Vendor: {response['vendor']}")
        print(f"     Category: {response['category']}")
        print(f"     Confidence: {response['confidence']}")
        print()
    
    # Calculate consensus
    amounts = [r['amount'] for r in model_responses.values()]
    vendors = [r['vendor'] for r in model_responses.values()]
    categories = [r['category'] for r in model_responses.values()]
    confidences = [r['confidence'] for r in model_responses.values()]
    
    print("🤝 Consensus Analysis:")
    print(f"   Amount Agreement: {len(set(amounts)) == 1} (All models agree: ${amounts[0]})")
    print(f"   Vendor Agreement: {len(set(vendors)) == 1} (All models agree: {vendors[0]})")
    print(f"   Category Agreement: {len(set(categories)) == 1} (Partial agreement)")
    print(f"   Average Confidence: {sum(confidences)/len(confidences):.2f}")
    print(f"   Highest Confidence: {max(confidences):.2f}")
    print()

async def demo_specialization():
    """Demo how different models specialize in different tasks"""
    print("🎨 Model Specialization Demo")
    print("=" * 50)
    
    tasks = {
        "Financial Analysis": {
            "description": "Analyze quarterly financial statements",
            "best_models": ["claude-3-5-sonnet", "gpt-4o", "gemini-1.5-pro"],
            "reason": "Strong reasoning and mathematical capabilities"
        },
        "Code Generation": {
            "description": "Generate Python code for expense calculation",
            "best_models": ["codellama-70b", "codellama-34b", "gpt-4o"],
            "reason": "Specialized in code generation and debugging"
        },
        "Document Summarization": {
            "description": "Summarize 50-page financial report",
            "best_models": ["claude-3-haiku", "gpt-4o-mini", "gemini-1.5-flash"],
            "reason": "Fast and efficient text processing"
        },
        "Fraud Detection": {
            "description": "Identify suspicious transaction patterns",
            "best_models": ["claude-3-5-sonnet", "gpt-4o", "mistral-large"],
            "reason": "Advanced pattern recognition and reasoning"
        }
    }
    
    for task, details in tasks.items():
        print(f"📋 {task}:")
        print(f"   Description: {details['description']}")
        print(f"   Best Models: {', '.join(details['best_models'])}")
        print(f"   Reason: {details['reason']}")
        print()

async def demo_cost_efficiency():
    """Demo how multiple models provide cost efficiency"""
    print("💰 Cost Efficiency Demo")
    print("=" * 50)
    
    model_costs = {
        "gpt-4o-mini": {"cost_per_1k_tokens": 0.00015, "speed": "fast", "accuracy": "good"},
        "gpt-4o": {"cost_per_1k_tokens": 0.005, "speed": "medium", "accuracy": "excellent"},
        "claude-3-haiku": {"cost_per_1k_tokens": 0.00025, "speed": "fast", "accuracy": "good"},
        "claude-3-5-sonnet": {"cost_per_1k_tokens": 0.003, "speed": "medium", "accuracy": "excellent"},
        "gemini-1.5-flash": {"cost_per_1k_tokens": 0.000075, "speed": "very_fast", "accuracy": "good"},
        "codellama-34b": {"cost_per_1k_tokens": 0.0001, "speed": "fast", "accuracy": "good"}
    }
    
    print("📊 Model Cost Comparison:")
    for model, specs in model_costs.items():
        print(f"   {model}:")
        print(f"     Cost: ${specs['cost_per_1k_tokens']:.6f}/1K tokens")
        print(f"     Speed: {specs['speed']}")
        print(f"     Accuracy: {specs['accuracy']}")
        print()
    
    print("🎯 Smart Routing Strategy:")
    print("   Simple tasks → Use cheaper models (gpt-4o-mini, gemini-1.5-flash)")
    print("   Complex tasks → Use expensive models (gpt-4o, claude-3-5-sonnet)")
    print("   Code tasks → Use specialized models (codellama-70b, codellama-34b)")
    print()

async def demo_real_world_scenarios():
    """Demo real-world scenarios where multiple models help"""
    print("🌍 Real-World Scenarios")
    print("=" * 50)
    
    scenarios = [
        {
            "scenario": "Invoice Processing",
            "challenge": "Extract amounts, vendors, and categorize expenses",
            "models_used": ["gpt-4o-mini", "claude-3-haiku", "gemini-1.5-flash"],
            "benefit": "Higher accuracy through consensus, faster processing"
        },
        {
            "scenario": "Financial Report Analysis",
            "challenge": "Analyze complex quarterly reports for insights",
            "models_used": ["claude-3-5-sonnet", "gpt-4o", "gemini-1.5-pro"],
            "benefit": "Deep reasoning, multiple perspectives, comprehensive analysis"
        },
        {
            "scenario": "Code Generation for Financial Calculations",
            "challenge": "Generate Python code for tax calculations",
            "models_used": ["codellama-70b", "codellama-34b", "gpt-4o"],
            "benefit": "Specialized code generation, debugging, documentation"
        },
        {
            "scenario": "Fraud Detection",
            "challenge": "Identify suspicious transaction patterns",
            "models_used": ["claude-3-5-sonnet", "gpt-4o", "mistral-large"],
            "benefit": "Advanced pattern recognition, multiple detection methods"
        }
    ]
    
    for scenario in scenarios:
        print(f"📋 {scenario['scenario']}:")
        print(f"   Challenge: {scenario['challenge']}")
        print(f"   Models: {', '.join(scenario['models_used'])}")
        print(f"   Benefit: {scenario['benefit']}")
        print()

async def main():
    """Main demo function"""
    print("🚀 How Multiple Models Help Vanta Ledger")
    print("=" * 60)
    print()
    
    await demo_accuracy_improvement()
    await demo_specialization()
    await demo_cost_efficiency()
    await demo_real_world_scenarios()
    
    print("🎉 Summary of Benefits:")
    print("=" * 30)
    print("✅ Higher Accuracy: Consensus from multiple models")
    print("✅ Better Reliability: Redundancy if one model fails")
    print("✅ Specialized Expertise: Right model for each task")
    print("✅ Cost Efficiency: Use cheaper models for simple tasks")
    print("✅ Faster Processing: Parallel execution")
    print("✅ Comprehensive Analysis: Multiple perspectives")
    print("✅ Future-Proof: Easy to add new models")

if __name__ == "__main__":
    asyncio.run(main())
