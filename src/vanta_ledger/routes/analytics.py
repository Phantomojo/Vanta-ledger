from typing import List

from fastapi import APIRouter, Depends, HTTPException

from ..auth import AuthService
from ..database import get_mongo_client, get_postgres_connection
from ..services.ai_analytics_service import enhanced_ai_analytics_service
from ..services.analytics_dashboard import analytics_dashboard

router = APIRouter(tags=["Analytics"])


@router.get("/extracted-data/analytics")
async def get_analytics(current_user: dict = Depends(AuthService.verify_token)):
    """
    Retrieve aggregated statistics for financial transactions.
    Enforces RBAC and company isolation.

    Returns:
        dict: A dictionary containing the total number of transactions, total amount, average amount, minimum amount, and maximum amount across accessible financial transactions.

    Raises:
        HTTPException: If no financial transaction data is found or access is denied.
    """
    # Enforce RBAC - only admins can see all data
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    conn = get_postgres_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT
                COUNT(*) as total_transactions,
                SUM(amount) as total_amount,
                AVG(amount) as avg_amount,
                MIN(amount) as min_amount,
                MAX(amount) as max_amount
            FROM financial_transactions
        """
        )
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="No financial data found")
        return {
            "total_transactions": result[0] or 0,
            "total_amount": (
                str(result[1]) if result[1] else "0"
            ),  # Return as string to preserve precision
            "average_amount": str(result[2]) if result[2] else "0",
            "min_amount": str(result[3]) if result[3] else "0",
            "max_amount": str(result[4]) if result[4] else "0",
        }
    finally:
        cursor.close()
        conn.close()


@router.post("/ai/analyze-document/{document_id}")
async def analyze_document_ai(
    document_id: str, current_user: dict = Depends(AuthService.verify_token)
):
    """
    Analyze a processed document using AI and return the analysis results.
    Enforces company isolation and RBAC.

    Parameters:
        document_id (str): The unique identifier of the document to analyze.

    Returns:
        dict: The AI-generated analysis results for the specified document.

    Raises:
        HTTPException: If document not found or access denied.
    """
    client = get_mongo_client()
    db = client.vanta_ledger
    collection = db.processed_documents

    try:
        document = collection.find_one({"document_id": document_id})
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Enforce company isolation - users can only access documents from their company
        if current_user.get("role") != "admin":
            user_company = current_user.get("company_id")
            if not user_company or document.get("company_id") != user_company:
                raise HTTPException(
                    status_code=403, detail="Access denied to this document"
                )

        analysis = await enhanced_ai_analytics_service.analyze_document_intelligence(
            document
        )
        collection.update_one(
            {"document_id": document_id}, {"$set": {"ai_analysis": analysis}}
        )
        return analysis
    finally:
        client.close()


@router.get("/ai/company-report/{company_id}")
async def generate_company_report(
    company_id: str, current_user: dict = Depends(AuthService.verify_token)
):
    """
    Generate an AI-powered company report based on all processed documents for the specified company.

    Parameters:
        company_id (str): The unique identifier of the company for which to generate the report.

    Returns:
        dict: The generated company report containing AI-driven analytics.

    Raises:
        HTTPException: If no documents are found for the specified company.
    """
    client = get_mongo_client()
    db = client.vanta_ledger
    collection = db.processed_documents
    # Limit to prevent unbounded reads - max 1000 documents per company
    documents = list(collection.find({"company": company_id}).limit(1000))
    if not documents:
        raise HTTPException(status_code=404, detail="No documents found for company")
    report = await enhanced_ai_analytics_service.generate_company_report(
        company_id, documents
    )
    db.ai_reports.insert_one(report)
    return report


@router.get("/ai/system-analytics")
async def generate_system_analytics(
    current_user: dict = Depends(AuthService.verify_token),
):
    """
    Generate and return system-wide analytics by analyzing all processed documents in the database.

    Raises:
        HTTPException: If no processed documents are found in the database.

    Returns:
        dict: The generated system analytics report.
    """
    client = get_mongo_client()
    db = client.vanta_ledger
    collection = db.processed_documents
    # Limit to prevent unbounded reads - max 5000 documents for system analytics
    all_documents = list(collection.find({}).limit(5000))
    if not all_documents:
        raise HTTPException(status_code=404, detail="No documents found")
    analytics = await enhanced_ai_analytics_service.generate_system_analytics(
        all_documents
    )
    db.system_analytics.insert_one(analytics)
    return analytics


@router.get("/ai/reports/")
async def list_ai_reports(current_user: dict = Depends(AuthService.verify_token)):
    """
    Retrieve a list of AI-generated company reports and system analytics reports.

    Returns:
        dict: A dictionary containing up to 20 company reports and up to 10 system analytics reports from the database.
    """
    client = get_mongo_client()
    db = client.vanta_ledger
    company_reports = list(db.ai_reports.find({}, {"_id": 0}).limit(20))
    system_analytics = list(db.system_analytics.find({}, {"_id": 0}).limit(10))
    return {"company_reports": company_reports, "system_analytics": system_analytics}


@router.get("/ai/reports/{report_id}")
async def get_ai_report(
    report_id: str, current_user: dict = Depends(AuthService.verify_token)
):
    """
    Retrieve an AI-generated report by report ID from either the company or system analytics collections.

    Searches for a report matching the given ID in the `ai_reports` collection by `company_id`, and if not found, in the `system_analytics` collection by `report_date`. Raises a 404 error if no report is found.

    Parameters:
        report_id (str): The identifier for the company or system analytics report.

    Returns:
        dict: The report data if found.

    Raises:
        HTTPException: If no report is found with the given ID.
    """
    client = get_mongo_client()
    db = client.vanta_ledger
    report = db.ai_reports.find_one({"company_id": report_id}, {"_id": 0})
    if report:
        return report
    report = db.system_analytics.find_one({"report_date": report_id}, {"_id": 0})
    if report:
        return report
    raise HTTPException(status_code=404, detail="Report not found")


@router.get("/dashboard/overview")
async def get_dashboard_overview(
    current_user: dict = Depends(AuthService.verify_token),
):
    """
    Retrieve an overview of analytics dashboard data by aggregating information from both MongoDB and PostgreSQL sources.

    Returns:
        dict: A summary of key analytics metrics for the dashboard overview.
    """
    mongo_client = get_mongo_client()
    postgres_conn = get_postgres_connection()
    overview = await analytics_dashboard.get_dashboard_overview(
        mongo_client, postgres_conn
    )
    postgres_conn.close()
    return overview


@router.get("/dashboard/company/{company_id}")
async def get_company_dashboard(
    company_id: str, current_user: dict = Depends(AuthService.verify_token)
):
    """
    Retrieve the dashboard overview for a specific company by aggregating data from MongoDB and PostgreSQL.

    Parameters:
        company_id (str): The unique identifier of the company whose dashboard data is requested.

    Returns:
        dict: The aggregated dashboard data for the specified company.
    """
    mongo_client = get_mongo_client()
    postgres_conn = get_postgres_connection()
    company_dashboard = await analytics_dashboard.get_company_dashboard(
        company_id, mongo_client, postgres_conn
    )
    postgres_conn.close()
    return company_dashboard


@router.get("/analytics/financial")
async def get_financial_analytics(
    current_user: dict = Depends(AuthService.verify_token),
):
    """
    Retrieve combined financial analytics data from both MongoDB and PostgreSQL sources.

    Returns:
        dict: Aggregated financial analytics combining data from MongoDB and PostgreSQL.
    """
    mongo_client = get_mongo_client()
    postgres_conn = get_postgres_connection()
    mongo_data = await analytics_dashboard._get_mongo_analytics(mongo_client)
    postgres_data = await analytics_dashboard._get_postgres_analytics(postgres_conn)
    financial_analytics = analytics_dashboard._combine_financial_data(
        mongo_data, postgres_data
    )
    postgres_conn.close()
    return financial_analytics


@router.get("/analytics/compliance")
async def get_compliance_analytics(
    current_user: dict = Depends(AuthService.verify_token),
):
    """
    Retrieve compliance analytics metrics from MongoDB data.

    Returns:
        dict: Compliance analytics metrics extracted from MongoDB analytics data.
    """
    mongo_client = get_mongo_client()
    mongo_data = await analytics_dashboard._get_mongo_analytics(mongo_client)
    compliance_analytics = analytics_dashboard._get_compliance_metrics(mongo_data)
    return compliance_analytics


@router.get("/analytics/processing")
async def get_processing_analytics(
    current_user: dict = Depends(AuthService.verify_token),
):
    """
    Retrieve processing analytics metrics from MongoDB data.

    Returns:
        dict: Processing analytics metrics extracted from MongoDB analytics data.
    """
    mongo_client = get_mongo_client()
    mongo_data = await analytics_dashboard._get_mongo_analytics(mongo_client)
    processing_analytics = analytics_dashboard._get_processing_metrics(mongo_data)
    return processing_analytics


@router.get("/analytics/trends")
async def get_trends_analytics(current_user: dict = Depends(AuthService.verify_token)):
    """
    Retrieve trends analytics data by processing MongoDB analytics information.

    Returns:
        dict: Trends analytics data extracted from MongoDB.
    """
    mongo_client = get_mongo_client()
    mongo_data = await analytics_dashboard._get_mongo_analytics(mongo_client)
    trends_analytics = await analytics_dashboard._get_trends(mongo_data)
    return trends_analytics


@router.get("/analytics/alerts")
async def get_system_alerts(current_user: dict = Depends(AuthService.verify_token)):
    """
    Retrieve system alerts analytics data.

    Returns:
        A list or dictionary containing system alerts extracted from analytics data.
    """
    mongo_client = get_mongo_client()
    mongo_data = await analytics_dashboard._get_mongo_analytics(mongo_client)
    alerts = await analytics_dashboard._get_alerts(mongo_data)
    return alerts


@router.get("/analytics/top-performers")
async def get_top_performers(current_user: dict = Depends(AuthService.verify_token)):
    """
    Retrieve analytics data for top-performing entities from the MongoDB data source.

    Returns:
        A list or dictionary containing information about the top performers as determined by analytics processing.
    """
    mongo_client = get_mongo_client()
    mongo_data = await analytics_dashboard._get_mongo_analytics(mongo_client)
    top_performers = analytics_dashboard._get_top_performers(mongo_data)
    return top_performers


@router.get("/analytics/risk-analysis")
async def get_risk_analysis(current_user: dict = Depends(AuthService.verify_token)):
    """
    Retrieve risk analysis metrics from analytics data.

    Returns:
        dict: Risk analysis metrics extracted from MongoDB analytics data.
    """
    mongo_client = get_mongo_client()
    mongo_data = await analytics_dashboard._get_mongo_analytics(mongo_client)
    risk_analysis = analytics_dashboard._get_risk_analysis(mongo_data)
    return risk_analysis
