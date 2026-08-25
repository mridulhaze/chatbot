import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger("NU_AUDIT_LOG")

def log_audit_event(
    action: str,
    user_id: Optional[str] = None,
    username: Optional[str] = None,
    role: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    success: bool = True
):
    """
    Structured audit logger for authentication, token mutations, solver actions,
    and MCP tool executions.
    """
    timestamp = datetime.utcnow().isoformat()
    record = {
        "timestamp": timestamp,
        "action": action,
        "user_id": user_id,
        "username": username,
        "role": role,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "ip_address": ip_address,
        "details": details or {},
        "success": success
    }
    
    # Format and log
    logger.info(f"[AUDIT] {json.dumps(record, ensure_ascii=False)}")
    
    # Store into SQLite/Postgres audit table if database is available
    try:
        from token_service.db import get_token_db_connection
        conn = get_token_db_connection()
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    action TEXT NOT NULL,
                    user_id TEXT,
                    username TEXT,
                    role TEXT,
                    resource_type TEXT,
                    resource_id TEXT,
                    ip_address TEXT,
                    details_json TEXT,
                    success INTEGER NOT NULL
                )
            """)
            conn.execute("""
                INSERT INTO audit_logs (
                    timestamp, action, user_id, username, role,
                    resource_type, resource_id, ip_address, details_json, success
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp, action, user_id, username, role,
                resource_type, resource_id, ip_address,
                json.dumps(details or {}, ensure_ascii=False),
                1 if success else 0
            ))
        conn.close()

        # Also mirror into system_activity_logs for activity dashboard & report exports
        try:
            from backend.services.activity_tracker import ActivityTracker
            ActivityTracker.record_event(
                event_type=action,
                service_code=(details or {}).get("service") or resource_type,
                user_identifier=username or user_id or "ANONYMOUS_STUDENT",
                solver_name=role or username,
                status="SUCCESS" if success else "FAILED",
                details=details,
                ip_address=ip_address
            )
        except Exception:
            pass

    except Exception as e:
        logger.warning(f"Could not persist audit log to DB: {e}")

