# 🚀 Practical Guide: Maximizing Paperless-ngx with AI

## 🎯 Quick Start Implementation

### Step 1: Test Your Current Setup

```bash
# Test Paperless-ngx connection
cd /home/phantomojo/Vanta-ledger
python test_paperless_connection.py

# Test Ollama integration
python test_ollama_integration.py

# Run basic AI analysis
python simple_integration.py
```

### Step 2: Install AI Dependencies

```bash
# Install AI system
python setup_ai_system.py

# Verify installation
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('✅ AI ready!')"
```

### Step 3: Run Enhanced Analysis

```bash
# Run LLM-enhanced analysis
python llm_enhanced_ai.py

# Monitor with dashboard
python ai_dashboard.py
```

## 🔧 Advanced Configuration

### 1. Paperless-ngx Custom Fields Setup

**Access Paperless-ngx Admin:**
1. Go to `http://localhost:8000/admin/`
2. Login with your credentials
3. Navigate to "Custom fields"

**Create Custom Fields:**
```json
{
  "ai_summary": {
    "type": "text",
    "description": "AI-generated document summary"
  },
  "risk_score": {
    "type": "number",
    "description": "AI risk assessment (0-1)"
  },
  "extracted_amount": {
    "type": "number",
    "description": "Financial amount extracted"
  },
  "project_code": {
    "type": "string",
    "description": "Construction project identifier"
  },
  "vendor_name": {
    "type": "string",
    "description": "Extracted vendor/company name"
  },
  "business_insights": {
    "type": "text",
    "description": "AI business insights"
  },
  "recommendations": {
    "type": "text",
    "description": "AI recommendations"
  }
}
```

### 2. Webhook Configuration

**Create Webhook Endpoint:**
```python
# webhook_handler.py
from flask import Flask, request, jsonify
import asyncio
from llm_enhanced_ai import LLMEnhancedDocumentAI

app = Flask(__name__)
ai_engine = LLMEnhancedDocumentAI(
    paperless_url="http://localhost:8000",
    username="Mike",
    password="[SET_VIA_ENV_VAR]"
)

@app.route('/webhook/paperless', methods=['POST'])
def paperless_webhook():
    data = request.json
    
    if data.get('event') == 'document_created':
        document_id = data.get('document_id')
        # Trigger AI analysis
        asyncio.create_task(process_document(document_id))
    
    return jsonify({'status': 'success'})

async def process_document(document_id):
    # Get document from Paperless
    document = await ai_engine.get_document(document_id)
    
    # Run AI analysis
    analysis = await ai_engine.analyze_document_with_llm(
        document_id, 
        document.get('content', '')
    )
    
    # Update document with AI insights
    await ai_engine.update_document_metadata(document_id, analysis)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

**Configure Paperless-ngx Webhook:**
1. Go to Paperless-ngx admin
2. Navigate to "Webhooks"
3. Create new webhook:
   - URL: `http://your-server:5000/webhook/paperless`
   - Events: `document_created`
   - Enabled: Yes

### 3. Advanced Search Configuration

**Create Search Templates:**
```python
# search_templates.py
SEARCH_TEMPLATES = {
    "high_value_contracts": {
        "query": "document_type:contract AND extracted_amount:>1000000",
        "description": "Contracts over 1M KES"
    },
    "pending_payments": {
        "query": "document_type:invoice AND payment_status:pending",
        "description": "Invoices awaiting payment"
    },
    "risk_documents": {
        "query": "risk_score:>0.7",
        "description": "High-risk documents"
    },
    "project_documents": {
        "query": "project_code:*",
        "description": "All project-related documents"
    },
    "recent_activity": {
        "query": "created:>30d",
        "description": "Documents from last 30 days"
    }
}
```

## 📊 Business Intelligence Dashboard

### 1. Real-time Dashboard Setup

```python
# business_dashboard.py
import asyncio
import json
from datetime import datetime, timedelta
from llm_enhanced_ai import LLMEnhancedDocumentAI

class BusinessDashboard:
    def __init__(self):
        self.ai_engine = LLMEnhancedDocumentAI(
            paperless_url="http://localhost:8000",
            username="Mike",
            password="[SET_VIA_ENV_VAR]"
        )
    
    async def get_financial_summary(self):
        """Get comprehensive financial summary"""
        documents = await self.ai_engine.get_all_documents()
        
        total_value = 0
        invoice_count = 0
        contract_count = 0
        pending_amount = 0
        
        for doc in documents:
            analysis = doc.get('ai_analysis', {})
            amount = analysis.get('extracted_amount', 0)
            
            if doc.get('document_type') == 'invoice':
                invoice_count += 1
                total_value += amount
                
                # Check if payment is pending
                if analysis.get('payment_status') == 'pending':
                    pending_amount += amount
                    
            elif doc.get('document_type') == 'contract':
                contract_count += 1
                total_value += amount
        
        return {
            'total_value': total_value,
            'invoice_count': invoice_count,
            'contract_count': contract_count,
            'pending_amount': pending_amount,
            'payment_efficiency': ((total_value - pending_amount) / total_value * 100) if total_value > 0 else 0
        }
    
    async def get_vendor_analysis(self):
        """Analyze vendor relationships"""
        documents = await self.ai_engine.get_all_documents()
        
        vendors = {}
        for doc in documents:
            vendor = doc.get('correspondent_name', 'Unknown')
            if vendor not in vendors:
                vendors[vendor] = {
                    'document_count': 0,
                    'total_value': 0,
                    'avg_payment_time': 0,
                    'risk_score': 0
                }
            
            vendors[vendor]['document_count'] += 1
            vendors[vendor]['total_value'] += doc.get('ai_analysis', {}).get('extracted_amount', 0)
            vendors[vendor]['risk_score'] = max(
                vendors[vendor]['risk_score'],
                doc.get('ai_analysis', {}).get('risk_score', 0)
            )
        
        # Sort by total value
        sorted_vendors = sorted(vendors.items(), key=lambda x: x[1]['total_value'], reverse=True)
        
        return {
            'top_vendors': sorted_vendors[:5],
            'total_vendors': len(vendors),
            'vendor_insights': self._generate_vendor_insights(vendors)
        }
    
    async def get_project_tracking(self):
        """Track construction projects"""
        documents = await self.ai_engine.get_all_documents()
        
        projects = {}
        for doc in documents:
            project_code = doc.get('ai_analysis', {}).get('project_code')
            if project_code:
                if project_code not in projects:
                    projects[project_code] = {
                        'total_value': 0,
                        'document_count': 0,
                        'start_date': None,
                        'last_activity': None,
                        'completion_status': 'active'
                    }
                
                projects[project_code]['total_value'] += doc.get('ai_analysis', {}).get('extracted_amount', 0)
                projects[project_code]['document_count'] += 1
                
                # Update dates
                doc_date = doc.get('created')
                if doc_date:
                    if not projects[project_code]['start_date'] or doc_date < projects[project_code]['start_date']:
                        projects[project_code]['start_date'] = doc_date
                    if not projects[project_code]['last_activity'] or doc_date > projects[project_code]['last_activity']:
                        projects[project_code]['last_activity'] = doc_date
        
        return {
            'active_projects': len(projects),
            'total_project_value': sum(p['total_value'] for p in projects.values()),
            'project_details': projects
        }
    
    def _generate_vendor_insights(self, vendors):
        """Generate insights about vendor relationships"""
        insights = []
        
        # Find most valuable vendor
        top_vendor = max(vendors.items(), key=lambda x: x[1]['total_value'])
        insights.append(f"Top vendor: {top_vendor[0]} (KES {top_vendor[1]['total_value']:,.2f})")
        
        # Find vendors with high risk
        high_risk_vendors = [v for v in vendors.items() if v[1]['risk_score'] > 0.7]
        if high_risk_vendors:
            insights.append(f"High-risk vendors: {len(high_risk_vendors)}")
        
        # Find vendors with many documents
        frequent_vendors = [v for v in vendors.items() if v[1]['document_count'] > 5]
        insights.append(f"Frequent vendors: {len(frequent_vendors)}")
        
        return insights

# Usage
async def main():
    dashboard = BusinessDashboard()
    
    print("📊 Business Intelligence Dashboard")
    print("=" * 50)
    
    # Financial Summary
    financial = await dashboard.get_financial_summary()
    print(f"\n💰 Financial Summary:")
    print(f"   Total Value: KES {financial['total_value']:,.2f}")
    print(f"   Invoices: {financial['invoice_count']}")
    print(f"   Contracts: {financial['contract_count']}")
    print(f"   Pending Payments: KES {financial['pending_amount']:,.2f}")
    print(f"   Payment Efficiency: {financial['payment_efficiency']:.1f}%")
    
    # Vendor Analysis
    vendors = await dashboard.get_vendor_analysis()
    print(f"\n🏢 Vendor Analysis:")
    print(f"   Total Vendors: {vendors['total_vendors']}")
    print(f"   Top Vendors:")
    for vendor, data in vendors['top_vendors'][:3]:
        print(f"     • {vendor}: KES {data['total_value']:,.2f} ({data['document_count']} docs)")
    
    # Project Tracking
    projects = await dashboard.get_project_tracking()
    print(f"\n🏗️ Project Tracking:")
    print(f"   Active Projects: {projects['active_projects']}")
    print(f"   Total Project Value: KES {projects['total_project_value']:,.2f}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Automated Reporting

```python
# automated_reports.py
import asyncio
from datetime import datetime, timedelta
import json
from business_dashboard import BusinessDashboard

class AutomatedReports:
    def __init__(self):
        self.dashboard = BusinessDashboard()
    
    async def generate_daily_report(self):
        """Generate daily business report"""
        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().isoformat(),
            'financial_summary': await self.dashboard.get_financial_summary(),
            'vendor_analysis': await self.dashboard.get_vendor_analysis(),
            'project_tracking': await self.dashboard.get_project_tracking(),
            'alerts': await self._generate_alerts()
        }
        
        # Save report
        filename = f"reports/daily_report_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return report
    
    async def generate_weekly_report(self):
        """Generate weekly summary report"""
        # Aggregate daily reports for the week
        week_start = datetime.now() - timedelta(days=7)
        
        weekly_data = {
            'period': f"{week_start.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}",
            'total_documents_processed': 0,
            'total_value_processed': 0,
            'new_vendors': [],
            'completed_projects': [],
            'risk_alerts': []
        }
        
        # Process daily reports
        for i in range(7):
            date = datetime.now() - timedelta(days=i)
            filename = f"reports/daily_report_{date.strftime('%Y%m%d')}.json"
            
            try:
                with open(filename, 'r') as f:
                    daily_report = json.load(f)
                    weekly_data['total_documents_processed'] += daily_report.get('document_count', 0)
                    weekly_data['total_value_processed'] += daily_report.get('financial_summary', {}).get('total_value', 0)
            except FileNotFoundError:
                continue
        
        # Save weekly report
        filename = f"reports/weekly_report_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'w') as f:
            json.dump(weekly_data, f, indent=2, default=str)
        
        return weekly_data
    
    async def _generate_alerts(self):
        """Generate business alerts"""
        alerts = []
        
        financial = await self.dashboard.get_financial_summary()
        
        # Payment alerts
        if financial['pending_amount'] > financial['total_value'] * 0.3:
            alerts.append({
                'type': 'warning',
                'message': f"High pending payments: KES {financial['pending_amount']:,.2f}",
                'priority': 'high'
            })
        
        # Vendor alerts
        vendors = await self.dashboard.get_vendor_analysis()
        high_risk_vendors = [v for v in vendors['top_vendors'] if v[1]['risk_score'] > 0.7]
        if high_risk_vendors:
            alerts.append({
                'type': 'risk',
                'message': f"High-risk vendors detected: {len(high_risk_vendors)}",
                'priority': 'medium'
            })
        
        return alerts

# Schedule automated reports
async def schedule_reports():
    reports = AutomatedReports()
    
    while True:
        now = datetime.now()
        
        # Daily report at 9 AM
        if now.hour == 9 and now.minute == 0:
            await reports.generate_daily_report()
            print("📊 Daily report generated")
        
        # Weekly report on Monday at 10 AM
        if now.weekday() == 0 and now.hour == 10 and now.minute == 0:
            await reports.generate_weekly_report()
            print("📊 Weekly report generated")
        
        await asyncio.sleep(60)  # Check every minute

if __name__ == "__main__":
    asyncio.run(schedule_reports())
```

## 🔍 Advanced Search & Filtering

### 1. Semantic Search Implementation

```python
# semantic_search.py
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import asyncio
from llm_enhanced_ai import LLMEnhancedDocumentAI

class SemanticSearch:
    def __init__(self):
        self.ai_engine = LLMEnhancedDocumentAI(
            paperless_url="http://localhost:8000",
            username="Mike",
            password="[SET_VIA_ENV_VAR]"
        )
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.document_vectors = None
        self.documents = []
    
    async def build_search_index(self):
        """Build search index from all documents"""
        documents = await self.ai_engine.get_all_documents()
        
        # Prepare document texts
        texts = []
        for doc in documents:
            # Combine title, content, and AI insights
            text = f"{doc.get('title', '')} {doc.get('content', '')}"
            
            # Add AI insights
            ai_analysis = doc.get('ai_analysis', {})
            if ai_analysis:
                text += f" {ai_analysis.get('summary', '')}"
                text += f" {' '.join(ai_analysis.get('key_points', []))}"
            
            texts.append(text)
            self.documents.append(doc)
        
        # Create TF-IDF vectors
        self.document_vectors = self.vectorizer.fit_transform(texts)
        print(f"✅ Search index built with {len(documents)} documents")
    
    def search(self, query, top_k=10):
        """Search documents semantically"""
        if self.document_vectors is None:
            raise ValueError("Search index not built. Run build_search_index() first.")
        
        # Vectorize query
        query_vector = self.vectorizer.transform([query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_vector, self.document_vectors).flatten()
        
        # Get top results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Minimum similarity threshold
                results.append({
                    'document': self.documents[idx],
                    'similarity': similarities[idx],
                    'score': similarities[idx]
                })
        
        return results
    
    def search_by_financial_criteria(self, min_amount=None, max_amount=None, doc_type=None):
        """Search by financial criteria"""
        results = []
        
        for doc in self.documents:
            ai_analysis = doc.get('ai_analysis', {})
            amount = ai_analysis.get('extracted_amount', 0)
            
            # Apply filters
            if min_amount and amount < min_amount:
                continue
            if max_amount and amount > max_amount:
                continue
            if doc_type and doc.get('document_type') != doc_type:
                continue
            
            results.append({
                'document': doc,
                'amount': amount,
                'relevance': 1.0
            })
        
        # Sort by amount
        results.sort(key=lambda x: x['amount'], reverse=True)
        return results

# Usage
async def main():
    search = SemanticSearch()
    
    # Build search index
    await search.build_search_index()
    
    # Example searches
    print("\n🔍 Semantic Search Examples:")
    
    # Search for road construction projects
    results = search.search("road construction project")
    print(f"\nRoad construction projects: {len(results)} results")
    for result in results[:3]:
        doc = result['document']
        print(f"  • {doc.get('title', 'Untitled')} (Score: {result['similarity']:.2f})")
    
    # Search for high-value contracts
    results = search.search_by_financial_criteria(min_amount=1000000, doc_type='contract')
    print(f"\nHigh-value contracts: {len(results)} results")
    for result in results[:3]:
        doc = result['document']
        print(f"  • {doc.get('title', 'Untitled')} (KES {result['amount']:,.2f})")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🚀 Performance Optimization

### 1. Batch Processing Optimization

```python
# optimized_processing.py
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from llm_enhanced_ai import LLMEnhancedDocumentAI

class OptimizedProcessor:
    def __init__(self, max_workers=4):
        self.ai_engine = LLMEnhancedDocumentAI(
            paperless_url="http://localhost:8000",
            username="Mike",
            password="[SET_VIA_ENV_VAR]"
        )
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def process_documents_batch(self, documents, batch_size=5):
        """Process documents in optimized batches"""
        results = []
        
        # Process in batches
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            print(f"Processing batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}")
            
            # Process batch concurrently
            batch_results = await asyncio.gather(
                *[self._process_single_document(doc) for doc in batch],
                return_exceptions=True
            )
            
            results.extend(batch_results)
            
            # Small delay between batches to prevent overwhelming the system
            await asyncio.sleep(1)
        
        return results
    
    async def _process_single_document(self, document):
        """Process a single document with error handling"""
        try:
            analysis = await self.ai_engine.analyze_document_with_llm(
                document['id'],
                document.get('content', '')
            )
            
            # Update document in Paperless
            await self._update_document_metadata(document['id'], analysis)
            
            return {
                'document_id': document['id'],
                'status': 'success',
                'analysis': analysis
            }
            
        except Exception as e:
            return {
                'document_id': document['id'],
                'status': 'error',
                'error': str(e)
            }
    
    async def _update_document_metadata(self, document_id, analysis):
        """Update document metadata in Paperless"""
        # This would update the custom fields in Paperless
        pass

# Usage
async def main():
    processor = OptimizedProcessor(max_workers=4)
    
    # Get all documents
    documents = await processor.ai_engine.get_all_documents()
    
    print(f"🚀 Processing {len(documents)} documents with optimization...")
    
    # Process with optimization
    results = await processor.process_documents_batch(documents, batch_size=5)
    
    # Summary
    successful = len([r for r in results if r['status'] == 'success'])
    failed = len([r for r in results if r['status'] == 'error'])
    
    print(f"\n✅ Processing complete!")
    print(f"   Successful: {successful}")
    print(f"   Failed: {failed}")
    print(f"   Success rate: {successful/len(results)*100:.1f}%")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📱 Mobile Integration

### 1. API Endpoints for Mobile

```python
# mobile_api.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import asyncio
from business_dashboard import BusinessDashboard
from semantic_search import SemanticSearch

app = Flask(__name__)
CORS(app)  # Enable CORS for mobile app

dashboard = BusinessDashboard()
search = SemanticSearch()

@app.route('/api/dashboard/summary', methods=['GET'])
async def get_dashboard_summary():
    """Get dashboard summary for mobile"""
    try:
        financial = await dashboard.get_financial_summary()
        vendors = await dashboard.get_vendor_analysis()
        projects = await dashboard.get_project_tracking()
        
        return jsonify({
            'financial': financial,
            'vendors': vendors,
            'projects': projects,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['POST'])
async def search_documents():
    """Search documents from mobile"""
    try:
        data = request.json
        query = data.get('query', '')
        filters = data.get('filters', {})
        
        if query:
            results = search.search(query, top_k=20)
        else:
            results = search.search_by_financial_criteria(**filters)
        
        return jsonify({
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/documents/<int:doc_id>', methods=['GET'])
async def get_document_details(doc_id):
    """Get detailed document information"""
    try:
        # Get document from Paperless
        document = await dashboard.ai_engine.get_document(doc_id)
        
        return jsonify({
            'document': document,
            'ai_analysis': document.get('ai_analysis', {})
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
```

## 🎯 Next Steps Checklist

### ✅ Immediate Actions (Today)
- [ ] Test Ollama integration: `python test_ollama_integration.py`
- [ ] Run basic analysis: `python simple_integration.py`
- [ ] Install AI dependencies: `python setup_ai_system.py`

### ✅ This Week
- [ ] Run LLM-enhanced analysis: `python llm_enhanced_ai.py`
- [ ] Setup custom fields in Paperless-ngx
- [ ] Create business dashboard: `python business_dashboard.py`
- [ ] Test semantic search: `python semantic_search.py`

### ✅ Next Week
- [ ] Implement webhooks for real-time processing
- [ ] Setup automated reporting
- [ ] Optimize performance with batch processing
- [ ] Create mobile API endpoints

### ✅ Next Month
- [ ] Implement predictive analytics
- [ ] Add advanced workflows
- [ ] Integrate with external systems
- [ ] Deploy production monitoring

---

**🎉 You now have a complete roadmap to maximize Paperless-ngx with advanced AI capabilities!**

**Key Benefits:**
- **Automated Processing**: 100% of your 60GB archive analyzed
- **Intelligent Insights**: Business context and recommendations
- **Real-time Monitoring**: Live dashboards and alerts
- **Mobile Access**: Access insights anywhere
- **Scalable Architecture**: Handles growing document volumes

**Ready to revolutionize your document management! 🚀** 