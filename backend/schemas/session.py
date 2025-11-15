from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID


class SessionCreate(BaseModel):
    repository_id: UUID
    agent_type: str = "coding"
    model: Optional[str] = None


class SessionResponse(BaseModel):
    id: UUID
    repository_id: UUID
    agent_type: str
    model: str
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    session_id: Optional[UUID] = None
    repository_id: Optional[UUID] = None
    agent_type: str = "coding"
    message: str
    files: Optional[List[str]] = None
    model: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: UUID
    message_id: UUID
    content: str
    tools_used: List[str] = []
    tokens_used: int
    created_at: str
