
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_, or_
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from ..database import get_db, Document, Company, Project, LedgerEntry
import calendar

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/financial_summary")
def get_financial_summary(
    company_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Central financial summary from all documents and ledger entries.
    This is the core of your business intelligence.
    """
    # Base query
    query = db.query(Document)
    
    # Apply filters
    if company_id:
        query = query.filter(Document.company_id == company_id)
    if start_date:
        query = query.filter(Document.created_at >= start_date)
    if end_date:
        query = query.filter(Document.created_at <= end_date)
    
    # Get all financial documents
    financial_docs = query.filter(
        or_(Document.is_income == True, Document.is_expense == True)
    ).all()
    
    # Calculate totals
    total_income = sum(doc.primary_amount for doc in financial_docs if doc.is_income and doc.primary_amount)
    total_expenses = sum(doc.primary_amount for doc in financial_docs if doc.is_expense and doc.primary_amount)
    net_profit = total_income - total_expenses
    
    # Document counts
    doc_counts = db.query(
        Document.doc_category,
        func.count(Document.id)
    ).group_by(Document.doc_category).all()
    
    # Recent documents affecting cash flow
    recent_cash_flow = query.filter(
        and_(
            Document.affects_cash_flow == True,
            Document.created_at >= datetime.now() - timedelta(days=30)
        )
    ).count()
    
    return {
        "financial_summary": {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_profit": net_profit,
            "profit_margin": (net_profit / total_income * 100) if total_income > 0 else 0
        },
        "document_distribution": dict(doc_counts),
        "recent_activity": {
            "documents_last_30_days": recent_cash_flow,
            "pending_reviews": query.filter(Document.requires_manual_review == True).count()
        },
        "data_quality": {
            "avg_extraction_score": db.query(func.avg(Document.data_quality_score)).scalar() or 0,
            "processing_status": db.query(
                Document.processing_status,
                func.count(Document.id)
            ).group_by(Document.processing_status).all()
        }
    }

@router.get("/cash_flow_trend")
def get_cash_flow_trend(
    months: int = 12,
    company_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Monthly cash flow trend from document data.
    Shows money in vs money out over time.
    """
    # Calculate start date
    start_date = datetime.now() - timedelta(days=months * 30)
    
    query = db.query(
        extract('year', Document.created_at).label('year'),
        extract('month', Document.created_at).label('month'),
        func.sum(
            func.case(
                (Document.is_income == True, Document.primary_amount),
                else_=0
            )
        ).label('income'),
        func.sum(
            func.case(
                (Document.is_expense == True, Document.primary_amount),
                else_=0
            )
        ).label('expenses')
    ).filter(
        Document.created_at >= start_date,
        Document.primary_amount.isnot(None)
    )
    
    if company_id:
        query = query.filter(Document.company_id == company_id)
    
    monthly_data = query.group_by(
        extract('year', Document.created_at),
        extract('month', Document.created_at)
    ).order_by('year', 'month').all()
    
    # Format data for charts
    trend_data = []
    for row in monthly_data:
        month_name = calendar.month_name[int(row.month)]
        trend_data.append({
            "period": f"{month_name} {int(row.year)}",
            "income": float(row.income or 0),
            "expenses": float(row.expenses or 0),
            "net": float((row.income or 0) - (row.expenses or 0))
        })
    
    return {"cash_flow_trend": trend_data}

@router.get("/project_performance")
def get_project_performance(db: Session = Depends(get_db)):
    """
    Performance analysis of all projects based on document data.
    """
    projects = db.query(Project).all()
    
    performance_data = []
    for project in projects:
        # Get project documents
        project_docs = db.query(Document).filter(Document.project_id == project.id).all()
        
        # Calculate document-based metrics
        total_doc_value = sum(doc.primary_amount for doc in project_docs if doc.primary_amount)
        income_docs = [doc for doc in project_docs if doc.is_income]
        expense_docs = [doc for doc in project_docs if doc.is_expense]
        
        project_income = sum(doc.primary_amount for doc in income_docs if doc.primary_amount)
        project_expenses = sum(doc.primary_amount for doc in expense_docs if doc.primary_amount)
        
        performance_data.append({
            "project_id": project.id,
            "project_name": project.name,
            "contract_value": project.contract_value,
            "actual_income": project_income,
            "actual_expenses": project_expenses,
            "profit_margin": ((project_income - project_expenses) / project_income * 100) if project_income > 0 else 0,
            "document_count": len(project_docs),
            "status": project.status,
            "budget_variance": ((project.contract_value - project_expenses) / project.contract_value * 100) if project.contract_value else 0
        })
    
    return {"project_performance": performance_data}

@router.get("/compliance_status")
def get_compliance_status(db: Session = Depends(get_db)):
    """
    Track compliance documents and their expiry status.
    Critical for tender applications.
    """
    today = date.today()
    
    # Documents expiring soon (next 30 days)
    expiring_soon = db.query(Document).filter(
        and_(
            Document.expiry_date.isnot(None),
            Document.expiry_date >= today,
            Document.expiry_date <= today + timedelta(days=30)
        )
    ).all()
    
    # Expired documents
    expired = db.query(Document).filter(
        and_(
            Document.expiry_date.isnot(None),
            Document.expiry_date < today
        )
    ).all()
    
    # Compliance by company
    compliance_by_company = []
    companies = db.query(Company).all()
    
    for company in companies:
        company_docs = db.query(Document).filter(
            and_(
                Document.company_id == company.id,
                Document.compliance_critical == True
            )
        ).all()
        
        valid_docs = [doc for doc in company_docs if not doc.expiry_date or doc.expiry_date >= today]
        compliance_rate = (len(valid_docs) / len(company_docs) * 100) if company_docs else 100
        
        compliance_by_company.append({
            "company_name": company.name,
            "total_compliance_docs": len(company_docs),
            "valid_docs": len(valid_docs),
            "compliance_rate": compliance_rate,
            "tender_ready": compliance_rate >= 90
        })
    
    return {
        "compliance_overview": {
            "expiring_soon": len(expiring_soon),
            "expired": len(expired),
            "total_compliance_docs": db.query(Document).filter(Document.compliance_critical == True).count()
        },
        "expiring_documents": [
            {
                "filename": doc.filename,
                "doc_type": doc.doc_type,
                "company_name": doc.company.name if doc.company else "Unknown",
                "expiry_date": doc.expiry_date,
                "days_until_expiry": (doc.expiry_date - today).days
            }
            for doc in expiring_soon
        ],
        "compliance_by_company": compliance_by_company
    }

@router.get("/document_insights")
def get_document_insights(db: Session = Depends(get_db)):
    """
    Advanced insights from your document filing system.
    """
    # Processing efficiency
    total_docs = db.query(Document).count()
    processed_docs = db.query(Document).filter(Document.processing_status == "processed").count()
    manual_review_needed = db.query(Document).filter(Document.requires_manual_review == True).count()
    
    # Data extraction quality
    avg_quality = db.query(func.avg(Document.data_quality_score)).scalar() or 0
    high_quality_docs = db.query(Document).filter(Document.data_quality_score >= 0.8).count()
    
    # Document types analysis
    doc_type_distribution = db.query(
        Document.doc_type,
        func.count(Document.id),
        func.avg(Document.data_quality_score)
    ).group_by(Document.doc_type).all()
    
    # Financial document analysis
    financial_docs = db.query(Document).filter(
        or_(Document.is_income == True, Document.is_expense == True)
    ).count()
    
    return {
        "processing_efficiency": {
            "total_documents": total_docs,
            "processed_percentage": (processed_docs / total_docs * 100) if total_docs > 0 else 0,
            "manual_review_needed": manual_review_needed,
            "automation_rate": ((total_docs - manual_review_needed) / total_docs * 100) if total_docs > 0 else 0
        },
        "data_quality": {
            "average_quality_score": round(avg_quality, 2),
            "high_quality_percentage": (high_quality_docs / total_docs * 100) if total_docs > 0 else 0
        },
        "document_distribution": [
            {
                "doc_type": dtype,
                "count": count,
                "avg_quality": round(avg_qual or 0, 2)
            }
            for dtype, count, avg_qual in doc_type_distribution
        ],
        "financial_coverage": {
            "financial_documents": financial_docs,
            "percentage_of_total": (financial_docs / total_docs * 100) if total_docs > 0 else 0
        }
    }
