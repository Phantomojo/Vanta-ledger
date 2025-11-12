#!/usr/bin/env python3
"""
Vanta Ledger - Minimal Testing Application
===========================================

TESTING ONLY - Minimal FastAPI application for development and testing.

Purpose:
- Quick testing of basic functionality
- Development environment verification
- CI/CD smoke tests
- Minimal dependencies

This version:
- No database connections required
- Basic CORS only
- Simple auth routes for testing
- Minimal middleware

DO NOT USE IN PRODUCTION - Use main.py instead.

Usage:
    uvicorn src.vanta_ledger.main_simple:app --reload
"""

import os
from datetime import datetime
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import settings
from .config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Vanta Ledger API",
    description="Advanced document processing and financial data management system",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend development server
        "http://localhost:5173",  # Vite development server
        "http://localhost:8080",  # Alternative frontend port
        "http://127.0.0.1:3000",  # Local development
        "http://127.0.0.1:5173",  # Local Vite development
        "http://127.0.0.1:8080",  # Alternative local port
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """
    Handles the root endpoint and returns a status message with the API version.

    Returns:
        dict: A JSON object containing a status message and the API version.
    """
    return {"message": "Vanta Ledger API is running", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    """
    Return the current health status, timestamp, and API version for service monitoring.

    Returns:
        dict: A JSON-serializable dictionary with keys "status", "timestamp", and "version".
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0",
    }


@app.get("/test")
async def test_endpoint():
    """
    Handles GET requests to the /test endpoint, returning a success message for verification purposes.

    Returns:
        dict: A JSON object with a confirmation message and success status.
    """
    return {"message": "Test endpoint working", "status": "success"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8500)  # Use localhost for security
