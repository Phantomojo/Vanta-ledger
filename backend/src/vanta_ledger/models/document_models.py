#!/usr/bin/env python3
"""
Document Models for Vanta Ledger
Defines enums and models for document management
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class DocumentType(str, Enum):
    """Document type enumeration"""
    INVOICE = "invoice"
    RECEIPT = "receipt"
    CONTRACT = "contract"
    REPORT = "report"
    STATEMENT = "statement"
    CERTIFICATE = "certificate"
    LICENSE = "license"
    PERMIT = "permit"
    OTHER = "other"


class DocumentStatus(str, Enum):
    """Document status enumeration"""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"
    DELETED = "deleted"


class DocumentPriority(str, Enum):
    """Document priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class DocumentCategory(str, Enum):
    """Document category enumeration"""
    FINANCIAL = "financial"
    LEGAL = "legal"
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"
    HR = "hr"
    MARKETING = "marketing"
    TECHNICAL = "technical"
    OTHER = "other"


class DocumentTag(BaseModel):
    """Document tag model"""
    name: str = Field(..., description="Tag name")
    color: Optional[str] = Field(None, description="Tag color for UI")
    description: Optional[str] = Field(None, description="Tag description")


class DocumentSearchCriteria(BaseModel):
    """Document search criteria model"""
    query: Optional[str] = Field(None, description="Search query")
    document_type: Optional[DocumentType] = Field(None, description="Filter by document type")
    status: Optional[DocumentStatus] = Field(None, description="Filter by status")
    priority: Optional[DocumentPriority] = Field(None, description="Filter by priority")
    category: Optional[DocumentCategory] = Field(None, description="Filter by category")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    date_from: Optional[datetime] = Field(None, description="Filter from date")
    date_to: Optional[datetime] = Field(None, description="Filter to date")
    company_id: Optional[str] = Field(None, description="Filter by company")
    project_id: Optional[str] = Field(None, description="Filter by project")
    created_by: Optional[str] = Field(None, description="Filter by creator")
    limit: Optional[int] = Field(50, description="Maximum number of results")
    offset: Optional[int] = Field(0, description="Number of results to skip")


class DocumentMetadata(BaseModel):
    """Document metadata model"""
    file_size: Optional[int] = Field(None, description="File size in bytes")
    mime_type: Optional[str] = Field(None, description="MIME type")
    page_count: Optional[int] = Field(None, description="Number of pages")
    language: Optional[str] = Field(None, description="Document language")
    ocr_text: Optional[str] = Field(None, description="OCR extracted text")
    extracted_data: Optional[Dict[str, Any]] = Field(None, description="Extracted structured data")
    checksum: Optional[str] = Field(None, description="File checksum")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class DocumentVersion(BaseModel):
    """Document version model"""
    version_number: int = Field(..., description="Version number")
    file_path: str = Field(..., description="Path to version file")
    created_at: datetime = Field(..., description="Version creation time")
    created_by: str = Field(..., description="User who created this version")
    change_description: Optional[str] = Field(None, description="Description of changes")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    checksum: Optional[str] = Field(None, description="File checksum")


class DocumentWorkflow(BaseModel):
    """Document workflow model"""
    workflow_id: str = Field(..., description="Workflow identifier")
    current_step: str = Field(..., description="Current workflow step")
    assigned_to: Optional[str] = Field(None, description="User assigned to current step")
    due_date: Optional[datetime] = Field(None, description="Due date for current step")
    status: str = Field(..., description="Workflow status")
    steps: List[Dict[str, Any]] = Field(..., description="Workflow steps")
    history: List[Dict[str, Any]] = Field(default_factory=list, description="Workflow history")


class DocumentAccess(BaseModel):
    """Document access control model"""
    user_id: str = Field(..., description="User ID")
    permission: str = Field(..., description="Permission level: read, write, admin")
    granted_by: str = Field(..., description="User who granted access")
    granted_at: datetime = Field(..., description="When access was granted")
    expires_at: Optional[datetime] = Field(None, description="When access expires")


class DocumentAudit(BaseModel):
    """Document audit trail model"""
    action: str = Field(..., description="Action performed")
    user_id: str = Field(..., description="User who performed action")
    timestamp: datetime = Field(..., description="When action was performed")
    details: Optional[Dict[str, Any]] = Field(None, description="Action details")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent")


class EnhancedDocument(BaseModel):
    """Enhanced document model with full metadata"""
    id: str = Field(..., description="Document ID")
    title: str = Field(..., description="Document title")
    description: Optional[str] = Field(None, description="Document description")
    document_type: DocumentType = Field(..., description="Type of document")
    status: DocumentStatus = Field(..., description="Document status")
    priority: DocumentPriority = Field(..., description="Document priority")
    category: DocumentCategory = Field(..., description="Document category")
    tags: List[DocumentTag] = Field(default_factory=list, description="Document tags")
    file_path: str = Field(..., description="Path to document file")
    file_name: str = Field(..., description="Original file name")
    metadata: DocumentMetadata = Field(..., description="Document metadata")
    versions: List[DocumentVersion] = Field(default_factory=list, description="Document versions")
    workflow: Optional[DocumentWorkflow] = Field(None, description="Document workflow")
    access_control: List[DocumentAccess] = Field(default_factory=list, description="Access control list")
    audit_trail: List[DocumentAudit] = Field(default_factory=list, description="Audit trail")
    company_id: Optional[str] = Field(None, description="Associated company ID")
    project_id: Optional[str] = Field(None, description="Associated project ID")
    created_by: str = Field(..., description="User who created the document")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    archived_at: Optional[datetime] = Field(None, description="Archival timestamp")
    deleted_at: Optional[datetime] = Field(None, description="Deletion timestamp")
    is_public: bool = Field(False, description="Whether document is public")
    is_encrypted: bool = Field(False, description="Whether document is encrypted")
    encryption_key_id: Optional[str] = Field(None, description="Encryption key ID")
    retention_policy: Optional[str] = Field(None, description="Retention policy")
    compliance_flags: List[str] = Field(default_factory=list, description="Compliance flags")
    ai_analysis: Optional[Dict[str, Any]] = Field(None, description="AI analysis results")
    search_vector: Optional[List[float]] = Field(None, description="Search vector for similarity")
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Custom fields")
