import os
#!/usr/bin/env python3
"""
Local LLM Service for Vanta Ledger
Main service integrating hardware detection, company context, and model orchestration
"""

import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID

# LLM and ML imports
try:
    from llama_cpp import Llama

    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    logging.warning("llama-cpp-python not available")

# Try to import optional dependencies
try:
    import torch
    from transformers import (
        LayoutLMv3ForSequenceClassification,
        LayoutLMv3Processor,
    )

    LAYOUTLM_AVAILABLE = True
except Exception as e:
    logging.warning(
        f"LayoutLMv3 not available - document layout understanding disabled: {e}"
    )
except ImportError:
    TORCH_AVAILABLE = False
    LAYOUTLM_AVAILABLE = False
    logging.warning("PyTorch/Transformers not available")

# Database and cache
import redis
# from pymongo import MongoClient
from ..database import get_mongo_client
from pymongo.database import Database

# Optional hardware monitoring
try:
    import GPUtil
    import psutil
    HARDWARE_MONITORING_AVAILABLE = True
except ImportError:
    HARDWARE_MONITORING_AVAILABLE = False
    logging.warning("GPUtil/psutil not available - hardware monitoring disabled")

from ..config import settings
from ..models.document_models import EnhancedDocument
from .llm.company_context import CompanyContextManager
from .llm.hardware_detector import HardwareDetector

logger = logging.getLogger(__name__)


class LocalLLMService:
    """Local LLM orchestration and management service"""

    def __init__(self):
        # Initialize hardware detector
        self.hardware_detector = HardwareDetector()
        self.hardware_config = self.hardware_detector.detect_hardware()

        # Initialize database connections
        self.mongo_client = get_mongo_client()
        self.db: Database = self.mongo_client[settings.DATABASE_NAME]
        self.redis_client = redis.Redis.from_url(
            settings.REDIS_URI, decode_responses=True
        )

        # Initialize company context manager
        self.company_context_manager = CompanyContextManager(self.db)

        # Model management
        self.models = {}
        self.model_configs = self._load_model_configs()
        self.performance_metrics = {}

        logger.info(
            f"Local LLM Service initialized with hardware: {self.hardware_detector.get_hardware_summary()}"
        )

    def _load_model_configs(self) -> Dict[str, Dict]:
        """Load model configurations based on hardware"""
        base_configs = {
            "mistral_7b": {
                "model_path": "models/mistral/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
                "context_length": 4096,
                "max_tokens": 512,
                "temperature": 0.7,
                "top_p": 0.9,
                "priority": "high",
            },
            "phi3_mini": {
                "model_path": "models/phi3/phi-3-mini-4k-instruct.Q4_K_M.gguf",
                "context_length": 4096,
                "max_tokens": 256,
                "temperature": 0.8,
                "priority": "medium",
            },
            "tinyllama": {
                "model_path": "models/tinyllama/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
                "context_length": 1024,
                "max_tokens": 128,
                "temperature": 0.8,
                "priority": "low",
            },
            "layoutlmv3": {
                "model_path": "models/layoutlm/layoutlmv3-base",
                "processor_path": "models/layoutlm/layoutlmv3-base",
                "max_length": 512,
                "priority": "high",
            },
        }

        # Adjust configurations based on hardware
        recommended_models = self.hardware_config.get("recommended_models", {})

        for model_name, config in base_configs.items():
            if model_name in recommended_models:
                recommended_config = recommended_models[model_name]
                config["context_length"] = recommended_config.get(
                    "context_length", config["context_length"]
                )
                config["batch_size"] = recommended_config.get("batch_size", 1)
                config["quantization"] = recommended_config.get(
                    "quantization", "Q4_K_M"
                )

        return base_configs

    async def initialize_models(self):
        """Initialize all required models based on hardware"""
        try:
            logger.info("Initializing local LLM models...")

            # Load primary model based on hardware
            primary_model = self.hardware_config["recommended_models"]["primary"][
                "name"
            ]
            await self._load_model(primary_model)

            # Load secondary model if different
            secondary_model = self.hardware_config["recommended_models"]["secondary"][
                "name"
            ]
            if secondary_model != primary_model:
                await self._load_model(secondary_model)

            # Load document understanding model if available
            if "document_understanding" in self.hardware_config["recommended_models"]:
                doc_model = self.hardware_config["recommended_models"][
                    "document_understanding"
                ]["name"]
                await self._load_model(doc_model)

            logger.info(f"Models initialized: {list(self.models.keys())}")

        except Exception as e:
            logger.error(f"Error initializing models: {str(e)}")
            raise

    async def _load_model(self, model_name: str):
        """Load a specific model"""
        try:
            if model_name not in self.model_configs:
                logger.warning(f"Model config not found for {model_name}")
                return

            config = self.model_configs[model_name]
            model_path = Path(config["model_path"])

            if not model_path.exists():
                logger.warning(f"Model file not found: {model_path}")
                return

            if model_name in ["mistral_7b", "phi3_mini", "tinyllama"]:
                await self._load_llama_model(model_name, config)
            elif model_name == "layoutlmv3":
                await self._load_layoutlm_model(config)

            logger.info(f"Model {model_name} loaded successfully")

        except Exception as e:
            logger.error(f"Error loading model {model_name}: {str(e)}")

    async def _load_llama_model(self, model_name: str, config: Dict):
        """Load Llama-based model (Mistral, Phi-3, TinyLlama)"""
        try:
            # Get hardware-specific settings
            gpu_config = self.hardware_config.get("gpu", {})
            optimizations = gpu_config.get("optimizations", {})

            # Configure model parameters
            model_params = {
                "model_path": str(Path(config["model_path"])),
                "n_ctx": config["context_length"],
                "n_threads": self.hardware_config["cpu"]["optimizations"]["threads"],
                "n_gpu_layers": optimizations.get("use_gpu_layers", 0),
                "n_batch": optimizations.get("max_batch_size", 1),
                "verbose": False,
            }

            # Add GPU-specific optimizations
            if gpu_config and "RTX 3050" in gpu_config.get("name", ""):
                model_params.update(
                    {
                        "tensor_split": optimizations.get("tensor_split", [0.8, 0.2]),
                        "rope_scaling": {"type": "linear", "factor": 1.0},
                    }
                )

            self.models[model_name] = Llama(**model_params)

        except Exception as e:
            logger.error(f"Error loading Llama model {model_name}: {str(e)}")

    async def _load_layoutlm_model(self, config: Dict):
        """Load LayoutLMv3 model for document understanding"""
        try:
            if not LAYOUTLM_AVAILABLE:
                logger.warning(
                    "LayoutLMv3 not available, skipping document layout model"
                )
                return

            model_path = Path(config["model_path"])
            processor_path = Path(config["processor_path"])

            if not model_path.exists() or not processor_path.exists():
                logger.warning("LayoutLMv3 model files not found")
                return

            # Load model and processor from local paths (not from Hugging Face Hub)
            # These are local file paths, not remote downloads
            processor = LayoutLMv3Processor.from_pretrained(  # nosec B615 - Local files only  # nosec B615 - Local file path, not remote download  # nosec B615
                str(processor_path), 
                local_files_only=True,  # Ensure only local files are used
                trust_remote_code=False
            )
            model = LayoutLMv3ForSequenceClassification.from_pretrained(  # nosec B615 - Local files only  # nosec B615 - Local file path, not remote download  # nosec B615
                str(model_path), 
                local_files_only=True,  # Ensure only local files are used
                trust_remote_code=False
            )

            # Move to GPU if available
            if torch.cuda.is_available() and self.hardware_config.get("gpu"):
                device = torch.device("cuda")
                model = model.to(device)
                logger.info("LayoutLMv3 moved to GPU")
            else:
                device = torch.device("cpu")
                logger.info("LayoutLMv3 using CPU")

            self.models["layoutlmv3"] = {
                "processor": processor,
                "model": model,
                "device": device,
            }

        except Exception as e:
            logger.error(f"Error loading LayoutLMv3: {str(e)}")

    async def process_document_for_company(
        self, document: EnhancedDocument, company_id: UUID
    ) -> Dict[str, Any]:
        """Process document with company-specific context"""
        try:
            start_time = time.time()

            # Get company context
            company_context = await self.company_context_manager.get_company_context(
                company_id
            )

            # Generate cache key including company context
            cache_key = self._generate_company_cache_key(document, company_id)

            # Check cache first
            cached_result = await self._get_cached_result(cache_key)
            if cached_result:
                return cached_result

            # Process document with company context
            results = await self._process_with_company_context(
                document, company_context
            )

            # Cache results
            await self._cache_result(cache_key, results)

            # Record performance metrics
            processing_time = time.time() - start_time
            self._record_performance_metrics(
                "company_document_processing", processing_time
            )

            return results

        except Exception as e:
            logger.error(f"Error processing document for company: {str(e)}")
            raise

    async def _process_with_company_context(
        self, document: EnhancedDocument, company_context: Dict
    ) -> Dict[str, Any]:
        """Process document with company-specific context"""
        results = {}

        # Build company-specific prompt context
        context_prompt = self.company_context_manager.build_company_prompt_context(
            company_context
        )

        if document.extracted_text:
            # Document classification with company context
            results["classification"] = await self._classify_document_with_context(
                document.extracted_text, company_context
            )

            # Generate summary with company context
            results["summary"] = await self._generate_summary_with_context(
                document.extracted_text, company_context
            )

            # Extract entities with company context
            results["entities"] = await self._extract_entities_with_context(
                document.extracted_text, company_context
            )

            # Extract financial data with company context
            results["financial_data"] = await self._extract_financial_data_with_context(
                document.extracted_text, company_context
            )

        # Document layout understanding
        if hasattr(document, "file_path") and document.file_path:
            results["document_understanding"] = await self._understand_document_layout(
                document.file_path
            )

        return results

    async def _classify_document_with_context(
        self, text: str, company_context: Dict
    ) -> Dict[str, Any]:
        """Classify document with company context"""
        try:
            # Use primary model for classification
            primary_model = self.hardware_config["recommended_models"]["primary"][
                "name"
            ]
            if primary_model not in self.models:
                return {"type": "unknown", "confidence": 0.0}

            # Get company-specific instructions
            instructions = (
                self.company_context_manager.get_company_specific_instructions(
                    company_context, "document_classification"
                )
            )

            prompt = f"""
            {instructions}
            
            Context: {self.company_context_manager.build_company_prompt_context(company_context)}
            
            Classify the following document into one of these categories:
            - invoice
            - receipt  
            - contract
            - financial_statement
            - tax_document
            - legal_document
            - other
            
            Document text: {text[:1000]}
            
            Respond with only the category name and confidence score (0-1).
            """

            response = self.models[primary_model](
                prompt, max_tokens=50, temperature=0.3, stop=["\n"]
            )

            result = response["choices"][0]["text"].strip().lower()

            # Parse response with company context
            return self._parse_classification_result(result, company_context)

        except Exception as e:
            logger.error(f"Error classifying document with context: {str(e)}")
            return {"type": "unknown", "confidence": 0.0}

    def _parse_classification_result(
        self, result: str, company_context: Dict
    ) -> Dict[str, Any]:
        """Parse classification result with company context"""
        # Basic classification
        if "invoice" in result:
            doc_type = "invoice"
            confidence = 0.9
        elif "receipt" in result:
            doc_type = "receipt"
            confidence = 0.9
        elif "contract" in result:
            doc_type = "contract"
            confidence = 0.8
        elif "financial" in result:
            doc_type = "financial_statement"
            confidence = 0.8
        elif "tax" in result:
            doc_type = "tax_document"
            confidence = 0.8
        elif "legal" in result:
            doc_type = "legal_document"
            confidence = 0.8
        else:
            doc_type = "other"
            confidence = 0.5

        # Adjust confidence based on company context
        if doc_type in company_context.get("document_types", []):
            confidence = min(confidence + 0.1, 1.0)

        return {
            "type": doc_type,
            "confidence": confidence,
            "company_context": company_context["company_name"],
        }

    async def _generate_summary_with_context(
        self, text: str, company_context: Dict
    ) -> str:
        """Generate summary with company context"""
        try:
            primary_model = self.hardware_config["recommended_models"]["primary"][
                "name"
            ]
            if primary_model not in self.models:
                return "Summary not available"

            instructions = (
                self.company_context_manager.get_company_specific_instructions(
                    company_context, "summary_generation"
                )
            )

            prompt = f"""
            {instructions}
            
            Context: {self.company_context_manager.build_company_prompt_context(company_context)}
            
            Generate a concise summary (2-3 sentences) of the following document, 
            focusing on information relevant to {company_context['company_name']}:
            
            {text[:2000]}
            
            Summary:
            """

            response = self.models[primary_model](
                prompt, max_tokens=150, temperature=0.5, stop=["\n\n"]
            )

            return response["choices"][0]["text"].strip()

        except Exception as e:
            logger.error(f"Error generating summary with context: {str(e)}")
            return "Summary generation failed"

    async def _extract_entities_with_context(
        self, text: str, company_context: Dict
    ) -> Dict[str, List[str]]:
        """Extract entities with company context"""
        try:
            primary_model = self.hardware_config["recommended_models"]["primary"][
                "name"
            ]
            if primary_model not in self.models:
                return {}

            instructions = (
                self.company_context_manager.get_company_specific_instructions(
                    company_context, "entity_extraction"
                )
            )

            prompt = f"""
            {instructions}
            
            Context: {self.company_context_manager.build_company_prompt_context(company_context)}
            
            Extract the following entities from the document text, 
            paying special attention to entities related to {company_context['company_name']}:
            - Company names (especially {company_context['company_name']} and related companies)
            - Dates
            - Amounts (money in {company_context['currency']})
            - Invoice numbers
            - Email addresses
            - Phone numbers
            - Account codes (from company's chart of accounts)
            
            Document: {text[:1500]}
            
            Return as JSON format:
            {{
                "companies": ["company1", "company2"],
                "dates": ["date1", "date2"],
                "amounts": ["amount1", "amount2"],
                "invoice_numbers": ["inv1", "inv2"],
                "emails": ["email1", "email2"],
                "phones": ["phone1", "phone2"],
                "account_codes": ["code1", "code2"]
            }}
            """

            response = self.models[primary_model](
                prompt, max_tokens=300, temperature=0.3
            )

            result_text = response["choices"][0]["text"].strip()

            # Parse JSON response
            try:
                import re

                json_match = re.search(r"\{.*\}", result_text, re.DOTALL)
                if json_match:
                    entities = json.loads(json_match.group())
                    # Filter entities based on company context
                    return self._filter_entities_by_context(entities, company_context)
            except (json.JSONDecodeError, ValueError) as e:
                logger.debug(f"Failed to parse JSON entities: {e}")
                pass

            # Fallback to simple extraction
            return self._simple_entity_extraction_with_context(text, company_context)

        except Exception as e:
            logger.error(f"Error extracting entities with context: {str(e)}")
            return {}

    def _filter_entities_by_context(
        self, entities: Dict, company_context: Dict
    ) -> Dict:
        """Filter entities based on company context"""
        filtered_entities = entities.copy()

        # Prioritize company name in companies list
        if company_context["company_name"] in entities.get("companies", []):
            filtered_entities["companies"] = [company_context["company_name"]] + [
                c
                for c in entities.get("companies", [])
                if c != company_context["company_name"]
            ]

        # Filter account codes based on company's chart of accounts
        company_accounts = [
            acc["code"] for acc in company_context.get("financial_accounts", [])
        ]
        if company_accounts:
            filtered_entities["account_codes"] = [
                code
                for code in entities.get("account_codes", [])
                if code in company_accounts
            ]

        return filtered_entities

    def _simple_entity_extraction_with_context(
        self, text: str, company_context: Dict
    ) -> Dict[str, List[str]]:
        """Simple rule-based entity extraction with company context"""
        import re

        entities = {
            "amounts": [],
            "dates": [],
            "emails": [],
            "phones": [],
            "companies": [company_context["company_name"]],
        }

        # Extract amounts with currency context
        currency_symbol = "KSh" if company_context["currency"] == "KES" else "$"
        amount_pattern = rf"[{currency_symbol}]?[\d,]+\.?\d*"
        entities["amounts"] = re.findall(amount_pattern, text)

        # Extract dates
        date_pattern = r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"
        entities["dates"] = re.findall(date_pattern, text)

        # Extract emails
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        entities["emails"] = re.findall(email_pattern, text)

        # Extract phone numbers
        phone_pattern = r"[\+]?[1-9][\d]{0,15}"
        entities["phones"] = re.findall(phone_pattern, text)

        return entities

    async def _extract_financial_data_with_context(
        self, text: str, company_context: Dict
    ) -> Dict[str, Any]:
        """Extract financial data with company context"""
        try:
            # Use secondary model for financial extraction
            secondary_model = self.hardware_config["recommended_models"]["secondary"][
                "name"
            ]
            if secondary_model not in self.models:
                return {}

            instructions = (
                self.company_context_manager.get_company_specific_instructions(
                    company_context, "financial_extraction"
                )
            )

            prompt = f"""
            {instructions}
            
            Context: {self.company_context_manager.build_company_prompt_context(company_context)}
            
            Extract financial information from this document for {company_context['company_name']}:
            - Total amount (in {company_context['currency']})
            - Tax amount (in {company_context['currency']})
            - Due date
            - Invoice number
            - Customer/vendor name (check against company's customer/vendor list)
            - Account codes (from company's chart of accounts)
            
            Document: {text[:1000]}
            
            Return as JSON:
            {{
                "total_amount": "amount",
                "tax_amount": "amount", 
                "due_date": "date",
                "invoice_number": "number",
                "customer_name": "name",
                "account_codes": ["code1", "code2"]
            }}
            """

            response = self.models[secondary_model](
                prompt, max_tokens=200, temperature=0.3
            )

            result_text = response["choices"][0]["text"].strip()

            # Parse JSON
            try:
                import re

                json_match = re.search(r"\{.*\}", result_text, re.DOTALL)
                if json_match:
                    financial_data = json.loads(json_match.group())
                    return self._validate_financial_data(
                        financial_data, company_context
                    )
            except (json.JSONDecodeError, ValueError) as e:
                logger.debug(f"Failed to parse JSON financial data: {e}")
                pass

            return {}

        except Exception as e:
            logger.error(f"Error extracting financial data with context: {str(e)}")
            return {}

    def _validate_financial_data(
        self, financial_data: Dict, company_context: Dict
    ) -> Dict:
        """Validate financial data against company context"""
        validated_data = financial_data.copy()

        # Validate customer/vendor names
        if financial_data.get("customer_name"):
            customers = [c["name"] for c in company_context.get("customers", [])]
            vendors = [v["name"] for v in company_context.get("vendors", [])]

            if financial_data["customer_name"] not in customers + vendors:
                validated_data["customer_name"] = (
                    f"Unknown: {financial_data['customer_name']}"
                )

        # Validate account codes
        if financial_data.get("account_codes"):
            company_accounts = [
                acc["code"] for acc in company_context.get("financial_accounts", [])
            ]
            validated_data["account_codes"] = [
                code
                for code in financial_data["account_codes"]
                if code in company_accounts
            ]

        return validated_data

    async def _understand_document_layout(self, file_path: str) -> Dict[str, Any]:
        """Understand document layout using LayoutLMv3"""
        try:
            if not LAYOUTLM_AVAILABLE or "layoutlmv3" not in self.models:
                return {"layout": "unknown", "reason": "LayoutLMv3 not available"}

            # Load and process image
            from PIL import Image

            image = Image.open(file_path).convert("RGB")
            processor = self.models["layoutlmv3"]["processor"]
            model = self.models["layoutlmv3"]["model"]
            device = self.models["layoutlmv3"]["device"]

            # Process image
            encoding = processor(image, return_tensors="pt")
            encoding = {k: v.to(device) for k, v in encoding.items()}

            # Get predictions
            with torch.no_grad():
                outputs = model(**encoding)
                predictions = outputs.logits.argmax(-1)

            # Analyze layout
            layout_analysis = {
                "has_table": "table" in str(predictions).lower(),
                "has_form": "form" in str(predictions).lower(),
                "text_regions": len(encoding["input_ids"][0]),
                "layout_type": (
                    "structured"
                    if "table" in str(predictions).lower()
                    else "unstructured"
                ),
                "processing_device": "gpu" if device.type == "cuda" else "cpu",
            }

            return layout_analysis

        except Exception as e:
            logger.error(f"Error understanding document layout: {str(e)}")
            return {"layout": "unknown"}

    def _generate_company_cache_key(
        self, document: EnhancedDocument, company_id: UUID
    ) -> str:
        """Generate cache key including company context"""
        content_hash = hashlib.sha256(
            f"{document.original_filename}{document.file_size}{document.checksum}{company_id}".encode()
        ).hexdigest()[
            :16
        ]  # Use first 16 chars for cache key compatibility
        return f"llm_company_cache:{content_hash}"

    async def _get_cached_result(self, cache_key: str) -> Optional[Dict]:
        """Get cached result from Redis"""
        try:
            cached = self.redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            return None
        except Exception as e:
            logger.error(f"Error getting cached result: {str(e)}")
            return None

    async def _cache_result(self, cache_key: str, result: Dict):
        """Cache result in Redis"""
        try:
            self.redis_client.setex(
                cache_key, 3600, json.dumps(result, default=str)  # 1 hour TTL
            )
        except Exception as e:
            logger.error(f"Error caching result: {str(e)}")

    def _record_performance_metrics(self, operation: str, duration: float):
        """Record performance metrics"""
        if operation not in self.performance_metrics:
            self.performance_metrics[operation] = []

        self.performance_metrics[operation].append(
            {
                "duration": duration,
                "timestamp": datetime.utcnow().isoformat(),
                "hardware_profile": self.hardware_config["performance_profile"],
            }
        )

        # Keep only last 100 metrics
        if len(self.performance_metrics[operation]) > 100:
            self.performance_metrics[operation] = self.performance_metrics[operation][
                -100:
            ]

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        metrics = {}

        for operation, data in self.performance_metrics.items():
            if data:
                durations = [item["duration"] for item in data]
                metrics[operation] = {
                    "avg_duration": sum(durations) / len(durations),
                    "min_duration": min(durations),
                    "max_duration": max(durations),
                    "total_operations": len(data),
                    "hardware_profile": data[-1].get("hardware_profile", "unknown"),
                }

        # Add hardware information
        metrics["hardware"] = {
            "gpu": self.hardware_config.get("gpu", {}).get("name", "None"),
            "cpu_cores": self.hardware_config["cpu"]["cores"],
            "memory_gb": round(self.hardware_config["memory"]["total"] / (1024**3), 2),
            "performance_profile": self.hardware_config["performance_profile"],
        }

        return metrics

    async def get_hardware_status(self) -> Dict[str, Any]:
        """Get current hardware status"""
        try:
            status = {
                "gpu": None,
                "cpu": {},
                "memory": {},
                "models_loaded": list(self.models.keys()),
            }

            # GPU status
            if self.hardware_config.get("gpu") and HARDWARE_MONITORING_AVAILABLE:
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        gpu = gpus[0]
                        status["gpu"] = {
                            "name": gpu.name,
                            "memory_used_percent": round(
                                (gpu.memoryUsed / gpu.memoryTotal) * 100, 1
                            ),
                            "temperature": gpu.temperature,
                            "load_percent": round(gpu.load * 100, 1) if gpu.load else 0,
                        }
                except Exception as e:
                    logger.debug(f"Failed to get GPU status: {e}")
                    pass

            # CPU status
            if HARDWARE_MONITORING_AVAILABLE:
                status["cpu"] = {
                    "usage_percent": psutil.cpu_percent(interval=1),
                    "cores": psutil.cpu_count(logical=True),
                }
            else:
                status["cpu"] = {"error": "Hardware monitoring not available"}

            # Memory status
            if HARDWARE_MONITORING_AVAILABLE:
                memory = psutil.virtual_memory()
                status["memory"] = {
                    "used_percent": memory.percent,
                    "available_gb": round(memory.available / (1024**3), 2),
                }
            else:
                status["memory"] = {"error": "Hardware monitoring not available"}

            return status

        except Exception as e:
            logger.error(f"Error getting hardware status: {str(e)}")
            return {"error": str(e)}


# Global instance
local_llm_service = LocalLLMService()
