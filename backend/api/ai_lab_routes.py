"""
National University AI Lab — FastAPI Management & Telemetry Endpoints
Provides real-time state, control triggers (START, PAUSE, STOP, RESUME), task queues, and cycle reports.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from ai_lab.lab_state import get_lab_state, LAB_DIR
from ai_lab.orchestrator_loop import get_lab_orchestrator

logger = logging.getLogger("NU_AI_LAB_API")
router = APIRouter(prefix="/api/v1/lab", tags=["AI Lab (Autonomous R&D)"])

class LabControlRequest(BaseModel):
    action: str  # "START", "PAUSE", "STOP", "RESUME", "TRIGGER_CYCLE"

@router.get("/status")
def get_lab_status():
    """Returns real-time 24/7 AI Lab operational telemetry, agent status, and scores."""
    state_mgr = get_lab_state()
    return state_mgr.get_state()

@router.post("/control")
def execute_lab_control(payload: LabControlRequest):
    """Controls the autonomous loop state."""
    orchestrator = get_lab_orchestrator()
    state_mgr = get_lab_state()
    act = payload.action.upper()

    if act == "START":
        orchestrator.start_loop()
        return {"status": "SUCCESS", "mode": "RUNNING", "message": "24/7 Autonomous AI Lab started."}
    elif act == "PAUSE":
        orchestrator.pause_loop()
        return {"status": "SUCCESS", "mode": "PAUSED", "message": "Autonomous AI Lab paused safely."}
    elif act == "RESUME":
        orchestrator.resume_loop()
        return {"status": "SUCCESS", "mode": "RUNNING", "message": "Autonomous AI Lab resumed."}
    elif act == "STOP":
        orchestrator.stop_loop()
        return {"status": "SUCCESS", "mode": "STOPPED", "message": "Autonomous AI Lab cleanly stopped."}
    elif act == "TRIGGER_CYCLE":
        report = orchestrator.execute_single_cycle()
        return {"status": "SUCCESS", "cycle_report": report}
    else:
        raise HTTPException(status_code=400, detail=f"Invalid action '{payload.action}'. Valid: START, PAUSE, STOP, RESUME, TRIGGER_CYCLE")

@router.get("/tasks")
def get_lab_tasks():
    """Returns all tasks created by Agent 1 and processed by Agent 2."""
    state_mgr = get_lab_state()
    return state_mgr.get_all_tasks()

@router.get("/reports")
def get_recent_reports(limit: int = 20):
    """Returns list of recent cycle reports."""
    reports = []
    for p in sorted((LAB_DIR / "cycle_reports").glob("*.json"), reverse=True)[:limit]:
        try:
            reports.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            pass
    return reports
