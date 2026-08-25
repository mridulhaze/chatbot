import pytest
from mcp_servers.token_mcp.server import get_token_mcp_server
from mcp_servers.knowledge_mcp.server import get_knowledge_mcp_server
from mcp_servers.document_mcp.server import get_document_mcp_server

def test_token_mcp_get_services():
    token_mcp = get_token_mcp_server()
    res = token_mcp.get_services()
    assert res["success"] is True
    assert isinstance(res["data"], list)
    assert len(res["data"]) > 0
    assert any(s["service_code"] == "EMS" for s in res["data"])

def test_token_mcp_create_and_status():
    token_mcp = get_token_mcp_server()
    res = token_mcp.create_token(
        service_code="CERTIFICATE",
        problem="Certificate delivery status inquiry",
        user_name="Karim Khan"
    )
    assert res["success"] is True
    token_id = res["data"]["token_id"]

    status_res = token_mcp.get_token_status(token_id=token_id)
    assert status_res["success"] is True
    assert status_res["data"]["token_id"] == token_id
    assert status_res["data"]["status"] == "PENDING"

def test_knowledge_mcp_tools():
    kmcp = get_knowledge_mcp_server()
    res = kmcp.search_notice(query="examination", limit=2)
    assert res["success"] is True
    assert isinstance(res["data"], list)

def test_document_mcp_tools():
    dmcp = get_document_mcp_server()
    res = dmcp.search_documents(query="form", limit=2)
    assert res["success"] is True
    assert isinstance(res["data"], list)
