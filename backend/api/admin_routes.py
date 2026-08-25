import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query

from backend.core.security import get_current_user_required, require_roles, Role
from backend.models.schemas import (
    TokenAdminDetail,
    TokenAssignRequest,
    TokenStatusUpdateRequest,
    TokenSolveRequest, TokenReturnRequest,
    SolverSchema,
    ServiceTypeSchema
)
from backend.services.token_service import get_token_domain_service
from token_service.db import get_token_db_connection

logger = logging.getLogger("NU_ADMIN_API")
router = APIRouter(prefix="/api/v1/admin", tags=["Admin & Solver Operations"])

@router.get("/dashboard-stats")
def get_dashboard_statistics(user: dict = Depends(get_current_user_required)):
    conn = get_token_db_connection()
    try:
        total = conn.execute("SELECT COUNT(*) as c FROM token_requests").fetchone()["c"]
        pending = conn.execute("SELECT COUNT(*) as c FROM token_requests WHERE status = 'PENDING'").fetchone()["c"]
        assigned = conn.execute("SELECT COUNT(*) as c FROM token_requests WHERE status = 'ASSIGNED'").fetchone()["c"]
        processing = conn.execute("SELECT COUNT(*) as c FROM token_requests WHERE status = 'PROCESSING'").fetchone()["c"]
        solved = conn.execute("SELECT COUNT(*) as c FROM token_requests WHERE status = 'SOLVED'").fetchone()["c"]
        closed = conn.execute("SELECT COUNT(*) as c FROM token_requests WHERE status = 'CLOSED'").fetchone()["c"]
        rejected = conn.execute("SELECT COUNT(*) as c FROM token_requests WHERE status = 'REJECTED'").fetchone()["c"]

        # Solved today
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        solved_today = conn.execute("SELECT COUNT(*) as c FROM token_requests WHERE status = 'SOLVED' AND solved_date LIKE ?", (f"{today_str}%",)).fetchone()["c"]

        return {
            "total_tokens": total,
            "pending": pending,
            "assigned": assigned,
            "processing": processing,
            "solved": solved,
            "closed": closed,
            "rejected": rejected,
            "solved_today": solved_today
        }
    finally:
        conn.close()

@router.get("/tokens", response_model=List[TokenAdminDetail])
def list_admin_tokens(
    status: Optional[str] = Query(None),
    service_type: Optional[str] = Query(None),
    solver_id: Optional[int] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    user: dict = Depends(get_current_user_required)
):
    service = get_token_domain_service()
    conn = get_token_db_connection()
    try:
        query = "SELECT token_id FROM token_requests WHERE 1=1"
        params = []

        user_role = user.get("role", "USER")
        if user_role == "SOLVER":
            user_dept = (user.get("department") or "").strip()
            user_full_name = (user.get("full_name") or "").strip()

            s_rows = conn.execute("""
                SELECT id, solver_name FROM token_solvers
                WHERE solver_name = ? OR department = ? OR solver_name LIKE ? OR department LIKE ?
            """, (user_dept, user_dept, f"%{user_dept}%", f"%{user_dept}%")).fetchall()
            s_ids = [r["id"] for r in s_rows]
            s_names = list(set([r["solver_name"] for r in s_rows] + [user_dept, user_full_name]))

            conds = []
            if s_ids:
                seq = ','.join(['?'] * len(s_ids))
                conds.append(f"solver_id IN ({seq})")
                params.extend(s_ids)
            if s_names:
                nseq = ','.join(['?'] * len(s_names))
                conds.append(f"solver_name IN ({nseq})")
                params.extend(s_names)
            if user_dept:
                conds.append("solver_name LIKE ?")
                params.append(f"%{user_dept}%")

            if conds:
                query += f" AND ({' OR '.join(conds)})"
            else:
                query += " AND 1=0"

        if status:
            query += " AND status = ?"
            params.append(status.upper())
        if service_type:
            query += " AND service_type = ?"
            params.append(service_type.upper())
        if solver_id:
            query += " AND solver_id = ?"
            params.append(solver_id)

        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        cur = conn.execute(query, params)
        token_ids = [r["token_id"] for r in cur.fetchall()]

        results = []
        for tid in token_ids:
            detail = service.get_admin_token_detail(tid)
            if detail:
                results.append(detail)
        return results
    finally:
        conn.close()

@router.get("/tokens/{token_id}", response_model=TokenAdminDetail)
def get_token_admin_detail(token_id: str, user: dict = Depends(get_current_user_required)):
    service = get_token_domain_service()
    detail = service.get_admin_token_detail(token_id.strip().upper())
    if not detail:
        raise HTTPException(status_code=404, detail=f"Token {token_id} not found.")
    return detail

@router.post("/tokens/{token_id}/assign")
def assign_token_solver(
    token_id: str,
    payload: TokenAssignRequest,
    user: dict = Depends(require_roles([Role.ADMIN, Role.SUPER_ADMIN]))
):
    service = get_token_domain_service()
    ok, msg = service.assign_solver(
        token_id=token_id.strip().upper(),
        solver_id=payload.solver_id,
        changed_by=user.get("username", "ADMIN"),
        admin_note=payload.admin_note
    )
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg}

@router.post("/tokens/{token_id}/status")
def update_token_status_endpoint(
    token_id: str,
    payload: TokenStatusUpdateRequest,
    user: dict = Depends(require_roles([Role.SOLVER, Role.ADMIN, Role.SUPER_ADMIN]))
):
    service = get_token_domain_service()
    ok, msg = service.update_status(
        token_id=token_id.strip().upper(),
        new_status=payload.status,
        changed_by=user.get("username", "ADMIN"),
        message=payload.message,
        admin_note=payload.admin_note
    )
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg}

@router.post("/tokens/{token_id}/return-to-admin")
def return_token_to_admin_endpoint(
    token_id: str,
    payload: TokenReturnRequest,
    user: dict = Depends(require_roles([Role.SOLVER, Role.ADMIN, Role.SUPER_ADMIN]))
):
    service = get_token_domain_service()
    solver_name = payload.solver_name or user.get("full_name") or user.get("username")
    ok, msg = service.return_to_admin(
        token_id=token_id.strip().upper(),
        reason=payload.reason,
        solver_name=solver_name,
        changed_by=user.get("username", "SOLVER")
    )
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg}

@router.post("/tokens/{token_id}/solve")
def solve_token_endpoint(
    token_id: str,
    payload: TokenSolveRequest, TokenReturnRequest,
    user: dict = Depends(require_roles([Role.SOLVER, Role.ADMIN, Role.SUPER_ADMIN]))
):
    service = get_token_domain_service()
    solver_name = payload.solver_name or user.get("full_name") or user.get("username")
    ok, msg = service.solve_token(
        token_id=token_id.strip().upper(),
        solve_message=payload.solve_message,
        solver_name=solver_name,
        changed_by=user.get("username", "SOLVER"),
        admin_note=payload.admin_note
    )
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg}

@router.get("/audit-logs")
def view_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    user: dict = Depends(require_roles([Role.ADMIN, Role.SUPER_ADMIN]))
):
    conn = get_token_db_connection()
    try:
        cur = conn.execute("""
            SELECT id, timestamp, action, username, role, resource_type, resource_id, success, details_json
            FROM audit_logs
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

# --- User & Department Solver Management Endpoints ---

from pydantic import BaseModel
from backend.core.security import hash_password

class AdminCreateUserRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    department: Optional[str] = None
    role: str = "SOLVER"

class AdminUpdatePasswordRequest(BaseModel):
    new_password: str

@router.get("/users")
def list_system_users(user: dict = Depends(require_roles([Role.ADMIN, Role.SUPER_ADMIN]))):
    conn = get_token_db_connection()
    try:
        cur = conn.execute("""
            SELECT id, username, email, full_name, department, role, active, created_at
            FROM users
            ORDER BY id ASC
        """)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

@router.post("/users")
def create_system_user(payload: AdminCreateUserRequest, user: dict = Depends(require_roles([Role.ADMIN, Role.SUPER_ADMIN]))):
    conn = get_token_db_connection()
    try:
        cur = conn.execute("SELECT id FROM users WHERE username = ?", (payload.username.strip(),))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail=f"Username '{payload.username}' already exists.")

        pwd_hash = hash_password(payload.password)
        now_str = datetime.utcnow().isoformat()
        role = payload.role.upper() if payload.role.upper() in ["ADMIN", "SOLVER", "USER", "SUPER_ADMIN"] else "SOLVER"

        with conn:
            cur = conn.execute("""
                INSERT INTO users (username, email, password_hash, full_name, department, role, active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?)
            """, (payload.username.strip(), payload.email, pwd_hash, payload.full_name, payload.department, role, now_str))
            new_id = cur.lastrowid

            # If department solver, ensure solver team row exists in token_solvers
            if role == "SOLVER" and payload.department:
                sol_cur = conn.execute("SELECT id FROM token_solvers WHERE solver_name = ? OR department = ?", (payload.full_name or payload.username, payload.department))
                if not sol_cur.fetchone():
                    conn.execute("""
                        INSERT INTO token_solvers (solver_name, department, email, phone, active)
                        VALUES (?, ?, ?, '+88029291000', 1)
                    """, (payload.full_name or payload.username, payload.department, payload.email))

        return {"success": True, "id": new_id, "username": payload.username, "message": f"User {payload.username} created successfully."}
    finally:
        conn.close()

@router.put("/users/{user_id}/status")
def toggle_user_active_status(user_id: int, user: dict = Depends(require_roles([Role.ADMIN, Role.SUPER_ADMIN]))):
    conn = get_token_db_connection()
    try:
        cur = conn.execute("SELECT id, active, username FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found.")
        new_status = 0 if row["active"] else 1
        with conn:
            conn.execute("UPDATE users SET active = ? WHERE id = ?", (new_status, user_id))
        return {"success": True, "active": bool(new_status), "message": f"User status updated."}
    finally:
        conn.close()

@router.put("/users/{user_id}/password")
def admin_reset_user_password(user_id: int, payload: AdminUpdatePasswordRequest, user: dict = Depends(require_roles([Role.ADMIN, Role.SUPER_ADMIN]))):
    if len(payload.new_password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters.")
    conn = get_token_db_connection()
    try:
        cur = conn.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="User not found.")
        pwd_hash = hash_password(payload.new_password)
        with conn:
            conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (pwd_hash, user_id))
        return {"success": True, "message": "Password reset successfully."}
    finally:
        conn.close()

@router.delete("/users/{user_id}")
def delete_system_user(user_id: int, user: dict = Depends(require_roles([Role.SUPER_ADMIN]))):
    conn = get_token_db_connection()
    try:
        cur = conn.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found.")
        if row["username"] == "admin":
            raise HTTPException(status_code=400, detail="Cannot delete default superadmin account.")
        with conn:
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        return {"success": True, "message": f"User {row['username']} deleted successfully."}
    finally:
        conn.close()

# --- Crawler MCP & Website Map Admin Endpoints ---

from mcp_servers.crawler_mcp import get_crawler_mcp_server

@router.get("/crawler/website-map")
def admin_get_website_map(user: dict = Depends(require_roles([Role.SOLVER, Role.ADMIN, Role.SUPER_ADMIN]))):
    server = get_crawler_mcp_server()
    return server.get_website_map()

@router.get("/crawler/stats")
def admin_get_crawler_stats(user: dict = Depends(require_roles([Role.SOLVER, Role.ADMIN, Role.SUPER_ADMIN]))):
    server = get_crawler_mcp_server()
    return server.get_crawl_statistics()

@router.post("/crawler/pause")
def admin_pause_crawler(user: dict = Depends(require_roles([Role.SOLVER, Role.ADMIN, Role.SUPER_ADMIN]))):
    server = get_crawler_mcp_server()
    return server.pause_crawl()

@router.post("/crawler/resume")
def admin_resume_crawler(user: dict = Depends(require_roles([Role.SOLVER, Role.ADMIN, Role.SUPER_ADMIN]))):
    server = get_crawler_mcp_server()
    return server.resume_crawl()

@router.post("/crawler/stop")
def admin_stop_crawler(user: dict = Depends(require_roles([Role.SOLVER, Role.ADMIN, Role.SUPER_ADMIN]))):
    server = get_crawler_mcp_server()
    return server.stop_crawl()

@router.post("/crawler/retry-failed")
def admin_retry_crawler_failed(user: dict = Depends(require_roles([Role.SOLVER, Role.ADMIN, Role.SUPER_ADMIN]))):
    server = get_crawler_mcp_server()
    return server.retry_failed_urls()

# --- System Activity, Service Logs & Report Export Endpoints ---

from fastapi import Response
from backend.services.activity_tracker import get_activity_tracker
from backend.services.report_exporter import get_report_exporter

@router.get("/logs/summary")
def get_system_logs_summary(user: dict = Depends(get_current_user_required)):
    """Returns aggregated system metrics: services provided, barcodes generated, tokens solved/processed/pending."""
    tracker = get_activity_tracker()
    return tracker.get_summary_metrics()

@router.get("/logs/records")
def get_system_log_records(
    event_type: Optional[str] = Query(None),
    service_code: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user_required)
):
    """Fetches paginated tabular audit & activity logs."""
    tracker = get_activity_tracker()
    return tracker.get_activity_records(
        event_type=event_type,
        service_code=service_code,
        status=status,
        search=search,
        limit=limit,
        offset=offset
    )

@router.get("/logs/export/excel")
def export_system_activity_excel(user: dict = Depends(get_current_user_required)):
    """Generates and downloads a multi-sheet formatted Excel report (.xlsx)."""
    exporter = get_report_exporter()
    excel_bytes = exporter.generate_excel_report()
    filename = f"NU_System_Activity_Report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/logs/export/pdf")
def export_system_activity_pdf(user: dict = Depends(get_current_user_required)):
    """Generates and downloads an executive PDF audit report (.pdf)."""
    exporter = get_report_exporter()
    pdf_bytes = exporter.generate_pdf_report()
    filename = f"NU_System_Activity_Report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/activity/record-qr")
def record_qr_generation_event(payload: Dict[str, Any] = None):
    """Logs a QR/Barcode generation event."""
    tracker = get_activity_tracker()
    tracker.record_event(
        event_type="BARCODE_GENERATED",
        service_code="MOBILE_QR",
        user_identifier=(payload or {}).get("identifier", "STUDENT_MOBILE"),
        details="Generated QR/Barcode for mobile instant chat and token tracking",
        status="SUCCESS"
    )
    return {"success": True, "message": "QR generation recorded"}



from fastapi.responses import FileResponse
from fastapi import UploadFile, File
from backend.services.backup_service import get_backup_service

@router.get("/backup/list", summary="List all system backups")
def get_backup_list(user: dict = Depends(get_current_user_required)):
    if user.get("role") not in ["SUPER_ADMIN", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Permission denied.")
    backup_svc = get_backup_service()
    return {"success": True, "backups": backup_svc.list_backups()}

@router.post("/backup/create", summary="Generate portable full system backup ZIP")
def create_system_backup(user: dict = Depends(get_current_user_required)):
    if user.get("role") not in ["SUPER_ADMIN", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Permission denied.")
    backup_svc = get_backup_service()
    backup_path, meta = backup_svc.create_backup()
    return FileResponse(
        path=str(backup_path),
        filename=backup_path.name,
        media_type="application/zip"
    )

@router.post("/backup/restore", summary="Restore full system from uploaded backup ZIP")
async def restore_system_backup(file: UploadFile = File(...), user: dict = Depends(get_current_user_required)):
    if user.get("role") != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Only SUPER_ADMIN can perform full system restore.")
    
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a valid .zip backup archive.")

    content = await file.read()
    backup_svc = get_backup_service()
    try:
        res = backup_svc.restore_backup(content, filename=file.filename)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
