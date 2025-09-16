#!/usr/bin/env python3
"""
Demo: How Multiple Models Help Vanta Ledger
Shows the benefits of using multiple AI models for better accuracy and reliability.
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

async def demo_accuracy_improvement():
    """Demo how multiple models improve accuracy"""
    logger.info("🎯 Accuracy Improvement Demo")
    logger.info("=")
    
    # Simulate different model responses for the same financial document
    document = "Invoice for $1,250 from ABC Consulting for Q4 2024 services"
    
    logger.info(f"📄 Document: {document}")
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
    
    logger.info("📊 Individual Model Responses:")
    for model, response in model_responses.items():
        logger.info(f"   {model}:")
        logger.info(f"     Amount: ${response[")
        logger.info(f"     Vendor: {response[")
        logger.info(f"     Category: {response[")
        logger.info(f"     Confidence: {response[")
        print()
    
    # Calculate consensus
    amounts = [r['amount'] for r in model_responses.values()]
    vendors = [r['vendor'] for r in model_responses.values()]
    categories = [r['category'] for r in model_responses.values()]
    confidences = [r['confidence'] for r in model_responses.values()]
    
    logger.info("🤝 Consensus Analysis:")
    logger.info(f"   Amount Agreement: {len(set(amounts)) == 1} (All models agree: ${amounts[0]})")
    logger.info(f"   Vendor Agreement: {len(set(vendors)) == 1} (All models agree: {vendors[0]})")
    logger.info(f"   Category Agreement: {len(set(categories)) == 1} (Partial agreement)")
    logger.info(f"   Average Confidence: {sum(confidences)/len(confidences):.2f}")
    logger.info(f"   Highest Confidence: {max(confidences):.2f}")
    print()

async def demo_specialization():
    """Demo how different models specialize in different tasks"""
    logger.info("🎨 Model Specialization Demo")
    logger.info("=")
    
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
        logger.info(f"📋 {task}:")
        logger.info(f"   Description: {details[")
        logger.info(f"   Best Models: {")
        logger.info(f"   Reason: {details[")
        print()

async def demo_cost_efficiency():
    """Demo how multiple models provide cost efficiency"""
    logger.info("💰 Cost Efficiency Demo")
    logger.info("=")
    
    model_costs = {
        "gpt-4o-mini": {"cost_per_1k_tokens": 0.00015, "speed": "fast", "accuracy": "good"},
        "gpt-4o": {"cost_per_1k_tokens": 0.005, "speed": "medium", "accuracy": "excellent"},
        "claude-3-haiku": {"cost_per_1k_tokens": 0.00025, "speed": "fast", "accuracy": "good"},
        "claude-3-5-sonnet": {"cost_per_1k_tokens": 0.003, "speed": "medium", "accuracy": "excellent"},
        "gemini-1.5-flash": {"cost_per_1k_tokens": 0.000075, "speed": "very_fast", "accuracy": "good"},
        "codellama-34b": {"cost_per_1k_tokens": 0.0001, "speed": "fast", "accuracy": "good"}
    }
    
    logger.info("📊 Model Cost Comparison:")
    for model, specs in model_costs.items():
        logger.info(f"   {model}:")
        logger.info(f"     Cost: ${specs[")
        logger.info(f"     Speed: {specs[")
        logger.info(f"     Accuracy: {specs[")
        print()
    
    logger.info("🎯 Smart Routing Strategy:")
    logger.info("   Simple tasks → Use cheaper models (gpt-4o-mini, gemini-1.5-flash)")
    logger.info("   Complex tasks → Use expensive models (gpt-4o, claude-3-5-sonnet)")
    logger.info("   Code tasks → Use specialized models (codellama-70b, codellama-34b)")
    print()

async def demo_real_world_scenarios():
    """Demo real-world scenarios where multiple models help"""
    logger.info("🌍 Real-World Scenarios")
    logger.info("=")
    
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
        logger.info(f"📋 {scenario[")
        logger.info(f"   Challenge: {scenario[")
        logger.info(f"   Models: {")
        logger.info(f"   Benefit: {scenario[")
        print()

async def main():
    """Main demo function"""
    logger.info("🚀 How Multiple Models Help Vanta Ledger")
    logger.info("=")
    print()
    
    await demo_accuracy_improvement()
    await demo_specialization()
    await demo_cost_efficiency()
    await demo_real_world_scenarios()
    
    logger.info("🎉 Summary of Benefits:")
    logger.info("=")
    logger.info("✅ Higher Accuracy: Consensus from multiple models")
    logger.error("✅ Better Reliability: Redundancy if one model fails")
    logger.info("✅ Specialized Expertise: Right model for each task")
    logger.info("✅ Cost Efficiency: Use cheaper models for simple tasks")
    logger.info("✅ Faster Processing: Parallel execution")
    logger.info("✅ Comprehensive Analysis: Multiple perspectives")
    logger.info("✅ Future-Proof: Easy to add new models")

if __name__ == "__main__":
    asyncio.run(main())
