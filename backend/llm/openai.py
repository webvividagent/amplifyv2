import openai
from .base import LLMProvider, LLMRequest, LLMResponse
from config import settings


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model_pricing = {
            "gpt-4": 0.03,
            "gpt-4-turbo": 0.01,
            "gpt-4-turbo-preview": 0.01,
            "gpt-3.5-turbo": 0.0015,
        }
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        messages = [{"role": msg["role"], "content": msg["content"]} for msg in request.messages]
        
        kwargs = {
            "model": request.model,
            "messages": messages,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
        }
        
        response = self.client.chat.completions.create(**kwargs)
        
        tokens_used = response.usage.prompt_tokens + response.usage.completion_tokens
        cost = (tokens_used / 1000) * self.get_cost_per_1k_tokens()
        
        return LLMResponse(
            content=response.choices[0].message.content,
            tokens_used=tokens_used,
            cost=cost,
            model=request.model,
            finish_reason=response.choices[0].finish_reason,
        )
    
    def count_tokens(self, text: str) -> int:
        return len(text) // 4
    
    def get_cost_per_1k_tokens(self) -> float:
        return self.model_pricing.get("gpt-3.5-turbo", 0.0015)
