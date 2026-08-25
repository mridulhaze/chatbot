import re
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple

from backend.core.config import settings
from backend.core.audit import log_audit_event
from backend.core.security import Role
from backend.models.schemas import (
    TokenCreateRequest,
    TokenCreateResponse,
    TokenPublicStatus,
    TokenAdminDetail,
    TokenHistorySchema,
    ServiceTypeSchema,
    SolverSchema
)
from token_service.db import get_token_db_connection

logger = logging.getLogger("NU_CORE_TOKEN_SERVICE")

STATUS_DISPLAY_MAP = {
    "PENDING": ("🟡 Pending", "bg-amber-100 text-amber-800 border-amber-300"),
    "ASSIGNED": ("🟣 Assigned", "bg-purple-100 text-purple-800 border-purple-300"),
    "PROCESSING": ("🔵 Processing", "bg-blue-100 text-blue-800 border-blue-300"),
    "SOLVED": ("🟢 Solved", "bg-emerald-100 text-emerald-800 border-emerald-300"),
    "CLOSED": ("⚫ Closed", "bg-slate-100 text-slate-800 border-slate-300"),
    "REJECTED": ("🔴 Rejected", "bg-rose-100 text-rose-800 border-rose-300")
}

# Strict Allowed State Machine Transitions
VALID_TRANSITIONS = {
    "PENDING": ["ASSIGNED", "PROCESSING", "REJECTED"],
    "ASSIGNED": ["PROCESSING", "REJECTED", "PENDING"],
    "PROCESSING": ["SOLVED", "ASSIGNED", "REJECTED", "PENDING"],
    "SOLVED": ["CLOSED", "PROCESSING"],
    "REJECTED": ["PENDING"],
    "CLOSED": []
}

class TokenDomainService:
    @staticmethod
    def generate_atomic_token_id() -> str:
        """
        Generates a concurrency-safe unique sequential Token ID (NU-YYYY-000001).
        Uses atomic sequence transactions in database.
        """
        current_year = datetime.utcnow().year
        conn = get_token_db_connection()
        try:
            with conn:
                # Ensure sequence table exists
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS token_sequences (
                        year INTEGER PRIMARY KEY,
                        last_seq INTEGER NOT NULL DEFAULT 0
                    )
                """)
                # Atomically increment
                conn.execute("INSERT OR IGNORE INTO token_sequences (year, last_seq) VALUES (?, 0)", (current_year,))
                conn.execute("UPDATE token_sequences SET last_seq = last_seq + 1 WHERE year = ?", (current_year,))
                cur = conn.execute("SELECT last_seq FROM token_sequences WHERE year = ?", (current_year,))
                row = cur.fetchone()
                seq_num = row["last_seq"] if row else 1
                
            return f"NU-{current_year}-{seq_num:06d}"
        finally:
            conn.close()

    def get_services(self) -> List[Dict[str, Any]]:
        """Returns active support service types ordered by sort_order."""
        conn = get_token_db_connection()
        try:
            cur = conn.execute("""
                SELECT id, service_code, service_name, service_name_bn, description, active, sort_order
                FROM token_service_types
                WHERE active = 1
                ORDER BY sort_order ASC
            """)
            return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    def get_solvers(self) -> List[Dict[str, Any]]:
        """Returns all registered solver teams."""
        conn = get_token_db_connection()
        try:
            cur = conn.execute("""
                SELECT id, solver_name, department, email, phone, active
                FROM token_solvers
                WHERE active = 1
                ORDER BY solver_name ASC
            """)
            return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    def create_token(self, req: TokenCreateRequest) -> TokenCreateResponse:
        """
        Creates a new support token with an atomic sequential ID,
        initial PENDING status, and records an initial history entry.
        """
        token_id = self.generate_atomic_token_id()
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        # Resolve service name
        services = self.get_services()
        service_map = {s["service_code"].upper(): s["service_name"] for s in services}
        service_code_upper = req.service_code.upper()
        service_name = service_map.get(service_code_upper, service_code_upper)

        conn = get_token_db_connection()
        try:
            with conn:
                conn.execute("""
                    INSERT INTO token_requests (
                        token_id, service_type, problem, status, priority,
                        user_id, user_name, user_email, user_phone, registration_no, college_code,
                        created_date, updated_date
                    ) VALUES (?, ?, ?, 'PENDING', ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    token_id, service_code_upper, req.problem.strip(), req.priority or "NORMAL",
                    req.user_id, req.user_name, req.user_email, req.user_phone,
                    req.registration_no, req.college_code, now_str, now_str
                ))

                conn.execute("""
                    INSERT INTO token_history (token_id, old_status, new_status, changed_by, message, created_date)
                    VALUES (?, NULL, 'PENDING', 'SYSTEM', 'Token created by user.', ?)
                """, (token_id, now_str))

            log_audit_event(
                action="TOKEN_CREATED",
                user_id=req.user_id,
                username=req.user_name,
                resource_type="token",
                resource_id=token_id,
                details={"service": service_code_upper, "priority": req.priority or "NORMAL"}
            )

            return TokenCreateResponse(
                success=True,
                token_id=token_id,
                service_code=service_code_upper,
                service_name=service_name,
                problem=req.problem.strip(),
                status="PENDING",
                created_date=now_str,
                message=f"Support token {token_id} created successfully."
            )
        finally:
            conn.close()

    def get_public_token_status(self, token_id: str) -> Optional[TokenPublicStatus]:
        """
        Fetches public-friendly token status with strict PII protection.
        Never returns user contact info or internal admin notes.
        """
        conn = get_token_db_connection()
        try:
            cur = conn.execute("""
                SELECT * FROM token_requests WHERE token_id = ?
            """, (token_id,))
            row = cur.fetchone()
            if not row:
                return None

            status = row["status"].upper()
            display_text, badge_class = STATUS_DISPLAY_MAP.get(status, ("🟡 Pending", "bg-amber-100 text-amber-800 border-amber-300"))
            
            services = self.get_services()
            service_map = {s["service_code"].upper(): s["service_name"] for s in services}
            s_type = row["service_type"].upper()
            s_name = service_map.get(s_type, s_type)

            hist_cur = conn.execute("""
                SELECT id, token_id, old_status, new_status, changed_by, message, created_date
                FROM token_history WHERE token_id = ? ORDER BY id ASC
            """, (token_id,))
            history = [TokenHistorySchema(**dict(h)) for h in hist_cur.fetchall()]

            return TokenPublicStatus(
                token_id=row["token_id"],
                service_code=s_type,
                service_name=s_name,
                problem=row["problem"],
                status=status,
                status_display=display_text,
                status_badge=badge_class,
                solver_name=row["solver_name"],
                solve_message=row["solve_message"],
                created_date=row["created_date"],
                updated_date=row["updated_date"],
                solved_date=row["solved_date"],
                history=history
            )
        finally:
            conn.close()

    def get_admin_token_detail(self, token_id: str) -> Optional[TokenAdminDetail]:
        """Fetches full admin/solver token view including contact info and notes."""
        conn = get_token_db_connection()
        try:
            cur = conn.execute("""
                SELECT * FROM token_requests WHERE token_id = ?
            """, (token_id,))
            row = cur.fetchone()
            if not row:
                return None

            status = row["status"].upper()
            display_text, badge_class = STATUS_DISPLAY_MAP.get(status, ("🟡 Pending", "bg-amber-100 text-amber-800 border-amber-300"))
            services = self.get_services()
            service_map = {s["service_code"].upper(): s["service_name"] for s in services}
            s_type = row["service_type"].upper()
            s_name = service_map.get(s_type, s_type)

            hist_cur = conn.execute("""
                SELECT id, token_id, old_status, new_status, changed_by, message, created_date
                FROM token_history WHERE token_id = ? ORDER BY id ASC
            """, (token_id,))
            history = [TokenHistorySchema(**dict(h)) for h in hist_cur.fetchall()]

            return TokenAdminDetail(
                id=row["id"],
                token_id=row["token_id"],
                service_code=s_type,
                service_name=s_name,
                problem=row["problem"],
                status=status,
                status_display=display_text,
                status_badge=badge_class,
                solver_name=row["solver_name"],
                solve_message=row["solve_message"],
                created_date=row["created_date"],
                updated_date=row["updated_date"],
                solved_date=row["solved_date"],
                history=history,
                user_id=row["user_id"],
                user_name=row["user_name"],
                user_email=row["user_email"],
                user_phone=row["user_phone"],
                registration_no=row["registration_no"],
                college_code=row["college_code"],
                priority=row["priority"],
                admin_note=row["admin_note"],
                solver_id=row["solver_id"]
            )
        finally:
            conn.close()

    def update_status(
        self,
        token_id: str,
        new_status: str,
        changed_by: str = "ADMIN",
        message: Optional[str] = None,
        admin_note: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Validates state machine transition rules and updates token status.
        """
        new_status_upper = new_status.upper()
        conn = get_token_db_connection()
        try:
            cur = conn.execute("SELECT status, admin_note FROM token_requests WHERE token_id = ?", (token_id,))
            row = cur.fetchone()
            if not row:
                return False, f"Token {token_id} not found."

            current_status = row["status"].upper()
            allowed = VALID_TRANSITIONS.get(current_status, [])
            if new_status_upper not in allowed and changed_by != "SUPER_ADMIN":
                return False, f"Illegal status transition from {current_status} to {new_status_upper}. Allowed: {allowed}"

            now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            updated_admin_note = admin_note if admin_note is not None else row["admin_note"]

            with conn:
                conn.execute("""
                    UPDATE token_requests
                    SET status = ?, updated_date = ?, admin_note = ?
                    WHERE token_id = ?
                """, (new_status_upper, now_str, updated_admin_note, token_id))

                conn.execute("""
                    INSERT INTO token_history (token_id, old_status, new_status, changed_by, message, created_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (token_id, current_status, new_status_upper, changed_by, message or f"Status changed to {new_status_upper}", now_str))

            log_audit_event(
                action="TOKEN_STATUS_CHANGED",
                username=changed_by,
                resource_type="token",
                resource_id=token_id,
                details={"old_status": current_status, "new_status": new_status_upper, "message": message}
            )

            return True, f"Status updated to {new_status_upper}."
        finally:
            conn.close()

    def assign_solver(
        self,
        token_id: str,
        solver_id: int,
        changed_by: str = "ADMIN",
        admin_note: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Assigns a token to an active department solver desk."""
        conn = get_token_db_connection()
        try:
            s_cur = conn.execute("SELECT id, solver_name, department FROM token_solvers WHERE id = ? AND active = 1", (solver_id,))
            solver = s_cur.fetchone()
            if not solver:
                return False, f"Solver ID {solver_id} not found or inactive."

            cur = conn.execute("SELECT status, admin_note FROM token_requests WHERE token_id = ?", (token_id,))
            row = cur.fetchone()
            if not row:
                return False, f"Token {token_id} not found."

            now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            solver_name = solver["solver_name"]
            current_status = row["status"]
            new_status = "ASSIGNED" if current_status == "PENDING" else current_status

            with conn:
                conn.execute("""
                    UPDATE token_requests
                    SET solver_id = ?, solver_name = ?, status = ?, updated_date = ?, admin_note = COALESCE(?, admin_note)
                    WHERE token_id = ?
                """, (solver["id"], solver_name, new_status, now_str, admin_note, token_id))

                conn.execute("""
                    INSERT INTO token_history (token_id, old_status, new_status, changed_by, message, created_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (token_id, current_status, new_status, changed_by, f"Assigned to {solver_name}", now_str))

            log_audit_event(
                action="TOKEN_ASSIGNED",
                username=changed_by,
                resource_type="token",
                resource_id=token_id,
                details={"solver_id": solver["id"], "solver_name": solver_name}
            )

            return True, f"Token assigned to {solver_name}."
        finally:
            conn.close()

    def return_to_admin(
        self,
        token_id: str,
        reason: str,
        solver_name: Optional[str] = None,
        changed_by: str = "SOLVER"
    ) -> Tuple[bool, str]:
        """
        Solver sends the token back to Admin (Not Solved) for further instructions or re-delegation.
        Status is transitioned back to PENDING with solver's reason logged in history and admin note.
        """
        conn = get_token_db_connection()
        try:
            cur = conn.execute("SELECT status, admin_note, solver_name FROM token_requests WHERE token_id = ?", (token_id,))
            row = cur.fetchone()
            if not row:
                return False, f"Token {token_id} not found."

            current_status = row["status"]
            now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            s_name = solver_name or row["solver_name"] or changed_by
            reason_clean = reason.strip()

            new_note = f"[Returned to Admin by {s_name} on {now_str} (Reason: {reason_clean})]"
            if row["admin_note"]:
                new_note = f"{row['admin_note']}\n{new_note}"

            with conn:
                conn.execute("""
                    UPDATE token_requests
                    SET status = 'PENDING', updated_date = ?, admin_note = ?
                    WHERE token_id = ?
                """, (now_str, new_note, token_id))

                conn.execute("""
                    INSERT INTO token_history (token_id, old_status, new_status, changed_by, message, created_date)
                    VALUES (?, ?, 'PENDING', ?, ?, ?)
                """, (token_id, current_status, changed_by, f"Sent back to Admin (Not Solved): {reason_clean}", now_str))

            log_audit_event(
                action="TOKEN_RETURNED_TO_ADMIN",
                username=changed_by,
                resource_type="token",
                resource_id=token_id,
                details={"solver_name": s_name, "reason": reason_clean}
            )

            return True, f"Token {token_id} sent back to Admin for further instruction."
        finally:
            conn.close()

    def solve_token(
        self,
        token_id: str,
        solve_message: str,
        solver_name: Optional[str] = None,
        changed_by: str = "SOLVER",
        admin_note: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Solves a support token, marks status as SOLVED, records solution message,
        and triggers automatic anonymized indexing into Chroma vector knowledge base.
        """
        conn = get_token_db_connection()
        try:
            cur = conn.execute("SELECT status, service_type, problem, solver_name, admin_note FROM token_requests WHERE token_id = ?", (token_id,))
            row = cur.fetchone()
            if not row:
                return False, f"Token {token_id} not found."

            current_status = row["status"]
            now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            s_name = solver_name or row["solver_name"] or changed_by

            with conn:
                conn.execute("""
                    UPDATE token_requests
                    SET status = 'SOLVED', solve_message = ?, solver_name = ?, solved_date = ?, updated_date = ?, admin_note = COALESCE(?, admin_note)
                    WHERE token_id = ?
                """, (solve_message.strip(), s_name, now_str, now_str, admin_note, token_id))

                conn.execute("""
                    INSERT INTO token_history (token_id, old_status, new_status, changed_by, message, created_date)
                    VALUES (?, ?, 'SOLVED', ?, ?, ?)
                """, (token_id, current_status, changed_by, f"Solved: {solve_message.strip()[:100]}...", now_str))

            log_audit_event(
                action="TOKEN_SOLVED",
                username=changed_by,
                resource_type="token",
                resource_id=token_id,
                details={"solver_name": s_name}
            )

            # Trigger auto-indexing of anonymized solved knowledge
            try:
                from backend.services.similarity_service import get_similarity_service
                get_similarity_service().index_solved_case(
                    token_id=token_id,
                    service_code=row["service_type"],
                    problem=row["problem"],
                    solution=solve_message.strip(),
                    solver_desk=s_name
                )
            except Exception as e:
                logger.warning(f"Failed to auto-index solved token {token_id} to vector base: {e}")

            return True, f"Token {token_id} marked as SOLVED successfully."
        finally:
            conn.close()

_token_domain_service_instance: Optional[TokenDomainService] = None

def get_token_domain_service() -> TokenDomainService:
    global _token_domain_service_instance
    if _token_domain_service_instance is None:
        _token_domain_service_instance = TokenDomainService()
    return _token_domain_service_instance
