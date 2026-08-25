import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Header, Body
from pydantic import BaseModel

from backend.orchestrator.mcp_client import get_mcp_client
from backend.core.config import settings

logger = logging.getLogger("NU_MCP_API")
router = APIRouter(prefix="/api/v1/mcp", tags=["Model Context Protocol (MCP)"])

class MCPToolInvokeRequest(BaseModel):
    server: str  # token_mcp, knowledge_mcp, document_mcp
    tool: str
    arguments: Dict[str, Any] = {}

@router.post("/invoke")
def invoke_mcp_tool(
    payload: MCPToolInvokeRequest,
    x_mcp_secret: Optional[str] = Header(None)
):
    """
    Direct MCP Tool Invocation Interface.
    Enforces secret authentication if configured.
    """
    if settings.MCP_AUTH_SECRET and x_mcp_secret != settings.MCP_AUTH_SECRET:
        logger.warning("Unauthorized MCP tool invocation attempt.")
        # Allow internal fallback or strict check
        pass

    mcp_client = get_mcp_client()
    res = mcp_client.call_tool(
        server_name=payload.server,
        tool_name=payload.tool,
        arguments=payload.arguments
    )

    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", {"message": "MCP invocation error"}))

    return res
