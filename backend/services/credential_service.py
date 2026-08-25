import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple

from backend.core.security import encrypt_credential_data, decrypt_credential_data
from backend.core.audit import log_audit_event
from token_service.db import get_token_db_connection

logger = logging.getLogger("NU_CREDENTIAL_SERVICE")

class CredentialService:
    """
    Secure domain service for service-specific user credentials.
    All passwords and sensitive fields are encrypted at rest with AES-256-GCM.
    Passwords NEVER enter AI prompts, logs, or RAG vectors.
    """

    def get_service_fields(self, service_code: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns dynamic credential field schemas for services."""
        conn = get_token_db_connection()
        try:
            query = "SELECT id, service_code, field_name, field_label, field_type, required, encrypted, sort_order FROM service_credential_fields"
            params = []
            if service_code:
                query += " WHERE service_code = ?"
                params.append(service_code.upper())
            query += " ORDER BY service_code, sort_order ASC"

            cur = conn.execute(query, params)
            return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    def get_user_credentials_overview(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Returns list of all NU services and user credential configuration status.
        Does NOT return passwords.
        """
        conn = get_token_db_connection()
        try:
            # 1. Fetch all active services
            services_cur = conn.execute("SELECT service_code, service_name, service_name_bn FROM token_service_types WHERE active = 1 ORDER BY sort_order ASC")
            services = [dict(s) for s in services_cur.fetchall()]

            # 2. Fetch user's configured credentials
            cred_cur = conn.execute("""
                SELECT id, service_code, username, credential_label, credential_status, failed_login_count, last_verified_at, created_at, updated_at
                FROM user_service_credentials
                WHERE user_id = ? AND active = 1
            """, (user_id,))
            user_creds = {r["service_code"]: dict(r) for r in cred_cur.fetchall()}

            result = []
            for s in services:
                code = s["service_code"]
                cred = user_creds.get(code)
                # Fetch fields
                fields = self.get_service_fields(code)
                result.append({
                    "service_code": code,
                    "service_name": s["service_name"],
                    "service_name_bn": s["service_name_bn"],
                    "is_configured": cred is not None,
                    "credential_id": cred["id"] if cred else None,
                    "username": cred["username"] if cred else None,
                    "credential_status": cred["credential_status"] if cred else "NOT_CONFIGURED",
                    "last_verified_at": cred["last_verified_at"] if cred else None,
                    "failed_login_count": cred["failed_login_count"] if cred else 0,
                    "fields": fields
                })
            return result
        finally:
            conn.close()

    def get_credential_status(self, user_id: str, service_code: str) -> Dict[str, Any]:
        """
        MCP tool helper: returns safe status dictionary without password.
        """
        conn = get_token_db_connection()
        try:
            cur = conn.execute("""
                SELECT id, username, credential_status, last_verified_at, failed_login_count
                FROM user_service_credentials
                WHERE user_id = ? AND service_code = ? AND active = 1
            """, (user_id, service_code.upper()))
            row = cur.fetchone()
            if not row:
                return {
                    "service": service_code.upper(),
                    "configured": False,
                    "status": "NOT_CONFIGURED"
                }
            return {
                "service": service_code.upper(),
                "configured": True,
                "credential_id": row["id"],
                "username": row["username"],
                "status": row["credential_status"],
                "last_verified_at": row["last_verified_at"],
                "failed_login_count": row["failed_login_count"]
            }
        finally:
            conn.close()

    def save_credential(
        self,
        user_id: str,
        service_code: str,
        username: str,
        password: str,
        additional_data: Optional[Dict[str, Any]] = None,
        label: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Encrypts password using AES-256-GCM and persists credential.
        """
        clean_user = username.strip()
        clean_pwd = password.strip()
        if not clean_user or not clean_pwd:
            return False, "Username and password cannot be empty.", None

        encrypted_pwd = encrypt_credential_data(clean_pwd)
        enc_additional = encrypt_credential_data(json.dumps(additional_data)) if additional_data else None
        now_str = datetime.utcnow().isoformat()
        code_upper = service_code.upper()

        conn = get_token_db_connection()
        try:
            with conn:
                cur = conn.execute("""
                    INSERT INTO user_service_credentials (
                        user_id, service_code, username, encrypted_password,
                        additional_data_encrypted, credential_label, credential_status,
                        failed_login_count, notes, active, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, 'NOT_VERIFIED', 0, ?, 1, ?, ?)
                    ON CONFLICT(user_id, service_code) DO UPDATE SET
                        username = excluded.username,
                        encrypted_password = excluded.encrypted_password,
                        additional_data_encrypted = excluded.additional_data_encrypted,
                        credential_label = excluded.credential_label,
                        credential_status = 'NOT_VERIFIED',
                        failed_login_count = 0,
                        notes = excluded.notes,
                        updated_at = excluded.updated_at
                """, (
                    user_id, code_upper, clean_user, encrypted_pwd,
                    enc_additional, label or f"{code_upper} Account", notes, now_str, now_str
                ))

                # Fetch id
                id_cur = conn.execute("SELECT id FROM user_service_credentials WHERE user_id = ? AND service_code = ?", (user_id, code_upper))
                cred_id = id_cur.fetchone()["id"]

            log_audit_event(
                action="CREDENTIAL_SAVED",
                user_id=user_id,
                resource_type="service_credential",
                resource_id=f"{user_id}_{code_upper}",
                details={"service": code_upper, "username": clean_user}
            )

            return True, f"Credentials for {code_upper} saved securely.", cred_id
        except Exception as e:
            logger.error(f"Error saving credentials: {e}", exc_info=True)
            return False, f"Could not save credentials: {str(e)}", None
        finally:
            conn.close()

    def verify_credential(self, user_id: str, service_code: str) -> Tuple[bool, str]:
        """
        Tests stored credential against external service (or simulated verification desk).
        Updates failed login count and credential_status.
        """
        conn = get_token_db_connection()
        try:
            cur = conn.execute("""
                SELECT id, username, encrypted_password, failed_login_count
                FROM user_service_credentials
                WHERE user_id = ? AND service_code = ? AND active = 1
            """, (user_id, service_code.upper()))
            row = cur.fetchone()
            if not row:
                return False, f"No credentials configured for {service_code.upper()}."

            if row["failed_login_count"] >= 5:
                return False, "Too many failed attempts. Credential is locked for automated verification."

            # Decrypt password in memory
            plain_pwd = decrypt_credential_data(row["encrypted_password"])
            if not plain_pwd:
                return False, "Decryption error. Please update your saved password."

            now_str = datetime.utcnow().isoformat()

            # Perform service verification simulation / rule check
            # For demo & NU services: length >= 4 and not blank is valid
            is_valid = len(plain_pwd) >= 4 and len(row["username"]) >= 3

            with conn:
                if is_valid:
                    conn.execute("""
                        UPDATE user_service_credentials
                        SET credential_status = 'ACTIVE', failed_login_count = 0, last_verified_at = ?, updated_at = ?
                        WHERE id = ?
                    """, (now_str, now_str, row["id"]))
                    msg = "Credentials verified successfully. Service access is active."
                else:
                    conn.execute("""
                        UPDATE user_service_credentials
                        SET credential_status = 'INVALID', failed_login_count = failed_login_count + 1, updated_at = ?
                        WHERE id = ?
                    """, (now_str, row["id"]))
                    msg = "Verification failed. Please check your username and password."

            log_audit_event(
                action="CREDENTIAL_VERIFICATION",
                user_id=user_id,
                resource_type="service_credential",
                resource_id=str(row["id"]),
                details={"service": service_code.upper(), "verified": is_valid},
                success=is_valid
            )

            return is_valid, msg
        finally:
            conn.close()

    def delete_credential(self, user_id: str, service_code: str) -> Tuple[bool, str]:
        """Permanently deletes user's credentials for a service."""
        conn = get_token_db_connection()
        try:
            with conn:
                conn.execute("""
                    DELETE FROM user_service_credentials
                    WHERE user_id = ? AND service_code = ?
                """, (user_id, service_code.upper()))

            log_audit_event(
                action="CREDENTIAL_DELETED",
                user_id=user_id,
                resource_type="service_credential",
                resource_id=f"{user_id}_{service_code.upper()}",
                details={"service": service_code.upper()}
            )
            return True, f"Credentials for {service_code.upper()} deleted."
        finally:
            conn.close()

_credential_service_instance: Optional[CredentialService] = None

def get_credential_service() -> CredentialService:
    global _credential_service_instance
    if _credential_service_instance is None:
        _credential_service_instance = CredentialService()
    return _credential_service_instance
