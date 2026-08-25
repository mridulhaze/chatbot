import os
from fastapi.testclient import TestClient

from backend.app import app
from token_service.db import init_token_database, get_token_db_connection
from token_service.service import get_token_service
from token_service.models import TokenCreateRequest, TokenSolveRequest, TokenAssignRequest, TokenStatusUpdateRequest
from backend.rag_engine import get_rag_engine

client = TestClient(app)
init_token_database()

def test_token_service_types_and_solvers_seeded():
    svc = get_token_service()
    services = svc.get_services()
    assert len(services) >= 10
    service_codes = [s["service_code"] for s in services]
    assert "FORM_FILLUP" in service_codes
    assert "EMS" in service_codes
    assert "CERTIFICATE" in service_codes
    assert "RESCRUTINY" in service_codes

    solvers = svc.get_solvers()
    assert len(solvers) >= 5
    solver_names = [s["solver_name"] for s in solvers]
    assert "ICT Support Team" in solver_names

def test_atomic_token_id_generation_and_creation():
    svc = get_token_service()
    req = TokenCreateRequest(
        service_type="FORM_FILLUP",
        problem="Payment completed but status shows pending in student portal",
        user_name="Test Student",
        user_phone="01700000000",
        registration_no="2026123456",
        priority="NORMAL"
    )
    res = svc.create_token(req)
    assert res.success is True
    assert res.token_id.startswith("NU-2026-")
    assert res.status == "PENDING"

    # Verify history
    details = svc.get_public_token_details(res.token_id)
    assert details is not None
    assert details.token_id == res.token_id
    assert len(details.history) >= 1
    assert details.history[0].new_status == "PENDING"

def test_token_lifecycle_assign_and_solve():
    svc = get_token_service()
    req = TokenCreateRequest(
        service_type="EMS",
        problem="Cannot login to EMS portal with college roll",
        user_name="Rahim Mia",
        user_phone="01800000000"
    )
    res = svc.create_token(req)
    token_id = res.token_id

    # 1. Assign solver
    solvers = svc.get_solvers()
    ict_solver = next(s for s in solvers if "ICT" in s["solver_name"])
    assigned = svc.assign_token(token_id, solver_id=ict_solver["id"], changed_by="ADMIN")
    assert assigned is True

    details_assigned = svc.get_public_token_details(token_id)
    assert details_assigned.status == "ASSIGNED"
    assert details_assigned.solver_name == ict_solver["solver_name"]

    # 2. Mark Processing
    processed = svc.update_status(token_id, "PROCESSING", changed_by="ICT Support Team", message="Investigating credential sync")
    assert processed is True
    assert svc.get_public_token_details(token_id).status == "PROCESSING"

    # 3. Solve Token
    solve_msg = "EMS account credentials have been synchronized and password reset successfully."
    solved = svc.solve_token(token_id, solve_message=solve_msg, solver_name="ICT Support Team")
    assert solved is True

    details_solved = svc.get_public_token_details(token_id)
    assert details_solved.status == "SOLVED"
    assert details_solved.solve_message == solve_msg
    assert details_solved.solved_date is not None
    assert len(details_solved.history) >= 4

def test_token_public_endpoint_privacy():
    """Verify that public endpoints never expose admin notes or sensitive PII."""
    svc = get_token_service()
    req = TokenCreateRequest(
        service_type="CERTIFICATE",
        problem="Delay in original certificate issuance",
        user_name="Private Student Name",
        user_phone="01999999999"
    )
    res = svc.create_token(req)
    svc.update_status(res.token_id, "PROCESSING", admin_note="Internal confidential security review")

    # Call Public API
    response = client.get(f"/api/token/{res.token_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["token_id"] == res.token_id
    assert "admin_note" not in data  # Never exposed in public response
    assert "user_phone" not in data  # Never exposed in public response

def test_instant_token_and_service_attachment():
    svc = get_token_service()
    
    # 1. Instant generation
    res = svc.generate_instant_token()
    assert res.success is True
    assert res.token_id.startswith("NU-2026-")
    assert res.status == "PENDING"
    t_id = res.token_id

    # 2. Attach service
    ok = svc.set_token_service(token_id=t_id, service_code="RESCRUTINY", problem="Result rescrutiny application submitted")
    assert ok is True

    details = svc.get_public_token_details(t_id)
    assert details.service_type == "RESCRUTINY"
    assert "rescrutiny" in details.problem.lower()
    assert details.status == "PENDING"

def test_quick_generate_rest_api():
    res = client.post("/api/token/quick-generate")
    assert res.status_code == 200
    t_id = res.json()["token_id"]
    assert t_id.startswith("NU-2026-")

    # Attach service
    res2 = client.post(f"/api/token/{t_id}/set-service", json={"service_code": "TC", "problem": "Transfer Certificate required"})
    assert res2.status_code == 200
    assert res2.json()["success"] is True

def test_rag_engine_instant_token_flow():
    rag = get_rag_engine()

    # Step 1: User clicks Token Service
    res_menu = rag.answer_query("Token Service", [])
    assert res_menu.intent == "token_service_menu"
    assert "NU-2026-" in res_menu.reply
    assert "টোকেন নম্বরটি" in res_menu.reply
    assert "সংরক্ষণ" in res_menu.reply

    # Extract the token ID generated in the reply
    import re
    m = re.search(r'(NU-\d{4}-\d{6})', res_menu.reply)
    assert m is not None
    generated_id = m.group(1)

    # Step 2: User clicks a service chip with that token ID
    res_attach = rag.answer_query(f"📝 ফরম পূরণ ({generated_id})", [])
    assert res_attach.intent == "token_attached"
    assert generated_id in res_attach.reply
    assert "সংরক্ষিত হয়েছে" in res_attach.reply
    assert "মনে রাখবেন" in res_attach.reply

    # Step 3: User queries status with token ID
    res_status = rag.answer_query(f"Check {generated_id}", [])
    assert res_status.intent == "token_lookup"
    assert generated_id in res_status.reply

def test_submit_details_and_solved_message_display():
    svc = get_token_service()
    rag = get_rag_engine()

    # 1. Instant create
    res = svc.generate_instant_token()
    t_id = res.token_id

    # 2. Submit details via endpoint
    payload = {
        "service_type": "FORM_FILLUP",
        "problem": "Sonali Seba payment completed but status unpaid in portal",
        "user_name": "Karim Uddin",
        "user_phone": "01711223344",
        "registration_no": "2026998877"
    }
    res_sub = client.post(f"/api/token/{t_id}/submit-details", json=payload)
    assert res_sub.status_code == 200
    sub_data = res_sub.json()
    assert sub_data["estimated_solve_date"] is not None
    assert sub_data["service_type"] == "FORM_FILLUP"

    # 3. Check status when PENDING
    status_pending = rag.answer_query(f"Check {t_id}", [])
    assert "Pending" in status_pending.reply or "PENDING" in status_pending.reply or "🟡" in status_pending.reply
    assert sub_data["estimated_solve_date"] in status_pending.reply or "কার্যদিবস" in status_pending.reply

    # 4. Admin solves token with resolution message
    solve_text = "Sonali seba transaction verified and portal status updated to PAID successfully."
    res_solve = client.post(f"/api/token/admin/{t_id}/solve", json={"solve_message": solve_text, "solver_name": "ICT Support Team"})
    assert res_solve.status_code == 200

    # 5. Check status when SOLVED
    status_solved = rag.answer_query(f"Check {t_id}", [])
    assert "SOLVED" in status_solved.reply or "Solved" in status_solved.reply or "🟢" in status_solved.reply
    assert solve_text in status_solved.reply
    assert "ICT Support Team" in status_solved.reply

