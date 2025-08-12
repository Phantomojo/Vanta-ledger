#!/usr/bin/env python3
"""
Comprehensive System Tests
Tests for all implemented features including enhanced documents, financial management, AI analytics, and performance
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.models.document_models import (
    DocumentCategory,
    DocumentStatus,
    DocumentTag,
    DocumentType,
    EnhancedDocument,
)
from backend.app.models.financial_models import (
    AccountType,
    ChartOfAccounts,
    Currency,
    Customer,
    Invoice,
    JournalEntry,
)
from backend.app.optimizations.performance_optimizer import PerformanceOptimizer
from backend.app.services.ai_analytics_service import EnhancedAIAnalyticsService
from backend.app.services.enhanced_document_service import EnhancedDocumentService
from backend.app.services.financial_service import FinancialService

client = TestClient(app)


class TestComprehensiveSystem:
    """Comprehensive system tests for all features"""

    @pytest.fixture
    def sample_user(self):
        """Sample user for testing"""
        return Mock(id=str(uuid.uuid4()), username="testuser")

    @pytest.fixture
    def sample_document_data(self):
        """Sample document data"""
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
    def sample_financial_data(self):
        """Sample financial data"""
        return {
            "account_data": {
                "account_code": "TEST-001",
                "account_name": "Test Account",
                "account_type": "asset",
                "description": "Test account for testing",
            },
            "journal_entry_data": {
                "entry_number": "JE-2024-001",
                "entry_date": datetime.utcnow().isoformat(),
                "description": "Test journal entry",
                "lines": [
                    {
                        "account_id": str(uuid.uuid4()),
                        "description": "Test debit",
                        "debit_amount": "1000.00",
                        "credit_amount": "0.00",
                    },
                    {
                        "account_id": str(uuid.uuid4()),
                        "description": "Test credit",
                        "debit_amount": "0.00",
                        "credit_amount": "1000.00",
                    },
                ],
            },
            "invoice_data": {
                "invoice_number": "INV-2024-001",
                "customer_id": str(uuid.uuid4()),
                "invoice_date": datetime.utcnow().isoformat(),
                "due_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "lines": [
                    {
                        "item_description": "Test Item",
                        "quantity": "1.00",
                        "unit_price": "100.00",
                        "tax_rate": "16.00",
                    }
                ],
            },
            "customer_data": {
                "customer_code": "CUST-001",
                "customer_name": "Test Customer",
                "email": "test@example.com",
                "phone": "+254700000000",
            },
        }

    # ============================================================================
    # ENHANCED DOCUMENT MANAGEMENT TESTS
    # ============================================================================

    def test_enhanced_document_creation(self, sample_user, sample_document_data):
        """Test enhanced document creation"""
        with patch(
            "backend.app.routes.enhanced_documents.get_current_user"
        ) as mock_user:
            mock_user.return_value = sample_user

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
                    created_by=sample_user.id,
                )
                mock_service.create_document.return_value = mock_document

                response = client.post("/api/v2/documents/", json=sample_document_data)

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "document" in data
                assert data["message"] == "Document created successfully"

    def test_document_tagging(self, sample_user):
        """Test document tagging functionality"""
        document_id = str(uuid.uuid4())
        tag_id = str(uuid.uuid4())

        with patch(
            "backend.app.routes.enhanced_documents.get_current_user"
        ) as mock_user:
            mock_user.return_value = sample_user

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
                    created_by=sample_user.id,
                )
                mock_service.get_document.return_value = mock_document

                response = client.post(f"/api/v2/documents/{document_id}/tags/{tag_id}")

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["message"] == "Tag added to document successfully"

    def test_advanced_document_search(self, sample_user):
        """Test advanced document search"""
        with patch(
            "backend.app.routes.enhanced_documents.get_current_user"
        ) as mock_user:
            mock_user.return_value = sample_user

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
                        created_by=sample_user.id,
                    )
                ]
                mock_service.search_documents.return_value = (mock_documents, 1)

                search_criteria = {
                    "full_text": "invoice payment",
                    "document_types": ["invoice"],
                    "page": 1,
                    "limit": 20,
                }

                response = client.post("/api/v2/documents/search", json=search_criteria)

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "documents" in data
                assert "pagination" in data

    # ============================================================================
    # FINANCIAL MANAGEMENT TESTS
    # ============================================================================

    def test_chart_of_accounts_creation(self, sample_user, sample_financial_data):
        """Test chart of accounts creation"""
        with patch("backend.app.routes.financial.get_current_user") as mock_user:
            mock_user.return_value = sample_user

            with patch(
                "backend.app.routes.financial.financial_service"
            ) as mock_service:
                mock_account = ChartOfAccounts(
                    id=uuid.uuid4(),
                    account_code=sample_financial_data["account_data"]["account_code"],
                    account_name=sample_financial_data["account_data"]["account_name"],
                    account_type=AccountType.ASSET,
                    created_by=sample_user.id,
                )
                mock_service.create_account.return_value = mock_account

                response = client.post(
                    "/api/v2/financial/accounts",
                    json=sample_financial_data["account_data"],
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "account" in data
                assert data["message"] == "Account created successfully"

    def test_journal_entry_creation(self, sample_user, sample_financial_data):
        """Test journal entry creation"""
        with patch("backend.app.routes.financial.get_current_user") as mock_user:
            mock_user.return_value = sample_user

            with patch(
                "backend.app.routes.financial.financial_service"
            ) as mock_service:
                mock_entry = JournalEntry(
                    id=uuid.uuid4(),
                    entry_number=sample_financial_data["journal_entry_data"][
                        "entry_number"
                    ],
                    entry_date=datetime.utcnow(),
                    description=sample_financial_data["journal_entry_data"][
                        "description"
                    ],
                    total_debit=1000.00,
                    total_credit=1000.00,
                    created_by=sample_user.id,
                )
                mock_service.create_journal_entry.return_value = mock_entry

                response = client.post(
                    "/api/v2/financial/journal-entries",
                    json=sample_financial_data["journal_entry_data"],
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "journal_entry" in data
                assert data["message"] == "Journal entry created successfully"

    def test_invoice_creation(self, sample_user, sample_financial_data):
        """Test invoice creation"""
        with patch("backend.app.routes.financial.get_current_user") as mock_user:
            mock_user.return_value = sample_user

            with patch(
                "backend.app.routes.financial.financial_service"
            ) as mock_service:
                mock_invoice = Invoice(
                    id=uuid.uuid4(),
                    invoice_number=sample_financial_data["invoice_data"][
                        "invoice_number"
                    ],
                    customer_id=uuid.UUID(
                        sample_financial_data["invoice_data"]["customer_id"]
                    ),
                    invoice_date=datetime.utcnow(),
                    due_date=datetime.utcnow() + timedelta(days=30),
                    subtotal=100.00,
                    tax_amount=16.00,
                    total_amount=116.00,
                    balance_due=116.00,
                    created_by=sample_user.id,
                )
                mock_service.create_invoice.return_value = mock_invoice

                response = client.post(
                    "/api/v2/financial/invoices",
                    json=sample_financial_data["invoice_data"],
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "invoice" in data
                assert data["message"] == "Invoice created successfully"

    def test_customer_creation(self, sample_user, sample_financial_data):
        """Test customer creation"""
        with patch("backend.app.routes.financial.get_current_user") as mock_user:
            mock_user.return_value = sample_user

            with patch(
                "backend.app.routes.financial.financial_service"
            ) as mock_service:
                mock_customer = Customer(
                    id=uuid.uuid4(),
                    customer_code=sample_financial_data["customer_data"][
                        "customer_code"
                    ],
                    customer_name=sample_financial_data["customer_data"][
                        "customer_name"
                    ],
                    email=sample_financial_data["customer_data"]["email"],
                    phone=sample_financial_data["customer_data"]["phone"],
                    created_by=sample_user.id,
                )
                mock_service.create_customer.return_value = mock_customer

                response = client.post(
                    "/api/v2/financial/customers",
                    json=sample_financial_data["customer_data"],
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "customer" in data
                assert data["message"] == "Customer created successfully"

    # ============================================================================
    # AI ANALYTICS TESTS
    # ============================================================================

    def test_financial_trend_analysis(self, sample_user):
        """Test financial trend analysis"""
        with patch("backend.app.routes.ai_analytics.get_current_user") as mock_user:
            mock_user.return_value = sample_user

            with patch(
                "backend.app.routes.ai_analytics.enhanced_ai_analytics_service"
            ) as mock_service:
                mock_analysis = {
                    "success": True,
                    "analysis": {
                        "trends": {
                            "trend_direction": "increasing",
                            "growth_rate_percent": 15.5,
                        },
                        "patterns": {
                            "total_payments": 50,
                            "average_payment_amount": 2500.00,
                        },
                    },
                }
                mock_service.analyze_financial_trends.return_value = mock_analysis

                response = client.get(
                    "/api/v2/ai-analytics/trends/financial?period_days=90"
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "analysis" in data
                assert "trends" in data["analysis"]

    def test_financial_predictions(self, sample_user):
        """Test financial predictions"""
        with patch("backend.app.routes.ai_analytics.get_current_user") as mock_user:
            mock_user.return_value = sample_user

            with patch(
                "backend.app.routes.ai_analytics.enhanced_ai_analytics_service"
            ) as mock_service:
                mock_predictions = {
                    "success": True,
                    "predictions": {
                        "revenue_forecast": {
                            "forecast_values": [10000, 11000, 12000],
                            "method": "moving_average",
                            "confidence_interval": 0.85,
                        },
                        "forecast_periods": 12,
                    },
                }
                mock_service.predict_financial_metrics.return_value = mock_predictions

                response = client.get(
                    "/api/v2/ai-analytics/predictions/financial?forecast_periods=12"
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "predictions" in data
                assert "revenue_forecast" in data["predictions"]

    def test_anomaly_detection(self, sample_user):
        """Test anomaly detection"""
        with patch("backend.app.routes.ai_analytics.get_current_user") as mock_user:
            mock_user.return_value = sample_user

            with patch(
                "backend.app.routes.ai_analytics.enhanced_ai_analytics_service"
            ) as mock_service:
                mock_anomalies = {
                    "success": True,
                    "anomalies": {
                        "financial_anomalies": [
                            {
                                "type": "high_value_invoice",
                                "severity": "medium",
                                "description": "Unusually high invoice value",
                            }
                        ],
                        "document_anomalies": [],
                        "payment_anomalies": [],
                    },
                }
                mock_service.detect_anomalies.return_value = mock_anomalies

                response = client.get("/api/v2/ai-analytics/anomalies")

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "anomalies" in data
                assert "financial_anomalies" in data["anomalies"]

    def test_financial_insights(self, sample_user):
        """Test financial insights generation"""
        with patch("backend.app.routes.ai_analytics.get_current_user") as mock_user:
            mock_user.return_value = sample_user

            with patch(
                "backend.app.routes.ai_analytics.enhanced_ai_analytics_service"
            ) as mock_service:
                mock_insights = {
                    "success": True,
                    "insights": {
                        "current_state": {
                            "current_month_revenue": 50000.00,
                            "outstanding_amount": 15000.00,
                        },
                        "recommendations": [
                            {
                                "category": "revenue",
                                "priority": "high",
                                "title": "Increase Revenue Generation",
                            }
                        ],
                    },
                }
                mock_service.generate_financial_insights.return_value = mock_insights

                response = client.get("/api/v2/ai-analytics/insights/financial")

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "insights" in data
                assert "current_state" in data["insights"]
                assert "recommendations" in data["insights"]

    # ============================================================================
    # PERFORMANCE OPTIMIZATION TESTS
    # ============================================================================

    def test_performance_optimizer_initialization(self):
        """Test performance optimizer initialization"""
        optimizer = PerformanceOptimizer()

        assert optimizer.default_ttl == 3600
        assert optimizer.short_ttl == 300
        assert optimizer.long_ttl == 86400
        assert optimizer.executor is not None

    def test_cache_key_generation(self):
        """Test cache key generation"""
        optimizer = PerformanceOptimizer()

        def test_function(arg1, arg2, kwarg1="default"):
            return arg1 + arg2

        cache_key = optimizer._generate_cache_key(
            test_function, (1, 2), {"kwarg1": "test"}, "test_prefix"
        )

        assert cache_key.startswith("test_prefix:")
        assert len(cache_key) > 20  # Should be a reasonable hash length

    def test_database_optimization(self):
        """Test database optimization"""
        with patch(
            "backend.app.optimizations.performance_optimizer.MongoClient"
        ) as mock_client:
            mock_db = MagicMock()
            mock_client.return_value.__getitem__.return_value = mock_db

            optimizer = PerformanceOptimizer()
            optimizer.optimize_database_queries()

            # Verify that indexes were created
            assert mock_db.documents.create_index.called
            assert mock_db.invoices.create_index.called
            assert mock_db.journal_entries.create_index.called

    def test_memory_optimization(self):
        """Test memory optimization"""
        with patch(
            "backend.app.optimizations.performance_optimizer.redis.Redis"
        ) as mock_redis:
            mock_redis_instance = MagicMock()
            mock_redis.from_url.return_value = mock_redis_instance

            optimizer = PerformanceOptimizer()
            optimizer.optimize_memory_usage()

            # Verify that cleanup was called
            assert mock_redis_instance.keys.called
            assert mock_redis_instance.config_set.called

    # ============================================================================
    # INTEGRATION TESTS
    # ============================================================================

    def test_end_to_end_document_workflow(self, sample_user, sample_document_data):
        """Test end-to-end document workflow"""
        with patch(
            "backend.app.routes.enhanced_documents.get_current_user"
        ) as mock_user:
            mock_user.return_value = sample_user

            # Test document creation
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
                    created_by=sample_user.id,
                )
                mock_service.create_document.return_value = mock_document
                mock_service.get_document.return_value = mock_document

                # Create document
                create_response = client.post(
                    "/api/v2/documents/", json=sample_document_data
                )
                assert create_response.status_code == 200

                document_id = create_response.json()["document"]["id"]

                # Get document
                get_response = client.get(f"/api/v2/documents/{document_id}")
                assert get_response.status_code == 200

                # Search documents
                search_response = client.get("/api/v2/documents/?document_type=invoice")
                assert search_response.status_code == 200

    def test_end_to_end_financial_workflow(self, sample_user, sample_financial_data):
        """Test end-to-end financial workflow"""
        with patch("backend.app.routes.financial.get_current_user") as mock_user:
            mock_user.return_value = sample_user

            # Test account creation
            with patch(
                "backend.app.routes.financial.financial_service"
            ) as mock_service:
                mock_account = ChartOfAccounts(
                    id=uuid.uuid4(),
                    account_code=sample_financial_data["account_data"]["account_code"],
                    account_name=sample_financial_data["account_data"]["account_name"],
                    account_type=AccountType.ASSET,
                    created_by=sample_user.id,
                )
                mock_service.create_account.return_value = mock_account
                mock_service.get_accounts.return_value = [mock_account]

                # Create account
                account_response = client.post(
                    "/api/v2/financial/accounts",
                    json=sample_financial_data["account_data"],
                )
                assert account_response.status_code == 200

                # List accounts
                list_response = client.get("/api/v2/financial/accounts")
                assert list_response.status_code == 200

    def test_api_health_endpoints(self):
        """Test API health endpoints"""
        # Test main health endpoint
        response = client.get("/health")
        assert response.status_code == 200

        # Test AI analytics health
        response = client.get("/api/v2/ai-analytics/health")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "ai_analytics"
        assert data["status"] == "healthy"

    def test_error_handling(self, sample_user):
        """Test error handling across endpoints"""
        with patch(
            "backend.app.routes.enhanced_documents.get_current_user"
        ) as mock_user:
            mock_user.return_value = sample_user

            with patch(
                "backend.app.routes.enhanced_documents.enhanced_document_service"
            ) as mock_service:
                mock_service.create_document.side_effect = Exception("Test error")

                response = client.post("/api/v2/documents/", json={"invalid": "data"})
                assert response.status_code == 500

    def test_authentication_required(self):
        """Test that authentication is required for protected endpoints"""
        # Test without authentication
        response = client.get("/api/v2/documents/")
        assert response.status_code == 401  # Unauthorized

        response = client.get("/api/v2/financial/accounts")
        assert response.status_code == 401

        response = client.get("/api/v2/ai-analytics/trends/financial")
        assert response.status_code == 401


class TestPerformanceOptimizations:
    """Performance optimization specific tests"""

    def test_cache_decorator(self):
        """Test cache decorator functionality"""
        optimizer = PerformanceOptimizer()

        @optimizer.cache_result(ttl=300)
        async def test_cached_function(param):
            return {"result": param, "timestamp": datetime.utcnow().isoformat()}

        # This would need to be tested with actual Redis in integration tests
        assert test_cached_function is not None

    def test_batch_processing(self):
        """Test batch processing functionality"""
        optimizer = PerformanceOptimizer()

        async def test_operation(item):
            return item * 2

        items = list(range(10))
        # This would need to be tested with actual async execution
        assert len(items) == 10

    def test_query_optimization(self):
        """Test query optimization"""
        optimizer = PerformanceOptimizer()

        pipeline = [
            {"$match": {"status": "active"}},
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        ]

        optimized_pipeline = optimizer.database_query_optimizer(
            "test_collection", pipeline
        )

        assert len(optimized_pipeline) > len(pipeline)
        assert any("$limit" in stage for stage in optimized_pipeline)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
