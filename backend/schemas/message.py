from pydantic import BaseModel
from typing import List
from uuid import UUID


class MessageResponse(BaseModel):
    id: UUID
    session_id: UUID
    role: str
    content: str
    files_referenced: List[str]
    tools_used: List[str]
    tokens_used: int
    created_at: str
    
    class Config:
        from_attributes = True
