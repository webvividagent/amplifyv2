from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSON, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import uuid
import enum


class EntityType(str, enum.Enum):
    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"
    CONSTANT = "constant"
    VARIABLE = "variable"
    IMPORT = "import"


class CodeBlock(Base):
    __tablename__ = "code_blocks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repository_id = Column(UUID(as_uuid=True), ForeignKey("repositories.id"), nullable=False)
    file_path = Column(String, nullable=False, index=True)
    start_line = Column(Integer, nullable=False)
    end_line = Column(Integer, nullable=False)
    language = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    entity_type = Column(SQLEnum(EntityType), nullable=True)
    entity_name = Column(String, nullable=True, index=True)
    dependencies = Column(ARRAY(String), default=list)
    imports = Column(ARRAY(String), default=list)
    docstring = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    repository = relationship("Repository", back_populates="code_blocks")
    
    def __repr__(self):
        return f"<CodeBlock {self.file_path}:{self.start_line}>"
