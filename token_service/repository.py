import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from .db import get_token_db_connection

logger = logging.getLogger("NU_TOKEN_REPO")

class TokenRepository:
    def __init__(self):
        pass

    def generate_next_token_id(self, year: Optional[int] = None) -> str:
        """
        Atomically generates a unique sequence-based Token ID: NU-YYYY-XXXXXX.
        Example: NU-2026-000001, NU-2026-000002.
        """
        if year is None:
            year = datetime.now().year

        conn = get_token_db_connection()
        try:
            with conn:
                # Ensure year row exists
                conn.execute(
                    "INSERT OR IGNORE INTO token_sequences (year, last_seq) VALUES (?, 0)",
                    (year,)
                )
                # Increment atomically
                conn.execute(
                    "UPDATE token_sequences SET last_seq = last_seq + 1 WHERE year = ?",
                    (year,)
                )
                row = conn.execute(
                    "SELECT last_seq FROM token_sequences WHERE year = ?",
                    (year,)
                ).fetchone()
                seq = row["last_seq"]
                return f"NU-{year}-{seq:06d}"
        finally:
            conn.close()

    def get_active_service_types(self) -> List[Dict[str, Any]]:
        conn = get_token_db_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM token_service_types WHERE active = 1 ORDER BY sort_order ASC, id ASC"
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def get_service_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        conn = get_token_db_connection()
        try:
            row = conn.execute(
                "SELECT * FROM token_service_types WHERE UPPER(service_code) = UPPER(?) LIMIT 1",
                (code.strip(),)
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_solvers(self) -> List[Dict[str, Any]]:
        conn = get_token_db_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM token_solvers WHERE active = 1 ORDER BY solver_name ASC"
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def get_solver_by_id(self, solver_id: int) -> Optional[Dict[str, Any]]:
        conn = get_token_db_connection()
        try:
            row = conn.execute(
                "SELECT * FROM token_solvers WHERE id = ?",
                (solver_id,)
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def create_token(self, token_data: Dict[str, Any]) -> str:
        """Inserts token into token_requests and adds first PENDING history log."""
        token_id = self.generate_next_token_id()
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")
        est_solve_date = (now + timedelta(days=3)).strftime("%Y-%m-%d")

        conn = get_token_db_connection()
        try:
            with conn:
                conn.execute("""
                    INSERT INTO token_requests (
                        token_id, problem, service_type, status,
                        solver_id, solver_name, solve_message,
                        created_date, updated_date, solved_date, estimated_solve_date,
                        user_id, user_name, user_email, user_phone,
                        registration_no, college_code, priority, admin_note, attachment_path
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    token_id,
                    token_data["problem"],
                    token_data["service_type"],
                    "PENDING",
                    token_data.get("solver_id"),
                    token_data.get("solver_name"),
                    None,
                    now_str,
                    now_str,
                    None,
                    token_data.get("estimated_solve_date") or est_solve_date,
                    token_data.get("user_id"),
                    token_data.get("user_name"),
                    token_data.get("user_email"),
                    token_data.get("user_phone"),
                    token_data.get("registration_no"),
                    token_data.get("college_code"),
                    token_data.get("priority", "NORMAL"),
                    token_data.get("admin_note"),
                    token_data.get("attachment_path")
                ))

                # Initial history log
                conn.execute("""
                    INSERT INTO token_history (token_id, old_status, new_status, changed_by, message, created_date)
                    VALUES (?, NULL, 'PENDING', 'USER', 'Support token created by student', ?)
                """, (token_id, now_str))

            return token_id
        finally:
            conn.close()

    def get_token_by_id(self, token_id: str) -> Optional[Dict[str, Any]]:
        conn = get_token_db_connection()
        try:
            row = conn.execute(
                "SELECT * FROM token_requests WHERE UPPER(token_id) = UPPER(?)",
                (token_id.strip(),)
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_token_history(self, token_id: str) -> List[Dict[str, Any]]:
        conn = get_token_db_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM token_history WHERE UPPER(token_id) = UPPER(?) ORDER BY id ASC",
                (token_id.strip(),)
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def update_token_status(self, token_id: str, new_status: str, changed_by: str = "ADMIN", message: Optional[str] = None, admin_note: Optional[str] = None) -> bool:
        conn = get_token_db_connection()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with conn:
                old = conn.execute(
                    "SELECT status, admin_note FROM token_requests WHERE UPPER(token_id) = UPPER(?)",
                    (token_id.strip(),)
                ).fetchone()
                if not old:
                    return False
                old_status = old["status"]

                note = admin_note if admin_note is not None else old["admin_note"]

                conn.execute("""
                    UPDATE token_requests
                    SET status = ?, updated_date = ?, admin_note = ?
                    WHERE UPPER(token_id) = UPPER(?)
                """, (new_status.upper(), now_str, note, token_id.strip()))

                conn.execute("""
                    INSERT INTO token_history (token_id, old_status, new_status, changed_by, message, created_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (token_id.strip(), old_status, new_status.upper(), changed_by, message or f"Status changed to {new_status}", now_str))

            return True
        finally:
            conn.close()

    def update_service_and_problem(self, token_id: str, service_type: str, problem: Optional[str] = None) -> bool:
        conn = get_token_db_connection()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with conn:
                old = conn.execute(
                    "SELECT service_type, problem FROM token_requests WHERE UPPER(token_id) = UPPER(?)",
                    (token_id.strip(),)
                ).fetchone()
                if not old:
                    return False
                
                prob = problem.strip() if problem and problem.strip() else old["problem"]

                conn.execute("""
                    UPDATE token_requests
                    SET service_type = ?, problem = ?, updated_date = ?
                    WHERE UPPER(token_id) = UPPER(?)
                """, (service_type.upper(), prob, now_str, token_id.strip()))

                conn.execute("""
                    INSERT INTO token_history (token_id, old_status, new_status, changed_by, message, created_date)
                    VALUES (?, 'PENDING', 'PENDING', 'USER', ?, ?)
                """, (token_id.strip(), f"Service selected: {service_type}", now_str))

            return True
        finally:
            conn.close()

    def update_token_submission_details(self, token_id: str, service_type: str, problem: str, user_name: Optional[str] = None, user_phone: Optional[str] = None, registration_no: Optional[str] = None, college_code: Optional[str] = None) -> bool:
        conn = get_token_db_connection()
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")
        est_solve_date = (now + timedelta(days=3)).strftime("%Y-%m-%d")
        try:
            with conn:
                old = conn.execute(
                    "SELECT id FROM token_requests WHERE UPPER(token_id) = UPPER(?)",
                    (token_id.strip(),)
                ).fetchone()
                if not old:
                    return False

                conn.execute("""
                    UPDATE token_requests
                    SET service_type = ?, problem = ?, user_name = ?, user_phone = ?, registration_no = ?, college_code = ?, updated_date = ?, estimated_solve_date = ?
                    WHERE UPPER(token_id) = UPPER(?)
                """, (
                    service_type.upper(),
                    problem.strip(),
                    user_name.strip() if user_name else None,
                    user_phone.strip() if user_phone else None,
                    registration_no.strip() if registration_no else None,
                    college_code.strip() if college_code else None,
                    now_str,
                    est_solve_date,
                    token_id.strip()
                ))

                conn.execute("""
                    INSERT INTO token_history (token_id, old_status, new_status, changed_by, message, created_date)
                    VALUES (?, 'PENDING', 'PENDING', 'USER', ?, ?)
                """, (token_id.strip(), f"Problem submitted for service: {service_type}", now_str))

            return True
        finally:
            conn.close()

    def assign_token(self, token_id: str, solver_id: int, solver_name: str, changed_by: str = "ADMIN", admin_note: Optional[str] = None) -> bool:
        conn = get_token_db_connection()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with conn:
                old = conn.execute(
                    "SELECT status, admin_note FROM token_requests WHERE UPPER(token_id) = UPPER(?)",
                    (token_id.strip(),)
                ).fetchone()
                if not old:
                    return False
                old_status = old["status"]
                new_status = "ASSIGNED" if old_status == "PENDING" else old_status

                note = admin_note if admin_note is not None else old["admin_note"]

                conn.execute("""
                    UPDATE token_requests
                    SET solver_id = ?, solver_name = ?, status = ?, updated_date = ?, admin_note = ?
                    WHERE UPPER(token_id) = UPPER(?)
                """, (solver_id, solver_name, new_status, now_str, note, token_id.strip()))

                conn.execute("""
                    INSERT INTO token_history (token_id, old_status, new_status, changed_by, message, created_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (token_id.strip(), old_status, new_status, changed_by, f"Assigned to {solver_name}", now_str))

            return True
        finally:
            conn.close()

    def solve_token(self, token_id: str, solve_message: str, solver_name: Optional[str] = None, changed_by: str = "ADMIN", admin_note: Optional[str] = None) -> bool:
        conn = get_token_db_connection()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with conn:
                old = conn.execute(
                    "SELECT status, solver_name, admin_note FROM token_requests WHERE UPPER(token_id) = UPPER(?)",
                    (token_id.strip(),)
                ).fetchone()
                if not old:
                    return False
                old_status = old["status"]

                final_solver = solver_name or old["solver_name"] or "National University Support Team"
                note = admin_note if admin_note is not None else old["admin_note"]

                conn.execute("""
                    UPDATE token_requests
                    SET status = 'SOLVED', solve_message = ?, solver_name = ?, solved_date = ?, updated_date = ?, admin_note = ?
                    WHERE UPPER(token_id) = UPPER(?)
                """, (solve_message.strip(), final_solver, now_str, now_str, note, token_id.strip()))

                conn.execute("""
                    INSERT INTO token_history (token_id, old_status, new_status, changed_by, message, created_date)
                    VALUES (?, ?, 'SOLVED', ?, ?, ?)
                """, (token_id.strip(), old_status, changed_by, f"Problem solved: {solve_message[:100]}", now_str))

            return True
        finally:
            conn.close()

    def list_tokens(
        self,
        status: Optional[str] = None,
        service_type: Optional[str] = None,
        search: Optional[str] = None,
        department: Optional[str] = None,
        solver_name: Optional[str] = None,
        role: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[Dict[str, Any]], int]:
        conn = get_token_db_connection()
        try:
            query = "SELECT * FROM token_requests WHERE 1=1"
            count_query = "SELECT COUNT(*) as total FROM token_requests WHERE 1=1"
            params = []

            # Strict Role & Department Isolation for Solvers
            if role == "SOLVER" or (department and role not in ["ADMIN", "SUPER_ADMIN"]):
                dept_clean = (department or "").strip()
                s_name_clean = (solver_name or "").strip()
                
                solver_ids = []
                solver_names = set()
                if dept_clean:
                    solver_names.add(dept_clean)
                    s_rows = conn.execute("""
                        SELECT id, solver_name FROM token_solvers
                        WHERE solver_name = ? OR department = ? OR solver_name LIKE ? OR department LIKE ?
                    """, (dept_clean, dept_clean, f"%{dept_clean}%", f"%{dept_clean}%")).fetchall()
                    for r in s_rows:
                        solver_ids.append(r["id"])
                        solver_names.add(r["solver_name"])
                
                if s_name_clean:
                    solver_names.add(s_name_clean)
                    s_rows = conn.execute("""
                        SELECT id, solver_name FROM token_solvers
                        WHERE solver_name = ? OR solver_name LIKE ?
                    """, (s_name_clean, f"%{s_name_clean}%")).fetchall()
                    for r in s_rows:
                        solver_ids.append(r["id"])
                        solver_names.add(r["solver_name"])

                solver_ids = list(set(solver_ids))
                solver_names = list(solver_names)

                dept_conditions = []
                dept_params = []

                if solver_ids:
                    seq = ','.join(['?'] * len(solver_ids))
                    dept_conditions.append(f"solver_id IN ({seq})")
                    dept_params.extend(solver_ids)

                if solver_names:
                    nseq = ','.join(['?'] * len(solver_names))
                    dept_conditions.append(f"solver_name IN ({nseq})")
                    dept_params.extend(solver_names)

                if dept_clean:
                    dept_conditions.append("solver_name LIKE ?")
                    dept_params.append(f"%{dept_clean}%")

                if dept_conditions:
                    clause = f" AND ({' OR '.join(dept_conditions)})"
                    query += clause
                    count_query += clause
                    params.extend(dept_params)
                else:
                    query += " AND 1=0"
                    count_query += " AND 1=0"

            if status and status.upper() in ["DELETED", "TRASH"]:
                query += " AND is_deleted = 1"
                count_query += " AND is_deleted = 1"
            else:
                query += " AND (is_deleted = 0 OR is_deleted IS NULL)"
                count_query += " AND (is_deleted = 0 OR is_deleted IS NULL)"
                if status and status.upper() != "ALL":
                    query += " AND UPPER(status) = UPPER(?)"
                    count_query += " AND UPPER(status) = UPPER(?)"
                    params.append(status.strip())

            if service_type and service_type.upper() != "ALL":
                query += " AND UPPER(service_type) = UPPER(?)"
                count_query += " AND UPPER(service_type) = UPPER(?)"
                params.append(service_type.strip())

            if search and search.strip():
                s = f"%{search.strip()}%"
                query += " AND (token_id LIKE ? OR problem LIKE ? OR user_name LIKE ? OR registration_no LIKE ? OR user_phone LIKE ?)"
                count_query += " AND (token_id LIKE ? OR problem LIKE ? OR user_name LIKE ? OR registration_no LIKE ? OR user_phone LIKE ?)"
                params.extend([s, s, s, s, s])

            total = conn.execute(count_query, params).fetchone()["total"]

            query += " ORDER BY id DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows], total
        finally:
            conn.close()

    def get_solved_tokens(self, service_type: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        conn = get_token_db_connection()
        try:
            query = "SELECT token_id, service_type, problem, solve_message, solved_date FROM token_requests WHERE status = 'SOLVED' AND solve_message IS NOT NULL AND length(solve_message) > 5"
            params = []
            if service_type:
                query += " AND UPPER(service_type) = UPPER(?)"
                params.append(service_type.strip())
            query += " ORDER BY id DESC LIMIT ?"
            params.append(limit)

            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def soft_delete_token(self, token_id: str, admin_user: str = "Admin") -> bool:
        conn = get_token_db_connection()
        try:
            from datetime import datetime, timezone
            now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            cur = conn.execute("""
                UPDATE token_requests
                SET is_deleted = 1, deleted_at = ?, updated_date = ?
                WHERE UPPER(token_id) = UPPER(?)
            """, (now_str, now_str, token_id.strip()))
            
            if cur.rowcount > 0:
                conn.execute("""
                    INSERT INTO token_history (token_id, old_status, new_status, changed_by, message, created_date)
                    VALUES (?, 'ACTIVE', 'DELETED', ?, 'Token moved to trash by Super Admin', ?)
                """, (token_id.strip(), admin_user, now_str))
                conn.commit()
                return True
            return False
        finally:
            conn.close()

    def restore_token(self, token_id: str, admin_user: str = "Admin") -> bool:
        conn = get_token_db_connection()
        try:
            from datetime import datetime, timezone
            now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            cur = conn.execute("""
                UPDATE token_requests
                SET is_deleted = 0, deleted_at = NULL, updated_date = ?
                WHERE UPPER(token_id) = UPPER(?)
            """, (now_str, token_id.strip()))
            
            if cur.rowcount > 0:
                conn.execute("""
                    INSERT INTO token_history (token_id, old_status, new_status, changed_by, message, created_date)
                    VALUES (?, 'DELETED', 'RESTORED', ?, 'Token restored from trash by Super Admin', ?)
                """, (token_id.strip(), admin_user, now_str))
                conn.commit()
                return True
            return False
        finally:
            conn.close()
