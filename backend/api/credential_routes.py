import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, Header
from pydantic import BaseModel, Field

from backend.services.credential_service import get_credential_service
from backend.core.security import get_current_user_optional

logger = logging.getLogger("NU_CREDENTIAL_API")
router = APIRouter(prefix="/api/v1/credentials", tags=["Service Credentials Management"])

class CredentialSaveRequest(BaseModel):
    user_id: Optional[str] = None
    service_code: str = Field(..., description="Service code (EMS, FORM_FILLUP, CERTIFICATE, etc.)")
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    additional_data: Optional[Dict[str, Any]] = None
    label: Optional[str] = None
    notes: Optional[str] = None

class CredentialVerifyRequest(BaseModel):
    user_id: Optional[str] = None
    service_code: str

def _resolve_user_id(user_id: Optional[str], auth_user: Optional[Dict[str, Any]], session_header: Optional[str]) -> str:
    if auth_user and auth_user.get("username"):
        return str(auth_user["username"])
    if user_id and user_id.strip():
        return user_id.strip()
    if session_header and session_header.strip():
        return session_header.strip()
    return "guest_user"

@router.get("/services-overview")
def get_user_credentials_overview(
    user_id: Optional[str] = Query(None),
    x_session_id: Optional[str] = Header(None),
    auth_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    uid = _resolve_user_id(user_id, auth_user, x_session_id)
    service = get_credential_service()
    return service.get_user_credentials_overview(uid)

@router.get("/fields/{service_code}")
def get_service_credential_fields(service_code: str):
    service = get_credential_service()
    fields = service.get_service_fields(service_code.upper())
    return {"service_code": service_code.upper(), "fields": fields}

@router.get("/status/{service_code}")
def get_credential_status(
    service_code: str,
    user_id: Optional[str] = Query(None),
    x_session_id: Optional[str] = Header(None),
    auth_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    uid = _resolve_user_id(user_id, auth_user, x_session_id)
    service = get_credential_service()
    return service.get_credential_status(uid, service_code.upper())

@router.post("/save")
def save_user_service_credential(
    payload: CredentialSaveRequest,
    x_session_id: Optional[str] = Header(None),
    auth_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    uid = _resolve_user_id(payload.user_id, auth_user, x_session_id)
    service = get_credential_service()
    ok, msg, cred_id = service.save_credential(
        user_id=uid,
        service_code=payload.service_code.upper(),
        username=payload.username,
        password=payload.password,
        additional_data=payload.additional_data,
        label=payload.label,
        notes=payload.notes
    )
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {
        "success": True,
        "message": msg,
        "credential_id": cred_id,
        "service_code": payload.service_code.upper()
    }

@router.post("/verify")
def verify_user_service_credential(
    payload: CredentialVerifyRequest,
    x_session_id: Optional[str] = Header(None),
    auth_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    uid = _resolve_user_id(payload.user_id, auth_user, x_session_id)
    service = get_credential_service()
    ok, msg = service.verify_credential(uid, payload.service_code.upper())
    if not ok:
        return {"success": False, "verified": False, "message": msg}
    return {"success": True, "verified": True, "message": msg}

@router.delete("/{service_code}")
def delete_user_service_credential(
    service_code: str,
    user_id: Optional[str] = Query(None),
    x_session_id: Optional[str] = Header(None),
    auth_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    uid = _resolve_user_id(user_id, auth_user, x_session_id)
    service = get_credential_service()
    ok, msg = service.delete_credential(uid, service_code.upper())
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg}
