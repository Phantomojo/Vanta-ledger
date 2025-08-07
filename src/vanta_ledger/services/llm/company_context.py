#!/usr/bin/env python3
"""
Company Context Manager for Multi-Company LLM Processing
Manages company-specific context and configurations for document processing
"""

import logging
from typing import Dict, List, Any, Optional
from uuid import UUID
from datetime import datetime

from pymongo.database import Database

logger = logging.getLogger(__name__)

class CompanyContextManager:
    """Manage company-specific context and configurations"""
    
    def __init__(self, db: Database):
        self.db = db
        self.company_configs = {}
        self.company_embeddings = {}
        
    async def get_company_context(self, company_id: UUID) -> Dict[str, Any]:
        """Get company-specific context for LLM processing"""
        try:
            # Get company configuration
            company_config = self.db.companies.find_one({"_id": str(company_id)})
            if not company_config:
                logger.warning(f"Company not found: {company_id}")
                return self._get_default_context()
            
            # Get company-specific data
            context = {
                "company_id": str(company_id),
                "company_name": company_config.get("name", "Unknown Company"),
                "industry": company_config.get("industry", "General"),
                "document_types": company_config.get("document_types", []),
                "financial_accounts": await self._get_company_accounts(company_id),
                "customers": await self._get_company_customers(company_id),
                "vendors": await self._get_company_vendors(company_id),
                "processing_rules": company_config.get("processing_rules", {}),
                "language": company_config.get("language", "en"),
                "currency": company_config.get("currency", "KES"),
                "tax_rate": company_config.get("tax_rate", 16.0),
                "business_type": company_config.get("business_type", "general"),
                "country": company_config.get("country", "Kenya"),
                "timezone": company_config.get("timezone", "Africa/Nairobi")
            }
            
            # Cache company context
            self.company_configs[str(company_id)] = context
            
            logger.debug(f"Loaded context for company: {context['company_name']}")
            return context
            
        except Exception as e:
            logger.error(f"Error getting company context: {str(e)}")
            return self._get_default_context()
    
    async def _get_company_accounts(self, company_id: UUID) -> List[Dict]:
        """Get company's chart of accounts"""
        try:
            accounts = self.db.chart_of_accounts.find({"company_id": str(company_id)})
            account_list = []
            for acc in accounts:
                account_list.append({
                    "code": acc["account_code"],
                    "name": acc["account_name"],
                    "type": acc.get("account_type", "unknown"),
                    "parent_id": acc.get("parent_account_id")
                })
            return account_list
        except Exception as e:
            logger.error(f"Error getting company accounts: {str(e)}")
            return []
    
    async def _get_company_customers(self, company_id: UUID) -> List[Dict]:
        """Get company's customers"""
        try:
            customers = self.db.customers.find({"company_id": str(company_id)})
            customer_list = []
            for cust in customers:
                customer_list.append({
                    "code": cust["customer_code"],
                    "name": cust["customer_name"],
                    "email": cust.get("email"),
                    "phone": cust.get("phone"),
                    "tax_id": cust.get("tax_id"),
                    "credit_limit": cust.get("credit_limit", 0)
                })
            return customer_list
        except Exception as e:
            logger.error(f"Error getting company customers: {str(e)}")
            return []
    
    async def _get_company_vendors(self, company_id: UUID) -> List[Dict]:
        """Get company's vendors"""
        try:
            vendors = self.db.vendors.find({"company_id": str(company_id)})
            vendor_list = []
            for vend in vendors:
                vendor_list.append({
                    "code": vend["vendor_code"],
                    "name": vend["vendor_name"],
                    "email": vend.get("email"),
                    "phone": vend.get("phone"),
                    "tax_id": vend.get("tax_id"),
                    "payment_terms": vend.get("payment_terms")
                })
            return vendor_list
        except Exception as e:
            logger.error(f"Error getting company vendors: {str(e)}")
            return []
    
    def _get_default_context(self) -> Dict[str, Any]:
        """Get default context for unknown companies"""
        return {
            "company_id": "default",
            "company_name": "Default Company",
            "industry": "General",
            "document_types": ["invoice", "receipt", "contract", "financial_statement"],
            "financial_accounts": [],
            "customers": [],
            "vendors": [],
            "processing_rules": {},
            "language": "en",
            "currency": "KES",
            "tax_rate": 16.0,
            "business_type": "general",
            "country": "Kenya",
            "timezone": "Africa/Nairobi"
        }
    
    def build_company_prompt_context(self, company_context: Dict) -> str:
        """Build company-specific context for LLM prompts"""
        context_parts = [
            f"Company: {company_context['company_name']}",
            f"Industry: {company_context['industry']}",
            f"Country: {company_context['country']}",
            f"Currency: {company_context['currency']}",
            f"Language: {company_context['language']}",
            f"Tax Rate: {company_context['tax_rate']}%"
        ]
        
        # Add key customers
        if company_context.get("customers"):
            customer_list = ", ".join([f"{c['code']}: {c['name']}" for c in company_context["customers"][:5]])
            context_parts.append(f"Key Customers: {customer_list}")
        
        # Add key vendors
        if company_context.get("vendors"):
            vendor_list = ", ".join([f"{v['code']}: {v['name']}" for v in company_context["vendors"][:5]])
            context_parts.append(f"Key Vendors: {vendor_list}")
        
        # Add key accounts
        if company_context.get("financial_accounts"):
            account_list = ", ".join([f"{a['code']}: {a['name']}" for a in company_context["financial_accounts"][:10]])
            context_parts.append(f"Key Accounts: {account_list}")
        
        return " | ".join(context_parts)
    
    def get_company_specific_instructions(self, company_context: Dict, task_type: str) -> str:
        """Get company-specific instructions for different tasks"""
        base_instructions = {
            "document_classification": f"""
            You are processing documents for {company_context['company_name']}, a {company_context['industry']} company in {company_context['country']}.
            Focus on document types relevant to this industry and business type.
            """,
            
            "entity_extraction": f"""
            Extract entities specific to {company_context['company_name']}.
            Pay special attention to:
            - Company names (especially {company_context['company_name']} and related companies)
            - Amounts in {company_context['currency']}
            - Account codes from the company's chart of accounts
            - Customer/vendor names from the company's database
            """,
            
            "financial_extraction": f"""
            Extract financial data for {company_context['company_name']}.
            Consider:
            - Currency: {company_context['currency']}
            - Tax rate: {company_context['tax_rate']}%
            - Company's chart of accounts
            - Customer/vendor relationships
            """,
            
            "summary_generation": f"""
            Generate summaries relevant to {company_context['company_name']}.
            Focus on information that would be important for this {company_context['industry']} business.
            Consider the company's specific business context and requirements.
            """
        }
        
        return base_instructions.get(task_type, "")
    
    def validate_entity_against_context(self, entity: str, entity_type: str, company_context: Dict) -> Dict[str, Any]:
        """Validate extracted entity against company context"""
        validation_result = {
            "entity": entity,
            "type": entity_type,
            "is_valid": False,
            "confidence": 0.0,
            "suggestions": []
        }
        
        try:
            if entity_type == "customer":
                # Check against company customers
                customers = company_context.get("customers", [])
                for customer in customers:
                    if entity.lower() in customer["name"].lower() or entity.lower() in customer["code"].lower():
                        validation_result.update({
                            "is_valid": True,
                            "confidence": 0.9,
                            "matched_customer": customer
                        })
                        break
            
            elif entity_type == "vendor":
                # Check against company vendors
                vendors = company_context.get("vendors", [])
                for vendor in vendors:
                    if entity.lower() in vendor["name"].lower() or entity.lower() in vendor["code"].lower():
                        validation_result.update({
                            "is_valid": True,
                            "confidence": 0.9,
                            "matched_vendor": vendor
                        })
                        break
            
            elif entity_type == "account_code":
                # Check against company chart of accounts
                accounts = company_context.get("financial_accounts", [])
                for account in accounts:
                    if entity.upper() == account["code"].upper():
                        validation_result.update({
                            "is_valid": True,
                            "confidence": 1.0,
                            "matched_account": account
                        })
                        break
            
            elif entity_type == "amount":
                # Validate amount format for company currency
                currency = company_context.get("currency", "KES")
                if currency == "KES":
                    # Kenyan Shilling format validation
                    if "KSh" in entity or "KES" in entity or any(c.isdigit() for c in entity):
                        validation_result.update({
                            "is_valid": True,
                            "confidence": 0.8
                        })
            
            elif entity_type == "date":
                # Validate date format
                try:
                    # Try to parse common date formats
                    date_formats = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%y"]
                    for fmt in date_formats:
                        try:
                            datetime.strptime(entity, fmt)
                            validation_result.update({
                                "is_valid": True,
                                "confidence": 0.9
                            })
                            break
                        except ValueError:
                            continue
                except:
                    pass
            
        except Exception as e:
            logger.error(f"Error validating entity: {str(e)}")
        
        return validation_result
    
    def get_company_processing_rules(self, company_context: Dict, document_type: str) -> Dict[str, Any]:
        """Get company-specific processing rules for document type"""
        processing_rules = company_context.get("processing_rules", {})
        document_rules = processing_rules.get(document_type, {})
        
        # Default rules
        default_rules = {
            "invoice": {
                "required_fields": ["invoice_number", "total_amount", "due_date"],
                "optional_fields": ["tax_amount", "discount_amount", "notes"],
                "validation_rules": {
                    "tax_rate": company_context.get("tax_rate", 16.0),
                    "currency": company_context.get("currency", "KES")
                }
            },
            "receipt": {
                "required_fields": ["receipt_number", "total_amount", "date"],
                "optional_fields": ["tax_amount", "payment_method"],
                "validation_rules": {
                    "currency": company_context.get("currency", "KES")
                }
            },
            "contract": {
                "required_fields": ["contract_number", "parties", "start_date", "end_date"],
                "optional_fields": ["value", "terms", "conditions"],
                "validation_rules": {}
            }
        }
        
        # Merge default rules with company-specific rules
        final_rules = default_rules.get(document_type, {})
        if document_rules:
            # Deep merge rules
            for key, value in document_rules.items():
                if key in final_rules and isinstance(final_rules[key], dict) and isinstance(value, dict):
                    final_rules[key].update(value)
                else:
                    final_rules[key] = value
        
        return final_rules
    
    def cache_company_context(self, company_id: UUID, context: Dict):
        """Cache company context for faster access"""
        self.company_configs[str(company_id)] = context
    
    def get_cached_context(self, company_id: UUID) -> Optional[Dict]:
        """Get cached company context"""
        return self.company_configs.get(str(company_id))
    
    def clear_cache(self, company_id: Optional[UUID] = None):
        """Clear company context cache"""
        if company_id:
            self.company_configs.pop(str(company_id), None)
        else:
            self.company_configs.clear()
    
    def get_company_statistics(self, company_id: UUID) -> Dict[str, Any]:
        """Get company processing statistics"""
        try:
            context = self.get_cached_context(company_id)
            if not context:
                return {}
            
            stats = {
                "company_name": context["company_name"],
                "total_customers": len(context.get("customers", [])),
                "total_vendors": len(context.get("vendors", [])),
                "total_accounts": len(context.get("financial_accounts", [])),
                "supported_document_types": context.get("document_types", []),
                "currency": context.get("currency"),
                "tax_rate": context.get("tax_rate"),
                "last_updated": datetime.utcnow().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting company statistics: {str(e)}")
            return {} 