from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..auth import AuthService
from ..database import get_postgres_connection, get_mongo_client
from ..services.ai_analytics_service import enhanced_ai_analytics_service
from ..services.analytics_dashboard import analytics_dashboard

router = APIRouter(tags=['Analytics'])

@router.get('/extracted-data/analytics')
async def get_analytics(current_user: dict = Depends(AuthService.verify_token)):
    conn = get_postgres_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT
            COUNT(*) as total_transactions,
            SUM(amount) as total_amount,
            AVG(amount) as avg_amount,
            MIN(amount) as min_amount,
            MAX(amount) as max_amount
        FROM financial_transactions
    ''')
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if not result:
        raise HTTPException(status_code=404, detail='No financial data found')
    return {
        'total_transactions': result[0] or 0,
        'total_amount': float(result[1]) if result[1] else 0,
        'average_amount': float(result[2]) if result[2] else 0,
        'min_amount': float(result[3]) if result[3] else 0,
        'max_amount': float(result[4]) if result[4] else 0
    }

@router.post('/ai/analyze-document/{document_id}')
async def analyze_document_ai(document_id: str, current_user: dict = Depends(AuthService.verify_token)):
    client = get_mongo_client()
    db = client.vanta_ledger
    collection = db.processed_documents
    document = collection.find_one({'document_id': document_id})
    if not document:
        raise HTTPException(status_code=404, detail='Document not found')
    analysis = await enhanced_ai_analytics_service.analyze_document_intelligence(document)
    collection.update_one({'document_id': document_id}, {'$set': {'ai_analysis': analysis}})
    return analysis

@router.get('/ai/company-report/{company_id}')
async def generate_company_report(company_id: str, current_user: dict = Depends(AuthService.verify_token)):
    client = get_mongo_client()
    db = client.vanta_ledger
    collection = db.processed_documents
    documents = list(collection.find({'company': company_id}))
    if not documents:
        raise HTTPException(status_code=404, detail='No documents found for company')
    report = await enhanced_ai_analytics_service.generate_company_report(company_id, documents)
    db.ai_reports.insert_one(report)
    return report

@router.get('/ai/system-analytics')
async def generate_system_analytics(current_user: dict = Depends(AuthService.verify_token)):
    client = get_mongo_client()
    db = client.vanta_ledger
    collection = db.processed_documents
    all_documents = list(collection.find({}))
    if not all_documents:
        raise HTTPException(status_code=404, detail='No documents found')
    analytics = await enhanced_ai_analytics_service.generate_system_analytics(all_documents)
    db.system_analytics.insert_one(analytics)
    return analytics

@router.get('/ai/reports/')
async def list_ai_reports(current_user: dict = Depends(AuthService.verify_token)):
    client = get_mongo_client()
    db = client.vanta_ledger
    company_reports = list(db.ai_reports.find({}, {'_id': 0}).limit(20))
    system_analytics = list(db.system_analytics.find({}, {'_id': 0}).limit(10))
    return {
        'company_reports': company_reports,
        'system_analytics': system_analytics
    }

@router.get('/ai/reports/{report_id}')
async def get_ai_report(report_id: str, current_user: dict = Depends(AuthService.verify_token)):
    client = get_mongo_client()
    db = client.vanta_ledger
    report = db.ai_reports.find_one({'company_id': report_id}, {'_id': 0})
    if report:
        return report
    report = db.system_analytics.find_one({'report_date': report_id}, {'_id': 0})
    if report:
        return report
    raise HTTPException(status_code=404, detail='Report not found')

@router.get('/dashboard/overview')
async def get_dashboard_overview(current_user: dict = Depends(AuthService.verify_token)):
    mongo_client = get_mongo_client()
    postgres_conn = get_postgres_connection()
    overview = await analytics_dashboard.get_dashboard_overview(mongo_client, postgres_conn)
    postgres_conn.close()
    return overview

@router.get('/dashboard/company/{company_id}')
async def get_company_dashboard(company_id: str, current_user: dict = Depends(AuthService.verify_token)):
    mongo_client = get_mongo_client()
    postgres_conn = get_postgres_connection()
    company_dashboard = await analytics_dashboard.get_company_dashboard(company_id, mongo_client, postgres_conn)
    postgres_conn.close()
    return company_dashboard

@router.get('/analytics/financial')
async def get_financial_analytics(current_user: dict = Depends(AuthService.verify_token)):
    mongo_client = get_mongo_client()
    postgres_conn = get_postgres_connection()
    mongo_data = await analytics_dashboard._get_mongo_analytics(mongo_client)
    postgres_data = await analytics_dashboard._get_postgres_analytics(postgres_conn)
    financial_analytics = analytics_dashboard._combine_financial_data(mongo_data, postgres_data)
    postgres_conn.close()
    return financial_analytics

@router.get('/analytics/compliance')
async def get_compliance_analytics(current_user: dict = Depends(AuthService.verify_token)):
    mongo_client = get_mongo_client()
    mongo_data = await analytics_dashboard._get_mongo_analytics(mongo_client)
    compliance_analytics = analytics_dashboard._get_compliance_metrics(mongo_data)
    return compliance_analytics

@router.get('/analytics/processing')
async def get_processing_analytics(current_user: dict = Depends(AuthService.verify_token)):
    mongo_client = get_mongo_client()
    mongo_data = await analytics_dashboard._get_mongo_analytics(mongo_client)
    processing_analytics = analytics_dashboard._get_processing_metrics(mongo_data)
    return processing_analytics

@router.get('/analytics/trends')
async def get_trends_analytics(current_user: dict = Depends(AuthService.verify_token)):
    mongo_client = get_mongo_client()
    mongo_data = await analytics_dashboard._get_mongo_analytics(mongo_client)
    trends_analytics = await analytics_dashboard._get_trends(mongo_data)
    return trends_analytics

@router.get('/analytics/alerts')
async def get_system_alerts(current_user: dict = Depends(AuthService.verify_token)):
    mongo_client = get_mongo_client()
    mongo_data = await analytics_dashboard._get_mongo_analytics(mongo_client)
    alerts = await analytics_dashboard._get_alerts(mongo_data)
    return alerts

@router.get('/analytics/top-performers')
async def get_top_performers(current_user: dict = Depends(AuthService.verify_token)):
    mongo_client = get_mongo_client()
    mongo_data = await analytics_dashboard._get_mongo_analytics(mongo_client)
    top_performers = analytics_dashboard._get_top_performers(mongo_data)
    return top_performers

@router.get('/analytics/risk-analysis')
async def get_risk_analysis(current_user: dict = Depends(AuthService.verify_token)):
    mongo_client = get_mongo_client()
    mongo_data = await analytics_dashboard._get_mongo_analytics(mongo_client)
    risk_analysis = analytics_dashboard._get_risk_analysis(mongo_data)
    return risk_analysis
