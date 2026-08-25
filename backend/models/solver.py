from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from backend.core.database import Base

class TokenSolver(Base):
    __tablename__ = "token_solvers"
    
    id = Column(Integer, primary_key=True, index=True)
    solver_name = Column(String(150), unique=True, nullable=False)
    department = Column(String(150), nullable=False)
    email = Column(String(150), nullable=True)
    phone = Column(String(50), nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
