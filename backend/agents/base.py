from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from llm.base import LLMRequest, LLMResponse


class BaseAgent(ABC):
    def __init__(self, db: Session, repo_id: str, model: str = "claude-3-sonnet"):
        self.db = db
        self.repo_id = repo_id
        self.model = model
        self.system_prompt = ""
    
    @abstractmethod
    async def process(self, user_message: str, context: dict = None) -> str:
        pass
    
    def _build_llm_request(self, user_message: str, history: list = None) -> LLMRequest:
        messages = history or []
        messages.append({"role": "user", "content": user_message})
        
        return LLMRequest(
            system_prompt=self.system_prompt,
            messages=messages,
            model=self.model,
            temperature=0.7,
            max_tokens=2000,
        )
    
    async def search_codebase(self, query: str, limit: int = 5):
        from models import CodeBlock
        results = self.db.query(CodeBlock).filter(
            CodeBlock.repository_id == self.repo_id,
            CodeBlock.entity_name.ilike(f"%{query}%")
        ).limit(limit).all()
        return results
    
    async def get_file_content(self, file_path: str):
        from models import CodeBlock
        blocks = self.db.query(CodeBlock).filter(
            (CodeBlock.repository_id == self.repo_id) &
            (CodeBlock.file_path == file_path)
        ).all()
        return blocks
