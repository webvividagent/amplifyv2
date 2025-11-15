from sqlalchemy.orm import Session
from .base import BaseAgent
from llm import OllamaProvider
from llm.base import LLMRequest


class CodingAgent(BaseAgent):
    def __init__(self, db: Session, repo_id: str, model: str = "codellama:latest"):
        super().__init__(db, repo_id, model)
        self.system_prompt = """You are an expert AI code generation and modification assistant.

Your capabilities include:
1. Generating new code from specifications
2. Refactoring existing code for better readability and performance
3. Fixing bugs and errors
4. Explaining code functionality
5. Suggesting improvements and best practices

When generating code:
- Follow best practices and design patterns
- Include appropriate comments and docstrings
- Consider error handling and edge cases
- Suggest tests when applicable

Always provide clear explanations of your changes and reasoning."""
        self.provider = OllamaProvider(model=model)
    
    async def process(self, user_message: str, context: dict = None, history: list = None) -> str:
        context = context or {}
        history = history or []
        
        relevant_code = await self.search_codebase(user_message, limit=3)
        
        context_str = ""
        if relevant_code:
            context_str = "\n\nRelevant code from the repository:\n"
            for block in relevant_code:
                context_str += f"\nFile: {block.file_path}\n{block.content}\n"
        
        enhanced_message = f"{user_message}{context_str}"
        
        llm_request = self._build_llm_request(enhanced_message, history)
        response = await self.provider.generate(llm_request)
        
        return response.content
    
    async def generate_code(self, specification: str, language: str = "python"):
        prompt = f"""Generate {language} code based on the following specification:

{specification}

Provide complete, working code with:
- Proper error handling
- Type hints (where applicable)
- Documentation
- Example usage if applicable"""
        
        return await self.process(prompt)
    
    async def refactor_code(self, code: str, improvement_focus: str = "readability"):
        prompt = f"""Refactor the following code focusing on {improvement_focus}:

```
{code}
```

Provide:
1. Refactored code
2. Explanation of changes
3. Any warnings or breaking changes"""
        
        return await self.process(prompt)
    
    async def debug_code(self, code: str, error_message: str):
        prompt = f"""Debug the following code:

Code:
```
{code}
```

Error: {error_message}

Provide:
1. Root cause analysis
2. Fixed code
3. Explanation of the fix"""
        
        return await self.process(prompt)
