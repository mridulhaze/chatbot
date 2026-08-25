import logging
from typing import Dict, Any, List, Optional
from backend.services.credential_service import get_credential_service

logger = logging.getLogger("NU_CREDENTIAL_MCP_SERVER")

class CredentialMCPServer:
    """
    Official MCP Server for User Service Credentials.
    Strict Security:
    - Never exposes passwords to AI or responses.
    - Encrypts all passwords at rest with AES-256-GCM.
    - Zero arbitrary SQL.
    """
    def __init__(self):
        self.service = get_credential_service()

    def get_user_services(self, user_id: str) -> Dict[str, Any]:
        """
        MCP Tool: get_user_services
        Lists services and whether the user has configured credentials.
        """
        try:
            overview = self.service.get_user_credentials_overview(user_id)
            return {"success": True, "data": overview, "error": None}
        except Exception as e:
            logger.error(f"MCP get_user_services error: {e}", exc_info=True)
            return {"success": False, "data": None, "error": {"code": "FETCH_FAILED", "message": str(e)}}

    def get_credential_status(self, user_id: str, service_code: str) -> Dict[str, Any]:
        """
        MCP Tool: get_credential_status
        Returns configuration status (configured, status, last_verified) WITHOUT password.
        """
        try:
            st = self.service.get_credential_status(user_id, service_code)
            return {"success": True, "data": st, "error": None}
        except Exception as e:
            return {"success": False, "data": None, "error": {"code": "STATUS_ERROR", "message": str(e)}}

    def save_service_credential(
        self,
        user_id: str,
        service_code: str,
        username: str,
        password: str,
        additional_data: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        MCP Tool: save_service_credential
        Encrypts and stores service credentials. Response NEVER includes the password.
        """
        try:
            ok, msg, cred_id = self.service.save_credential(
                user_id=user_id,
                service_code=service_code,
                username=username,
                password=password,
                additional_data=additional_data,
                notes=notes
            )
            if not ok:
                return {"success": False, "data": None, "error": {"code": "SAVE_FAILED", "message": msg}}
            
            return {
                "success": True,
                "data": {
                    "service": service_code.upper(),
                    "credential_id": cred_id,
                    "status": "NOT_VERIFIED",
                    "message": msg
                },
                "error": None
            }
        except Exception as e:
            return {"success": False, "data": None, "error": {"code": "SAVE_ERROR", "message": str(e)}}

    def verify_service_credential(self, user_id: str, service_code: str) -> Dict[str, Any]:
        """
        MCP Tool: verify_service_credential
        Tests validity of saved credential.
        """
        try:
            ok, msg = self.service.verify_credential(user_id, service_code)
            return {
                "success": True,
                "data": {
                    "service": service_code.upper(),
                    "verified": ok,
                    "message": msg
                },
                "error": None
            }
        except Exception as e:
            return {"success": False, "data": None, "error": {"code": "VERIFY_ERROR", "message": str(e)}}

    def delete_service_credential(self, user_id: str, service_code: str) -> Dict[str, Any]:
        """
        MCP Tool: delete_service_credential
        Permanently deletes credential.
        """
        try:
            ok, msg = self.service.delete_credential(user_id, service_code)
            return {"success": True, "data": {"service": service_code.upper(), "message": msg}, "error": None}
        except Exception as e:
            return {"success": False, "data": None, "error": {"code": "DELETE_ERROR", "message": str(e)}}

_credential_mcp_server_instance: Optional[CredentialMCPServer] = None

def get_credential_mcp_server() -> CredentialMCPServer:
    global _credential_mcp_server_instance
    if _credential_mcp_server_instance is None:
        _credential_mcp_server_instance = CredentialMCPServer()
    return _credential_mcp_server_instance
