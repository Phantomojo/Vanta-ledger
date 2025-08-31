import os
#!/usr/bin/env python3
"""
System Health Routes
Provides real-time system and database health snapshots and optional AI analysis
"""

import asyncio
import json
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException

from ..services.system_analysis_service import SystemAnalysisService

router = APIRouter(prefix="/health/system", tags=["System Health"])


@router.get("")
async def system_health_snapshot():
    """
    Return a real-time snapshot of system and database health (no AI).
    """
    svc = SystemAnalysisService()
    return svc.get_snapshot()


@router.get("/ai")
async def system_health_ai(include_logs: bool = True, log_lines: int = 800):
    """
    Return an AI-generated analysis of current system health. Requires GitHub Models to be enabled.
    """
    svc = SystemAnalysisService()
    result = await svc.analyze_system_health(include_logs=include_logs, log_lines=log_lines)
    if isinstance(result, dict) and result.get("error"):
        # If service isn't enabled or other error, return 503 to indicate not available
        raise HTTPException(status_code=503, detail=result.get("error"))
    return result


@router.websocket("/ws")
async def system_health_ws(ws: WebSocket, interval_seconds: Optional[int] = 2):
    """
    WebSocket streaming endpoint sending periodic health snapshots.
    """
    await ws.accept()
    svc = SystemAnalysisService()
    interval = max(1, int(interval_seconds or 2))
    try:
        while True:
            snapshot = svc.get_snapshot()
            await ws.send_text(json.dumps(snapshot))
            await asyncio.sleep(interval)
    except WebSocketDisconnect:
        # Client disconnected gracefully
        return
    except Exception as e:
        # Send error once then close
        await ws.send_text(json.dumps({"error": str(e)}))
        await ws.close()