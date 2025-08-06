#!/usr/bin/env python3
"""
AI Analytics Service for Vanta Ledger
====================================

This service provides intelligent analysis of processed documents using cloud-based LLMs,
generates comprehensive reports, and connects insights across the entire ledger system.
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

# Cloud LLM providers
import openai
from anthropic import Anthropic
import google.generativeai as genai

logger = logging.getLogger(__name__)

class AIAnalyticsService:
    """AI Analytics Service with cloud-based LLM integration"""
    
    def __init__(self):
        """Initialize the AI analytics service"""
        self.openai_client = None
        self.anthropic_client = None
        self.gemini_client = None
        
        # Initialize cloud LLM clients
        self._setup_llm_clients()
        
        # Analytics cache
        self.analytics_cache = {}
        
        logger.info("🚀 AI Analytics Service initialized")

    def _setup_llm_clients(self):
        """Setup cloud-based LLM clients"""
        try:
            # OpenAI (GPT-4)
            if os.getenv("OPENAI_API_KEY"):
                openai.api_key = os.getenv("OPENAI_API_KEY")
                self.openai_client = openai
                logger.info("✅ OpenAI client configured")
            
            # Anthropic (Claude)
            if os.getenv("ANTHROPIC_API_KEY"):
                self.anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
                logger.info("✅ Anthropic client configured")
            
            # Google Gemini
            if os.getenv("GOOGLE_API_KEY"):
                genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                self.gemini_client = genai.GenerativeModel('gemini-pro')
                logger.info("✅ Google Gemini client configured")
                
        except Exception as e:
            logger.error(f"❌ Failed to setup LLM clients: {e}")

    async def analyze_document_intelligence(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze document using cloud-based LLM for intelligent insights"""
        try:
            # Prepare document context
            context = self._prepare_document_context(document_data)
            
            # Generate analysis prompts
            analysis_prompts = self._generate_analysis_prompts(context)
            
            # Get LLM analysis
            llm_insights = await self._get_llm_analysis(analysis_prompts)
            
            # Process and structure insights
            structured_insights = self._structure_llm_insights(llm_insights, document_data)
            
            logger.info(f"✅ Document intelligence analysis completed for {document_data.get('filename', 'Unknown')}")
            return structured_insights
            
        except Exception as e:
            logger.error(f"❌ Document intelligence analysis failed: {e}")
            return {"error": str(e)}

    def _prepare_document_context(self, document_data: Dict[str, Any]) -> str:
        """Prepare document context for LLM analysis"""
        context_parts = []
        
        # Basic document info
        context_parts.append(f"Document: {document_data.get('filename', 'Unknown')}")
        context_parts.append(f"Company: {document_data.get('company', 'Unknown')}")
        context_parts.append(f"Category: {document_data.get('category', 'Unknown')}")
        context_parts.append(f"Document Type: {document_data.get('document_type', 'Unknown')}")
        
        # Extracted text (truncated for LLM)
        text = document_data.get('text', '')[:4000]  # Limit for LLM context
        context_parts.append(f"Document Text: {text}")
        
        # Extracted entities
        entities = document_data.get('entities', {})
        if entities:
            entity_summary = []
            for entity_type, values in entities.items():
                if values:
                    entity_summary.append(f"{entity_type}: {', '.join(str(v) for v in values[:5])}")
            context_parts.append(f"Extracted Entities: {'; '.join(entity_summary)}")
        
        # Financial data
        amounts = entities.get('amounts', [])
        if amounts:
            context_parts.append(f"Financial Amounts: {', '.join(str(amt) for amt in amounts[:10])}")
        
        # Dates
        dates = entities.get('dates', [])
        if dates:
            context_parts.append(f"Important Dates: {', '.join(str(date) for date in dates[:5])}")
        
        return "\n".join(context_parts)

    def _generate_analysis_prompts(self, context: str) -> Dict[str, str]:
        """Generate analysis prompts for different aspects"""
        return {
            "business_insights": f"""
            Analyze this Kenyan business document and provide intelligent business insights:
            
            {context}
            
            Please provide:
            1. Key business insights and implications
            2. Financial analysis and trends
            3. Risk assessment and opportunities
            4. Compliance and regulatory considerations
            5. Strategic recommendations
            
            Focus on Kenyan business context, KSH currency, and local market dynamics.
            """,
            
            "compliance_analysis": f"""
            Analyze this document for compliance and regulatory requirements:
            
            {context}
            
            Please identify:
            1. Tax compliance requirements (KRA, VAT, etc.)
            2. Regulatory obligations
            3. Required documentation
            4. Compliance deadlines
            5. Potential compliance risks
            
            Focus on Kenyan regulatory framework.
            """,
            
            "financial_analysis": f"""
            Perform detailed financial analysis of this document:
            
            {context}
            
            Please analyze:
            1. Financial performance indicators
            2. Cash flow implications
            3. Cost-benefit analysis
            4. Budget impact
            5. Financial risk assessment
            
            Consider KSH currency and Kenyan financial context.
            """,
            
            "strategic_recommendations": f"""
            Provide strategic recommendations based on this document:
            
            {context}
            
            Please provide:
            1. Strategic opportunities
            2. Risk mitigation strategies
            3. Operational improvements
            4. Growth recommendations
            5. Competitive advantages
            
            Focus on Kenyan market opportunities and challenges.
            """
        }

    async def _get_llm_analysis(self, prompts: Dict[str, str]) -> Dict[str, str]:
        """Get analysis from cloud-based LLMs"""
        results = {}
        
        for analysis_type, prompt in prompts.items():
            try:
                # Try different LLM providers
                if self.openai_client:
                    response = await self._call_openai(prompt)
                    results[analysis_type] = response
                elif self.anthropic_client:
                    response = await self._call_anthropic(prompt)
                    results[analysis_type] = response
                elif self.gemini_client:
                    response = await self._call_gemini(prompt)
                    results[analysis_type] = response
                else:
                    results[analysis_type] = "No LLM provider available"
                    
            except Exception as e:
                logger.error(f"❌ LLM analysis failed for {analysis_type}: {e}")
                results[analysis_type] = f"Analysis failed: {str(e)}"
        
        return results

    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI GPT-4"""
        try:
            response = await asyncio.to_thread(
                self.openai_client.ChatCompletion.create,
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Kenyan business analyst expert in financial documents, compliance, and strategic analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI error: {e}")

    async def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic Claude"""
        try:
            response = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Anthropic error: {e}")

    async def _call_gemini(self, prompt: str) -> str:
        """Call Google Gemini"""
        try:
            response = await asyncio.to_thread(
                self.gemini_client.generate_content,
                prompt
            )
            return response.text
        except Exception as e:
            raise Exception(f"Gemini error: {e}")

    def _structure_llm_insights(self, llm_insights: Dict[str, str], document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Structure LLM insights into organized format"""
        return {
            "document_id": document_data.get('document_id'),
            "filename": document_data.get('filename'),
            "company": document_data.get('company'),
            "analysis_timestamp": datetime.now().isoformat(),
            "business_insights": llm_insights.get('business_insights', ''),
            "compliance_analysis": llm_insights.get('compliance_analysis', ''),
            "financial_analysis": llm_insights.get('financial_analysis', ''),
            "strategic_recommendations": llm_insights.get('strategic_recommendations', ''),
            "confidence_score": self._calculate_confidence_score(document_data),
            "risk_level": self._assess_risk_level(document_data),
            "priority_level": self._assess_priority_level(document_data)
        }

    def _calculate_confidence_score(self, document_data: Dict[str, Any]) -> float:
        """Calculate confidence score based on document quality"""
        score = 0.0
        
        # Text quality
        text = document_data.get('text', '')
        if len(text) > 100:
            score += 0.3
        
        # Entity extraction
        entities = document_data.get('entities', {})
        if entities.get('amounts'):
            score += 0.2
        if entities.get('dates'):
            score += 0.2
        if entities.get('companies'):
            score += 0.2
        if entities.get('tax_numbers'):
            score += 0.1
        
        return min(score, 1.0)

    def _assess_risk_level(self, document_data: Dict[str, Any]) -> str:
        """Assess risk level of document"""
        entities = document_data.get('entities', {})
        
        # High risk indicators
        if entities.get('tax_numbers') or entities.get('compliance_issues'):
            return "HIGH"
        
        # Medium risk indicators
        if entities.get('amounts') and any(float(str(amt).replace(',', '')) > 1000000 for amt in entities.get('amounts', [])):
            return "MEDIUM"
        
        return "LOW"

    def _assess_priority_level(self, document_data: Dict[str, Any]) -> str:
        """Assess priority level of document"""
        entities = document_data.get('entities', {})
        
        # High priority indicators
        if entities.get('compliance_issues') or entities.get('deadlines'):
            return "HIGH"
        
        # Medium priority indicators
        if entities.get('amounts') and any(float(str(amt).replace(',', '')) > 500000 for amt in entities.get('amounts', [])):
            return "MEDIUM"
        
        return "LOW"

    async def generate_company_report(self, company_id: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive company report using LLM analysis"""
        try:
            # Prepare company context
            company_context = self._prepare_company_context(documents)
            
            # Generate company analysis prompt
            prompt = f"""
            Analyze this Kenyan company's financial documents and provide a comprehensive business report:
            
            {company_context}
            
            Please provide:
            1. Executive Summary
            2. Financial Performance Analysis
            3. Compliance Status
            4. Risk Assessment
            5. Strategic Recommendations
            6. Market Position Analysis
            7. Operational Insights
            8. Growth Opportunities
            
            Focus on Kenyan business context and provide actionable insights.
            """
            
            # Get LLM analysis
            llm_analysis = await self._get_llm_analysis({"company_report": prompt})
            
            # Structure report
            report = {
                "company_id": company_id,
                "report_date": datetime.now().isoformat(),
                "total_documents": len(documents),
                "analysis": llm_analysis.get('company_report', ''),
                "financial_summary": self._generate_financial_summary(documents),
                "compliance_summary": self._generate_compliance_summary(documents),
                "risk_summary": self._generate_risk_summary(documents),
                "recommendations": self._generate_recommendations(documents)
            }
            
            logger.info(f"✅ Company report generated for company {company_id}")
            return report
            
        except Exception as e:
            logger.error(f"❌ Company report generation failed: {e}")
            return {"error": str(e)}

    def _prepare_company_context(self, documents: List[Dict[str, Any]]) -> str:
        """Prepare company context from multiple documents"""
        context_parts = []
        
        # Company info
        if documents:
            company = documents[0].get('company', 'Unknown')
            context_parts.append(f"Company: {company}")
        
        # Document summary
        context_parts.append(f"Total Documents: {len(documents)}")
        
        # Financial summary
        total_amount = 0
        all_amounts = []
        for doc in documents:
            amounts = doc.get('entities', {}).get('amounts', [])
            all_amounts.extend(amounts)
            for amt in amounts:
                try:
                    total_amount += float(str(amt).replace(',', ''))
                except:
                    pass
        
        context_parts.append(f"Total Financial Value: KSh {total_amount:,.2f}")
        context_parts.append(f"Number of Transactions: {len(all_amounts)}")
        
        # Document types
        doc_types = {}
        for doc in documents:
            doc_type = doc.get('document_type', 'Unknown')
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        context_parts.append(f"Document Types: {', '.join([f'{k} ({v})' for k, v in doc_types.items()])}")
        
        # Key entities
        all_entities = {}
        for doc in documents:
            entities = doc.get('entities', {})
            for entity_type, values in entities.items():
                if entity_type not in all_entities:
                    all_entities[entity_type] = []
                all_entities[entity_type].extend(values)
        
        for entity_type, values in all_entities.items():
            if values:
                context_parts.append(f"{entity_type}: {', '.join(str(v) for v in set(values)[:10])}")
        
        return "\n".join(context_parts)

    def _generate_financial_summary(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate financial summary from documents"""
        total_amount = 0
        amounts = []
        dates = []
        
        for doc in documents:
            doc_amounts = doc.get('entities', {}).get('amounts', [])
            doc_dates = doc.get('entities', {}).get('dates', [])
            
            amounts.extend(doc_amounts)
            dates.extend(doc_dates)
            
            for amt in doc_amounts:
                try:
                    total_amount += float(str(amt).replace(',', ''))
                except:
                    pass
        
        return {
            "total_value": total_amount,
            "transaction_count": len(amounts),
            "average_transaction": total_amount / len(amounts) if amounts else 0,
            "date_range": f"{min(dates)} to {max(dates)}" if dates else "Unknown"
        }

    def _generate_compliance_summary(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate compliance summary from documents"""
        tax_numbers = []
        compliance_issues = []
        
        for doc in documents:
            entities = doc.get('entities', {})
            tax_numbers.extend(entities.get('tax_numbers', []))
            compliance_issues.extend(entities.get('compliance_issues', []))
        
        return {
            "tax_numbers_found": len(set(tax_numbers)),
            "compliance_issues": len(set(compliance_issues)),
            "compliance_status": "COMPLIANT" if not compliance_issues else "NON_COMPLIANT"
        }

    def _generate_risk_summary(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate risk summary from documents"""
        high_risk_docs = 0
        medium_risk_docs = 0
        low_risk_docs = 0
        
        for doc in documents:
            risk_level = self._assess_risk_level(doc)
            if risk_level == "HIGH":
                high_risk_docs += 1
            elif risk_level == "MEDIUM":
                medium_risk_docs += 1
            else:
                low_risk_docs += 1
        
        return {
            "high_risk_documents": high_risk_docs,
            "medium_risk_documents": medium_risk_docs,
            "low_risk_documents": low_risk_docs,
            "overall_risk_level": "HIGH" if high_risk_docs > 0 else "MEDIUM" if medium_risk_docs > 0 else "LOW"
        }

    def _generate_recommendations(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on document analysis"""
        recommendations = []
        
        # Analyze patterns
        total_docs = len(documents)
        high_risk_docs = sum(1 for doc in documents if self._assess_risk_level(doc) == "HIGH")
        
        if high_risk_docs > total_docs * 0.2:
            recommendations.append("Implement enhanced risk monitoring procedures")
        
        if not any(doc.get('entities', {}).get('tax_numbers') for doc in documents):
            recommendations.append("Ensure proper tax documentation and compliance")
        
        if total_docs < 5:
            recommendations.append("Consider expanding document collection for better analysis")
        
        return recommendations

    async def generate_system_analytics(self, all_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate system-wide analytics and insights"""
        try:
            # Prepare system context
            system_context = self._prepare_system_context(all_documents)
            
            # Generate system analysis prompt
            prompt = f"""
            Analyze this comprehensive dataset of Kenyan business documents and provide system-wide insights:
            
            {system_context}
            
            Please provide:
            1. Market Trends and Insights
            2. Industry Analysis
            3. Economic Indicators
            4. Compliance Trends
            5. Risk Patterns
            6. Strategic Opportunities
            7. System Performance Insights
            8. Recommendations for Improvement
            
            Focus on Kenyan business ecosystem and provide actionable insights.
            """
            
            # Get LLM analysis
            llm_analysis = await self._get_llm_analysis({"system_analytics": prompt})
            
            # Structure analytics
            analytics = {
                "report_date": datetime.now().isoformat(),
                "total_documents": len(all_documents),
                "analysis": llm_analysis.get('system_analytics', ''),
                "system_metrics": self._calculate_system_metrics(all_documents),
                "trends": self._identify_trends(all_documents),
                "insights": self._generate_system_insights(all_documents)
            }
            
            logger.info("✅ System analytics generated")
            return analytics
            
        except Exception as e:
            logger.error(f"❌ System analytics generation failed: {e}")
            return {"error": str(e)}

    def _prepare_system_context(self, all_documents: List[Dict[str, Any]]) -> str:
        """Prepare system-wide context"""
        context_parts = []
        
        # Basic stats
        context_parts.append(f"Total Documents: {len(all_documents)}")
        
        # Company distribution
        companies = {}
        for doc in all_documents:
            company = doc.get('company', 'Unknown')
            companies[company] = companies.get(company, 0) + 1
        
        context_parts.append(f"Companies: {len(companies)}")
        context_parts.append(f"Company Distribution: {', '.join([f'{k} ({v})' for k, v in list(companies.items())[:10]])}")
        
        # Document types
        doc_types = {}
        for doc in all_documents:
            doc_type = doc.get('document_type', 'Unknown')
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        context_parts.append(f"Document Types: {', '.join([f'{k} ({v})' for k, v in doc_types.items()])}")
        
        # Financial summary
        total_amount = 0
        for doc in all_documents:
            amounts = doc.get('entities', {}).get('amounts', [])
            for amt in amounts:
                try:
                    total_amount += float(str(amt).replace(',', ''))
                except:
                    pass
        
        context_parts.append(f"Total Financial Value: KSh {total_amount:,.2f}")
        
        return "\n".join(context_parts)

    def _calculate_system_metrics(self, all_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate system-wide metrics"""
        return {
            "total_documents": len(all_documents),
            "total_companies": len(set(doc.get('company') for doc in all_documents)),
            "total_financial_value": sum(
                sum(float(str(amt).replace(',', '')) for amt in doc.get('entities', {}).get('amounts', []))
                for doc in all_documents
            ),
            "average_documents_per_company": len(all_documents) / len(set(doc.get('company') for doc in all_documents)) if all_documents else 0,
            "processing_success_rate": len([doc for doc in all_documents if doc.get('processing_status') == 'success']) / len(all_documents) if all_documents else 0
        }

    def _identify_trends(self, all_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify trends in the data"""
        # This would analyze temporal patterns, financial trends, etc.
        return {
            "financial_trends": "Analysis of financial patterns over time",
            "compliance_trends": "Analysis of compliance patterns",
            "document_type_trends": "Analysis of document type distribution"
        }

    def _generate_system_insights(self, all_documents: List[Dict[str, Any]]) -> List[str]:
        """Generate system-wide insights"""
        insights = []
        
        # Add insights based on data analysis
        total_docs = len(all_documents)
        if total_docs > 1000:
            insights.append("Large-scale document processing system with significant data volume")
        
        companies = set(doc.get('company') for doc in all_documents)
        if len(companies) > 50:
            insights.append("Diverse client base with multiple companies")
        
        return insights

# Global instance
ai_analytics_service = AIAnalyticsService() 