from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class RepositoryCreate(BaseModel):
    name: str
    git_url: Optional[str] = None
    local_path: Optional[str] = None
    language: Optional[str] = None
    description: Optional[str] = None


class RepositoryResponse(BaseModel):
    id: UUID
    name: str
    git_url: Optional[str] = None
    local_path: Optional[str] = None
    language: Optional[str] = None
    indexed: bool
    index_version: Optional[str] = None
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class RepositorySearchRequest(BaseModel):
    query: str
    entity_type: Optional[str] = None
    limit: int = 10
