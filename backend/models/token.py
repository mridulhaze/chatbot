from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from backend.core.database import Base

class TokenServiceType(Base):
    __tablename__ = "token_service_types"
    
    id = Column(Integer, primary_key=True, index=True)
    service_code = Column(String(50), unique=True, nullable=False, index=True)
    service_name = Column(String(150), nullable=False)
    service_name_bn = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TokenRequest(Base):
    __tablename__ = "token_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    token_id = Column(String(50), unique=True, nullable=False, index=True)
    service_type = Column(String(50), nullable=False, index=True)
    service_name = Column(String(150), nullable=True)
    problem = Column(Text, nullable=False)
    status = Column(String(50), default="PENDING", nullable=False, index=True)
    priority = Column(String(50), default="NORMAL", nullable=False)
    
    solver_id = Column(Integer, ForeignKey("token_solvers.id"), nullable=True)
    solver_name = Column(String(150), nullable=True)
    solve_message = Column(Text, nullable=True)
    admin_note = Column(Text, nullable=True)  # Strictly hidden from public/AI
    
    user_id = Column(String(100), nullable=True, index=True)
    user_name = Column(String(150), nullable=True)
    user_email = Column(String(150), nullable=True)
    user_phone = Column(String(50), nullable=True)
    registration_no = Column(String(50), nullable=True)
    college_code = Column(String(50), nullable=True)
    
    created_date = Column(String(50), nullable=False)
    updated_date = Column(String(50), nullable=False)
    solved_date = Column(String(50), nullable=True)
    estimated_solve_date = Column(String(50), nullable=True)
    closed_date = Column(String(50), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TokenSequence(Base):
    __tablename__ = "token_sequences"
    
    year = Column(Integer, primary_key=True)
    last_seq = Column(Integer, default=0, nullable=False)
