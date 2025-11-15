from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import uuid


class Repository(Base):
    __tablename__ = "repositories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False, index=True)
    git_url = Column(String, nullable=True)
    local_path = Column(String, nullable=True)
    language = Column(String, nullable=True)
    indexed = Column(Boolean, default=False)
    index_version = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    repo_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_synced = Column(DateTime, nullable=True)
    
    owner = relationship("User", back_populates="repositories")
    sessions = relationship("Session", back_populates="repository")
    code_blocks = relationship("CodeBlock", back_populates="repository")
    
    def __repr__(self):
        return f"<Repository {self.name}>"
