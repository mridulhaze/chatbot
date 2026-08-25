import logging
from typing import Dict, Any, Optional

from mcp_servers.token_mcp.server import get_token_mcp_server
from mcp_servers.knowledge_mcp.server import get_knowledge_mcp_server
from mcp_servers.document_mcp.server import get_document_mcp_server
from mcp_servers.credential_mcp.server import get_credential_mcp_server
from mcp_servers.crawler_mcp.server import get_crawler_mcp_server
from mcp_servers.enrichment_mcp.server import get_enrichment_mcp_server
from backend.core.audit import log_audit_event

logger = logging.getLogger("NU_MCP_CLIENT")

class MCPClient:
    """
    Central dispatcher for MCP tool calls.
    Translates tool requests to the appropriate MCP server with strict typing and audit logging.
    """
    def __init__(self):
        self.token_mcp = get_token_mcp_server()
        self.knowledge_mcp = get_knowledge_mcp_server()
        self.document_mcp = get_document_mcp_server()
        self.credential_mcp = get_credential_mcp_server()
        self.crawler_mcp = get_crawler_mcp_server()
        self.enrichment_mcp = get_enrichment_mcp_server()

    def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes a typed tool call against an MCP server.
        """
        logger.info(f"[MCP CALL] Server={server_name} | Tool={tool_name} | Args={arguments}")
        
        try:
            if server_name == "token_mcp":
                if tool_name == "get_services":
                    res = self.token_mcp.get_services()
                elif tool_name == "create_token":
                    res = self.token_mcp.create_token(**arguments)
                elif tool_name == "get_token_status":
                    res = self.token_mcp.get_token_status(**arguments)
                elif tool_name == "get_token_history":
                    res = self.token_mcp.get_token_history(**arguments)
                elif tool_name == "search_similar_solved_problems":
                    res = self.token_mcp.search_similar_solved_problems(**arguments)
                elif tool_name == "assign_token":
                    res = self.token_mcp.assign_token(**arguments)
                elif tool_name == "update_token_status":
                    res = self.token_mcp.update_token_status(**arguments)
                elif tool_name == "solve_token":
                    res = self.token_mcp.solve_token(**arguments)
                else:
                    return {"success": False, "data": None, "error": {"code": "UNKNOWN_TOOL", "message": f"Tool {tool_name} not found in token_mcp."}}

            elif server_name == "knowledge_mcp":
                if tool_name in ["search_nu_knowledge", "search_knowledge"]:
                    res = self.knowledge_mcp.search_nu_knowledge(**arguments)
                elif tool_name in ["search_notice", "search_notices"]:
                    res = self.knowledge_mcp.search_notices(**arguments)
                elif tool_name == "search_exam_information":
                    res = self.knowledge_mcp.search_exam_information(**arguments)
                elif tool_name == "search_admission_information":
                    res = self.knowledge_mcp.search_admission_information(**arguments)
                elif tool_name == "get_page":
                    res = self.knowledge_mcp.get_page(**arguments)
                else:
                    return {"success": False, "data": None, "error": {"code": "UNKNOWN_TOOL", "message": f"Tool {tool_name} not found in knowledge_mcp."}}

            elif server_name == "document_mcp":
                if tool_name == "search_documents":
                    res = self.document_mcp.search_documents(**arguments)
                elif tool_name == "get_document_text":
                    res = self.document_mcp.get_document_text(**arguments)
                elif tool_name == "get_document_metadata":
                    res = self.document_mcp.get_document_metadata(**arguments)
                else:
                    return {"success": False, "data": None, "error": {"code": "UNKNOWN_TOOL", "message": f"Tool {tool_name} not found in document_mcp."}}

            elif server_name == "credential_mcp":
                if tool_name == "get_user_services":
                    res = self.credential_mcp.get_user_services(**arguments)
                elif tool_name == "get_credential_status":
                    res = self.credential_mcp.get_credential_status(**arguments)
                elif tool_name == "save_service_credential":
                    res = self.credential_mcp.save_service_credential(**arguments)
                elif tool_name == "verify_service_credential":
                    res = self.credential_mcp.verify_service_credential(**arguments)
                elif tool_name == "delete_service_credential":
                    res = self.credential_mcp.delete_service_credential(**arguments)
                else:
                    return {"success": False, "data": None, "error": {"code": "UNKNOWN_TOOL", "message": f"Tool {tool_name} not found in credential_mcp."}}

            elif server_name == "crawler_mcp":
                if tool_name == "start_crawl":
                    res = self.crawler_mcp.start_crawl(**arguments)
                elif tool_name == "crawl_status":
                    res = self.crawler_mcp.crawl_status()
                elif tool_name == "pause_crawl":
                    res = self.crawler_mcp.pause_crawl()
                elif tool_name == "resume_crawl":
                    res = self.crawler_mcp.resume_crawl()
                elif tool_name == "stop_crawl":
                    res = self.crawler_mcp.stop_crawl()
                elif tool_name == "retry_failed_urls":
                    res = self.crawler_mcp.retry_failed_urls()
                elif tool_name == "get_website_map":
                    res = self.crawler_mcp.get_website_map()
                elif tool_name == "get_crawl_statistics":
                    res = self.crawler_mcp.get_crawl_statistics()
                else:
                    return {"success": False, "data": None, "error": {"code": "UNKNOWN_TOOL", "message": f"Tool {tool_name} not found in crawler_mcp."}}

            elif server_name == "enrichment_mcp":
                if tool_name == "get_enrichment_status":
                    res = self.enrichment_mcp.get_enrichment_status()
                elif tool_name == "get_recent_knowledge_updates":
                    res = self.enrichment_mcp.get_recent_knowledge_updates(**arguments)
                elif tool_name == "get_knowledge_manifest":
                    res = self.enrichment_mcp.get_knowledge_manifest()
                elif tool_name == "trigger_enrichment_cycle":
                    res = self.enrichment_mcp.trigger_enrichment_cycle(**arguments)
                else:
                    return {"success": False, "data": None, "error": {"code": "UNKNOWN_TOOL", "message": f"Tool {tool_name} not found in enrichment_mcp."}}

            else:
                return {"success": False, "data": None, "error": {"code": "UNKNOWN_SERVER", "message": f"Server {server_name} not recognized."}}

            log_audit_event(
                action="MCP_TOOL_EXECUTION",
                user_id=user_context.get("user_id") if user_context else None,
                username=user_context.get("username") if user_context else None,
                resource_type=server_name,
                resource_id=tool_name,
                details={"arguments": arguments, "success": res.get("success", False)},
                success=res.get("success", False)
            )

            return res

        except Exception as e:
            logger.error(f"MCP Call Exception on {server_name}.{tool_name}: {e}", exc_info=True)
            return {"success": False, "data": None, "error": {"code": "EXECUTION_ERROR", "message": str(e)}}

_mcp_client_instance: Optional[MCPClient] = None

def get_mcp_client() -> MCPClient:
    global _mcp_client_instance
    if _mcp_client_instance is None:
        _mcp_client_instance = MCPClient()
    return _mcp_client_instance
