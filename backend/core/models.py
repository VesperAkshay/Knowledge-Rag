"""
Pydantic Models for API
"""
from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str
    stream: bool = False

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str

class UploadURLRequest(BaseModel):
    """Request model for URL upload"""
    url: str

class UploadResponse(BaseModel):
    """Response model for upload endpoints"""
    success: bool
    message: str
    chunks: int
    filename: Optional[str] = None
    url: Optional[str] = None

class KnowledgeBaseInfo(BaseModel):
    """Knowledge base information"""
    document_count: int
    last_updated: Optional[str] = None

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str = "1.0.0"
