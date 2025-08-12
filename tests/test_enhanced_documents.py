#!/usr/bin/env python3
"""
Enhanced Document Management Tests
Tests for advanced document management features
"""

import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.models.document_models import (
    DocumentCategory,
    DocumentMetadata,
    DocumentPriority,
    DocumentSearchCriteria,
    DocumentStatus,
    DocumentTag,
    DocumentType,
    EnhancedDocument,
)
from backend.app.services.enhanced_document_service import EnhancedDocumentService

client = TestClient(app)


class TestEnhancedDocumentManagement:
    """Test enhanced document management features"""

    @pytest.fixture
    def sample_document_data(self):
        """Sample document data for testing"""
        return {
            "original_filename": "test_invoice.pdf",
            "secure_filename": "user123_abc123_uuid.pdf",
            "file_path": "/tmp/test_invoice.pdf",
            "file_size": 1024000,
            "file_extension": ".pdf",
            "mime_type": "application/pdf",
            "checksum": "abc123def456",
            "metadata": {
                "title": "Test Invoice",
                "description": "Sample invoice for testing",
                "document_type": "invoice",
                "priority": "medium",
                "keywords": ["invoice", "test", "sample"],
            },
        }

    @pytest.fixture
    def sample_tag_data(self):
        """Sample tag data for testing"""
        return {
            "name": "Test Tag",
            "color": "#FF5733",
            "description": "A test tag for testing purposes",
        }

    @pytest.fixture
    def sample_category_data(self):
        """Sample category data for testing"""
        return {
            "name": "Test Category",
            "description": "A test category for testing purposes",
            "color": "#33FF57",
            "icon": "test-icon",
        }

    def test_create_enhanced_document(self, sample_document_data):
        """Test creating an enhanced document"""
        # Mock authentication
        with patch(
            "backend.app.routes.enhanced_documents.get_current_user"
        ) as mock_user:
            mock_user.return_value = Mock(id=str(uuid.uuid4()))

            # Mock document service
            with patch(
                "backend.app.routes.enhanced_documents.enhanced_document_service"
            ) as mock_service:
                mock_document = EnhancedDocument(
                    id=uuid.uuid4(),
                    original_filename=sample_document_data["original_filename"],
                    secure_filename=sample_document_data["secure_filename"],
                    file_path=sample_document_data["file_path"],
                    file_size=sample_document_data["file_size"],
                    file_extension=sample_document_data["file_extension"],
                    mime_type=sample_document_data["mime_type"],
                    checksum=sample_document_data["checksum"],
                    created_by=mock_user.return_value.id,
                )
                mock_service.create_document.return_value = mock_document

                response = client.post("/api/v2/documents/", json=sample_document_data)

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "document" in data
                assert data["message"] == "Document created successfully"

    def test_get_enhanced_document(self):
        """Test retrieving an enhanced document"""
        document_id = str(uuid.uuid4())

        # Mock authentication
        with patch(
            "backend.app.routes.enhanced_documents.get_current_user"
        ) as mock_user:
            mock_user.return_value = Mock(id=str(uuid.uuid4()))

            # Mock document service
            with patch(
                "backend.app.routes.enhanced_documents.enhanced_document_service"
            ) as mock_service:
                mock_document = EnhancedDocument(
                    id=uuid.UUID(document_id),
                    original_filename="test.pdf",
                    secure_filename="secure_test.pdf",
                    file_path="/tmp/test.pdf",
                    file_size=1024,
                    file_extension=".pdf",
                    mime_type="application/pdf",
                    checksum="test123",
                    created_by=mock_user.return_value.id,
                )
                mock_service.get_document.return_value = mock_document

                response = client.get(f"/api/v2/documents/{document_id}")

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "document" in data
                assert data["document"]["id"] == document_id

    def test_list_documents_with_filters(self):
        """Test listing documents with various filters"""
        # Mock authentication
        with patch(
            "backend.app.routes.enhanced_documents.get_current_user"
        ) as mock_user:
            mock_user.return_value = Mock(id=str(uuid.uuid4()))

            # Mock document service
            with patch(
                "backend.app.routes.enhanced_documents.enhanced_document_service"
            ) as mock_service:
                mock_documents = [
                    EnhancedDocument(
                        id=uuid.uuid4(),
                        original_filename="doc1.pdf",
                        secure_filename="secure_doc1.pdf",
                        file_path="/tmp/doc1.pdf",
                        file_size=1024,
                        file_extension=".pdf",
                        mime_type="application/pdf",
                        checksum="test123",
                        created_by=mock_user.return_value.id,
                    ),
                    EnhancedDocument(
                        id=uuid.uuid4(),
                        original_filename="doc2.pdf",
                        secure_filename="secure_doc2.pdf",
                        file_path="/tmp/doc2.pdf",
                        file_size=2048,
                        file_extension=".pdf",
                        mime_type="application/pdf",
                        checksum="test456",
                        created_by=mock_user.return_value.id,
                    ),
                ]
                mock_service.search_documents.return_value = (mock_documents, 2)

                # Test with various filters
                response = client.get(
                    "/api/v2/documents/",
                    params={
                        "page": 1,
                        "limit": 10,
                        "document_type": "invoice",
                        "status": "processed",
                        "sort_by": "created_at",
                        "sort_order": "desc",
                    },
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "documents" in data
                assert "pagination" in data
                assert len(data["documents"]) == 2

    def test_advanced_search(self):
        """Test advanced document search"""
        # Mock authentication
        with patch(
            "backend.app.routes.enhanced_documents.get_current_user"
        ) as mock_user:
            mock_user.return_value = Mock(id=str(uuid.uuid4()))

            # Mock document service
            with patch(
                "backend.app.routes.enhanced_documents.enhanced_document_service"
            ) as mock_service:
                mock_documents = [
                    EnhancedDocument(
                        id=uuid.uuid4(),
                        original_filename="search_result.pdf",
                        secure_filename="secure_search.pdf",
                        file_path="/tmp/search.pdf",
                        file_size=1024,
                        file_extension=".pdf",
                        mime_type="application/pdf",
                        checksum="search123",
                        created_by=mock_user.return_value.id,
                    )
                ]
                mock_service.search_documents.return_value = (mock_documents, 1)

                search_criteria = {
                    "full_text": "invoice payment",
                    "document_types": ["invoice"],
                    "created_after": (
                        datetime.utcnow() - timedelta(days=30)
                    ).isoformat(),
                    "page": 1,
                    "limit": 20,
                }

                response = client.post("/api/v2/documents/search", json=search_criteria)

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "documents" in data
                assert "pagination" in data

    def test_create_tag(self, sample_tag_data):
        """Test creating a document tag"""
        # Mock authentication
        with patch(
            "backend.app.routes.enhanced_documents.get_current_user"
        ) as mock_user:
            mock_user.return_value = Mock(id=str(uuid.uuid4()))

            # Mock document service
            with patch(
                "backend.app.routes.enhanced_documents.enhanced_document_service"
            ) as mock_service:
                mock_tag = DocumentTag(
                    id=uuid.uuid4(),
                    name=sample_tag_data["name"],
                    color=sample_tag_data["color"],
                    description=sample_tag_data["description"],
                    created_by=mock_user.return_value.id,
                )
                mock_service.create_tag.return_value = mock_tag

                response = client.post("/api/v2/documents/tags", json=sample_tag_data)

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "tag" in data
                assert data["message"] == "Tag created successfully"

    def test_list_tags(self):
        """Test listing document tags"""
        # Mock authentication
        with patch(
            "backend.app.routes.enhanced_documents.get_current_user"
        ) as mock_user:
            mock_user.return_value = Mock(id=str(uuid.uuid4()))

            # Mock document service
            with patch(
                "backend.app.routes.enhanced_documents.enhanced_document_service"
            ) as mock_service:
                mock_tags = [
                    DocumentTag(
                        id=uuid.uuid4(),
                        name="Important",
                        color="#FF0000",
                        created_by=mock_user.return_value.id,
                    ),
                    DocumentTag(
                        id=uuid.uuid4(),
                        name="Urgent",
                        color="#FFA500",
                        created_by=mock_user.return_value.id,
                    ),
                ]
                mock_service.get_tags.return_value = mock_tags

                response = client.get("/api/v2/documents/tags")

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "tags" in data
                assert len(data["tags"]) == 2

    def test_add_tag_to_document(self):
        """Test adding a tag to a document"""
        document_id = str(uuid.uuid4())
        tag_id = str(uuid.uuid4())

        # Mock authentication
        with patch(
            "backend.app.routes.enhanced_documents.get_current_user"
        ) as mock_user:
            mock_user.return_value = Mock(id=str(uuid.uuid4()))

            # Mock document service
            with patch(
                "backend.app.routes.enhanced_documents.enhanced_document_service"
            ) as mock_service:
                mock_document = EnhancedDocument(
                    id=uuid.UUID(document_id),
                    original_filename="test.pdf",
                    secure_filename="secure_test.pdf",
                    file_path="/tmp/test.pdf",
                    file_size=1024,
                    file_extension=".pdf",
                    mime_type="application/pdf",
                    checksum="test123",
                    created_by=mock_user.return_value.id,
                )
                mock_service.get_document.return_value = mock_document

                response = client.post(f"/api/v2/documents/{document_id}/tags/{tag_id}")

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["message"] == "Tag added to document successfully"

    def test_create_category(self, sample_category_data):
        """Test creating a document category"""
        # Mock authentication
        with patch(
            "backend.app.routes.enhanced_documents.get_current_user"
        ) as mock_user:
            mock_user.return_value = Mock(id=str(uuid.uuid4()))

            # Mock document service
            with patch(
                "backend.app.routes.enhanced_documents.enhanced_document_service"
            ) as mock_service:
                mock_category = DocumentCategory(
                    id=uuid.uuid4(),
                    name=sample_category_data["name"],
                    description=sample_category_data["description"],
                    color=sample_category_data["color"],
                    icon=sample_category_data["icon"],
                    created_by=mock_user.return_value.id,
                )
                mock_service.create_category.return_value = mock_category

                response = client.post(
                    "/api/v2/documents/categories", json=sample_category_data
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "category" in data
                assert data["message"] == "Category created successfully"

    def test_list_categories(self):
        """Test listing document categories"""
        # Mock authentication
        with patch(
            "backend.app.routes.enhanced_documents.get_current_user"
        ) as mock_user:
            mock_user.return_value = Mock(id=str(uuid.uuid4()))

            # Mock document service
            with patch(
                "backend.app.routes.enhanced_documents.enhanced_document_service"
            ) as mock_service:
                mock_categories = [
                    DocumentCategory(
                        id=uuid.uuid4(),
                        name="Financial Documents",
                        description="Invoices, receipts, financial statements",
                        color="#10B981",
                        icon="dollar-sign",
                        created_by=mock_user.return_value.id,
                    ),
                    DocumentCategory(
                        id=uuid.uuid4(),
                        name="Legal Documents",
                        description="Contracts, agreements, legal correspondence",
                        color="#EF4444",
                        icon="gavel",
                        created_by=mock_user.return_value.id,
                    ),
                ]
                mock_service.get_categories.return_value = mock_categories

                response = client.get("/api/v2/documents/categories")

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "categories" in data
                assert len(data["categories"]) == 2

    def test_get_document_statistics(self):
        """Test getting document statistics"""
        # Mock authentication
        with patch(
            "backend.app.routes.enhanced_documents.get_current_user"
        ) as mock_user:
            mock_user.return_value = Mock(id=str(uuid.uuid4()))

            # Mock document service
            with patch(
                "backend.app.routes.enhanced_documents.enhanced_document_service"
            ) as mock_service:
                mock_stats = {
                    "total_documents": 100,
                    "by_status": {"processed": 80, "uploaded": 15, "processing": 5},
                    "by_type": {"invoice": 50, "receipt": 30, "contract": 20},
                    "total_storage_bytes": 1048576000,  # 1GB
                }
                mock_service.get_document_statistics.return_value = mock_stats

                response = client.get("/api/v2/documents/statistics/overview")

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "statistics" in data
                assert data["statistics"]["total_documents"] == 100
                assert "storage_size_formatted" in data["statistics"]

    def test_get_document_types(self):
        """Test getting available document types"""
        response = client.get("/api/v2/documents/types")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "document_types" in data
        assert "invoice" in data["document_types"]
        assert "receipt" in data["document_types"]
        assert "contract" in data["document_types"]

    def test_get_document_statuses(self):
        """Test getting available document statuses"""
        response = client.get("/api/v2/documents/statuses")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "statuses" in data
        assert "uploaded" in data["statuses"]
        assert "processed" in data["statuses"]
        assert "archived" in data["statuses"]

    def test_get_search_suggestions(self):
        """Test getting search suggestions"""
        # Mock authentication
        with patch(
            "backend.app.routes.enhanced_documents.get_current_user"
        ) as mock_user:
            mock_user.return_value = Mock(id=str(uuid.uuid4()))

            # Mock document service
            with patch(
                "backend.app.routes.enhanced_documents.enhanced_document_service"
            ) as mock_service:
                mock_tags = [
                    DocumentTag(
                        id=uuid.uuid4(),
                        name="Invoice Tag",
                        color="#FF0000",
                        created_by=mock_user.return_value.id,
                    )
                ]
                mock_categories = [
                    DocumentCategory(
                        id=uuid.uuid4(),
                        name="Invoice Category",
                        description="Invoice related documents",
                        color="#10B981",
                        created_by=mock_user.return_value.id,
                    )
                ]
                mock_service.get_tags.return_value = mock_tags
                mock_service.get_categories.return_value = mock_categories

                response = client.get(
                    "/api/v2/documents/search/suggestions", params={"query": "invoice"}
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "suggestions" in data
                assert "invoice" in data["suggestions"]["document_types"]
                assert "Invoice Tag" in data["suggestions"]["tags"]
                assert "Invoice Category" in data["suggestions"]["categories"]


class TestEnhancedDocumentService:
    """Test the enhanced document service directly"""

    def test_create_document_validation(self):
        """Test document creation with validation"""
        service = EnhancedDocumentService()

        # Test with invalid data
        with pytest.raises(Exception):
            service.create_document({}, str(uuid.uuid4()))

        # Test with valid data
        valid_data = {
            "original_filename": "test.pdf",
            "secure_filename": "secure_test.pdf",
            "file_path": "/tmp/test.pdf",
            "file_size": 1024,
            "file_extension": ".pdf",
            "mime_type": "application/pdf",
            "checksum": "test123",
        }

        # Mock the service to avoid database operations
        with patch.object(service, "documents") as mock_collection:
            with patch.object(service, "_update_search_index"):
                mock_collection.insert_one.return_value = None

                document = service.create_document(valid_data, str(uuid.uuid4()))

                assert document.original_filename == "test.pdf"
                assert document.file_size == 1024
                assert document.status == DocumentStatus.UPLOADED

    def test_search_criteria_validation(self):
        """Test search criteria validation"""
        # Valid criteria
        valid_criteria = DocumentSearchCriteria(
            page=1, limit=20, sort_by="created_at", sort_order="desc"
        )
        assert valid_criteria.page == 1
        assert valid_criteria.limit == 20

        # Invalid sort_by
        with pytest.raises(ValueError):
            DocumentSearchCriteria(sort_by="invalid_field")

        # Invalid sort_order
        with pytest.raises(ValueError):
            DocumentSearchCriteria(sort_order="invalid_order")

    def test_document_metadata_operations(self):
        """Test document metadata operations"""
        document = EnhancedDocument(
            id=uuid.uuid4(),
            original_filename="test.pdf",
            secure_filename="secure_test.pdf",
            file_path="/tmp/test.pdf",
            file_size=1024,
            file_extension=".pdf",
            mime_type="application/pdf",
            checksum="test123",
            created_by=str(uuid.uuid4()),
        )

        # Test adding tag
        tag_id = uuid.uuid4()
        document.add_tag(tag_id)
        assert tag_id in document.metadata.tags

        # Test removing tag
        document.remove_tag(tag_id)
        assert tag_id not in document.metadata.tags

        # Test setting category
        category_id = uuid.uuid4()
        document.set_category(category_id)
        assert document.metadata.category_id == category_id

        # Test access recording
        user_id = uuid.uuid4()
        document.record_access(user_id)
        assert user_id in document.accessed_by
        assert len(document.accessed_at) > 0


if __name__ == "__main__":
    pytest.main([__file__])
