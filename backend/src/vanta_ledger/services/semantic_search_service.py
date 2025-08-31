import os
#!/usr/bin/env python3
"""
Semantic Search Service
Inspired by Paperless-AI - Intelligent document search and AI-assisted tagging
"""

import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

import redis
from pymongo.collection import Collection
from pymongo.database import Database

# Optional ML imports for semantic search
try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    import torch
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False
    logging.warning("Semantic search libraries not available - using basic search")

try:
    from transformers import pipeline
    TAGGING_AVAILABLE = True
except ImportError:
    TAGGING_AVAILABLE = False
    logging.warning("AI tagging libraries not available - using basic tagging")

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


class SemanticSearchService:
    """Semantic search and AI-assisted tagging service inspired by Paperless-AI"""

    def __init__(self):
        # Database connections
        self.mongo_client = get_mongo_client()
        self.db: Database = self.mongo_client[settings.DATABASE_NAME]
        try:
            self.redis_client = redis.Redis.from_url(
                settings.REDIS_URI, decode_responses=True
            )
        except Exception:
            class _NoopRedis:
                def get(self, *a, **k): return None
                def setex(self, *a, **k): return None
            self.redis_client = _NoopRedis()
            logger.warning("Redis unavailable; caching disabled for semantic search")

        # Collections
        self.documents: Collection = self.db.documents
        self.document_embeddings: Collection = self.db.document_embeddings
        self.search_index: Collection = self.db.search_index
        self.ai_tags: Collection = self.db.ai_tags
        self.search_history: Collection = self.db.search_history

        # Initialize ML models if available
        self.embedding_model = None
        self.tagging_pipeline = None
        self._initialize_ml_models()

        # Create indexes
        self._create_indexes()

        logger.info(f"Semantic Search Service initialized. Semantic Available: {SEMANTIC_AVAILABLE}, Tagging Available: {TAGGING_AVAILABLE}")

    def _initialize_ml_models(self):
        """Initialize ML models for semantic search and tagging"""
        if not SEMANTIC_AVAILABLE:
            logger.warning("Semantic search libraries not available - using basic search")
            return

        try:
            # Initialize sentence transformer for embeddings
            model_name = "all-MiniLM-L6-v2"  # Lightweight but effective
            self.embedding_model = SentenceTransformer(model_name)
            
            # Move to GPU if available
            if torch.cuda.is_available():
                self.embedding_model = self.embedding_model.to('cuda')
                logger.info("Embedding model loaded on GPU")
            else:
                logger.info("Embedding model loaded on CPU")

            # Initialize tagging pipeline
            if TAGGING_AVAILABLE:
                self.tagging_pipeline = pipeline(
                    "text-classification",
                    model="facebook/bart-large-mnli",
                    device=0 if torch.cuda.is_available() else -1
                )
                logger.info("Tagging pipeline initialized")

            logger.info("ML models initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing ML models: {str(e)}")
            self.embedding_model = None
            self.tagging_pipeline = None

    def _create_indexes(self):
        """Create database indexes for optimal performance"""
        try:
            # Document embeddings indexes
            self.document_embeddings.create_index([("document_id", 1)])
            self.document_embeddings.create_index([("embedding_type", 1)])
            self.document_embeddings.create_index([("created_at", -1)])

            # Search index indexes
            self.search_index.create_index([("search_term", "text")])
            self.search_index.create_index([("document_id", 1)])
            self.search_index.create_index([("relevance_score", -1)])

            # AI tags indexes
            self.ai_tags.create_index([("document_id", 1)])
            self.ai_tags.create_index([("tag_type", 1)])
            self.ai_tags.create_index([("confidence_score", -1)])

            # Search history indexes
            self.search_history.create_index([("user_id", 1)])
            self.search_history.create_index([("search_query", 1)])
            self.search_history.create_index([("created_at", -1)])

            logger.info("Semantic search service indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {str(e)}")

    async def semantic_search(
        self,
        query: str,
        company_id: UUID,
        user_id: UUID,
        filters: Dict[str, Any] = None,
        limit: int = 20,
        threshold: float = 0.3
    ) -> Dict[str, Any]:
        """
        Perform semantic search on documents
        
        Args:
            query: Search query
            company_id: Company ID for filtering
            user_id: User ID for search history
            filters: Additional filters (date range, document type, etc.)
            limit: Maximum number of results
            threshold: Minimum similarity threshold
            
        Returns:
            Dictionary containing search results
        """
        try:
            # Log search query
            await self._log_search_query(query, user_id, company_id)

            # Get documents for the company
            documents = await self._get_company_documents(company_id, filters)
            
            if not documents:
                return {
                    "query": query,
                    "results": [],
                    "total_found": 0,
                    "search_time": 0.0,
                    "filters_applied": filters or {}
                }

            # Perform semantic search
            if self.embedding_model and SEMANTIC_AVAILABLE:
                results = await self._semantic_search_with_embeddings(query, documents, limit, threshold)
            else:
                results = await self._basic_text_search(query, documents, limit)

            # Update search index
            await self._update_search_index(query, results)

            return {
                "query": query,
                "results": results,
                "total_found": len(results),
                "search_time": 0.0,  # TODO: Add actual timing
                "filters_applied": filters or {},
                "search_method": "semantic" if self.embedding_model else "basic"
            }

        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            return {
                "query": query,
                "results": [],
                "total_found": 0,
                "search_time": 0.0,
                "error": str(e)
            }

    async def _semantic_search_with_embeddings(
        self,
        query: str,
        documents: List[Dict],
        limit: int,
        threshold: float
    ) -> List[Dict]:
        """Perform semantic search using embeddings"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])[0]
            
            # Get or generate document embeddings
            document_embeddings = []
            for doc in documents:
                embedding = await self._get_document_embedding(doc["id"])
                if embedding is not None:
                    document_embeddings.append({
                        "document": doc,
                        "embedding": embedding
                    })

            if not document_embeddings:
                return []

            # Calculate similarities
            similarities = []
            for doc_emb in document_embeddings:
                similarity = cosine_similarity(
                    [query_embedding], 
                    [doc_emb["embedding"]]
                )[0][0]
                
                if similarity >= threshold:
                    similarities.append({
                        "document": doc_emb["document"],
                        "similarity": float(similarity),
                        "relevance_score": float(similarity)
                    })

            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            return similarities[:limit]

        except Exception as e:
            logger.error(f"Error in semantic search with embeddings: {str(e)}")
            return []

    async def _basic_text_search(
        self,
        query: str,
        documents: List[Dict],
        limit: int
    ) -> List[Dict]:
        """Perform basic text search"""
        try:
            query_terms = query.lower().split()
            results = []

            for doc in documents:
                # Search in document content and metadata
                searchable_text = f"{doc.get('content', '')} {doc.get('title', '')} {doc.get('description', '')}".lower()
                
                # Calculate simple relevance score
                matches = sum(1 for term in query_terms if term in searchable_text)
                if matches > 0:
                    relevance_score = matches / len(query_terms)
                    results.append({
                        "document": doc,
                        "similarity": relevance_score,
                        "relevance_score": relevance_score,
                        "matches": matches
                    })

            # Sort by relevance and return top results
            results.sort(key=lambda x: x["relevance_score"], reverse=True)
            return results[:limit]

        except Exception as e:
            logger.error(f"Error in basic text search: {str(e)}")
            return []

    async def _get_document_embedding(self, document_id: UUID) -> Optional[List[float]]:
        """Get or generate document embedding"""
        try:
            # Check if embedding exists in cache
            cache_key = f"doc_embedding:{document_id}"
            cached_embedding = self.redis_client.get(cache_key)
            
            if cached_embedding:
                return json.loads(cached_embedding)

            # Check database
            embedding_doc = self.document_embeddings.find_one({
                "document_id": str(document_id),
                "embedding_type": "semantic"
            })

            if embedding_doc:
                embedding = embedding_doc["embedding"]
                # Cache for 24 hours
                self.redis_client.setex(cache_key, 86400, json.dumps(embedding))
                return embedding

            # Generate new embedding
            if self.embedding_model:
                document = await self._get_document_content(document_id)
                if document:
                    text_content = f"{document.get('title', '')} {document.get('content', '')} {document.get('description', '')}"
                    embedding = self.embedding_model.encode([text_content])[0].tolist()
                    
                    # Save to database
                    self.document_embeddings.insert_one({
                        "document_id": str(document_id),
                        "embedding_type": "semantic",
                        "embedding": embedding,
                        "created_at": datetime.utcnow()
                    })
                    
                    # Cache
                    self.redis_client.setex(cache_key, 86400, json.dumps(embedding))
                    return embedding

            return None

        except Exception as e:
            logger.error(f"Error getting document embedding: {str(e)}")
            return None

    async def _get_document_content(self, document_id: UUID) -> Optional[Dict]:
        """Get document content for embedding generation"""
        try:
            doc = self.documents.find_one({"_id": str(document_id)})
            return doc
        except Exception as e:
            logger.error(f"Error getting document content: {str(e)}")
            return None

    async def _get_company_documents(self, company_id: UUID, filters: Dict = None) -> List[Dict]:
        """Get documents for a company with optional filters"""
        try:
            query = {"company_id": str(company_id)}
            
            if filters:
                if filters.get("date_from"):
                    query["created_at"] = {"$gte": filters["date_from"]}
                if filters.get("date_to"):
                    if "created_at" in query:
                        query["created_at"]["$lte"] = filters["date_to"]
                    else:
                        query["created_at"] = {"$lte": filters["date_to"]}
                if filters.get("document_type"):
                    query["document_type"] = filters["document_type"]
                if filters.get("status"):
                    query["status"] = filters["status"]

            documents = list(self.documents.find(query))
            return documents

        except Exception as e:
            logger.error(f"Error getting company documents: {str(e)}")
            return []

    async def generate_ai_tags(self, document_id: UUID) -> Dict[str, Any]:
        """
        Generate AI-assisted tags for a document
        
        Args:
            document_id: Document ID to tag
            
        Returns:
            Dictionary containing generated tags
        """
        try:
            # Get document content
            document = await self._get_document_content(document_id)
            if not document:
                return {"error": "Document not found"}

            # Generate tags using AI
            if self.tagging_pipeline and TAGGING_AVAILABLE:
                tags = await self._generate_ai_tags_with_pipeline(document)
            else:
                tags = await self._generate_basic_tags(document)

            # Save tags to database
            await self._save_ai_tags(document_id, tags)

            return {
                "document_id": str(document_id),
                "tags": tags,
                "generation_method": "ai" if self.tagging_pipeline else "basic",
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error generating AI tags: {str(e)}")
            return {"error": str(e)}

    async def _generate_ai_tags_with_pipeline(self, document: Dict) -> List[Dict]:
        """Generate tags using AI pipeline"""
        try:
            text_content = f"{document.get('title', '')} {document.get('content', '')} {document.get('description', '')}"
            
            # Define candidate labels for classification
            candidate_labels = [
                "invoice", "receipt", "contract", "report", "statement",
                "financial", "legal", "tax", "expense", "income",
                "urgent", "important", "confidential", "draft", "final",
                "approved", "pending", "rejected", "archived", "active"
            ]

            # Generate tags using zero-shot classification
            results = self.tagging_pipeline(text_content, candidate_labels, multi_label=True)
            
            tags = []
            for result in results:
                if result["score"] > 0.5:  # Confidence threshold
                    tags.append({
                        "tag": result["label"],
                        "confidence": float(result["score"]),
                        "tag_type": "ai_generated"
                    })

            return tags

        except Exception as e:
            logger.error(f"Error generating AI tags with pipeline: {str(e)}")
            return []

    async def _generate_basic_tags(self, document: Dict) -> List[Dict]:
        """Generate basic tags using rule-based approach"""
        try:
            text_content = f"{document.get('title', '')} {document.get('content', '')} {document.get('description', '')}".lower()
            
            # Define tag patterns
            tag_patterns = {
                "invoice": r"invoice|bill|payment|amount|total",
                "receipt": r"receipt|purchase|transaction|paid",
                "contract": r"contract|agreement|terms|conditions|signature",
                "financial": r"financial|money|currency|dollar|euro|amount",
                "urgent": r"urgent|asap|immediate|priority",
                "confidential": r"confidential|private|secret|restricted"
            }

            tags = []
            for tag, pattern in tag_patterns.items():
                if re.search(pattern, text_content):
                    tags.append({
                        "tag": tag,
                        "confidence": 0.7,  # Default confidence for rule-based
                        "tag_type": "rule_based"
                    })

            return tags

        except Exception as e:
            logger.error(f"Error generating basic tags: {str(e)}")
            return []

    async def _save_ai_tags(self, document_id: UUID, tags: List[Dict]):
        """Save AI-generated tags to database"""
        try:
            # Remove existing tags for this document
            self.ai_tags.delete_many({"document_id": str(document_id)})
            
            # Insert new tags
            for tag in tags:
                tag_data = {
                    "document_id": str(document_id),
                    "tag": tag["tag"],
                    "tag_type": tag["tag_type"],
                    "confidence_score": tag["confidence"],
                    "created_at": datetime.utcnow()
                }
                self.ai_tags.insert_one(tag_data)

        except Exception as e:
            logger.error(f"Error saving AI tags: {str(e)}")

    async def _log_search_query(self, query: str, user_id: UUID, company_id: UUID):
        """Log search query for analytics"""
        try:
            self.search_history.insert_one({
                "user_id": str(user_id),
                "company_id": str(company_id),
                "search_query": query,
                "created_at": datetime.utcnow()
            })
        except Exception as e:
            logger.error(f"Error logging search query: {str(e)}")

    async def _update_search_index(self, query: str, results: List[Dict]):
        """Update search index with query and results"""
        try:
            for result in results:
                self.search_index.insert_one({
                    "search_term": query,
                    "document_id": result["document"]["id"],
                    "relevance_score": result["relevance_score"],
                    "created_at": datetime.utcnow()
                })
        except Exception as e:
            logger.error(f"Error updating search index: {str(e)}")

    async def get_search_suggestions(self, partial_query: str, company_id: UUID) -> List[str]:
        """Get search suggestions based on partial query"""
        try:
            # Get recent searches for the company
            recent_searches = self.search_history.find({
                "company_id": str(company_id),
                "search_query": {"$regex": f"^{partial_query}", "$options": "i"}
            }).distinct("search_query")
            
            return list(recent_searches)[:5]  # Return top 5 suggestions

        except Exception as e:
            logger.error(f"Error getting search suggestions: {str(e)}")
            return []

    async def get_popular_searches(self, company_id: UUID, days: int = 30) -> List[Dict]:
        """Get popular search queries for a company"""
        try:
            from datetime import timedelta
            
            date_from = datetime.utcnow() - timedelta(days=days)
            
            pipeline = [
                {"$match": {
                    "company_id": str(company_id),
                    "created_at": {"$gte": date_from}
                }},
                {"$group": {
                    "_id": "$search_query",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            
            results = list(self.search_history.aggregate(pipeline))
            return [{"query": r["_id"], "count": r["count"]} for r in results]

        except Exception as e:
            logger.error(f"Error getting popular searches: {str(e)}")
            return []

    def get_search_capabilities(self) -> Dict[str, Any]:
        """Get current search capabilities"""
        return {
            "semantic_available": SEMANTIC_AVAILABLE,
            "tagging_available": TAGGING_AVAILABLE,
            "embedding_model_loaded": self.embedding_model is not None,
            "tagging_pipeline_loaded": self.tagging_pipeline is not None,
            "gpu_available": torch.cuda.is_available() if SEMANTIC_AVAILABLE else False,
            "search_features": [
                "semantic_search",
                "ai_tagging",
                "search_suggestions",
                "popular_searches",
                "search_analytics"
            ]
        }


# Global instance
semantic_search_service = SemanticSearchService()
