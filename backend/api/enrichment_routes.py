"""
Enrichment API Routes
Exposes endpoints for monitoring 24/7 knowledge enrichment agents, querying knowledge manifests, and triggering learning cycles.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import PlainTextResponse
from typing import Dict, Any, List, Optional

from backend.agents.autonomous_24x7_worker import get_24x7_worker
from backend.agents.knowledge_provenance import get_knowledge_provenance, CHANGELOG_MD_PATH
from backend.core.security import require_roles, Role

router = APIRouter(prefix="/api/v1/enrichment", tags=["Autonomous Knowledge Enrichment Agents"])

@router.get("/status")
def get_enrichment_agent_status() -> Dict[str, Any]:
    """Returns 24/7 autonomous enrichment worker telemetry and statistics."""
    worker = get_24x7_worker()
    return {"success": True, "data": worker.get_status()}

@router.get("/manifest")
def get_knowledge_manifest() -> Dict[str, Any]:
    """Returns the machine-readable RFC 8259 knowledge manifest for other AI agents."""
    provenance = get_knowledge_provenance()
    manifest = provenance.get_manifest()
    return {"success": True, "data": manifest}

@router.get("/updates")
def get_recent_updates(limit: int = Query(25, ge=1, le=100)) -> Dict[str, Any]:
    """Returns recent structured knowledge update entries."""
    provenance = get_knowledge_provenance()
    records = provenance.get_recent_updates_stream(limit=limit)
    return {"success": True, "count": len(records), "data": records}

@router.get("/changelog", response_class=PlainTextResponse)
def get_knowledge_changelog_markdown() -> str:
    """Returns the Markdown version of the AI Knowledge Changelog."""
    if CHANGELOG_MD_PATH.exists():
        with open(CHANGELOG_MD_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return "# 📜 National University AI Knowledge Changelog\nNo updates recorded yet."

@router.post("/trigger")
def trigger_enrichment_cycle(
    batch_size: int = Query(10, ge=1, le=50),
    current_user: Any = Depends(require_roles([Role.SOLVER, Role.ADMIN, Role.SUPER_ADMIN]))
) -> Dict[str, Any]:
    """Manually triggers an immediate batch analysis and enrichment cycle."""
    worker = get_24x7_worker()
    result = worker.run_enrichment_cycle(batch_size=batch_size)
    return {"success": True, "data": result}
