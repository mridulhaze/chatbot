import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Body, Path, Header
from fastapi.responses import JSONResponse

from .service import get_token_service
from .models import (
    TokenCreateRequest,
    TokenCreateResponse,
    TokenSubmitDetailsRequest,
    TokenPublicDetailResponse,
    TokenAdminDetailResponse,
    TokenAssignRequest,
    TokenStatusUpdateRequest,
    TokenSolveRequest,
    SolvedSimilarProblem
)

logger = logging.getLogger("NU_TOKEN_ROUTES")

router = APIRouter(prefix="/api/token", tags=["Token Service"])

# --- Public Endpoints (Chatbot & Student Portal) ---

@router.get("/services", summary="List active support service types")
def get_service_types():
    svc = get_token_service()
    services = svc.get_services()
    return {"success": True, "services": services}

@router.post("/create", response_model=TokenCreateResponse, summary="Create a new support token")
def create_support_token(payload: TokenCreateRequest):
    svc = get_token_service()
    try:
        res = svc.create_token(payload)
        return res
    except Exception as e:
        logger.error(f"Failed to create support token: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not create support token. Please try again.")

@router.post("/quick-generate", response_model=TokenCreateResponse, summary="Instant 1-click token generation")
def quick_generate_token():
    svc = get_token_service()
    try:
        res = svc.generate_instant_token()
        return res
    except Exception as e:
        logger.error(f"Failed to instant-generate token: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not generate token.")

@router.post("/{token_id}/set-service", summary="Attach service and problem to instant token")
def set_token_service(token_id: str = Path(...), service_code: str = Body(..., embed=True), problem: Optional[str] = Body(None, embed=True)):
    svc = get_token_service()
    success = svc.set_token_service(token_id=token_id, service_code=service_code, problem=problem)
    if not success:
        raise HTTPException(status_code=400, detail="Token ID not found.")
    return {"success": True, "token_id": token_id, "service_code": service_code, "message": "Service attached successfully."}

@router.post("/{token_id}/submit-details", response_model=TokenPublicDetailResponse, summary="Submit full problem details from interactive form")
def submit_token_full_details(token_id: str = Path(...), payload: TokenSubmitDetailsRequest = Body(...)):
    svc = get_token_service()
    details = svc.submit_token_details(
        token_id=token_id,
        service_type=payload.service_type,
        problem=payload.problem,
        user_name=payload.user_name,
        user_phone=payload.user_phone,
        registration_no=payload.registration_no,
        college_code=payload.college_code
    )
    if not details:
        raise HTTPException(status_code=400, detail="Token ID not found or could not be updated.")
    return details

@router.get("/{token_id}", response_model=TokenPublicDetailResponse, summary="Public token details & timeline")
def get_token_details(token_id: str = Path(..., description="Token ID e.g. NU-2026-000001")):
    svc = get_token_service()
    details = svc.get_public_token_details(token_id)
    if not details:
        raise HTTPException(status_code=404, detail="Sorry, I could not find this Token ID. Please check the Token ID and try again.")
    return details

@router.get("/{token_id}/status", summary="Quick token status check")
def get_token_status_quick(token_id: str = Path(...)):
    svc = get_token_service()
    details = svc.get_public_token_details(token_id)
    if not details:
        raise HTTPException(status_code=404, detail="Token ID not found.")
    return {
        "token_id": details.token_id,
        "service_name": details.service_name,
        "status": details.status,
        "status_display": details.status_display,
        "solver": details.solver_name or "Pending Assignment",
        "solve_message": details.solve_message,
        "created_date": details.created_date,
        "solved_date": details.solved_date
    }

@router.get("/solved-similar", response_model=List[SolvedSimilarProblem], summary="Search anonymized solved support cases")
def get_solved_similar_cases(query: str = Query(..., min_length=3), service_type: Optional[str] = None):
    svc = get_token_service()
    cases = svc.find_similar_solved_cases(query=query, service_type=service_type, top_k=3)
    return cases

# --- Admin & Solver Management Endpoints ---

@router.get("/admin/solvers", summary="List all support solvers/teams")
def admin_get_solvers():
    svc = get_token_service()
    return {"success": True, "solvers": svc.get_solvers()}

@router.get("/admin/tokens", summary="Admin token search & listing")
def admin_list_tokens(
    status: Optional[str] = Query(None, description="Filter by status e.g. PENDING, PROCESSING, SOLVED"),
    service_type: Optional[str] = Query(None, description="Filter by service type e.g. FORM_FILLUP, EMS"),
    search: Optional[str] = Query(None, description="Search token ID, problem, user name, reg no"),
    department: Optional[str] = Query(None, description="Filter by solver department"),
    solver_name: Optional[str] = Query(None, description="Filter by solver name"),
    role: Optional[str] = Query(None, description="User role"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    authorization: Optional[str] = Header(None)
):
    svc = get_token_service()
    
    auth_user = None
    if authorization and authorization.startswith("Bearer "):
        try:
            from backend.core.security import decode_jwt_token
            token_str = authorization.split("Bearer ", 1)[1].strip()
            auth_user = decode_jwt_token(token_str)
        except Exception:
            pass

    final_role = (auth_user.get("role") if auth_user else None) or role
    final_dept = (auth_user.get("department") if auth_user else None) or department
    final_solver = (auth_user.get("full_name") if auth_user else None) or solver_name

    tokens, total = svc.repo.list_tokens(
        status=status,
        service_type=service_type,
        search=search,
        department=final_dept,
        solver_name=final_solver,
        role=final_role,
        limit=limit,
        offset=offset
    )
    return {
        "success": True,
        "total": total,
        "limit": limit,
        "offset": offset,
        "tokens": tokens
    }

@router.get("/admin/{token_id}", response_model=TokenAdminDetailResponse, summary="Admin full token detail")
def admin_get_token(token_id: str = Path(...)):
    svc = get_token_service()
    details = svc.get_admin_token_details(token_id)
    if not details:
        raise HTTPException(status_code=404, detail="Token not found.")
    return details

@router.post("/admin/{token_id}/assign", summary="Assign token to a solver team")
def admin_assign_token(token_id: str = Path(...), payload: TokenAssignRequest = Body(...)):
    svc = get_token_service()
    success = svc.assign_token(token_id, solver_id=payload.solver_id, changed_by="ADMIN", admin_note=payload.admin_note)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to assign solver. Check Token ID and Solver ID.")
    return {"success": True, "message": f"Token {token_id} assigned successfully."}

@router.post("/admin/{token_id}/status", summary="Update token status")
def admin_update_token_status(token_id: str = Path(...), payload: TokenStatusUpdateRequest = Body(...)):
    svc = get_token_service()
    success = svc.update_status(
        token_id=token_id,
        status=payload.status,
        changed_by="ADMIN",
        message=payload.message,
        admin_note=payload.admin_note
    )
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update status. Check Token ID.")
    return {"success": True, "message": f"Token {token_id} status updated to {payload.status}."}

@router.post("/admin/{token_id}/solve", summary="Mark token as SOLVED with solution message")
def admin_solve_token(token_id: str = Path(...), payload: TokenSolveRequest = Body(...)):
    svc = get_token_service()
    success = svc.solve_token(
        token_id=token_id,
        solve_message=payload.solve_message,
        solver_name=payload.solver_name,
        changed_by="ADMIN",
        admin_note=payload.admin_note
    )
    if not success:
        raise HTTPException(status_code=400, detail="Failed to solve token. Check Token ID.")
    return {"success": True, "message": f"Token {token_id} marked as SOLVED and indexed into knowledge base."}

@router.post("/admin/{token_id}/delete", summary="Super Admin soft-delete token")
def admin_delete_token(token_id: str, authorization: Optional[str] = Header(None)):
    auth_user = None
    if authorization and authorization.startswith("Bearer "):
        try:
            from backend.core.security import decode_jwt_token
            auth_user = decode_jwt_token(authorization.split("Bearer ", 1)[1].strip())
        except Exception:
            pass

    if not auth_user or auth_user.get("role") not in ["SUPER_ADMIN", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Permission denied. Only Super Admin can delete tokens.")

    svc = get_token_service()
    admin_name = auth_user.get("username", "Super Admin")
    success = svc.repo.soft_delete_token(token_id, admin_user=admin_name)
    if not success:
        raise HTTPException(status_code=404, detail="Token ID not found or already deleted.")
    return {"success": True, "message": f"Token {token_id} moved to trash successfully."}

@router.post("/admin/{token_id}/restore", summary="Super Admin restore token")
def admin_restore_token(token_id: str, authorization: Optional[str] = Header(None)):
    auth_user = None
    if authorization and authorization.startswith("Bearer "):
        try:
            from backend.core.security import decode_jwt_token
            auth_user = decode_jwt_token(authorization.split("Bearer ", 1)[1].strip())
        except Exception:
            pass

    if not auth_user or auth_user.get("role") not in ["SUPER_ADMIN", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Permission denied. Only Super Admin can restore tokens.")

    svc = get_token_service()
    admin_name = auth_user.get("username", "Super Admin")
    success = svc.repo.restore_token(token_id, admin_user=admin_name)
    if not success:
        raise HTTPException(status_code=404, detail="Token ID not found.")
    return {"success": True, "message": f"Token {token_id} restored from trash successfully."}
