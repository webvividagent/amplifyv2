import httpx
import json
from .base import LLMProvider, LLMRequest, LLMResponse
from config import settings


class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip('/')
        self.model = model or settings.DEFAULT_OLLAMA_MODEL
        self.client = httpx.Client(timeout=120.0)
        
        self.model_info = {
            "codellama:latest": {"tokens_per_second": 10, "code_focused": True},
            "codellama:7b": {"tokens_per_second": 10, "code_focused": True},
            "granite-8b-code-base-128k-GGUF:Q4_K_M": {"tokens_per_second": 8, "code_focused": True},
            "deepseek-coder:latest": {"tokens_per_second": 12, "code_focused": True},
            "qwen3:8b": {"tokens_per_second": 15, "code_focused": False},
            "llama3:latest": {"tokens_per_second": 12, "code_focused": False},
            "mistral:latest": {"tokens_per_second": 15, "code_focused": False},
        }
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        messages = request.messages
        
        if request.system_prompt:
            messages = [
                {"role": "system", "content": request.system_prompt},
                *messages
            ]
        
        payload = {
            "model": request.model or self.model,
            "messages": messages,
            "stream": False,
            "temperature": request.temperature,
        }
        
        try:
            response = self.client.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=300.0
            )
            response.raise_for_status()
            
            result = response.json()
            
            tokens_used = self._count_tokens(result.get("message", {}).get("content", ""))
            
            return LLMResponse(
                content=result.get("message", {}).get("content", ""),
                tokens_used=tokens_used,
                cost=0.0,
                model=request.model or self.model,
                finish_reason=result.get("done", True) and "stop" or "incomplete",
            )
        
        except Exception as e:
            raise RuntimeError(f"Ollama API error: {str(e)}")
    
    def count_tokens(self, text: str) -> int:
        return self._count_tokens(text)
    
    def _count_tokens(self, text: str) -> int:
        return len(text.split()) + len(text.split('\n'))
    
    def get_cost_per_1k_tokens(self) -> float:
        return 0.0
    
    async def list_available_models(self) -> list:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                
                result = response.json()
                models = [model.get("name", "") for model in result.get("models", [])]
                return models
        
        except Exception as e:
            raise RuntimeError(f"Failed to list Ollama models: {str(e)}")
    
    async def pull_model(self, model_name: str) -> bool:
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                response = await client.post(
                    f"{self.base_url}/api/pull",
                    json={"name": model_name}
                )
                response.raise_for_status()
                return True
        
        except Exception as e:
            raise RuntimeError(f"Failed to pull model {model_name}: {str(e)}")
    
    def get_recommended_code_models(self) -> list:
        code_focused_models = [
            name for name, info in self.model_info.items()
            if info.get("code_focused", False)
        ]
        return code_focused_models
    
    def close(self):
        self.client.close()
