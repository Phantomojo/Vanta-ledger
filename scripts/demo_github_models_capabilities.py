#!/usr/bin/env python3
"""
Demo GitHub Models Capabilities
Shows the integration structure and available features without requiring API calls
"""

import json
from pathlib import Path

def show_project_structure():
    """Show the GitHub Models integration structure"""
    print("🏗️  GitHub Models Integration Structure")
    print("=" * 50)
    
    structure = {
        "📁 prompts/": {
            "financial_analysis/": [
                "invoice_analyzer.prompt.yml - Extract structured data from invoices",
                "expense_categorizer.prompt.yml - Categorize business expenses",
                "financial_insights.prompt.yml - Generate strategic insights",
                "report_generator.prompt.yml - Create comprehensive reports"
            ],
            "program_analysis/": [
                "code_reviewer.prompt.yml - Review code quality and security",
                "system_health_analyzer.prompt.yml - Analyze system metrics"
            ]
        },
        "📁 src/vanta_ledger/services/": [
            "github_models_service.py - Core GitHub Models integration",
            "system_analysis_service.py - System health and code analysis",
            "document_processor.py - Enhanced with AI capabilities"
        ],
        "📁 src/vanta_ledger/routes/": [
            "github_models.py - API endpoints for GitHub Models"
        ],
        "📄 Files": [
            "requirements.txt - Updated with openai==1.98.0",
            "test_github_models_integration.py - Comprehensive test suite",
            "demo_github_models_capabilities.py - This demo"
        ]
    }
    
    def print_structure(items, indent=0):
        for key, value in items.items():
            print("  " * indent + key)
            if isinstance(value, dict):
                print_structure(value, indent + 1)
            elif isinstance(value, list):
                for item in value:
                    print("  " * (indent + 1) + "• " + item)
    
    print_structure(structure)

def show_prompt_templates():
    """Show available YAML prompt templates"""
    print("\n📝 YAML Prompt Templates")
    print("=" * 50)
    
    prompt_dir = Path("prompts")
    if prompt_dir.exists():
        for prompt_file in prompt_dir.rglob("*.prompt.yml"):
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extract name and description from YAML
                lines = content.split('\n')
                name = "Unknown"
                description = "No description"
                model = "Unknown"
                
                for line in lines:
                    if line.startswith('name:'):
                        name = line.split(':', 1)[1].strip()
                    elif line.startswith('description:'):
                        description = line.split(':', 1)[1].strip()
                    elif line.startswith('model:'):
                        model = line.split(':', 1)[1].strip()
                
                print(f"\n✅ {prompt_file.name}")
                print(f"   Name: {name}")
                print(f"   Description: {description}")
                print(f"   Model: {model}")
                
            except Exception as e:
                print(f"❌ Error reading {prompt_file}: {e}")
    else:
        print("❌ Prompts directory not found")

def show_api_endpoints():
    """Show available API endpoints"""
    print("\n🌐 GitHub Models API Endpoints")
    print("=" * 50)
    
    endpoints = {
        "Health & Status": [
            "GET /github-models/health - Check service status and configuration"
        ],
        "Document Analysis": [
            "POST /github-models/analyze-document - Analyze document text",
            "POST /github-models/analyze-document-upload - Upload and analyze files",
            "POST /github-models/batch-analyze - Batch process multiple documents"
        ],
        "Financial Intelligence": [
            "POST /github-models/categorize-expense - Categorize business expenses",
            "POST /github-models/generate-insights - Generate financial insights",
            "POST /github-models/generate-report - Create comprehensive reports"
        ],
        "Natural Language": [
            "POST /github-models/query - Process natural language queries"
        ],
        "Template Management": [
            "GET /github-models/prompts - List available prompt templates",
            "GET /github-models/prompts/{name} - Get prompt template details"
        ]
    }
    
    for category, endpoint_list in endpoints.items():
        print(f"\n📂 {category}:")
        for endpoint in endpoint_list:
            print(f"   • {endpoint}")

def show_usage_examples():
    """Show usage examples"""
    print("\n💡 Usage Examples")
    print("=" * 50)
    
    examples = {
        "Environment Setup": '''
# Set your GitHub token
export GITHUB_TOKEN="your_github_token_here"

# Or add to .env file
echo "GITHUB_TOKEN=your_github_token_here" >> .env
        ''',
        
        "Python Service Usage": '''
from src.vanta_ledger.services.github_models_service import github_models_service

# Analyze an invoice
result = await github_models_service.analyze_financial_document(
    document_text="INVOICE #001...",
    document_type="invoice"
)

# Categorize an expense
category = await github_models_service.categorize_expense(
    description="Office supplies from Staples",
    amount=45.99,
    vendor="Staples"
)

# Generate financial insights
insights = await github_models_service.generate_financial_insights(
    financial_data={"total_expenses": 50000, ...},
    period="Q1 2024",
    company_size="startup"
)
        ''',
        
        "API Usage (curl)": '''
# Health check
curl http://localhost:8500/github-models/health

# Analyze document
curl -X POST http://localhost:8500/github-models/analyze-document \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -d '{
    "document_text": "INVOICE #001...",
    "document_type": "invoice"
  }'

# Upload and analyze file
curl -X POST http://localhost:8500/github-models/analyze-document-upload \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -F "file=@invoice.pdf" \\
  -F "document_type=invoice"
        ''',
        
        "System Analysis": '''
from src.vanta_ledger.services.system_analysis_service import system_analysis_service

# Analyze system health
health = await system_analysis_service.analyze_system_health()

# Review code quality
code_review = await system_analysis_service.analyze_code_quality(
    file_path="src/vanta_ledger/auth.py",
    context="Authentication service security review"
)

# Analyze entire project
project_analysis = await system_analysis_service.analyze_project_codebase(
    project_dir=".",
    include_patterns=["*.py"],
    exclude_patterns=["__pycache__", ".venv"]
)
        '''
    }
    
    for category, example in examples.items():
        print(f"\n📋 {category}:")
        print("```")
        print(example.strip())
        print("```")

def show_capabilities():
    """Show AI capabilities and features"""
    print("\n🤖 AI Capabilities")
    print("=" * 50)
    
    capabilities = {
        "Financial Document Processing": [
            "✅ Invoice data extraction (vendor, amounts, dates, line items)",
            "✅ Receipt processing and categorization",
            "✅ Contract analysis and key term identification",
            "✅ Financial report parsing and insights"
        ],
        "Expense Management": [
            "✅ Intelligent expense categorization (14+ business categories)",
            "✅ Tax deductibility assessment",
            "✅ Compliance notes and recommendations",
            "✅ Vendor analysis and optimization"
        ],
        "Financial Intelligence": [
            "✅ Strategic financial insights and recommendations",
            "✅ Trend analysis and anomaly detection",
            "✅ Risk assessment and mitigation strategies",
            "✅ Executive-level reporting and KPI analysis"
        ],
        "System Analysis": [
            "✅ Code quality and security review",
            "✅ System health monitoring and alerts",
            "✅ Performance analysis and optimization",
            "✅ Architecture and design pattern evaluation"
        ],
        "Natural Language Processing": [
            "✅ Query financial data in plain English",
            "✅ Generate human-readable reports",
            "✅ Extract insights from unstructured data",
            "✅ Contextual recommendations and suggestions"
        ]
    }
    
    for category, feature_list in capabilities.items():
        print(f"\n🎯 {category}:")
        for feature in feature_list:
            print(f"   {feature}")

def show_security_features():
    """Show security and best practices"""
    print("\n🔒 Security & Best Practices")
    print("=" * 50)
    
    security_features = [
        "✅ No hardcoded secrets - uses environment variables only",
        "✅ Secure token handling with GitHub Models API",
        "✅ Request caching with Redis to minimize API calls",
        "✅ Error handling that doesn't expose sensitive information",
        "✅ JWT-based authentication for all API endpoints",
        "✅ Rate limiting and request validation",
        "✅ Structured logging without sensitive data",
        "✅ Template-based prompts prevent injection attacks"
    ]
    
    print("🛡️  Security Features:")
    for feature in security_features:
        print(f"   {feature}")
    
    print(f"\n⚠️  Important Notes:")
    print(f"   • Never commit GITHUB_TOKEN to version control")
    print(f"   • Use environment variables or secure secret management")
    print(f"   • Monitor API usage and costs")
    print(f"   • Review AI responses before acting on recommendations")
    print(f"   • Implement proper access controls for sensitive endpoints")

def main():
    """Run the complete demo"""
    print("🚀 GitHub Models Integration Demo")
    print("Vanta Ledger - Advanced AI-Powered Financial Analysis")
    print("=" * 80)
    
    show_project_structure()
    show_prompt_templates()
    show_api_endpoints()
    show_capabilities()
    show_usage_examples()
    show_security_features()
    
    print(f"\n🎉 GitHub Models Integration Complete!")
    print("=" * 80)
    print(f"📚 Next Steps:")
    print(f"   1. Set your GITHUB_TOKEN environment variable")
    print(f"   2. Run: python test_github_models_integration.py")
    print(f"   3. Start the server: python -m uvicorn src.vanta_ledger.main:app --reload")
    print(f"   4. Test API endpoints at: http://localhost:8500/docs")
    print(f"   5. Upload documents via: /github-models/analyze-document-upload")
    
    print(f"\n📖 Documentation:")
    print(f"   • API Docs: http://localhost:8500/docs")
    print(f"   • GitHub Models: https://github.com/marketplace/models")
    print(f"   • Prompts: ./prompts/ directory")
    print(f"   • Services: ./src/vanta_ledger/services/")

if __name__ == "__main__":
    main()





