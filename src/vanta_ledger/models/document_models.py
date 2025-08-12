#!/usr/bin/env python3
"""
Advanced Document Models
Enhanced document management with tagging, categorization, version control, and archiving
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Set
from enum import Enum
from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4
import json

class DocumentStatus(str, Enum):
    """Document processing status"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ARCHIVED = "archived"
    DELETED = "deleted"
    ERROR = "error"

class DocumentType(str, Enum):
    """Document type categories"""
    INVOICE = "invoice"
    RECEIPT = "receipt"
    CONTRACT = "contract"
    PROPOSAL = "proposal"
    REPORT = "report"
    STATEMENT = "statement"
    CERTIFICATE = "certificate"
    ID_DOCUMENT = "id_document"
    FINANCIAL_STATEMENT = "financial_statement"
    TAX_DOCUMENT = "tax_document"
    LEGAL_DOCUMENT = "legal_document"
    OTHER = "other"

class DocumentPriority(str, Enum):
    """Document priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class RetentionPolicy(str, Enum):
    """Document retention policies"""
    ONE_YEAR = "1_year"
    THREE_YEARS = "3_years"
    SEVEN_YEARS = "7_years"
    TEN_YEARS = "10_years"
    PERMANENT = "permanent"
    CUSTOM = "custom"

class DocumentTag(BaseModel):
    """Document tag model"""
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field(default="#3B82F6", pattern=r"^#[0-9A-Fa-f]{6}$")
    description: Optional[str] = Field(None, max_length=200)
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_system: bool = Field(default=False)  # System-generated tags
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }

class DocumentCategory(BaseModel):
    """Document category model"""
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    parent_category_id: Optional[UUID] = None
    color: str = Field(default="#6B7280", pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(None, max_length=50)
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_system: bool = Field(default=False)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }

class DocumentVersion(BaseModel):
    """Document version model for version control"""
    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    version_number: int
    file_path: str
    file_size: int
    checksum: str
    changes_summary: Optional[str] = Field(None, max_length=500)
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }

class DocumentMetadata(BaseModel):
    """Enhanced document metadata"""
    # Basic Information
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    keywords: List[str] = Field(default_factory=list)
    
    # Classification
    document_type: DocumentType = Field(default=DocumentType.OTHER)
    priority: DocumentPriority = Field(default=DocumentPriority.MEDIUM)
    
    # Organization
    tags: List[UUID] = Field(default_factory=list)  # Tag IDs
    category_id: Optional[UUID] = None
    
    # Retention and Archiving
    retention_policy: RetentionPolicy = Field(default=RetentionPolicy.SEVEN_YEARS)
    retention_date: Optional[datetime] = None
    archive_date: Optional[datetime] = None
    
    # Security and Access
    is_confidential: bool = Field(default=False)
    access_level: str = Field(default="standard")  # standard, restricted, confidential
    allowed_users: List[UUID] = Field(default_factory=list)
    
    # Workflow
    workflow_status: Optional[str] = None
    assigned_to: Optional[UUID] = None
    due_date: Optional[datetime] = None
    
    # Custom Fields
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }

class DocumentSearchCriteria(BaseModel):
    """Advanced search criteria for documents"""
    # Text Search
    full_text: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    
    # Classification
    document_types: List[DocumentType] = Field(default_factory=list)
    tags: List[UUID] = Field(default_factory=list)
    category_id: Optional[UUID] = None
    
    # Date Range
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    modified_after: Optional[datetime] = None
    modified_before: Optional[datetime] = None
    
    # Status and Priority
    status: List[DocumentStatus] = Field(default_factory=list)
    priority: List[DocumentPriority] = Field(default_factory=list)
    
    # File Properties
    min_file_size: Optional[int] = None
    max_file_size: Optional[int] = None
    file_extensions: List[str] = Field(default_factory=list)
    
    # Users and Access
    created_by: Optional[UUID] = None
    assigned_to: Optional[UUID] = None
    
    # Pagination
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    sort_by: str = Field(default="created_at")
    sort_order: str = Field(default="desc")  # asc or desc
    
    @validator('sort_by')
    def validate_sort_by(cls, v):
        allowed_fields = [
            'created_at', 'modified_at', 'title', 'file_size', 
            'priority', 'status', 'document_type'
        ]
        if v not in allowed_fields:
            raise ValueError(f'sort_by must be one of {allowed_fields}')
        return v
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v not in ['asc', 'desc']:
            raise ValueError('sort_order must be asc or desc')
        return v

class DocumentArchivePolicy(BaseModel):
    """Document archiving policy configuration"""
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    
    # Retention Rules
    retention_period_days: int = Field(..., ge=1)
    archive_after_days: int = Field(..., ge=1)
    delete_after_days: Optional[int] = Field(None, ge=1)
    
    # Conditions
    document_types: List[DocumentType] = Field(default_factory=list)
    tags: List[UUID] = Field(default_factory=list)
    categories: List[UUID] = Field(default_factory=list)
    min_file_size: Optional[int] = None
    max_file_size: Optional[int] = None
    
    # Actions
    compress_on_archive: bool = Field(default=True)
    move_to_cold_storage: bool = Field(default=False)
    send_notification: bool = Field(default=True)
    
    # Schedule
    is_active: bool = Field(default=True)
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }

class DocumentWorkflow(BaseModel):
    """Document workflow definition"""
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    
    # Triggers
    trigger_conditions: Dict[str, Any] = Field(default_factory=dict)
    
    # Steps
    steps: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Settings
    is_active: bool = Field(default=True)
    auto_start: bool = Field(default=False)
    allow_manual_start: bool = Field(default=True)
    
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }

class EnhancedDocument(BaseModel):
    """Enhanced document model with all advanced features"""
    # Core Document Information
    id: UUID = Field(default_factory=uuid4)
    original_filename: str
    secure_filename: str
    file_path: str
    file_size: int
    file_extension: str
    mime_type: str
    
    # Processing Information
    status: DocumentStatus = Field(default=DocumentStatus.UPLOADED)
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    processing_errors: List[str] = Field(default_factory=list)
    
    # Content Analysis
    extracted_text: Optional[str] = None
    ocr_confidence: Optional[float] = None
    language: Optional[str] = None
    
    # AI Analysis Results
    ai_analysis: Dict[str, Any] = Field(default_factory=dict)
    entities: Dict[str, List[str]] = Field(default_factory=dict)
    sentiment: Optional[str] = None
    risk_score: Optional[float] = None
    
    # Enhanced Metadata
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    
    # Version Control
    current_version: int = Field(default=1)
    versions: List[DocumentVersion] = Field(default_factory=list)
    
    # Workflow
    workflow_instance_id: Optional[UUID] = None
    workflow_status: Optional[str] = None
    
    # Audit Trail
    created_by: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_by: Optional[UUID] = None
    modified_at: Optional[datetime] = None
    accessed_by: List[UUID] = Field(default_factory=list)
    accessed_at: List[datetime] = Field(default_factory=list)
    
    # Security
    encryption_key_id: Optional[str] = None
    checksum: str
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
    
    def add_version(self, file_path: str, file_size: int, checksum: str, 
                   created_by: UUID, changes_summary: Optional[str] = None) -> DocumentVersion:
        """Add a new version to the document"""
        new_version = DocumentVersion(
            document_id=self.id,
            version_number=self.current_version + 1,
            file_path=file_path,
            file_size=file_size,
            checksum=checksum,
            changes_summary=changes_summary,
            created_by=created_by
        )
        self.versions.append(new_version)
        self.current_version += 1
        self.modified_by = created_by
        self.modified_at = datetime.utcnow()
        return new_version
    
    def add_tag(self, tag_id: UUID) -> None:
        """Add a tag to the document"""
        if tag_id not in self.metadata.tags:
            self.metadata.tags.append(tag_id)
            self.modified_at = datetime.utcnow()
    
    def remove_tag(self, tag_id: UUID) -> None:
        """Remove a tag from the document"""
        if tag_id in self.metadata.tags:
            self.metadata.tags.remove(tag_id)
            self.modified_at = datetime.utcnow()
    
    def set_category(self, category_id: UUID) -> None:
        """Set the document category"""
        self.metadata.category_id = category_id
        self.modified_at = datetime.utcnow()
    
    def should_archive(self) -> bool:
        """Check if document should be archived based on retention policy"""
        if not self.metadata.retention_date:
            return False
        
        return datetime.utcnow() >= self.metadata.retention_date
    
    def should_delete(self) -> bool:
        """Check if document should be deleted based on retention policy"""
        if not self.metadata.retention_date:
            return False
        
        # Add buffer time after archive date
        delete_date = self.metadata.retention_date + timedelta(days=30)
        return datetime.utcnow() >= delete_date
    
    def record_access(self, user_id: UUID) -> None:
        """Record document access"""
        self.accessed_by.append(user_id)
        self.accessed_at.append(datetime.utcnow())
        
        # Keep only last 10 access records
        if len(self.accessed_by) > 10:
            self.accessed_by = self.accessed_by[-10:]
            self.accessed_at = self.accessed_at[-10:]
    
    def to_search_index(self) -> Dict[str, Any]:
        """Convert document to search index format"""
        return {
            "id": str(self.id),
            "title": self.metadata.title or self.original_filename,
            "content": self.extracted_text or "",
            "document_type": self.metadata.document_type.value,
            "tags": [str(tag_id) for tag_id in self.metadata.tags],
            "category_id": str(self.metadata.category_id) if self.metadata.category_id else None,
            "created_at": self.created_at.isoformat(),
            "created_by": str(self.created_by),
            "status": self.status.value,
            "priority": self.metadata.priority.value,
            "keywords": self.metadata.keywords,
            "entities": self.entities,
            "file_size": self.file_size,
            "file_extension": self.file_extension
        } 