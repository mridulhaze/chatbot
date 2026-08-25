import pytest
from backend.orchestrator.intent import get_intent_classifier
from backend.orchestrator.router import get_skill_router
from backend.orchestrator.skill_registry import get_skill_registry
from backend.orchestrator.mcp_client import get_mcp_client

def test_skill_registry_discovery():
    registry = get_skill_registry()
    skills = registry.list_skills()
    assert "token_service" in skills
    assert "nu_general" in skills
    assert "examination" in skills
    assert "admission" in skills

def test_intent_classification():
    classifier = get_intent_classifier()

    # Token ID Pattern
    intent, entities = classifier.classify("Check status of NU-2026-000123")
    assert intent == "TOKEN_STATUS"
    assert entities.get("token_id") == "NU-2026-000123"

    # Exam Query
    intent, entities = classifier.classify("Honours 4th year exam routine 2026")
    assert intent == "EXAM_QUERY"

    # Admission Query
    intent, entities = classifier.classify("When is Honours 1st year admission release slip?")
    assert intent == "ADMISSION_QUERY"

def test_skill_routing_rules():
    router = get_skill_router()
    
    # Priority 1: Token ID -> Token Service Skill
    assert router.route("TOKEN_STATUS", {"token_id": "NU-2026-000123"}) == "token_service"

    # Priority 2: Token Service workflow -> Token Service Skill
    assert router.route("TOKEN_SERVICE_MENU", {}) == "token_service"

    # Priority 3: Exam -> examination Skill
    assert router.route("EXAM_QUERY", {}) == "examination"

    # Default -> nu_general Skill
    assert router.route("GENERAL_NU_QUERY", {}) == "nu_general"

def test_mcp_client_execution():
    client = get_mcp_client()
    res = client.call_tool("token_mcp", "get_services", {})
    assert res["success"] is True
    assert isinstance(res["data"], list)
