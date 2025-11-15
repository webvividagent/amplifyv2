from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class LLMMessage:
    role: str
    content: str


@dataclass
class LLMTool:
    name: str
    description: str
    parameters: Dict[str, Any]


class LLMRequest(BaseModel):
    system_prompt: Optional[str] = None
    messages: List[Dict[str, str]]
    model: str
    temperature: float = 0.7
    max_tokens: int = 2000
    tools: Optional[List[LLMTool]] = None


class LLMResponse(BaseModel):
    content: str
    tokens_used: int
    cost: float
    model: str
    finish_reason: str


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        pass
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        pass
    
    @abstractmethod
    def get_cost_per_1k_tokens(self) -> float:
        pass
