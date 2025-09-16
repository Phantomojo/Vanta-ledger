#!/usr/bin/env python3
"""
Document Analysis Dashboard

This script analyzes the documents in your database and provides insights
about your document landscape.
"""

import sys
from pathlib import Path
from sqlalchemy import func, desc
from datetime import datetime, timedelta

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from vanta_ledger.database import SessionLocal, Document, Company, DocumentAnalysis
import logging
logger = logging.getLogger(__name__)

def analyze_document_landscape():
    """Analyze the overall document landscape"""
    db = SessionLocal()
    
    logger.info("📊 Vanta Ledger Document Analysis Dashboard")
    logger.info("=")
    
    try:
        # Basic statistics
        total_docs = db.query(Document).count()
        total_companies = db.query(Company).count()
        
        logger.info(f"\n📈 Basic Statistics:")
        logger.info(f"   Total Documents: {total_docs:,}")
        logger.info(f"   Total Companies: {total_companies}")
        
        if total_docs == 0:
            logger.info("\n⚠️  No documents found in database.")
            logger.info("   Run the Paperless-ngx integration first:")
            logger.info("   cd src && python -m vanta_ledger.paperless_integration")
            return
        
        # Document categories
        logger.info(f"\n📁 Document Categories:")
        categories = db.query(
            Document.doc_category,
            func.count(Document.id).label('count')
        ).group_by(Document.doc_category).order_by(desc('count')).all()
        
        for category, count in categories:
            percentage = (count / total_docs) * 100
            logger.info(f"   {category.title()}: {count:,} ({percentage:.1f}%)")
        
        # Document types
        logger.info(f"\n📄 Document Types:")
        doc_types = db.query(
            Document.doc_type,
            func.count(Document.id).label('count')
        ).group_by(Document.doc_type).order_by(desc('count')).limit(10).all()
        
        for doc_type, count in doc_types:
            percentage = (count / total_docs) * 100
            logger.info(f"   {doc_type}: {count:,} ({percentage:.1f}%)")
        
        # Companies with most documents
        logger.info(f"\n🏢 Companies by Document Count:")
        company_docs = db.query(
            Company.name,
            func.count(Document.id).label('count')
        ).join(Document).group_by(Company.name).order_by(desc('count')).limit(10).all()
        
        for company, count in company_docs:
            percentage = (count / total_docs) * 100
            logger.info(f"   {company}: {count:,} ({percentage:.1f}%)")
        
        # Financial analysis
        logger.info(f"\n💰 Financial Analysis:")
        financial_docs = db.query(Document).filter(
            Document.doc_category == 'financial'
        ).count()
        
        total_amount = db.query(func.sum(Document.amount)).filter(
            Document.amount.isnot(None)
        ).scalar() or 0
        
        avg_amount = db.query(func.avg(Document.amount)).filter(
            Document.amount.isnot(None)
        ).scalar() or 0
        
        logger.info(f"   Financial Documents: {financial_docs:,}")
        logger.info(f"   Total Amount Tracked: KES {total_amount:,.2f}")
        logger.info(f"   Average Document Amount: KES {avg_amount:,.2f}")
        
        # Document processing timeline
        logger.info(f"\n📅 Document Processing Timeline:")
        recent_docs = db.query(Document).order_by(desc(Document.created_at)).limit(5).all()
        
        for doc in recent_docs:
            days_ago = (datetime.now() - doc.created_at).days
            logger.info(f"   {doc.filename} - {days_ago} days ago")
        
        # Analysis quality
        logger.info(f"\n🔍 Analysis Quality:")
        high_confidence = db.query(DocumentAnalysis).filter(
            DocumentAnalysis.confidence_score >= 0.7
        ).count()
        
        total_analysis = db.query(DocumentAnalysis).count()
        
        if total_analysis > 0:
            quality_percentage = (high_confidence / total_analysis) * 100
            logger.info(f"   High Confidence Analysis: {high_confidence:,} ({quality_percentage:.1f}%)")
            logger.info(f"   Total Analyzed: {total_analysis:,}")
        
        # Recommendations
        logger.info(f"\n💡 Recommendations:")
        
        # Check for missing company assignments
        unassigned_docs = db.query(Document).filter(
            Document.company_id.is_(None)
        ).count()
        
        if unassigned_docs > 0:
            logger.info(f"   ⚠️  {unassigned_docs:,} documents need company assignment")
        
        # Check for expired documents
        expired_docs = db.query(Document).filter(
            Document.expiry_date < datetime.now().date()
        ).count()
        
        if expired_docs > 0:
            logger.info(f"   ⚠️  {expired_docs:,} documents have expired")
        
        # Check for documents without amounts
        docs_without_amounts = db.query(Document).filter(
            Document.amount.is_(None),
            Document.doc_category == 'financial'
        ).count()
        
        if docs_without_amounts > 0:
            logger.info(f"   ⚠️  {docs_without_amounts:,} financial documents need amount extraction")
        
        logger.info(f"\n✅ Analysis complete!")
        
    except Exception as e:
        logger.error(f"❌ Error during analysis: {e}")
    finally:
        db.close()

def show_document_details():
    """Show detailed information about specific documents"""
    db = SessionLocal()
    
    logger.info(f"\n📋 Recent Document Details:")
    logger.info("-")
    
    try:
        recent_docs = db.query(Document).order_by(desc(Document.created_at)).limit(10).all()
        
        for doc in recent_docs:
            logger.info(f"\n📄 {doc.filename}")
            logger.info(f"   Type: {doc.doc_type}")
            logger.info(f"   Category: {doc.doc_category}")
            logger.info(f"   Company: {doc.company.name if doc.company else ")
            logger.info(f"   Amount: KES {doc.amount:,.2f}")
            logger.info(f"   Created: {doc.created_at.strftime(")}")
            
            if doc.ocr_text:
                preview = doc.ocr_text[:100].replace('\n', ' ') + "..."
                logger.info(f"   Preview: {preview}")
    
    except Exception as e:
        logger.error(f"❌ Error showing document details: {e}")
    finally:
        db.close()

def main():
    """Main function"""
    analyze_document_landscape()
    show_document_details()
    
    logger.info(f"\n🎯 Next Steps:")
    logger.info("1. Assign companies to unassigned documents")
    logger.info("2. Extract amounts from financial documents")
    logger.info("3. Review and update expired documents")
    logger.info("4. Set up automated tagging and categorization")

if __name__ == "__main__":
    main() 