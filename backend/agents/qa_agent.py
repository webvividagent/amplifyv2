from sqlalchemy.orm import Session
from .base import BaseAgent
from llm import OllamaProvider


class QAAgent(BaseAgent):
    def __init__(self, db: Session, repo_id: str, model: str = "llama3:latest"):
        super().__init__(db, repo_id, model)
        self.system_prompt = """You are a knowledgeable code analysis and explanation assistant.

Your capabilities include:
1. Explaining how code works
2. Answering questions about the codebase
3. Providing documentation and examples
4. Suggesting improvements and best practices
5. Analyzing code architecture and design

When answering:
- Be clear and concise
- Provide examples when helpful
- Reference specific code sections when relevant
- Explain both the "what" and "why"
- Suggest alternatives when applicable"""
        self.provider = OllamaProvider(model=model)
    
    async def process(self, user_message: str, context: dict = None, history: list = None) -> str:
        context = context or {}
        history = history or []
        
        relevant_code = await self.search_codebase(user_message, limit=5)
        
        context_str = ""
        if relevant_code:
            context_str = "\n\nRelevant code from the repository:\n"
            for block in relevant_code:
                context_str += f"\nFile: {block.file_path}\nFunction/Class: {block.entity_name}\n"
                context_str += f"{block.content}\n"
        
        enhanced_message = f"{user_message}{context_str}"
        
        llm_request = self._build_llm_request(enhanced_message, history)
        response = await self.provider.generate(llm_request)
        
        return response.content
    
    async def explain_code(self, code: str):
        prompt = f"""Explain the following code in detail:

```
{code}
```

Cover:
1. What the code does
2. How it works
3. Key components and their purpose
4. Any important edge cases or considerations"""
        
        return await self.process(prompt)
    
    async def answer_question(self, question: str):
        prompt = f"""Answer the following question about the codebase:

{question}

Provide:
1. Direct answer
2. Relevant code examples if applicable
3. Additional context or suggestions"""
        
        return await self.process(prompt)
    
    async def suggest_improvements(self, code_section: str = None):
        if code_section:
            prompt = f"""Analyze the following code and suggest improvements:

```
{code_section}
```

Provide:
1. Identified issues or areas for improvement
2. Suggested improvements with reasoning
3. Potential risks or considerations"""
        else:
            prompt = """Analyze the codebase and suggest overall improvements in:
1. Code quality
2. Performance
3. Maintainability
4. Test coverage
5. Documentation"""
        
        return await self.process(prompt)
