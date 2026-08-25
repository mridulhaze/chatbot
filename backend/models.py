from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role: 'user' or 'bot' / 'assistant'")
    content: str = Field(..., description="Message text")

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1500, description="User question or query")
    history: List[ChatMessage] = Field(default_factory=list, description="Recent multi-turn conversation messages")
    session_id: Optional[str] = Field(default=None, description="Optional client session ID")

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

class GapApprovalRequest(BaseModel):
    custom_answer: Optional[str] = None

class ManualCrawlRequest(BaseModel):
    source: Optional[str] = Field(default="all", description="Source to crawl: all, notices, admission, results, ems, ict")

class DeepCrawlRequest(BaseModel):
    max_pages: int = Field(default=50, ge=5, le=5000, description="Max recursive pages to crawl")
    delay_seconds: float = Field(default=0.5, ge=0.2, le=5.0, description="Polite delay between requests")
