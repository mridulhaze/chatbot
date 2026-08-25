from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from backend.core.database import Base

class TokenHistory(Base):
    __tablename__ = "token_history"
    
    id = Column(Integer, primary_key=True, index=True)
    token_id = Column(String(50), nullable=False, index=True)
    old_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False)
    changed_by = Column(String(100), default="SYSTEM", nullable=False)
    message = Column(Text, nullable=True)
    created_date = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class TokenAttachment(Base):
    __tablename__ = "token_attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    token_id = Column(String(50), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=True)
    uploaded_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
