from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ServiceTypeModel(BaseModel):
    id: int
    service_code: str
    service_name: str
    service_name_bn: str
    description: Optional[str] = None
    active: bool = True
    sort_order: int = 0

class SolverModel(BaseModel):
    id: int
    solver_name: str
    department: str
    email: Optional[str] = None
    phone: Optional[str] = None
    active: bool = True

class TokenHistoryModel(BaseModel):
    id: int
    token_id: str
    old_status: Optional[str] = None
    new_status: str
    changed_by: str
    message: Optional[str] = None
    created_date: str

class TokenCreateRequest(BaseModel):
    service_type: str = Field(..., description="Service code (e.g. FORM_FILLUP, EMS, CERTIFICATE, etc.)")
    problem: str = Field(..., min_length=5, max_length=2000, description="Detailed problem description")
    user_name: Optional[str] = Field(None, max_length=150)
    user_email: Optional[str] = Field(None, max_length=150)
    user_phone: Optional[str] = Field(None, max_length=50)
    registration_no: Optional[str] = Field(None, max_length=50)
    college_code: Optional[str] = Field(None, max_length=50)
    priority: Optional[str] = Field("NORMAL", description="NORMAL, HIGH, URGENT")

class TokenSubmitDetailsRequest(BaseModel):
    service_type: str = Field(..., description="Service code (e.g. FORM_FILLUP, EMS, TC)")
    problem: str = Field(..., min_length=3, description="Problem description")
    user_name: Optional[str] = None
    user_phone: Optional[str] = None
    registration_no: Optional[str] = None
    college_code: Optional[str] = None

class TokenCreateResponse(BaseModel):
    success: bool
    token_id: str
    service_type: str
    service_name: str
    problem: str
    status: str
    created_date: str
    estimated_solve_date: Optional[str] = None
    message: str

class TokenPublicDetailResponse(BaseModel):
    token_id: str
    service_type: str
    service_name: str
    problem: str
    status: str
    status_display: str
    status_badge: str
    solver_name: Optional[str] = None
    solve_message: Optional[str] = None
    created_date: str
    updated_date: str
    estimated_solve_date: Optional[str] = None
    solved_date: Optional[str] = None
    history: List[TokenHistoryModel] = Field(default_factory=list)

class TokenAdminDetailResponse(TokenPublicDetailResponse):
    id: int
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    user_phone: Optional[str] = None
    registration_no: Optional[str] = None
    college_code: Optional[str] = None
    priority: str
    admin_note: Optional[str] = None
    solver_id: Optional[int] = None

class TokenAssignRequest(BaseModel):
    solver_id: int
    admin_note: Optional[str] = None

class TokenStatusUpdateRequest(BaseModel):
    status: str = Field(..., description="PENDING, ASSIGNED, PROCESSING, SOLVED, CLOSED, REJECTED")
    message: Optional[str] = None
    admin_note: Optional[str] = None

class TokenSolveRequest(BaseModel):
    solve_message: str = Field(..., min_length=5, description="Clear solution message explaining how the problem was resolved")
    solver_name: Optional[str] = None
    admin_note: Optional[str] = None

class SolvedSimilarProblem(BaseModel):
    token_id: str
    service_type: str
    service_name: str
    problem: str
    solution: str
    solved_date: Optional[str] = None
    similarity_score: float = 1.0
