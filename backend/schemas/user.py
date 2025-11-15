from pydantic import BaseModel, EmailStr, field_serializer
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: UUID
    subscription_tier: str
    created_at: datetime
    
    @field_serializer('created_at')
    def serialize_created_at(self, value: datetime):
        return value.isoformat() if isinstance(value, datetime) else value
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
