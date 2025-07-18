#!/usr/bin/env python3
"""
LLM-Enhanced Document AI System for Vanta Ledger
================================================

Enhanced AI system using Ollama and Llama2 for advanced document understanding,
summarization, and intelligent analysis.
"""

import asyncio
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import re
from decimal import Decimal

# Import the base AI system
from advanced_document_ai import DocumentAIEngine, FinancialData, DocumentAnalysis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LLMAnalysis:
    """LLM-enhanced analysis results"""
    summary: str
    key_points: List[str]
    business_insights: List[str]
    recommendations: List[str]
    risk_assessment: str
    confidence: float

class OllamaLLMClient:
    """Client for Ollama LLM integration"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.session = requests.Session()
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except Exception as e:
            logger.error(f"Error getting models: {e}")
            return []
    
    def generate_response(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate response using Ollama"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "max_tokens": max_tokens
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', '')
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return ""
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return ""

class LLMEnhancedDocumentAI(DocumentAIEngine):
    """Enhanced document AI with LLM capabilities"""
    
    def __init__(self, paperless_url: str, username: str, password: str, 
                 ollama_url: str = "http://localhost:11434", model: str = "llama2"):
        super().__init__(paperless_url, username, password)
        self.llm_client = OllamaLLMClient(ollama_url, model)
        self.llm_available = self.llm_client.is_available()
        
        if self.llm_available:
            logger.info(f"✅ LLM integration available with model: {model}")
            available_models = self.llm_client.get_available_models()
            logger.info(f"Available models: {available_models}")
        else:
            logger.warning("⚠️ LLM integration not available - running in basic mode")
    
    def create_document_prompt(self, text: str, doc_type: str, financial_data: List[FinancialData]) -> str:
        """Create a prompt for LLM analysis"""
        
        # Format financial data
        financial_summary = ""
        if financial_data:
            amounts = [f"KES {fd.amount:,.2f}" for fd in financial_data if fd.amount]
            dates = [fd.date.strftime("%Y-%m-%d") for fd in financial_data if fd.date]
            invoices = [fd.invoice_number for fd in financial_data if fd.invoice_number]
            
            financial_summary = f"""
Financial Data Found:
- Amounts: {', '.join(amounts) if amounts else 'None'}
- Dates: {', '.join(dates) if dates else 'None'}
- Invoice Numbers: {', '.join(invoices) if invoices else 'None'}
"""
        
        prompt = f"""You are an expert business analyst specializing in construction and tender documents. 
Analyze the following document and provide insights.

Document Type: {doc_type}
{financial_summary}

Document Content:
{text[:2000]}...

Please provide:
1. A concise summary (2-3 sentences)
2. Key business points (bullet points)
3. Business insights and implications
4. Recommendations for action
5. Risk assessment (low/medium/high with reasoning)

Format your response as JSON:
{{
    "summary": "brief summary",
    "key_points": ["point1", "point2"],
    "business_insights": ["insight1", "insight2"],
    "recommendations": ["rec1", "rec2"],
    "risk_assessment": "risk level with explanation",
    "confidence": 0.85
}}"""
        
        return prompt
    
    def parse_llm_response(self, response: str) -> Optional[LLMAnalysis]:
        """Parse LLM response into structured data"""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return LLMAnalysis(
                    summary=data.get('summary', ''),
                    key_points=data.get('key_points', []),
                    business_insights=data.get('business_insights', []),
                    recommendations=data.get('recommendations', []),
                    risk_assessment=data.get('risk_assessment', ''),
                    confidence=data.get('confidence', 0.0)
                )
            else:
                # Fallback parsing for non-JSON responses
                return LLMAnalysis(
                    summary=response[:200] + "..." if len(response) > 200 else response,
                    key_points=[],
                    business_insights=[],
                    recommendations=[],
                    risk_assessment="Unable to parse",
                    confidence=0.5
                )
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return None
    
    async def analyze_document_with_llm(self, document_id: int, text: str, 
                                      existing_documents: List[Dict] = None) -> DocumentAnalysis:
        """Analyze document with LLM enhancement"""
        
        # Get base analysis
        base_analysis = await self.analyze_document(document_id, text, existing_documents)
        
        # Add LLM analysis if available
        if self.llm_available and text.strip():
            logger.info(f"🤖 Running LLM analysis for document {document_id}")
            
            try:
                # Create prompt
                prompt = self.create_document_prompt(
                    text, 
                    base_analysis.document_type, 
                    base_analysis.financial_data
                )
                
                # Get LLM response
                llm_response = self.llm_client.generate_response(prompt)
                
                if llm_response:
                    # Parse response
                    llm_analysis = self.parse_llm_response(llm_response)
                    
                    if llm_analysis:
                        # Enhance base analysis with LLM insights
                        base_analysis.business_insights.update({
                            'llm_summary': llm_analysis.summary,
                            'llm_key_points': llm_analysis.key_points,
                            'llm_business_insights': llm_analysis.business_insights,
                            'llm_recommendations': llm_analysis.recommendations,
                            'llm_risk_assessment': llm_analysis.risk_assessment,
                            'llm_confidence': llm_analysis.confidence
                        })
                        
                        # Add LLM insights to tags
                        if llm_analysis.key_points:
                            base_analysis.tags.extend([f"llm_insight:{point[:20]}" for point in llm_analysis.key_points[:3]])
                        
                        logger.info(f"✅ LLM analysis completed for document {document_id}")
                    else:
                        logger.warning(f"⚠️ Failed to parse LLM response for document {document_id}")
                else:
                    logger.warning(f"⚠️ No LLM response for document {document_id}")
                    
            except Exception as e:
                logger.error(f"❌ LLM analysis error for document {document_id}: {e}")
        
        return base_analysis
    
    def generate_business_report(self, analyses: List[DocumentAnalysis]) -> Dict[str, Any]:
        """Generate comprehensive business report with LLM insights"""
        
        # Get base insights
        base_insights = self.generate_business_insights(analyses)
        
        # Add LLM-enhanced insights
        llm_insights = {
            'document_summaries': [],
            'key_trends': [],
            'risk_analysis': [],
            'recommendations': []
        }
        
        # Collect LLM insights from all documents
        for analysis in analyses:
            llm_data = analysis.business_insights
            
            if 'llm_summary' in llm_data:
                llm_insights['document_summaries'].append({
                    'document_id': analysis.document_id,
                    'summary': llm_data['llm_summary'],
                    'confidence': llm_data.get('llm_confidence', 0.0)
                })
            
            if 'llm_business_insights' in llm_data:
                llm_insights['key_trends'].extend(llm_data['llm_business_insights'])
            
            if 'llm_risk_assessment' in llm_data:
                llm_insights['risk_analysis'].append({
                    'document_id': analysis.document_id,
                    'assessment': llm_data['llm_risk_assessment']
                })
            
            if 'llm_recommendations' in llm_data:
                llm_insights['recommendations'].extend(llm_data['llm_recommendations'])
        
        # Generate executive summary using LLM
        if self.llm_available:
            executive_summary = self._generate_executive_summary(analyses, llm_insights)
            llm_insights['executive_summary'] = executive_summary
        
        # Combine insights
        enhanced_insights = {**base_insights, 'llm_enhanced': llm_insights}
        
        return enhanced_insights
    
    def _generate_executive_summary(self, analyses: List[DocumentAnalysis], 
                                  llm_insights: Dict) -> str:
        """Generate executive summary using LLM"""
        
        # Prepare summary data
        total_docs = len(analyses)
        total_value = sum(
            float(fd.amount) 
            for analysis in analyses 
            for fd in analysis.financial_data 
            if fd.amount
        )
        
        doc_types = {}
        for analysis in analyses:
            doc_type = analysis.document_type
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        # Create prompt for executive summary
        prompt = f"""As a business analyst, provide an executive summary for a construction company's document analysis.

Document Analysis Summary:
- Total Documents: {total_docs}
- Total Financial Value: KES {total_value:,.2f}
- Document Types: {dict(doc_types)}

Key Business Insights:
{chr(10).join(llm_insights.get('key_trends', [])[:5])}

Risk Assessments:
{chr(10).join([f"- {risk['assessment']}" for risk in llm_insights.get('risk_analysis', [])[:3]])}

Provide a concise executive summary (3-4 sentences) highlighting the most important findings and recommendations for the business leadership."""

        response = self.llm_client.generate_response(prompt, max_tokens=300)
        return response if response else "Executive summary generation failed."
    
    async def analyze_all_documents_with_llm(self) -> Dict[str, Any]:
        """Analyze all documents with LLM enhancement"""
        
        if not await self.authenticate():
            return {"error": "Authentication failed"}
        
        headers = {'Authorization': f'Token {self.token}'}
        
        # Get all documents
        documents = []
        page = 1
        
        while True:
            try:
                response = requests.get(
                    f"{self.paperless_url}/api/documents/",
                    headers=headers,
                    params={'page': page}
                )
                
                if response.status_code != 200:
                    break
                
                data = response.json()
                if not data.get('results'):
                    break
                
                documents.extend(data['results'])
                page += 1
                
            except Exception as e:
                logger.error(f"Error fetching documents: {e}")
                break
        
        logger.info(f"📄 Found {len(documents)} documents to analyze with LLM")
        
        # Analyze each document with LLM
        analyses = []
        existing_docs = []
        
        for i, doc in enumerate(documents, 1):
            try:
                logger.info(f"🔍 Analyzing document {i}/{len(documents)} (ID: {doc['id']})")
                
                # Get document content
                content_response = requests.get(
                    f"{self.paperless_url}/api/documents/{doc['id']}/",
                    headers=headers
                )
                
                if content_response.status_code == 200:
                    doc_data = content_response.json()
                    text = doc_data.get('content', '')
                    
                    # Analyze document with LLM
                    analysis = await self.analyze_document_with_llm(
                        doc['id'], 
                        text, 
                        existing_docs
                    )
                    analyses.append(analysis)
                    existing_docs.append(doc)
                
            except Exception as e:
                logger.error(f"Error analyzing document {doc['id']}: {e}")
        
        # Generate enhanced business insights
        insights = self.generate_business_report(analyses)
        
        return {
            'total_documents': len(analyses),
            'analyses': analyses,
            'insights': insights,
            'llm_available': self.llm_available
        }

async def main():
    """Main function to run the LLM-enhanced AI system"""
    print("🚀 LLM-Enhanced Document AI System")
    print("=" * 50)
    
    # Initialize enhanced AI engine
    ai_engine = LLMEnhancedDocumentAI(
        paperless_url="http://localhost:8000",
        username="Mike",
        password="106730!@#",
        ollama_url="http://localhost:11434",
        model="llama2"
    )
    
    # Check LLM availability
    if ai_engine.llm_available:
        print("✅ LLM integration available")
        models = ai_engine.llm_client.get_available_models()
        print(f"Available models: {models}")
    else:
        print("⚠️ LLM not available - running in basic mode")
    
    # Run enhanced analysis
    results = await ai_engine.analyze_all_documents_with_llm()
    
    if 'error' in results:
        print(f"❌ Error: {results['error']}")
        return
    
    # Display results
    print(f"\n📊 LLM-Enhanced Analysis Complete!")
    print(f"Total Documents Analyzed: {results['total_documents']}")
    print(f"LLM Available: {results['llm_available']}")
    
    # Show LLM insights
    if results['llm_available']:
        llm_insights = results['insights'].get('llm_enhanced', {})
        
        if 'executive_summary' in llm_insights:
            print(f"\n📋 Executive Summary:")
            print(llm_insights['executive_summary'])
        
        if 'key_trends' in llm_insights:
            print(f"\n🔍 Key Business Trends:")
            for trend in llm_insights['key_trends'][:5]:
                print(f"   • {trend}")
        
        if 'recommendations' in llm_insights:
            print(f"\n💡 Recommendations:")
            for rec in llm_insights['recommendations'][:5]:
                print(f"   • {rec}")
    
    # Show document summaries
    analyses = results['analyses']
    if analyses:
        print(f"\n📄 Sample Document Summaries:")
        for analysis in analyses[:3]:
            llm_data = analysis.business_insights
            if 'llm_summary' in llm_data:
                print(f"\nDocument {analysis.document_id} ({analysis.document_type}):")
                print(f"   {llm_data['llm_summary']}")
    
    print(f"\n🎉 LLM-enhanced analysis complete!")
    print("Check 'document_ai.log' for detailed logs.")

if __name__ == "__main__":
    asyncio.run(main()) 