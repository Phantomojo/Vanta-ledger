
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from ..database import get_db, Document, Company, Project, LedgerEntry
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/financial_statement")
def generate_financial_statement(
    company_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive financial statement from document data.
    This is your primary business report.
    """
    # Set default date range if not provided
    if not start_date:
        start_date = datetime.now().replace(day=1, month=1).date()  # Start of year
    if not end_date:
        end_date = date.today()
    
    # Base query
    query = db.query(Document).filter(
        Document.created_at >= start_date,
        Document.created_at <= end_date
    )
    
    if company_id:
        query = query.filter(Document.company_id == company_id)
        company = db.query(Company).filter(Company.id == company_id).first()
        company_name = company.name if company else "Unknown Company"
    else:
        company_name = "All Companies"
    
    # Revenue Analysis
    revenue_docs = query.filter(Document.is_income == True).all()
    total_revenue = sum(doc.primary_amount for doc in revenue_docs if doc.primary_amount)
    
    # Expense Analysis
    expense_docs = query.filter(Document.is_expense == True).all()
    total_expenses = sum(doc.primary_amount for doc in expense_docs if doc.primary_amount)
    
    # Expense breakdown by category
    expense_breakdown = {}
    for doc in expense_docs:
        if doc.primary_amount and doc.doc_subcategory:
            category = doc.doc_subcategory
            expense_breakdown[category] = expense_breakdown.get(category, 0) + doc.primary_amount
    
    # Monthly breakdown
    monthly_revenue = {}
    monthly_expenses = {}
    
    for doc in revenue_docs:
        if doc.primary_amount:
            month_key = doc.created_at.strftime("%Y-%m")
            monthly_revenue[month_key] = monthly_revenue.get(month_key, 0) + doc.primary_amount
    
    for doc in expense_docs:
        if doc.primary_amount:
            month_key = doc.created_at.strftime("%Y-%m")
            monthly_expenses[month_key] = monthly_expenses.get(month_key, 0) + doc.primary_amount
    
    # Calculate key metrics
    gross_profit = total_revenue - total_expenses
    profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    return {
        "report_metadata": {
            "company_name": company_name,
            "report_period": f"{start_date} to {end_date}",
            "generated_at": datetime.now().isoformat(),
            "document_count": len(revenue_docs) + len(expense_docs)
        },
        "income_statement": {
            "total_revenue": round(total_revenue, 2),
            "total_expenses": round(total_expenses, 2),
            "gross_profit": round(gross_profit, 2),
            "profit_margin_percentage": round(profit_margin, 2)
        },
        "expense_breakdown": {
            category: round(amount, 2) 
            for category, amount in expense_breakdown.items()
        },
        "monthly_trends": {
            "revenue": {month: round(amount, 2) for month, amount in monthly_revenue.items()},
            "expenses": {month: round(amount, 2) for month, amount in monthly_expenses.items()}
        },
        "key_metrics": {
            "average_monthly_revenue": round(total_revenue / max(len(monthly_revenue), 1), 2),
            "average_monthly_expenses": round(total_expenses / max(len(monthly_expenses), 1), 2),
            "document_processing_rate": f"{len(revenue_docs) + len(expense_docs)} documents processed"
        }
    }

@router.get("/project_report/{project_id}")
def generate_project_report(project_id: int, db: Session = Depends(get_db)):
    """
    Detailed project report based on all documents and data.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get all project documents
    project_docs = db.query(Document).filter(Document.project_id == project_id).all()
    
    # Financial analysis
    income_docs = [doc for doc in project_docs if doc.is_income and doc.primary_amount]
    expense_docs = [doc for doc in project_docs if doc.is_expense and doc.primary_amount]
    
    total_income = sum(doc.primary_amount for doc in income_docs)
    total_expenses = sum(doc.primary_amount for doc in expense_docs)
    
    # Document analysis
    doc_categories = {}
    for doc in project_docs:
        category = doc.doc_category or "uncategorized"
        doc_categories[category] = doc_categories.get(category, 0) + 1
    
    # Timeline analysis
    if project_docs:
        first_doc_date = min(doc.created_at for doc in project_docs)
        last_doc_date = max(doc.created_at for doc in project_docs)
        project_duration = (last_doc_date - first_doc_date).days
    else:
        first_doc_date = last_doc_date = None
        project_duration = 0
    
    # Compliance status
    compliance_docs = [doc for doc in project_docs if doc.compliance_critical]
    valid_compliance = [doc for doc in compliance_docs if not doc.expiry_date or doc.expiry_date >= date.today()]
    
    return {
        "project_details": {
            "name": project.name,
            "company": project.company.name if project.company else "Unknown",
            "status": project.status,
            "contract_value": project.contract_value,
            "start_date": project.start_date,
            "end_date": project.end_date
        },
        "financial_summary": {
            "total_income": round(total_income, 2),
            "total_expenses": round(total_expenses, 2),
            "net_profit": round(total_income - total_expenses, 2),
            "profit_margin": round((total_income - total_expenses) / total_income * 100, 2) if total_income > 0 else 0,
            "budget_variance": round((project.contract_value - total_expenses) / project.contract_value * 100, 2) if project.contract_value else None
        },
        "document_analysis": {
            "total_documents": len(project_docs),
            "categories": doc_categories,
            "first_document": first_doc_date.isoformat() if first_doc_date else None,
            "last_document": last_doc_date.isoformat() if last_doc_date else None,
            "project_duration_days": project_duration
        },
        "compliance_status": {
            "total_compliance_docs": len(compliance_docs),
            "valid_compliance_docs": len(valid_compliance),
            "compliance_rate": round(len(valid_compliance) / len(compliance_docs) * 100, 2) if compliance_docs else 100,
            "tender_ready": len(valid_compliance) == len(compliance_docs)
        }
    }

@router.get("/compliance_report")
def generate_compliance_report(db: Session = Depends(get_db)):
    """
    Comprehensive compliance report for all companies.
    Critical for tender readiness.
    """
    companies = db.query(Company).all()
    compliance_report = []
    
    today = date.today()
    next_month = today + timedelta(days=30)
    
    for company in companies:
        # Get all compliance documents for this company
        compliance_docs = db.query(Document).filter(
            and_(
                Document.company_id == company.id,
                Document.compliance_critical == True
            )
        ).all()
        
        # Categorize by status
        valid_docs = []
        expiring_soon = []
        expired_docs = []
        
        for doc in compliance_docs:
            if not doc.expiry_date:
                valid_docs.append(doc)  # No expiry means always valid
            elif doc.expiry_date >= today:
                if doc.expiry_date <= next_month:
                    expiring_soon.append(doc)
                else:
                    valid_docs.append(doc)
            else:
                expired_docs.append(doc)
        
        # Calculate compliance score
        total_docs = len(compliance_docs)
        valid_count = len(valid_docs)
        compliance_score = (valid_count / total_docs * 100) if total_docs > 0 else 100
        
        compliance_report.append({
            "company_name": company.name,
            "company_id": company.id,
            "total_compliance_documents": total_docs,
            "valid_documents": valid_count,
            "expiring_soon": len(expiring_soon),
            "expired_documents": len(expired_docs),
            "compliance_score": round(compliance_score, 2),
            "tender_ready": compliance_score >= 90,
            "expiring_document_details": [
                {
                    "filename": doc.filename,
                    "doc_type": doc.doc_type,
                    "expiry_date": doc.expiry_date.isoformat(),
                    "days_until_expiry": (doc.expiry_date - today).days
                }
                for doc in expiring_soon
            ]
        })
    
    # Overall summary
    total_companies = len(companies)
    tender_ready_companies = sum(1 for comp in compliance_report if comp["tender_ready"])
    
    return {
        "summary": {
            "total_companies": total_companies,
            "tender_ready_companies": tender_ready_companies,
            "overall_readiness_rate": round(tender_ready_companies / total_companies * 100, 2) if total_companies > 0 else 0,
            "report_generated": datetime.now().isoformat()
        },
        "company_compliance": compliance_report,
        "action_items": [
            comp for comp in compliance_report 
            if comp["expiring_soon"] > 0 or comp["expired_documents"] > 0
        ]
    }

@router.get("/business_intelligence")
def generate_business_intelligence_report(db: Session = Depends(get_db)):
    """
    High-level business intelligence report combining all data sources.
    Your executive dashboard report.
    """
    # Overall document processing stats
    total_docs = db.query(Document).count()
    processed_docs = db.query(Document).filter(Document.processing_status == "processed").count()
    
    # Financial overview
    all_income = db.query(func.sum(Document.primary_amount)).filter(Document.is_income == True).scalar() or 0
    all_expenses = db.query(func.sum(Document.primary_amount)).filter(Document.is_expense == True).scalar() or 0
    
    # Recent activity (last 30 days)
    recent_cutoff = datetime.now() - timedelta(days=30)
    recent_docs = db.query(Document).filter(Document.created_at >= recent_cutoff).count()
    recent_income = db.query(func.sum(Document.primary_amount)).filter(
        and_(Document.is_income == True, Document.created_at >= recent_cutoff)
    ).scalar() or 0
    
    # Company performance
    company_performance = []
    companies = db.query(Company).all()
    
    for company in companies:
        company_docs = db.query(Document).filter(Document.company_id == company.id).count()
        company_income = db.query(func.sum(Document.primary_amount)).filter(
            and_(Document.company_id == company.id, Document.is_income == True)
        ).scalar() or 0
        
        active_projects = db.query(Project).filter(
            and_(Project.company_id == company.id, Project.status == "active")
        ).count()
        
        company_performance.append({
            "company_name": company.name,
            "documents_count": company_docs,
            "total_income": round(company_income, 2),
            "active_projects": active_projects
        })
    
    # Data quality metrics
    avg_quality = db.query(func.avg(Document.data_quality_score)).scalar() or 0
    manual_review_needed = db.query(Document).filter(Document.requires_manual_review == True).count()
    
    return {
        "executive_summary": {
            "total_documents_managed": total_docs,
            "processing_efficiency": round(processed_docs / total_docs * 100, 2) if total_docs > 0 else 0,
            "total_business_value": round(all_income, 2),
            "net_profit": round(all_income - all_expenses, 2),
            "recent_activity_score": recent_docs
        },
        "financial_health": {
            "total_income": round(all_income, 2),
            "total_expenses": round(all_expenses, 2),
            "profit_margin": round((all_income - all_expenses) / all_income * 100, 2) if all_income > 0 else 0,
            "recent_income": round(recent_income, 2)
        },
        "operational_efficiency": {
            "document_processing_rate": round(processed_docs / total_docs * 100, 2) if total_docs > 0 else 0,
            "data_quality_score": round(avg_quality * 100, 2),
            "automation_rate": round((total_docs - manual_review_needed) / total_docs * 100, 2) if total_docs > 0 else 0
        },
        "company_breakdown": company_performance,
        "recommendations": [
            "Focus on improving data quality for better analytics" if avg_quality < 0.8 else "Data quality is good",
            "Reduce manual review backlog" if manual_review_needed > 10 else "Manual review workload is manageable",
            "Recent activity is strong" if recent_docs > 50 else "Consider increasing document intake"
        ]
    }
