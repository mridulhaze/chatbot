from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any

# --- Auth Schemas ---
class UserLoginRequest(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=4)

class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = "USER"  # USER, SOLVER, ADMIN

class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: str
    department: Optional[str] = None
    active: bool

class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# --- Chat & Orchestrator Schemas ---
class ChatMessage(BaseModel):
    role: str = Field(..., description="Role: 'user' or 'bot' / 'assistant'")
    content: str = Field(..., description="Message text")

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User query or message")
    history: List[ChatMessage] = Field(default_factory=list, description="Multi-turn conversation history")
    session_id: Optional[str] = Field(default=None, description="Unique client session ID")
    service_code: Optional[str] = Field(default=None, description="Preselected service context")

class SourceCitation(BaseModel):
    title: str
    url: str
    date: Optional[str] = None
    category: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    sources: List[str] = Field(default_factory=list)
    citations: List[SourceCitation] = Field(default_factory=list)
    suggested_chips: List[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0)
    intent: str = Field(default="general")
    language: str = Field(default="bn")
    is_fallback: bool = Field(default=False)
    skill_used: Optional[str] = None
    token_card: Optional[Dict[str, Any]] = None
    interactive_buttons: Optional[List[Dict[str, str]]] = None

# --- MCP Standard Response Wrapper ---
class MCPResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

# --- Token Service Schemas ---
class ServiceTypeSchema(BaseModel):
    id: int
    service_code: str
    service_name: str
    service_name_bn: str
    description: Optional[str] = None
    active: bool = True
    sort_order: int = 0

class SolverSchema(BaseModel):
    id: int
    solver_name: str
    department: str
    email: Optional[str] = None
    phone: Optional[str] = None
    active: bool = True

class TokenCreateRequest(BaseModel):
    service_code: str = Field(..., description="Service code (e.g. FORM_FILLUP, EMS, CERTIFICATE, etc.)")
    problem: str = Field(..., min_length=5, max_length=2000, description="Problem description")
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    user_phone: Optional[str] = None
    registration_no: Optional[str] = None
    college_code: Optional[str] = None
    priority: Optional[str] = "NORMAL"

class TokenCreateResponse(BaseModel):
    success: bool
    token_id: str
    service_code: str
    service_name: str
    problem: str
    status: str
    created_date: str
    message: str

class TokenHistorySchema(BaseModel):
    id: int
    token_id: str
    old_status: Optional[str] = None
    new_status: str
    changed_by: str
    message: Optional[str] = None
    created_date: str

class TokenPublicStatus(BaseModel):
    token_id: str
    service_code: str
    service_name: str
    problem: str
    status: str
    status_display: str
    status_badge: str
    solver_name: Optional[str] = None
    solve_message: Optional[str] = None
    created_date: str
    updated_date: str
    solved_date: Optional[str] = None
    history: List[TokenHistorySchema] = Field(default_factory=list)

class TokenAdminDetail(TokenPublicStatus):
    id: int
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    user_phone: Optional[str] = None
    registration_no: Optional[str] = None
    college_code: Optional[str] = None
    priority: str
    admin_note: Optional[str] = None
    solver_id: Optional[int] = None

class SolvedSimilarProblem(BaseModel):
    token_id: str
    service_code: str
    service_name: str
    problem: str
    solution: str
    solved_date: Optional[str] = None
    similarity_score: float = 1.0

# --- Token Management Actions ---
class TokenAssignRequest(BaseModel):
    solver_id: int
    admin_note: Optional[str] = None

class TokenStatusUpdateRequest(BaseModel):
    status: str = Field(..., description="PENDING, ASSIGNED, PROCESSING, SOLVED, CLOSED, REJECTED")
    message: Optional[str] = None
    admin_note: Optional[str] = None

class TokenReturnRequest(BaseModel):
    reason: str = Field(..., min_length=3, description="Reason for sending back to admin for further instructions")
    solver_name: Optional[str] = None

class TokenSolveRequest(BaseModel):
    solve_message: str = Field(..., min_length=5, description="Clear solution steps for the student")
    solver_name: Optional[str] = None
    admin_note: Optional[str] = None

class GapApprovalRequest(BaseModel):
    custom_answer: Optional[str] = None

class ManualCrawlRequest(BaseModel):
    source: Optional[str] = Field(default="all", description="Source to crawl: all, notices, admission, results, ems, ict")

class DeepCrawlRequest(BaseModel):
    max_pages: int = Field(default=50, ge=5, le=5000, description="Max recursive pages to crawl")
    delay_seconds: float = Field(default=0.5, ge=0.2, le=5.0, description="Polite delay between requests")
