import os
#!/usr/bin/env python3
"""
Extracted Data API Routes
Legacy compatibility for frontend extracted data features
"""

import csv
import io
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse

from ..auth import AuthService
from ..database import get_mongo_client

router = APIRouter(prefix="/extracted-data", tags=["Extracted Data"])


@router.get("/")
async def get_extracted_data(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0),
    has_amount: Optional[bool] = Query(None),
    transaction_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    current_user: dict = Depends(AuthService.verify_token),
):
    """Get extracted data with filtering and pagination"""
    try:
        mongo_client = get_mongo_client()
        db = mongo_client.vanta_ledger
        collection = db.extracted_data

        # Build query filter
        query_filter = {}

        if min_confidence is not None:
            query_filter["confidence"] = {"$gte": min_confidence}

        if has_amount is not None:
            if has_amount:
                query_filter["amount"] = {"$exists": True, "$ne": None}
            else:
                query_filter["amount"] = {"$exists": False}

        if transaction_type:
            query_filter["transaction_type"] = transaction_type

        if category:
            query_filter["category"] = category

        # Calculate pagination
        skip = (page - 1) * limit

        # Get data with pagination
        cursor = (
            collection.find(query_filter)
            .skip(skip)
            .limit(limit)
            .sort("created_date", -1)
        )
        extracted_data = list(cursor)

        # Convert ObjectId to string for JSON serialization
        for item in extracted_data:
            if "_id" in item:
                item["_id"] = str(item["_id"])

        # Get total count for pagination
        total_count = collection.count_documents(query_filter)
        total_pages = (total_count + limit - 1) // limit

        return {
            "data": extracted_data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": total_pages,
            },
        }

    except Exception as e:
        # Return empty data structure if no extracted data exists yet
        return {
            "data": [],
            "pagination": {"page": 1, "limit": limit, "total": 0, "pages": 0},
        }


@router.get("/analytics")
async def get_extracted_data_analytics(
    current_user: dict = Depends(AuthService.verify_token),
):
    """Get analytics for extracted data"""
    try:
        mongo_client = get_mongo_client()
        db = mongo_client.vanta_ledger
        collection = db.extracted_data

        # Aggregate analytics
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_extractions": {"$sum": 1},
                    "avg_confidence": {"$avg": "$confidence"},
                    "total_amount": {"$sum": {"$toDouble": "$amount"}},
                    "high_confidence_count": {
                        "$sum": {"$cond": [{"$gte": ["$confidence", 0.8]}, 1, 0]}
                    },
                }
            }
        ]

        result = list(collection.aggregate(pipeline))

        if result:
            analytics = result[0]
            # Remove the _id field from grouping
            analytics.pop("_id", None)
        else:
            analytics = {
                "total_extractions": 0,
                "avg_confidence": 0.0,
                "total_amount": 0.0,
                "high_confidence_count": 0,
            }

        return analytics

    except Exception as e:
        return {
            "total_extractions": 0,
            "avg_confidence": 0.0,
            "total_amount": 0.0,
            "high_confidence_count": 0,
        }


@router.get("/stats")
async def get_extracted_data_stats(
    current_user: dict = Depends(AuthService.verify_token),
):
    """Get detailed statistics for extracted data"""
    try:
        mongo_client = get_mongo_client()
        db = mongo_client.vanta_ledger
        collection = db.extracted_data

        # Get category distribution
        category_pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]

        categories = list(collection.aggregate(category_pipeline))

        # Get transaction type distribution
        type_pipeline = [
            {"$group": {"_id": "$transaction_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]

        transaction_types = list(collection.aggregate(type_pipeline))

        return {
            "categories": [
                {"category": item["_id"] or "Unknown", "count": item["count"]}
                for item in categories
            ],
            "transaction_types": [
                {"type": item["_id"] or "Unknown", "count": item["count"]}
                for item in transaction_types
            ],
            "confidence_distribution": {
                "high": collection.count_documents({"confidence": {"$gte": 0.8}}),
                "medium": collection.count_documents(
                    {"confidence": {"$gte": 0.5, "$lt": 0.8}}
                ),
                "low": collection.count_documents({"confidence": {"$lt": 0.5}}),
            },
        }

    except Exception as e:
        return {
            "categories": [],
            "transaction_types": [],
            "confidence_distribution": {"high": 0, "medium": 0, "low": 0},
        }


@router.get("/export")
async def export_extracted_data(
    format: str = Query("json", regex="^(json|csv)$"),
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0),
    current_user: dict = Depends(AuthService.verify_token),
):
    """Export extracted data in JSON or CSV format"""
    try:
        mongo_client = get_mongo_client()
        db = mongo_client.vanta_ledger
        collection = db.extracted_data

        # Build query filter
        query_filter = {}
        if min_confidence is not None:
            query_filter["confidence"] = {"$gte": min_confidence}

        # Get data
        cursor = collection.find(query_filter).sort("created_date", -1)
        extracted_data = list(cursor)

        # Convert ObjectId to string
        for item in extracted_data:
            if "_id" in item:
                item["_id"] = str(item["_id"])

        if format == "json":
            # Return JSON export
            json_str = json.dumps(extracted_data, indent=2, default=str)

            return StreamingResponse(
                io.StringIO(json_str),
                media_type="application/json",
                headers={
                    "Content-Disposition": "attachment; filename=extracted_data.json"
                },
            )

        elif format == "csv":
            # Return CSV export
            if not extracted_data:
                csv_content = "No data available"
            else:
                output = io.StringIO()
                fieldnames = extracted_data[0].keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(extracted_data)
                csv_content = output.getvalue()

            return StreamingResponse(
                io.StringIO(csv_content),
                media_type="text/csv",
                headers={
                    "Content-Disposition": "attachment; filename=extracted_data.csv"
                },
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
