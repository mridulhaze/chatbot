from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from backend.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(150), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=True)
    department = Column(String(150), nullable=True)
    role = Column(String(50), default="USER", nullable=False)  # USER, SOLVER, ADMIN, SUPER_ADMIN
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
