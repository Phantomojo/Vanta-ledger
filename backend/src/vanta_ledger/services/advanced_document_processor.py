#!/usr/bin/env python3
"""
Advanced Document Processor Service
Inspired by Docling + Documind - Enhanced document processing with layout understanding
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

import redis
from pymongo.collection import Collection
from pymongo.database import Database

# Optional ML imports
try:
    import torch
    from transformers import (
        LayoutLMv3ForSequenceClassification,
        LayoutLMv3Processor,
        AutoTokenizer,
        AutoModelForSequenceClassification
    )
    from PIL import Image
    import numpy as np
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logging.warning("ML libraries not available - advanced features disabled")

try:
    import cv2
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logging.warning("OCR libraries not available - OCR features disabled")

from ..database import get_mongo_client
from ..config import settings
from ..models.document_models import (
    DocumentCategory,
    DocumentMetadata,
    DocumentStatus,
    DocumentType,
    EnhancedDocument,
)
from ..utils.validation import input_validator

logger = logging.getLogger(__name__)


class AdvancedDocumentProcessor:
    """Advanced document processing with layout understanding inspired by Docling + Documind"""

    def __init__(self):
        # Database connections
        self.mongo_client = get_mongo_client()
        self.db: Database = self.mongo_client[settings.DATABASE_NAME]
        self.redis_client = redis.Redis.from_url(
            settings.REDIS_URI, decode_responses=True
        )

        # Collections
        self.documents: Collection = self.db.documents
        self.document_analyses: Collection = self.db.document_analyses
        self.extracted_tables: Collection = self.db.extracted_tables
        self.layout_analyses: Collection = self.db.layout_analyses

        # Initialize ML models if available
        self.layout_model = None
        self.table_model = None
        self.processor = None
        self._initialize_ml_models()

        # Create indexes
        self._create_indexes()

        logger.info(f"Advanced Document Processor initialized. ML Available: {ML_AVAILABLE}, OCR Available: {OCR_AVAILABLE}")

    def _initialize_ml_models(self):
        """Initialize ML models for advanced document processing"""
        if not ML_AVAILABLE:
            logger.warning("ML libraries not available - using basic processing")
            return

        try:
            # Initialize LayoutLMv3 for layout understanding
            model_name = "microsoft/layoutlmv3-base"
            self.layout_model = LayoutLMv3ForSequenceClassification.from_pretrained(model_name)
            self.processor = LayoutLMv3Processor.from_pretrained(model_name)
            
            # Move to GPU if available
            if torch.cuda.is_available():
                self.layout_model = self.layout_model.to('cuda')
                logger.info("LayoutLMv3 model loaded on GPU")
            else:
                logger.info("LayoutLMv3 model loaded on CPU")

            logger.info("ML models initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing ML models: {str(e)}")
            self.layout_model = None
            self.table_model = None
            self.processor = None

    def _create_indexes(self):
        """Create database indexes for optimal performance"""
        try:
            # Document analysis indexes
            self.document_analyses.create_index([("document_id", 1)])
            self.document_analyses.create_index([("analysis_type", 1)])
            self.document_analyses.create_index([("created_at", -1)])

            # Extracted tables indexes
            self.extracted_tables.create_index([("document_id", 1)])
            self.extracted_tables.create_index([("table_type", 1)])
            self.extracted_tables.create_index([("confidence_score", -1)])

            # Layout analysis indexes
            self.layout_analyses.create_index([("document_id", 1)])
            self.layout_analyses.create_index([("layout_type", 1)])

            logger.info("Advanced document processor indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {str(e)}")

    async def process_complex_document(
        self, 
        document: EnhancedDocument,
        processing_options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process complex documents with advanced layout understanding
        
        Args:
            document: Enhanced document to process
            processing_options: Optional processing configuration
            
        Returns:
            Dictionary containing processing results
        """
        try:
            processing_options = processing_options or {}
            
            # Initialize results
            results = {
                "document_id": str(document.id),
                "processing_timestamp": datetime.utcnow().isoformat(),
                "processing_options": processing_options,
                "extracted_text": "",
                "extracted_tables": [],
                "layout_analysis": {},
                "confidence_scores": {},
                "processing_errors": []
            }

            # Step 1: Basic OCR and text extraction
            if OCR_AVAILABLE:
                text_result = await self._extract_text_advanced(document)
                results["extracted_text"] = text_result.get("text", "")
                results["confidence_scores"]["ocr"] = text_result.get("confidence", 0.0)
            else:
                logger.warning("OCR not available - skipping text extraction")

            # Step 2: Layout analysis
            if self.layout_model and ML_AVAILABLE:
                layout_result = await self._analyze_layout(document)
                results["layout_analysis"] = layout_result
                results["confidence_scores"]["layout"] = layout_result.get("confidence", 0.0)
            else:
                logger.warning("Layout model not available - skipping layout analysis")

            # Step 3: Handwritten text processing
            if processing_options.get("process_handwritten", False):
                handwritten_result = await self._process_handwritten_text(document)
                results["handwritten_text"] = handwritten_result.get("text", "")
                results["confidence_scores"]["handwritten"] = handwritten_result.get("confidence", 0.0)

            # Step 4: Save analysis results
            await self._save_analysis_results(document.id, results)

            logger.info(f"Advanced document processing completed for {document.original_filename}")
            return results

        except Exception as e:
            logger.error(f"Error processing complex document: {str(e)}")
            results["processing_errors"].append(str(e))
            return results

    async def _extract_text_advanced(self, document: EnhancedDocument) -> Dict[str, Any]:
        """Advanced text extraction with OCR"""
        try:
            if not OCR_AVAILABLE:
                return {"text": "", "confidence": 0.0, "error": "OCR not available"}

            # Get document file path
            file_path = Path(document.file_path)
            if not file_path.exists():
                return {"text": "", "confidence": 0.0, "error": "File not found"}

            # Read image
            image = cv2.imread(str(file_path))
            if image is None:
                return {"text": "", "confidence": 0.0, "error": "Could not read image"}

            # Convert to grayscale for better OCR
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply preprocessing for better OCR results
            # Noise reduction
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Thresholding
            _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Extract text using Tesseract
            text = pytesseract.image_to_string(thresh, config='--psm 6')
            
            # Get confidence scores
            data = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            return {
                "text": text.strip(),
                "confidence": avg_confidence / 100.0,  # Normalize to 0-1
                "word_count": len(text.split()),
                "processing_method": "advanced_ocr"
            }

        except Exception as e:
            logger.error(f"Error in advanced text extraction: {str(e)}")
            return {"text": "", "confidence": 0.0, "error": str(e)}

    async def _analyze_layout(self, document: EnhancedDocument) -> Dict[str, Any]:
        """Analyze document layout using LayoutLMv3"""
        try:
            if not self.layout_model or not ML_AVAILABLE:
                return {"error": "Layout model not available"}

            # Get document file path
            file_path = Path(document.file_path)
            if not file_path.exists():
                return {"error": "File not found"}

            # Load image
            image = Image.open(file_path).convert("RGB")
            
            # Process with LayoutLMv3
            encoding = self.processor(
                image,
                return_tensors="pt",
                truncation=True,
                max_length=512
            )

            # Move to GPU if available
            if torch.cuda.is_available():
                encoding = {k: v.to('cuda') for k, v in encoding.items()}

            # Get predictions
            with torch.no_grad():
                outputs = self.layout_model(**encoding)
                predictions = outputs.logits.argmax(-1)

                # Analyze layout structure
    confidence_tensor = torch.softmax(outputs.logits, dim=-1).max()
    confidence = confidence_tensor.detach().float().cpu().item()
    layout_analysis = {
        "layout_type": self._classify_layout_type(predictions),
        "regions": self._extract_layout_regions(encoding, predictions),
        "confidence": confidence,
        "processing_method": "layoutlmv3"
    }

            return layout_analysis

        except Exception as e:
            logger.error(f"Error in layout analysis: {str(e)}")
            return {"error": str(e)}

    async def _process_handwritten_text(self, document: EnhancedDocument) -> Dict[str, Any]:
        """Process handwritten text in documents"""
        try:
            if not OCR_AVAILABLE:
                return {"text": "", "confidence": 0.0, "error": "OCR not available"}

            # Get document file path
            file_path = Path(document.file_path)
            if not file_path.exists():
                return {"text": "", "confidence": 0.0, "error": "File not found"}

            # Read image
            image = cv2.imread(str(file_path))
            if image is None:
                return {"text": "", "confidence": 0.0, "error": "Could not read image"}

            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply preprocessing optimized for handwritten text
            # Adaptive thresholding for better handwritten text recognition
            adaptive_thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )

            # Extract text with handwritten text configuration
            text = pytesseract.image_to_string(
                adaptive_thresh, 
                config='--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,()-/$'
            )

            # Get confidence scores
            data = pytesseract.image_to_data(adaptive_thresh, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            return {
                "text": text.strip(),
                "confidence": avg_confidence / 100.0,
                "word_count": len(text.split()),
                "processing_method": "handwritten_ocr"
            }

        except Exception as e:
            logger.error(f"Error in handwritten text processing: {str(e)}")
            return {"text": "", "confidence": 0.0, "error": str(e)}

    def _classify_layout_type(self, predictions) -> str:
        """Classify document layout type based on predictions"""
        try:
            # Simple layout classification based on prediction patterns
            prediction_list = predictions.cpu().numpy().tolist()
            
            # Count different layout elements
            element_counts = {}
            for pred in prediction_list:
                element_counts[pred] = element_counts.get(pred, 0) + 1
            
            # Classify based on dominant elements
            if element_counts.get(1, 0) > element_counts.get(0, 0):  # Text dominant
                return "text_dominant"
            elif element_counts.get(2, 0) > 0:  # Table present
                return "table_dominant"
            elif element_counts.get(3, 0) > 0:  # Form present
                return "form_dominant"
            else:
                return "mixed_layout"
                
        except Exception as e:
            logger.error(f"Error in layout classification: {str(e)}")
            return "unknown"

    def _extract_layout_regions(self, encoding, predictions) -> List[Dict]:
        """Extract layout regions from document"""
        try:
            regions = []
            prediction_list = predictions.cpu().numpy().tolist()
            
            # Extract bounding boxes and labels
            for i, pred in enumerate(prediction_list):
                if i < len(encoding['bbox']):
                    bbox = encoding['bbox'][i].cpu().numpy().tolist()
                    regions.append({
                        "type": f"region_{pred}",
                        "bbox": bbox,
                        "confidence": 0.8  # Placeholder confidence
                    })
            
            return regions
            
        except Exception as e:
            logger.error(f"Error extracting layout regions: {str(e)}")
            return []

    async def _save_analysis_results(self, document_id: UUID, results: Dict[str, Any]):
        """Save analysis results to database"""
        try:
            # Save document analysis
            analysis_data = {
                "document_id": str(document_id),
                "analysis_type": "advanced_processing",
                "results": results,
                "created_at": datetime.utcnow(),
                "processing_version": "1.0.0"
            }
            
            self.document_analyses.insert_one(analysis_data)

            # Save layout analysis
            if results.get("layout_analysis"):
                layout_data = {
                    "document_id": str(document_id),
                    "layout_type": results["layout_analysis"].get("layout_type", "unknown"),
                    "layout_data": results["layout_analysis"],
                    "confidence_score": results["layout_analysis"].get("confidence", 0.0),
                    "created_at": datetime.utcnow()
                }
                
                self.layout_analyses.insert_one(layout_data)

            logger.info(f"Analysis results saved for document {document_id}")

        except Exception as e:
            logger.error(f"Error saving analysis results: {str(e)}")

    async def get_document_analysis(self, document_id: UUID) -> Dict[str, Any]:
        """Get analysis results for a document"""
        try:
            analysis = self.document_analyses.find_one({"document_id": str(document_id)})
            if analysis:
                return analysis["results"]
            else:
                return {"error": "Analysis not found"}

        except Exception as e:
            logger.error(f"Error getting document analysis: {str(e)}")
            return {"error": str(e)}

    async def get_layout_analysis(self, document_id: UUID) -> Dict[str, Any]:
        """Get layout analysis for a document"""
        try:
            layout = self.layout_analyses.find_one({"document_id": str(document_id)})
            if layout:
                return layout["layout_data"]
            else:
                return {"error": "Layout analysis not found"}

        except Exception as e:
            logger.error(f"Error getting layout analysis: {str(e)}")
            return {"error": str(e)}

    def get_processing_capabilities(self) -> Dict[str, Any]:
        """Get current processing capabilities"""
        return {
            "ml_available": ML_AVAILABLE,
            "ocr_available": OCR_AVAILABLE,
            "layout_model_loaded": self.layout_model is not None,
            "gpu_available": torch.cuda.is_available() if ML_AVAILABLE else False,
            "processing_features": [
                "advanced_ocr",
                "layout_analysis",
                "handwritten_text_processing"
            ]
        }


# Global instance
advanced_document_processor = AdvancedDocumentProcessor()
