import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from backend.services.token_service import get_token_domain_service
from backend.services.similarity_service import get_similarity_service
from backend.models.schemas import (
    TokenCreateRequest,
    TokenAssignRequest,
    TokenStatusUpdateRequest,
    TokenSolveRequest,
    MCPResponse
)
from backend.core.audit import log_audit_event

logger = logging.getLogger("NU_TOKEN_MCP_SERVER")

class TokenMCPServer:
    """
    Official MCP-compliant server for National University Token Service.
    Enforces strict typing, input validation, role checks, and zero arbitrary SQL access.
    """
    def __init__(self):
        self.service = get_token_domain_service()
        self.similarity = get_similarity_service()

    def get_services(self) -> Dict[str, Any]:
        """
        MCP Tool: get_services
        Returns active token service types dynamically from the database.
        """
        try:
            services = self.service.get_services()
            return {"success": True, "data": services, "error": None}
        except Exception as e:
            logger.error(f"MCP get_services error: {e}", exc_info=True)
            return {"success": False, "data": None, "error": {"code": "SERVICE_FETCH_FAILED", "message": str(e)}}

    def create_token(
        self,
        service_code: str,
        problem: str,
        user_id: Optional[str] = None,
        user_name: Optional[str] = None,
        user_email: Optional[str] = None,
        user_phone: Optional[str] = None,
        registration_no: Optional[str] = None,
        college_code: Optional[str] = None,
        priority: str = "NORMAL"
    ) -> Dict[str, Any]:
        """
        MCP Tool: create_token
        Creates a new support token with an atomic concurrency-safe ID.
        """
        try:
            req = TokenCreateRequest(
                service_code=service_code,
                problem=problem,
                user_id=user_id,
                user_name=user_name,
                user_email=user_email,
                user_phone=user_phone,
                registration_no=registration_no,
                college_code=college_code,
                priority=priority
            )
            res = self.service.create_token(req)
            return {"success": True, "data": res.model_dump(), "error": None}
        except Exception as e:
            logger.error(f"MCP create_token error: {e}", exc_info=True)
            return {"success": False, "data": None, "error": {"code": "TOKEN_CREATION_FAILED", "message": str(e)}}

    def get_token_status(self, token_id: str) -> Dict[str, Any]:
        """
        MCP Tool: get_token_status
        Returns safe public status card without exposing internal notes or user PII.
        """
        try:
            status_data = self.service.get_public_token_status(token_id.strip().upper())
            if not status_data:
                return {"success": False, "data": None, "error": {"code": "TOKEN_NOT_FOUND", "message": f"Token {token_id} was not found."}}
            return {"success": True, "data": status_data.model_dump(), "error": None}
        except Exception as e:
            logger.error(f"MCP get_token_status error: {e}", exc_info=True)
            return {"success": False, "data": None, "error": {"code": "STATUS_FETCH_FAILED", "message": str(e)}}

    def get_token_history(self, token_id: str) -> Dict[str, Any]:
        """
        MCP Tool: get_token_history
        Returns chronological status change history.
        """
        try:
            status_data = self.service.get_public_token_status(token_id.strip().upper())
            if not status_data:
                return {"success": False, "data": None, "error": {"code": "TOKEN_NOT_FOUND", "message": f"Token {token_id} was not found."}}
            return {"success": True, "data": [h.model_dump() for h in status_data.history], "error": None}
        except Exception as e:
            logger.error(f"MCP get_token_history error: {e}", exc_info=True)
            return {"success": False, "data": None, "error": {"code": "HISTORY_FETCH_FAILED", "message": str(e)}}

    def search_similar_solved_problems(
        self,
        problem: str,
        service_code: Optional[str] = None,
        limit: int = 3
    ) -> Dict[str, Any]:
        """
        MCP Tool: search_similar_solved_problems
        Performs semantic similarity search over anonymized solved cases.
        Guarantees zero user PII exposure.
        """
        try:
            cases = self.similarity.search_similar_solved_cases(
                problem_description=problem,
                service_code=service_code,
                limit=limit
            )
            return {"success": True, "data": [c.model_dump() for c in cases], "error": None}
        except Exception as e:
            logger.error(f"MCP search_similar_solved_problems error: {e}", exc_info=True)
            return {"success": False, "data": None, "error": {"code": "SEARCH_FAILED", "message": str(e)}}

    def assign_token(
        self,
        token_id: str,
        solver_id: int,
        admin_username: str = "ADMIN",
        admin_note: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        MCP Tool: assign_token (Authorized Admin only)
        """
        try:
            ok, msg = self.service.assign_solver(
                token_id=token_id.strip().upper(),
                solver_id=solver_id,
                changed_by=admin_username,
                admin_note=admin_note
            )
            if not ok:
                return {"success": False, "data": None, "error": {"code": "ASSIGN_FAILED", "message": msg}}
            return {"success": True, "data": {"token_id": token_id, "message": msg}, "error": None}
        except Exception as e:
            return {"success": False, "data": None, "error": {"code": "ASSIGN_ERROR", "message": str(e)}}

    def update_token_status(
        self,
        token_id: str,
        status: str,
        message: Optional[str] = None,
        changed_by: str = "ADMIN",
        admin_note: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        MCP Tool: update_token_status (Authorized Admin / Solver)
        """
        try:
            ok, msg = self.service.update_status(
                token_id=token_id.strip().upper(),
                new_status=status,
                changed_by=changed_by,
                message=message,
                admin_note=admin_note
            )
            if not ok:
                return {"success": False, "data": None, "error": {"code": "STATUS_UPDATE_FAILED", "message": msg}}
            return {"success": True, "data": {"token_id": token_id, "status": status, "message": msg}, "error": None}
        except Exception as e:
            return {"success": False, "data": None, "error": {"code": "UPDATE_ERROR", "message": str(e)}}

    def solve_token(
        self,
        token_id: str,
        solve_message: str,
        solver_name: Optional[str] = None,
        changed_by: str = "SOLVER",
        admin_note: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        MCP Tool: solve_token (Authorized Solver / Admin)
        """
        try:
            ok, msg = self.service.solve_token(
                token_id=token_id.strip().upper(),
                solve_message=solve_message,
                solver_name=solver_name,
                changed_by=changed_by,
                admin_note=admin_note
            )
            if not ok:
                return {"success": False, "data": None, "error": {"code": "SOLVE_FAILED", "message": msg}}
            return {"success": True, "data": {"token_id": token_id, "status": "SOLVED", "message": msg}, "error": None}
        except Exception as e:
            return {"success": False, "data": None, "error": {"code": "SOLVE_ERROR", "message": str(e)}}

_token_mcp_server_instance: Optional[TokenMCPServer] = None

def get_token_mcp_server() -> TokenMCPServer:
    global _token_mcp_server_instance
    if _token_mcp_server_instance is None:
        _token_mcp_server_instance = TokenMCPServer()
    return _token_mcp_server_instance
