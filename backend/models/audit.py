from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from backend.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False, index=True)
    user_id = Column(String(100), nullable=True)
    username = Column(String(100), nullable=True)
    role = Column(String(50), nullable=True)
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(String(100), nullable=True)
    ip_address = Column(String(50), nullable=True)
    details_json = Column(Text, nullable=True)
    success = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
