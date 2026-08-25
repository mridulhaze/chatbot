import time
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class SessionState(BaseModel):
    session_id: str
    active_skill: Optional[str] = None
    selected_service_code: Optional[str] = None
    selected_service_name: Optional[str] = None
    problem_description: Optional[str] = None
    similar_case_shown: bool = False
    pending_token_confirmation: bool = False
    last_created_token_id: Optional[str] = None
    turn_count: int = 0
    last_activity_time: float = Field(default_factory=time.time)

class ContextManager:
    """
    In-memory multi-turn session state manager.
    Maintains user workflow state across conversation turns.
    """
    def __init__(self, ttl_seconds: int = 3600):
        self._sessions: Dict[str, SessionState] = {}
        self.ttl_seconds = ttl_seconds

    def get_session(self, session_id: Optional[str]) -> SessionState:
        sid = session_id or "default_session"
        now = time.time()
        
        # Cleanup if expired
        if sid in self._sessions:
            if now - self._sessions[sid].last_activity_time > self.ttl_seconds:
                del self._sessions[sid]

        if sid not in self._sessions:
            self._sessions[sid] = SessionState(session_id=sid)
            
        self._sessions[sid].last_activity_time = now
        return self._sessions[sid]

    def update_session(self, session: SessionState):
        session.last_activity_time = time.time()
        session.turn_count += 1
        self._sessions[session.session_id] = session

    def reset_session_workflow(self, session_id: str):
        if session_id in self._sessions:
            s = self._sessions[session_id]
            s.active_skill = None
            s.selected_service_code = None
            s.selected_service_name = None
            s.problem_description = None
            s.similar_case_shown = False
            s.pending_token_confirmation = False

_context_manager_instance: Optional[ContextManager] = None

def get_context_manager() -> ContextManager:
    global _context_manager_instance
    if _context_manager_instance is None:
        _context_manager_instance = ContextManager()
    return _context_manager_instance
