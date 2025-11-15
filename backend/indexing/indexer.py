import os
import ast
from pathlib import Path
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from models import CodeBlock, Repository
from models.code_index import EntityType


class RepositoryIndexer:
    def __init__(self, db: Session, repo_id: str, repo_path: str):
        self.db = db
        self.repo_id = repo_id
        self.repo_path = repo_path
        self.supported_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.java', '.cpp', '.c'}
    
    async def index_repository(self) -> Dict[str, any]:
        total_files = 0
        indexed_files = 0
        errors = []
        
        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__' and d != 'node_modules']
            
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, self.repo_path)
                
                ext = os.path.splitext(file)[1]
                if ext not in self.supported_extensions:
                    continue
                
                total_files += 1
                try:
                    await self._index_file(file_path, relative_path, ext)
                    indexed_files += 1
                except Exception as e:
                    errors.append(f"{relative_path}: {str(e)}")
        
        repo = self.db.query(Repository).filter(Repository.id == self.repo_id).first()
        if repo:
            repo.indexed = True
            repo.index_version = "1.0"
            self.db.commit()
        
        return {
            "total_files": total_files,
            "indexed_files": indexed_files,
            "errors": errors
        }
    
    async def _index_file(self, file_path: str, relative_path: str, ext: str):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        language = self._get_language(ext)
        
        if ext == '.py':
            await self._index_python_file(relative_path, content, language)
        else:
            await self._index_generic_file(relative_path, content, language)
    
    async def _index_python_file(self, file_path: str, content: str, language: str):
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return
        
        lines = content.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                docstring = ast.get_docstring(node)
                code_block = CodeBlock(
                    repository_id=self.repo_id,
                    file_path=file_path,
                    start_line=node.lineno,
                    end_line=node.end_lineno or node.lineno,
                    language=language,
                    content='\n'.join(lines[node.lineno - 1:node.end_lineno or node.lineno]),
                    entity_type=EntityType.FUNCTION,
                    entity_name=node.name,
                    docstring=docstring,
                )
                self.db.add(code_block)
            
            elif isinstance(node, ast.ClassDef):
                docstring = ast.get_docstring(node)
                code_block = CodeBlock(
                    repository_id=self.repo_id,
                    file_path=file_path,
                    start_line=node.lineno,
                    end_line=node.end_lineno or node.lineno,
                    language=language,
                    content='\n'.join(lines[node.lineno - 1:node.end_lineno or node.lineno]),
                    entity_type=EntityType.CLASS,
                    entity_name=node.name,
                    docstring=docstring,
                )
                self.db.add(code_block)
        
        self.db.commit()
    
    async def _index_generic_file(self, file_path: str, content: str, language: str):
        code_block = CodeBlock(
            repository_id=self.repo_id,
            file_path=file_path,
            start_line=1,
            end_line=len(content.split('\n')),
            language=language,
            content=content[:5000],
            entity_type=EntityType.MODULE,
            entity_name=file_path.split('/')[-1],
        )
        self.db.add(code_block)
        self.db.commit()
    
    def _get_language(self, ext: str) -> str:
        ext_to_lang = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.go': 'go',
            '.rs': 'rust',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
        }
        return ext_to_lang.get(ext, 'unknown')
