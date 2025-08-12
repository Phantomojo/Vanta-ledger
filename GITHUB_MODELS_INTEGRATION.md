# GitHub Models Integration Guide

## 🚀 Overview

The Vanta Ledger project now includes comprehensive GitHub Models integration for advanced AI-powered financial document processing, analysis, and reporting. This integration provides state-of-the-art AI capabilities for business intelligence and automation.

## 🎯 Key Features

### 📄 Document Processing
- **Invoice Analysis**: Extract structured data (vendor, amounts, dates, line items)
- **Receipt Processing**: Categorize and process business receipts
- **Contract Analysis**: Extract key terms and financial obligations
- **Multi-format Support**: PDF, DOCX, images with OCR capabilities

### 💰 Financial Intelligence
- **Expense Categorization**: 14+ standard business categories with confidence scoring
- **Tax Compliance**: Automatic deductibility assessment and compliance notes
- **Vendor Analysis**: Optimize vendor relationships and spending patterns
- **Financial Insights**: Strategic recommendations based on spending data

### 📊 Reporting & Analytics
- **Executive Reports**: Comprehensive financial reports with KPIs
- **Trend Analysis**: Spending patterns and anomaly detection
- **Risk Assessment**: Financial risk evaluation and mitigation strategies
- **Natural Language Queries**: Ask questions in plain English

### 🔧 System Analysis
- **Code Review**: Security and quality analysis of source code
- **Health Monitoring**: System performance and operational metrics
- **Architecture Analysis**: Design pattern evaluation and recommendations

## 🏗️ Architecture

### Core Components

```
prompts/                          # YAML prompt templates
├── financial_analysis/           # Financial AI prompts
│   ├── invoice_analyzer.prompt.yml
│   ├── expense_categorizer.prompt.yml
│   ├── financial_insights.prompt.yml
│   └── report_generator.prompt.yml
└── program_analysis/             # System analysis prompts
    ├── code_reviewer.prompt.yml
    └── system_health_analyzer.prompt.yml

src/vanta_ledger/services/        # AI services
├── github_models_service.py      # Core GitHub Models integration
├── system_analysis_service.py    # System health & code analysis
└── document_processor.py         # Enhanced document processing

src/vanta_ledger/routes/          # API endpoints
└── github_models.py              # GitHub Models API routes
```

### Service Integration

```python
# GitHub Models Service - Core AI functionality
github_models_service = GitHubModelsService()

# System Analysis Service - Health monitoring and code review
system_analysis_service = SystemAnalysisService()

# Enhanced Document Processor - AI-powered document processing
document_processor = DocumentProcessor()
```

## 🛠️ Setup & Configuration

### 1. Environment Setup

```bash
# Set GitHub token (required)
export GITHUB_TOKEN="your_github_token_here"

# Or add to .env file
echo "GITHUB_TOKEN=your_github_token_here" >> .env

# Optional configuration
export GITHUB_MODELS_DEFAULT_MODEL="openai/gpt-4o"
export GITHUB_MODELS_CACHE_TTL="3600"
```

### 2. Install Dependencies

```bash
# Install OpenAI client (already included in requirements.txt)
pip install openai==1.98.0

# Or install all requirements
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
# Run the demo
python demo_github_models_capabilities.py

# Run comprehensive tests (requires GITHUB_TOKEN)
python test_github_models_integration.py
```

## 📚 Usage Examples

### Python Service Usage

#### Document Analysis
```python
from src.vanta_ledger.services.github_models_service import github_models_service

# Analyze an invoice
result = await github_models_service.analyze_financial_document(
    document_text="INVOICE #001...",
    document_type="invoice"
)

print(f"Vendor: {result['vendor']}")
print(f"Amount: ${result['amount']}")
print(f"Confidence: {result['confidence']}%")
```

#### Expense Categorization
```python
# Categorize a business expense
category = await github_models_service.categorize_expense(
    description="Microsoft Office 365 subscription",
    amount=29.99,
    vendor="Microsoft"
)

print(f"Category: {category['category']}")
print(f"Tax Deductible: {category['tax_deductible']}")
print(f"Compliance: {category.get('compliance_notes', 'N/A')}")
```

#### Financial Insights
```python
# Generate strategic insights
insights = await github_models_service.generate_financial_insights(
    financial_data={
        "total_expenses": 125000,
        "expense_categories": {"Software": 35000, "Marketing": 28000},
        "monthly_growth": 12.5
    },
    period="Q1 2024",
    company_size="startup",
    industry="technology"
)

print(f"Executive Summary: {insights['executive_summary']}")
print(f"Key Insights: {insights['key_insights']}")
print(f"Recommendations: {insights['recommendations']}")
```

#### System Analysis
```python
from src.vanta_ledger.services.system_analysis_service import system_analysis_service

# Analyze system health
health = await system_analysis_service.analyze_system_health()
print(f"System Status: {health['system_status']}")
print(f"Health Score: {health['overall_health_score']}")

# Review code quality
review = await system_analysis_service.analyze_code_quality(
    file_path="src/vanta_ledger/auth.py",
    context="Security review of authentication service"
)
print(f"Quality Score: {review['overall_score']}")
print(f"Security Issues: {len(review['security_issues'])}")
```

### API Usage

#### Health Check
```bash
curl http://localhost:8500/github-models/health
```

#### Document Analysis
```bash
curl -X POST http://localhost:8500/github-models/analyze-document \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "document_text": "INVOICE #001 TechCorp Solutions...",
    "document_type": "invoice"
  }'
```

#### File Upload Analysis
```bash
curl -X POST http://localhost:8500/github-models/analyze-document-upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@invoice.pdf" \
  -F "document_type=invoice"
```

#### Expense Categorization
```bash
curl -X POST http://localhost:8500/github-models/categorize-expense \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "description": "Office supplies from Staples",
    "amount": 45.99,
    "vendor": "Staples"
  }'
```

#### Natural Language Query
```bash
curl -X POST http://localhost:8500/github-models/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "query": "What is our biggest expense category?",
    "context_data": {"total_expenses": 50000, "categories": {...}}
  }'
```

## 🎨 YAML Prompt Templates

### Template Structure
```yaml
name: Template Name
description: What this template does
model: openai/gpt-4o
modelParameters:
  temperature: 0.1
  max_tokens: 2000
messages:
  - role: system
    content: |
      System prompt with instructions...
  - role: user
    content: |
      User prompt with {{variables}}
testData:
  - variable1: "test value"
    expected: "expected output"
evaluators:
  - name: "validation rule"
    type: "validation criteria"
```

### Available Templates

#### Financial Analysis
- **`invoice_analyzer.prompt.yml`**: Extract structured data from invoices
- **`expense_categorizer.prompt.yml`**: Categorize business expenses
- **`financial_insights.prompt.yml`**: Generate strategic insights
- **`report_generator.prompt.yml`**: Create comprehensive reports

#### System Analysis
- **`code_reviewer.prompt.yml`**: Review code quality and security
- **`system_health_analyzer.prompt.yml`**: Analyze system health metrics

### Creating Custom Templates

```yaml
name: Custom Financial Analyzer
description: Custom analysis for specific use case
model: openai/gpt-4o
modelParameters:
  temperature: 0.2
messages:
  - role: system
    content: |
      You are a custom financial analyst...
  - role: user
    content: |
      Analyze this data: {{input_data}}
      Context: {{context}}
```

## 🔒 Security & Best Practices

### Security Features
- ✅ **No Hardcoded Secrets**: All tokens use environment variables
- ✅ **Secure API Handling**: Proper token management and error handling
- ✅ **Request Caching**: Redis caching to minimize API calls and costs
- ✅ **Error Sanitization**: No sensitive data in error responses
- ✅ **JWT Authentication**: All endpoints require proper authentication
- ✅ **Rate Limiting**: Built-in request rate limiting
- ✅ **Structured Logging**: Security-conscious logging without secrets

### Best Practices

#### Token Management
```bash
# ✅ GOOD: Use environment variables
export GITHUB_TOKEN="ghp_your_token_here"

# ❌ BAD: Never hardcode tokens
GITHUB_TOKEN="ghp_your_token_here"  # Don't do this!
```

#### Error Handling
```python
# ✅ GOOD: Generic error messages to users
try:
    result = await analyze_document(text)
except Exception as e:
    logger.error(f"Analysis failed: {e}")  # Log detailed error
    return {"error": "Analysis failed"}     # Generic user message

# ❌ BAD: Exposing internal errors
except Exception as e:
    return {"error": str(e)}  # Don't expose internal details
```

#### Cost Management
```python
# ✅ GOOD: Use caching to reduce API calls
@cache(ttl=3600)
async def analyze_document(text):
    return await github_models_service.analyze_financial_document(text)

# ✅ GOOD: Limit input size
if len(document_text) > 50000:
    document_text = document_text[:50000]  # Truncate large documents
```

## 📊 Monitoring & Analytics

### Health Monitoring
```python
# Check service health
health = await github_models_service._check_availability()
print(f"Service Available: {health}")

# Monitor API usage
metrics = {
    "requests_today": redis_client.get("github_models:requests:today"),
    "cache_hit_rate": redis_client.get("github_models:cache:hit_rate"),
    "average_response_time": redis_client.get("github_models:latency:avg")
}
```

### Performance Metrics
- **Response Time**: API call latency tracking
- **Cache Hit Rate**: Percentage of cached responses
- **Error Rate**: Failed request monitoring
- **Token Usage**: GitHub Models API consumption

## 🚀 Advanced Features

### Batch Processing
```python
# Process multiple documents
documents = [
    {"text": "Invoice 1...", "type": "invoice"},
    {"text": "Receipt 1...", "type": "receipt"}
]

results = []
for doc in documents:
    result = await github_models_service.analyze_financial_document(
        doc["text"], doc["type"]
    )
    results.append(result)
```

### Custom Prompt Development
```python
# Add custom variables to prompts
variables = {
    "company_name": "TechStart Inc",
    "fiscal_year": "2024",
    "custom_context": "SaaS startup analysis"
}

messages = github_models_service._render_prompt_template(
    "financial_insights", variables
)
```

### Integration with Existing Services
```python
# Enhanced document processor with AI
processor = DocumentProcessor()
result = await processor.process_document_async(
    file_path="invoice.pdf",
    original_filename="Q1_invoice.pdf"
)

# AI analysis is automatically included
ai_analysis = result["analysis"]["ai_analysis"]
```

## 🔧 Troubleshooting

### Common Issues

#### 1. GitHub Token Not Found
```
❌ Error: GITHUB_TOKEN not set
💡 Solution: export GITHUB_TOKEN="your_token_here"
```

#### 2. OpenAI Client Not Available
```
❌ Error: No module named 'openai'
💡 Solution: pip install openai==1.98.0
```

#### 3. Service Not Enabled
```python
if not github_models_service.enabled:
    print("Check GITHUB_TOKEN and OpenAI installation")
```

#### 4. API Rate Limits
```python
# Implement backoff strategy
import asyncio
from random import uniform

async def analyze_with_backoff(text):
    for attempt in range(3):
        try:
            return await github_models_service.analyze_financial_document(text)
        except Exception as e:
            if "rate limit" in str(e).lower():
                await asyncio.sleep(uniform(1, 3) * (2 ** attempt))
            else:
                raise
```

### Debug Mode
```python
# Enable debug logging
import logging
logging.getLogger("src.vanta_ledger.services.github_models_service").setLevel(logging.DEBUG)

# Check service status
print(f"Service enabled: {github_models_service.enabled}")
print(f"Token configured: {bool(github_models_service.token)}")
print(f"Available prompts: {github_models_service.get_available_prompts()}")
```

## 📈 Future Enhancements

### Planned Features
- 🔄 **Workflow Automation**: Auto-process uploaded documents
- 📧 **Email Integration**: Process emailed invoices and receipts
- 🔗 **Bank Integration**: Connect with bank APIs for transaction analysis
- 📱 **Mobile Support**: Mobile app for document capture and processing
- 🤖 **Chatbot Interface**: Conversational AI for financial queries
- 📊 **Advanced Visualizations**: Interactive charts and dashboards

### Extensibility
- **Custom Models**: Support for additional AI models
- **Plugin Architecture**: Modular extensions for specific use cases
- **API Webhooks**: Real-time notifications and integrations
- **Multi-language Support**: International document processing

## 📞 Support & Resources

### Documentation
- **API Documentation**: http://localhost:8500/docs
- **GitHub Models**: https://github.com/marketplace/models
- **OpenAI API**: https://platform.openai.com/docs

### Getting Help
1. **Test Integration**: Run `python test_github_models_integration.py`
2. **Check Health**: Call `/github-models/health` endpoint
3. **Review Logs**: Check application logs for detailed error information
4. **Verify Configuration**: Ensure GITHUB_TOKEN is properly set

### Contributing
- Add new prompt templates in `prompts/` directory
- Extend services in `src/vanta_ledger/services/`
- Create new API endpoints in `src/vanta_ledger/routes/`
- Follow security best practices and never commit secrets

---

**🎉 The GitHub Models integration provides enterprise-grade AI capabilities for the Vanta Ledger financial management system, enabling automated document processing, intelligent expense categorization, and strategic financial insights.**





