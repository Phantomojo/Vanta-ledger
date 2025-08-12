#!/usr/bin/env python3
"""
Enhanced Document Management Service
Advanced document management with tagging, categorization, search, and archiving
"""

import hashlib
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

import redis
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from ..config import settings
from ..models.document_models import (
    DocumentCategory,
    DocumentSearchCriteria,
    DocumentStatus,
    DocumentTag,
    DocumentType,
    DocumentVersion,
    EnhancedDocument,
)
from ..utils.validation import input_validator
from .local_llm_service import local_llm_service

logger = logging.getLogger(__name__)


class EnhancedDocumentService:
    """Enhanced document management service with advanced features"""

    def __init__(self):
        # Database connections
        self.mongo_client = MongoClient(settings.MONGO_URI)
        self.db: Database = self.mongo_client[settings.DATABASE_NAME]
        self.redis_client = redis.Redis.from_url(
            settings.REDIS_URI, decode_responses=True
        )

        # Collections
        self.documents: Collection = self.db.documents
        self.tags: Collection = self.db.document_tags
        self.categories: Collection = self.db.document_categories
        self.search_index: Collection = self.db.document_search_index

        # Create indexes for performance
        self._create_indexes()

        # Initialize default categories and tags
        self._initialize_defaults()

    def _create_indexes(self):
        """Create database indexes for optimal performance"""
        try:
            # Document indexes
            self.documents.create_index([("created_at", -1)])
            self.documents.create_index([("status", 1)])
            self.documents.create_index([("metadata.document_type", 1)])
            self.documents.create_index([("metadata.category_id", 1)])
            self.documents.create_index([("metadata.tags", 1)])
            self.documents.create_index([("created_by", 1)])

            # Search index
            self.search_index.create_index([("title", "text"), ("content", "text")])
            self.search_index.create_index([("document_type", 1)])
            self.search_index.create_index([("tags", 1)])
            self.search_index.create_index([("created_at", -1)])

            # Tags and categories
            self.tags.create_index([("name", 1)], unique=True)
            self.categories.create_index([("name", 1)])

            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {str(e)}")

    def _initialize_defaults(self):
        """Initialize default categories and tags"""
        try:
            # Default categories
            default_categories = [
                {
                    "name": "Financial Documents",
                    "description": "Invoices, receipts, financial statements",
                    "color": "#10B981",
                    "icon": "dollar-sign",
                    "is_system": True,
                },
                {
                    "name": "Legal Documents",
                    "description": "Contracts, agreements, legal correspondence",
                    "color": "#EF4444",
                    "icon": "gavel",
                    "is_system": True,
                },
                {
                    "name": "HR Documents",
                    "description": "Employee records, policies, contracts",
                    "color": "#8B5CF6",
                    "icon": "users",
                    "is_system": True,
                },
            ]

            for cat_data in default_categories:
                if not self.categories.find_one({"name": cat_data["name"]}):
                    category = DocumentCategory(
                        name=cat_data["name"],
                        description=cat_data["description"],
                        color=cat_data["color"],
                        icon=cat_data["icon"],
                        is_system=True,
                        created_by=uuid4(),  # System user
                    )
                    self.categories.insert_one(category.dict())

            # Default tags
            default_tags = [
                {"name": "Important", "color": "#EF4444", "is_system": True},
                {"name": "Urgent", "color": "#F59E0B", "is_system": True},
                {"name": "Reviewed", "color": "#10B981", "is_system": True},
                {"name": "Pending", "color": "#6B7280", "is_system": True},
            ]

            for tag_data in default_tags:
                if not self.tags.find_one({"name": tag_data["name"]}):
                    tag = DocumentTag(
                        name=tag_data["name"],
                        color=tag_data["color"],
                        is_system=True,
                        created_by=uuid4(),  # System user
                    )
                    self.tags.insert_one(tag.dict())

            logger.info("Default categories and tags initialized")
        except Exception as e:
            logger.error(f"Error initializing defaults: {str(e)}")

    def create_document(
        self, document_data: Dict[str, Any], user_id: UUID
    ) -> EnhancedDocument:
        """Create a new enhanced document"""
        try:
            # Validate input
            document_data = input_validator.validate_json_payload(document_data)

            # Create enhanced document
            document = EnhancedDocument(
                original_filename=document_data["original_filename"],
                secure_filename=document_data["secure_filename"],
                file_path=document_data["file_path"],
                file_size=document_data["file_size"],
                file_extension=document_data["file_extension"],
                mime_type=document_data["mime_type"],
                checksum=document_data["checksum"],
                created_by=user_id,
            )

            # Set metadata if provided
            if "metadata" in document_data:
                document.metadata = DocumentMetadata(**document_data["metadata"])

            # Add initial version
            initial_version = DocumentVersion(
                document_id=document.id,
                version_number=1,
                file_path=document.file_path,
                file_size=document.file_size,
                checksum=document.checksum,
                created_by=user_id,
            )
            document.versions.append(initial_version)

            # Save to database
            self.documents.insert_one(document.dict())

            # Add to search index
            self._update_search_index(document)

            logger.info(f"Document created: {document.id}")
            return document

        except Exception as e:
            logger.error(f"Error creating document: {str(e)}")
            raise

    def get_document(
        self, document_id: UUID, user_id: UUID
    ) -> Optional[EnhancedDocument]:
        """Get document by ID with access tracking"""
        try:
            # Validate document ID
            document_id = input_validator.validate_uuid(document_id, "document_id")

            # Get document
            doc_data = self.documents.find_one({"_id": str(document_id)})
            if not doc_data:
                return None

            document = EnhancedDocument(**doc_data)

            # Record access
            document.record_access(user_id)
            self.documents.update_one(
                {"_id": str(document_id)},
                {
                    "$set": {
                        "accessed_by": document.accessed_by,
                        "accessed_at": document.accessed_at,
                    }
                },
            )

            return document

        except Exception as e:
            logger.error(f"Error getting document: {str(e)}")
            raise

    def search_documents(
        self, criteria: DocumentSearchCriteria, user_id: UUID
    ) -> Tuple[List[EnhancedDocument], int]:
        """Advanced document search with multiple criteria"""
        try:
            # Build MongoDB query
            query = {}

            # Text search
            if criteria.full_text:
                # Use text search index
                text_results = list(
                    self.search_index.find(
                        {"$text": {"$search": criteria.full_text}}, {"_id": 1}
                    )
                )
                doc_ids = [r["_id"] for r in text_results]
                if doc_ids:
                    query["_id"] = {"$in": doc_ids}
                else:
                    # No text matches, return empty
                    return [], 0

            # Title and description search
            if criteria.title:
                query["metadata.title"] = {"$regex": criteria.title, "$options": "i"}
            if criteria.description:
                query["metadata.description"] = {
                    "$regex": criteria.description,
                    "$options": "i",
                }

            # Classification filters
            if criteria.document_types:
                query["metadata.document_type"] = {
                    "$in": [dt.value for dt in criteria.document_types]
                }
            if criteria.tags:
                query["metadata.tags"] = {
                    "$in": [str(tag_id) for tag_id in criteria.tags]
                }
            if criteria.category_id:
                query["metadata.category_id"] = str(criteria.category_id)

            # Date range filters
            if criteria.created_after:
                query["created_at"] = {"$gte": criteria.created_after}
            if criteria.created_before:
                if "created_at" in query:
                    query["created_at"]["$lte"] = criteria.created_before
                else:
                    query["created_at"] = {"$lte": criteria.created_before}

            # Status and priority filters
            if criteria.status:
                query["status"] = {"$in": [s.value for s in criteria.status]}
            if criteria.priority:
                query["metadata.priority"] = {
                    "$in": [p.value for p in criteria.priority]
                }

            # Get total count
            total_count = self.documents.count_documents(query)

            # Build sort
            sort_field = criteria.sort_by
            if criteria.sort_by == "modified_at":
                sort_field = "modified_at"
            elif criteria.sort_by == "title":
                sort_field = "metadata.title"
            elif criteria.sort_by == "priority":
                sort_field = "metadata.priority"
            elif criteria.sort_by == "status":
                sort_field = "status"
            elif criteria.sort_by == "document_type":
                sort_field = "metadata.document_type"

            sort_order = -1 if criteria.sort_order == "desc" else 1

            # Execute query with pagination
            skip = (criteria.page - 1) * criteria.limit
            cursor = (
                self.documents.find(query)
                .sort(sort_field, sort_order)
                .skip(skip)
                .limit(criteria.limit)
            )

            # Convert to EnhancedDocument objects
            documents = []
            for doc_data in cursor:
                documents.append(EnhancedDocument(**doc_data))

            return documents, total_count

        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            raise

    def create_tag(self, tag_data: Dict[str, Any], user_id: UUID) -> DocumentTag:
        """Create a new document tag"""
        try:
            # Validate input
            tag_data = input_validator.validate_json_payload(
                tag_data, required_fields=["name"]
            )

            # Check if tag already exists
            existing_tag = self.tags.find_one({"name": tag_data["name"]})
            if existing_tag:
                raise ValueError(f"Tag '{tag_data['name']}' already exists")

            # Create tag
            tag = DocumentTag(
                name=tag_data["name"],
                color=tag_data.get("color", "#3B82F6"),
                description=tag_data.get("description"),
                created_by=user_id,
            )

            # Save to database
            self.tags.insert_one(tag.dict())

            logger.info(f"Tag created: {tag.name}")
            return tag

        except Exception as e:
            logger.error(f"Error creating tag: {str(e)}")
            raise

    def get_tags(self, include_system: bool = True) -> List[DocumentTag]:
        """Get all document tags"""
        try:
            query = {}
            if not include_system:
                query["is_system"] = False

            cursor = self.tags.find(query).sort("name", 1)
            return [DocumentTag(**tag_data) for tag_data in cursor]

        except Exception as e:
            logger.error(f"Error getting tags: {str(e)}")
            raise

    def create_category(
        self, category_data: Dict[str, Any], user_id: UUID
    ) -> DocumentCategory:
        """Create a new document category"""
        try:
            # Validate input
            category_data = input_validator.validate_json_payload(
                category_data, required_fields=["name"]
            )

            # Check if category already exists
            existing_category = self.categories.find_one(
                {"name": category_data["name"]}
            )
            if existing_category:
                raise ValueError(f"Category '{category_data['name']}' already exists")

            # Create category
            category = DocumentCategory(
                name=category_data["name"],
                description=category_data.get("description"),
                parent_category_id=category_data.get("parent_category_id"),
                color=category_data.get("color", "#6B7280"),
                icon=category_data.get("icon"),
                created_by=user_id,
            )

            # Save to database
            self.categories.insert_one(category.dict())

            logger.info(f"Category created: {category.name}")
            return category

        except Exception as e:
            logger.error(f"Error creating category: {str(e)}")
            raise

    def get_categories(self, include_system: bool = True) -> List[DocumentCategory]:
        """Get all document categories"""
        try:
            query = {}
            if not include_system:
                query["is_system"] = False

            cursor = self.categories.find(query).sort("name", 1)
            return [DocumentCategory(**cat_data) for cat_data in cursor]

        except Exception as e:
            logger.error(f"Error getting categories: {str(e)}")
            raise

    def _update_search_index(self, document: EnhancedDocument):
        """Update document in search index"""
        try:
            search_data = document.to_search_index()

            # Update or insert in search index
            self.search_index.update_one(
                {"id": search_data["id"]}, {"$set": search_data}, upsert=True
            )

        except Exception as e:
            logger.error(f"Error updating search index: {str(e)}")

    def get_document_statistics(self, user_id: UUID) -> Dict[str, Any]:
        """Get document statistics for dashboard"""
        try:
            stats = {}

            # Total documents
            stats["total_documents"] = self.documents.count_documents({})

            # Documents by status
            stats["by_status"] = {}
            for status in DocumentStatus:
                count = self.documents.count_documents({"status": status.value})
                stats["by_status"][status.value] = count

            # Documents by type
            stats["by_type"] = {}
            for doc_type in DocumentType:
                count = self.documents.count_documents(
                    {"metadata.document_type": doc_type.value}
                )
                stats["by_type"][doc_type.value] = count

            # Recent activity
            recent_docs = list(self.documents.find().sort("created_at", -1).limit(10))
            stats["recent_documents"] = len(recent_docs)

            # Storage usage
            pipeline = [{"$group": {"_id": None, "total_size": {"$sum": "$file_size"}}}]
            size_result = list(self.documents.aggregate(pipeline))
            stats["total_storage_bytes"] = (
                size_result[0]["total_size"] if size_result else 0
            )

            return stats

        except Exception as e:
            logger.error(f"Error getting document statistics: {str(e)}")
            raise

    async def create_document_with_llm(
        self, document_data: Dict[str, Any], user_id: UUID, company_id: UUID
    ) -> EnhancedDocument:
        """Create document with LLM enhancement for company-specific processing"""
        try:
            # Create basic document first
            document = self.create_document(document_data, user_id)

            # Add company context
            document.company_id = str(company_id)

            # Process with local LLM if text is available
            if document.extracted_text:
                try:
                    # Process document with company context
                    llm_results = await local_llm_service.process_document_for_company(
                        document, company_id
                    )

                    # Update document with LLM insights
                    if llm_results:
                        # Update classification
                        if "classification" in llm_results:
                            document.metadata["llm_classification"] = llm_results[
                                "classification"
                            ]
                            document.metadata["document_type"] = llm_results[
                                "classification"
                            ].get("type", "unknown")

                        # Update summary
                        if "summary" in llm_results:
                            document.metadata["llm_summary"] = llm_results["summary"]

                        # Update entities
                        if "entities" in llm_results:
                            document.metadata["llm_entities"] = llm_results["entities"]

                        # Update financial data
                        if "financial_data" in llm_results:
                            document.metadata["llm_financial_data"] = llm_results[
                                "financial_data"
                            ]

                        # Update document understanding
                        if "document_understanding" in llm_results:
                            document.metadata["llm_document_understanding"] = (
                                llm_results["document_understanding"]
                            )

                        # Add LLM processing timestamp
                        document.metadata["llm_processed_at"] = (
                            datetime.utcnow().isoformat()
                        )

                        # Update document in database
                        self.documents.update_one(
                            {"_id": document.id},
                            {
                                "$set": {
                                    "metadata": document.metadata,
                                    "company_id": str(company_id),
                                }
                            },
                        )

                        logger.info(
                            f"Document {document.id} processed with LLM for company {company_id}"
                        )

                except Exception as e:
                    logger.error(f"Error processing document with LLM: {str(e)}")
                    # Continue without LLM processing - document is still created

            return document

        except Exception as e:
            logger.error(f"Error creating document with LLM: {str(e)}")
            raise


# Global instance
enhanced_document_service = EnhancedDocumentService()
