import anthropic
from .base import LLMProvider, LLMRequest, LLMResponse
from config import settings


class ClaudeProvider(LLMProvider):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model_pricing = {
            "claude-3-opus": 0.015,
            "claude-3-sonnet": 0.003,
            "claude-3-haiku": 0.00025,
        }
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        messages = [{"role": msg["role"], "content": msg["content"]} for msg in request.messages]
        
        kwargs = {
            "model": request.model,
            "max_tokens": request.max_tokens,
            "messages": messages,
        }
        
        if request.system_prompt:
            kwargs["system"] = request.system_prompt
        
        response = self.client.messages.create(**kwargs)
        
        tokens_used = response.usage.input_tokens + response.usage.output_tokens
        cost = (tokens_used / 1000) * self.get_cost_per_1k_tokens()
        
        return LLMResponse(
            content=response.content[0].text,
            tokens_used=tokens_used,
            cost=cost,
            model=request.model,
            finish_reason=response.stop_reason,
        )
    
    def count_tokens(self, text: str) -> int:
        return len(text) // 4
    
    def get_cost_per_1k_tokens(self) -> float:
        for model, price in self.model_pricing.items():
            if model in self.client._model_name or self.client._model_name in model:
                return price
        return self.model_pricing.get("claude-3-sonnet", 0.003)
