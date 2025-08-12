#!/usr/bin/env python3
"""
Advanced Document Processing Service
Handles file uploads, OCR, AI analysis, and information extraction
"""

import hashlib
import json
import logging
import mimetypes
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# OCR and document processing
try:
    import docx2txt
    import fitz  # PyMuPDF
    import pdf2image
    import pytesseract
    from PIL import Image

    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logging.warning(
        "OCR libraries not available. Install: pip install pytesseract pdf2image python-docx2txt PyMuPDF Pillow"
    )

# AI and text processing
import re
from collections import defaultdict

import spacy

try:
    nlp = spacy.load("en_core_web_sm")
    NLP_AVAILABLE = True
except OSError:
    NLP_AVAILABLE = False
    logging.warning(
        "spaCy model not available. Install: python -m spacy download en_core_web_sm"
    )


class DocumentProcessor:
    """Advanced document processing with OCR, AI analysis, and information extraction"""

    def __init__(
        self,
        upload_dir: str = "../data/uploads",
        processed_dir: str = "../data/processed_documents",
    ):
        self.upload_dir = Path(upload_dir)
        self.processed_dir = Path(processed_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        # Supported file types
        self.supported_types = {
            ".pdf": self._extract_pdf_text,
            ".docx": self._extract_docx_text,
            ".doc": self._extract_docx_text,
            ".txt": self._extract_txt_text,
            ".png": self._extract_image_text,
            ".jpg": self._extract_image_text,
            ".jpeg": self._extract_image_text,
            ".tiff": self._extract_image_text,
            ".bmp": self._extract_image_text,
        }

        # Document type patterns
        self.document_patterns = {
            "invoice": [
                r"invoice",
                r"bill",
                r"payment",
                r"amount due",
                r"total amount",
                r"customer",
                r"client",
                r"account",
                r"balance",
            ],
            "contract": [
                r"contract",
                r"agreement",
                r"terms",
                r"conditions",
                r"parties",
                r"effective date",
                r"expiration",
                r"termination",
            ],
            "receipt": [
                r"receipt",
                r"purchase",
                r"item",
                r"quantity",
                r"price",
                r"cash",
                r"credit",
                r"debit",
                r"transaction",
            ],
            "report": [
                r"report",
                r"summary",
                r"analysis",
                r"findings",
                r"conclusion",
                r"recommendation",
                r"overview",
                r"status",
            ],
            "proposal": [
                r"proposal",
                r"quote",
                r"estimate",
                r"bid",
                r"offer",
                r"scope of work",
                r"project",
                r"cost",
            ],
        }

        # Financial patterns
        self.financial_patterns = {
            "amounts": r"\$[\d,]+\.?\d*|\d+\.?\d*\s*(?:dollars?|USD|euros?|EUR|pounds?|GBP)",
            "percentages": r"\d+\.?\d*\s*%|\d+\.?\d*\s*percent",
            "dates": r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",
            "phone": r"\+?1?\s*\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}",
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "url": r"https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?",
        }

    def process_document(
        self, file_path: str, original_filename: str
    ) -> Dict[str, Any]:
        """Process a document and extract comprehensive information"""
        try:
            # Generate unique document ID
            doc_id = self._generate_doc_id(file_path, original_filename)

            # Extract text content
            text_content = self._extract_text(file_path)
            if not text_content:
                raise ValueError("Could not extract text from document")

            # Store original file
            original_file_path = self._store_original_file(
                file_path, doc_id, original_filename
            )

            # Perform comprehensive analysis
            analysis = self._analyze_document(text_content, doc_id)

            # Store analysis results
            self._store_analysis(doc_id, analysis)

            # Store text content
            self._store_text_content(doc_id, text_content)

            return {
                "doc_id": doc_id,
                "original_filename": original_filename,
                "file_path": str(original_file_path),
                "text_content": text_content,
                "analysis": analysis,
                "status": "processed",
            }

        except Exception as e:
            logging.error(f"Error processing document {original_filename}: {str(e)}")
            raise

    def _generate_doc_id(self, file_path: str, original_filename: str) -> str:
        """Generate unique document ID based on content hash"""
        with open(file_path, "rb") as f:
            content_hash = hashlib.sha256(f.read()).hexdigest()[:8]
        return f"{content_hash}_{int(datetime.now().timestamp())}"

    def _extract_text(self, file_path: str) -> str:
        """Extract text from various file formats"""
        file_ext = Path(file_path).suffix.lower()

        if file_ext not in self.supported_types:
            raise ValueError(f"Unsupported file type: {file_ext}")

        return self.supported_types[file_ext](file_path)

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF files"""
        text = ""

        # Try PyMuPDF first (faster and more secure)
        try:
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text() + "\n"
            doc.close()
            if text.strip():
                return text
        except Exception as e:
            logging.warning(f"PyMuPDF failed for {file_path}: {e}")

        # Fallback to OCR if PyMuPDF fails or no text found
        if OCR_AVAILABLE:
            try:
                images = pdf2image.convert_from_path(file_path)
                for image in images:
                    text += pytesseract.image_to_string(image) + "\n"
                return text
            except Exception as e:
                logging.error(f"OCR failed for {file_path}: {e}")

        return text

    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX files"""
        try:
            return docx2txt.process(file_path)
        except Exception as e:
            logging.error(f"Failed to extract text from DOCX {file_path}: {e}")
            return ""

    def _extract_txt_text(self, file_path: str) -> str:
        """Extract text from TXT files"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, "r", encoding="latin-1") as f:
                    return f.read()
            except Exception as e:
                logging.error(f"Failed to read TXT file {file_path}: {e}")
                return ""

    def _extract_image_text(self, file_path: str) -> str:
        """Extract text from images using OCR"""
        if not OCR_AVAILABLE:
            raise ValueError("OCR not available for image processing")

        try:
            image = Image.open(file_path)
            return pytesseract.image_to_string(image)
        except Exception as e:
            logging.error(f"OCR failed for image {file_path}: {e}")
            return ""

    def _store_original_file(
        self, file_path: str, doc_id: str, original_filename: str
    ) -> Path:
        """Store original file with proper naming"""
        file_ext = Path(original_filename).suffix
        new_filename = f"{doc_id}{file_ext}"
        new_path = self.upload_dir / new_filename

        shutil.copy2(file_path, new_path)
        return new_path

    def _store_text_content(self, doc_id: str, text_content: str) -> Path:
        """Store extracted text content"""
        text_file = self.processed_dir / f"{doc_id}.txt"
        with open(text_file, "w", encoding="utf-8") as f:
            f.write(text_content)
        return text_file

    def _analyze_document(self, text_content: str, doc_id: str) -> Dict[str, Any]:
        """Perform comprehensive document analysis"""
        analysis = {
            "doc_id": doc_id,
            "type": self._classify_document(text_content),
            "keywords": self._extract_keywords(text_content),
            "dates": self._extract_dates(text_content),
            "companies": self._extract_companies(text_content),
            "financial_data": self._extract_financial_data(text_content),
            "projects": self._extract_projects(text_content),
            "entities": self._extract_entities(text_content),
            "summary": self._generate_summary(text_content),
            "metadata": self._extract_metadata(text_content),
            "processed_at": datetime.now().isoformat(),
        }

        return analysis

    def _classify_document(self, text: str) -> str:
        """Classify document type based on content patterns"""
        text_lower = text.lower()
        scores = defaultdict(int)

        for doc_type, patterns in self.document_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    scores[doc_type] += 1

        if scores:
            return max(scores, key=scores.get)
        return "unknown"

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        if not NLP_AVAILABLE:
            # Fallback to simple keyword extraction
            words = re.findall(r"\b\w+\b", text.lower())
            word_freq = defaultdict(int)
            for word in words:
                if len(word) > 3 and word not in [
                    "the",
                    "and",
                    "for",
                    "with",
                    "this",
                    "that",
                ]:
                    word_freq[word] += 1
            return sorted(word_freq, key=word_freq.get, reverse=True)[:10]

        # Use spaCy for better keyword extraction
        doc = nlp(text)
        keywords = []

        # Extract noun phrases and named entities
        for chunk in doc.noun_chunks:
            if len(chunk.text) > 3:
                keywords.append(chunk.text.lower())

        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT", "GPE", "PERSON"]:
                keywords.append(ent.text.lower())

        return list(set(keywords))[:15]

    def _extract_dates(self, text: str) -> List[str]:
        """Extract dates from text"""
        date_patterns = [
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
            r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",
            r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b",
            r"\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b",
        ]

        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)

        return list(set(dates))

    def _extract_companies(self, text: str) -> List[str]:
        """Extract company names from text"""
        if not NLP_AVAILABLE:
            # Simple pattern matching
            company_patterns = [
                r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc|Corp|LLC|Ltd|Company|Co|Corporation)\b",
                r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:&|and)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b",
            ]
            companies = []
            for pattern in company_patterns:
                matches = re.findall(pattern, text)
                companies.extend(matches)
            return list(set(companies))

        # Use spaCy for better entity recognition
        doc = nlp(text)
        companies = []

        for ent in doc.ents:
            if ent.label_ == "ORG":
                companies.append(ent.text)

        return list(set(companies))

    def _extract_financial_data(self, text: str) -> List[Dict[str, str]]:
        """Extract financial information"""
        financial_data = []

        # Extract amounts
        amounts = re.findall(self.financial_patterns["amounts"], text)
        for amount in amounts:
            financial_data.append(
                {
                    "type": "amount",
                    "value": amount,
                    "context": self._get_context(text, amount, 50),
                }
            )

        # Extract percentages
        percentages = re.findall(self.financial_patterns["percentages"], text)
        for percentage in percentages:
            financial_data.append(
                {
                    "type": "percentage",
                    "value": percentage,
                    "context": self._get_context(text, percentage, 50),
                }
            )

        return financial_data

    def _extract_projects(self, text: str) -> List[str]:
        """Extract project names/references"""
        project_patterns = [
            r"Project:\s*([A-Z][a-zA-Z0-9\s]+)",
            r"Project\s+([A-Z][a-zA-Z0-9\s]+)",
            r"([A-Z][a-zA-Z0-9\s]+)\s+Project",
        ]

        projects = []
        for pattern in project_patterns:
            matches = re.findall(pattern, text)
            projects.extend(matches)

        return list(set(projects))

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities using spaCy"""
        if not NLP_AVAILABLE:
            return {}

        doc = nlp(text)
        entities = defaultdict(list)

        for ent in doc.ents:
            entities[ent.label_].append(ent.text)

        return {k: list(set(v)) for k, v in entities.items()}

    def _generate_summary(self, text: str) -> str:
        """Generate a brief summary of the document"""
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

        if len(sentences) <= 3:
            return text[:200] + "..." if len(text) > 200 else text

        # Return first few sentences as summary
        summary = ". ".join(sentences[:3])
        return summary + "..." if len(summary) > 200 else summary

    def _extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract document metadata"""
        return {
            "word_count": len(text.split()),
            "character_count": len(text),
            "line_count": len(text.split("\n")),
            "has_numbers": bool(re.search(r"\d", text)),
            "has_emails": bool(re.search(self.financial_patterns["email"], text)),
            "has_phones": bool(re.search(self.financial_patterns["phone"], text)),
            "has_urls": bool(re.search(self.financial_patterns["url"], text)),
        }

    def _get_context(self, text: str, match: str, context_length: int = 50) -> str:
        """Get context around a match"""
        start = max(0, text.find(match) - context_length)
        end = min(len(text), text.find(match) + len(match) + context_length)
        return text[start:end].strip()

    def _store_analysis(self, doc_id: str, analysis: Dict[str, Any]) -> Path:
        """Store analysis results"""
        analysis_file = self.processed_dir / f"{doc_id}_analysis.json"
        with open(analysis_file, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        return analysis_file

    def get_document_content(self, doc_id: str) -> Optional[str]:
        """Get stored text content for a document"""
        text_file = self.processed_dir / f"{doc_id}.txt"
        if text_file.exists():
            with open(text_file, "r", encoding="utf-8") as f:
                return f.read()
        return None

    def get_document_analysis(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get stored analysis for a document"""
        analysis_file = self.processed_dir / f"{doc_id}_analysis.json"
        if analysis_file.exists():
            with open(analysis_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def list_documents(self) -> List[Dict[str, Any]]:
        """List all processed documents"""
        documents = []

        for analysis_file in self.processed_dir.glob("*_analysis.json"):
            doc_id = analysis_file.stem.replace("_analysis", "")

            try:
                analysis = self.get_document_analysis(doc_id)
                if analysis:
                    documents.append(
                        {
                            "doc_id": doc_id,
                            "type": analysis.get("type", "unknown"),
                            "summary": analysis.get("summary", ""),
                            "keywords": analysis.get("keywords", []),
                            "processed_at": analysis.get("processed_at", ""),
                            "word_count": analysis.get("metadata", {}).get(
                                "word_count", 0
                            ),
                        }
                    )
            except Exception as e:
                logging.error(f"Error reading analysis for {doc_id}: {e}")

        return sorted(documents, key=lambda x: x["processed_at"], reverse=True)
