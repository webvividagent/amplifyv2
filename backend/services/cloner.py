"""
Repository cloning and templating service.
Allows users to create a new instance of Amplify with custom naming.
"""

import os
import re
import shutil
from pathlib import Path
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class RepositoryCloner:
    """Clone and customize Amplify repository with new app name."""
    
    # Files that should NOT be cloned
    SKIP_DIRS = {
        '.git', '__pycache__', '.pytest_cache', 'node_modules',
        '.venv', 'venv', 'env', '.idea', '.vscode', '.DS_Store',
        'postgres_data', 'ollama_data', '.env', 'icons'
    }
    
    # Files to skip
    SKIP_FILES = {
        '.gitignore', '.DS_Store', '.env', '.env.local',
        '*.pyc', '*.log', 'instance'
    }
    
    # Files that contain text to replace
    TEXT_REPLACEMENT_FILES = {
        '.py', '.md', '.yml', '.yaml', '.json', '.toml',
        '.sh', '.bat', '.txt', '.html', '.js', '.ts'
    }
    
    # Text replacements mapping
    DEFAULT_REPLACEMENTS = {
        'Amplify': '{APP_NAME}',
        'amplify': '{APP_NAME_LOWER}',
        'self clone': '{APP_NAME_LOWER}',
        'selfclone': '{APP_NAME_LOWER_NO_SPACE}',
        'AMPLIFY': '{APP_NAME_UPPER}',
    }
    
    # Directories to rename
    RENAME_DIRS = {
        'selfclone': 'docker_app_name',
    }
    
    def __init__(self, source_path: str):
        """Initialize cloner with source repository path."""
        self.source_path = Path(source_path)
        if not self.source_path.exists():
            raise ValueError(f"Source path does not exist: {source_path}")
    
    def validate_app_name(self, app_name: str) -> tuple[bool, Optional[str]]:
        """
        Validate app name format.
        
        Args:
            app_name: Proposed app name
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not app_name:
            return False, "App name cannot be empty"
        
        if len(app_name) < 2:
            return False, "App name must be at least 2 characters"
        
        if len(app_name) > 50:
            return False, "App name must be less than 50 characters"
        
        # Check for valid characters (alphanumeric, spaces, hyphens, underscores)
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', app_name):
            return False, "App name can only contain letters, numbers, spaces, hyphens, and underscores"
        
        if app_name.lower() in {'amplify', 'self clone', 'selfclone'}:
            return False, f"Cannot use reserved name: {app_name}"
        
        return True, None
    
    def generate_replacements(self, app_name: str) -> Dict[str, str]:
        """
        Generate text replacements based on app name.
        
        Args:
            app_name: Target app name
            
        Returns:
            Dictionary of text replacements
        """
        app_name_lower = app_name.lower()
        app_name_no_space = app_name_lower.replace(' ', '_').replace('-', '_')
        app_name_upper = app_name.upper()
        app_name_docker = app_name_lower.replace(' ', '-').replace('_', '-')
        
        return {
            'Amplify': app_name,
            'amplify': app_name_lower,
            'AMPLIFY': app_name_upper,
            'self clone': app_name,
            'selfclone': app_name_docker,
            'self_clone': app_name_no_space,
            'ai-coding-agent': app_name_docker,
            'ai_coding_agent': app_name_no_space,
            'coding_agent': app_name_no_space,
            'coding-agent': app_name_docker,
        }
    
    def should_skip(self, path: Path, is_dir: bool = False) -> bool:
        """Check if path should be skipped during cloning."""
        name = path.name
        
        if is_dir:
            return name in self.SKIP_DIRS or name.startswith('.')
        else:
            return (name in self.SKIP_FILES or 
                    name.startswith('.') or
                    name.endswith('.pyc'))
    
    def process_text(self, content: str, replacements: Dict[str, str]) -> str:
        """Replace text in content."""
        result = content
        for old, new in replacements.items():
            # Case-sensitive replacement for exact matches
            result = result.replace(old, new)
            # Handle in URLs and identifiers
            result = result.replace(old.lower(), new.lower())
        return result
    
    def clone_repo(self, dest_path: str, app_name: str) -> tuple[bool, Optional[str]]:
        """
        Clone repository with new app name.
        
        Args:
            dest_path: Destination directory path
            app_name: New app name
            
        Returns:
            Tuple of (success, error_message)
        """
        # Validate app name
        is_valid, error = self.validate_app_name(app_name)
        if not is_valid:
            return False, error
        
        dest = Path(dest_path)
        
        # Check if destination already exists
        if dest.exists():
            return False, f"Destination already exists: {dest_path}"
        
        try:
            # Generate replacements
            replacements = self.generate_replacements(app_name)
            
            logger.info(f"Starting clone: {self.source_path} → {dest}")
            logger.info(f"App name: {app_name}")
            
            # Create destination directory
            dest.mkdir(parents=True, exist_ok=True)
            
            # Copy and process files
            self._copy_tree(self.source_path, dest, replacements)
            
            logger.info(f"Successfully cloned to {dest}")
            return True, None
            
        except Exception as e:
            logger.error(f"Clone failed: {str(e)}")
            # Cleanup on failure
            if dest.exists():
                shutil.rmtree(dest)
            return False, f"Clone failed: {str(e)}"
    
    def _copy_tree(self, src: Path, dst: Path, replacements: Dict[str, str]) -> None:
        """Recursively copy directory tree with text replacements."""
        for item in src.iterdir():
            if self.should_skip(item, is_dir=item.is_dir()):
                continue
            
            dst_item = dst / item.name
            
            if item.is_dir():
                dst_item.mkdir(exist_ok=True)
                self._copy_tree(item, dst_item, replacements)
            else:
                self._copy_file(item, dst_item, replacements)
    
    def _copy_file(self, src: Path, dst: Path, replacements: Dict[str, str]) -> None:
        """Copy file with text replacements if applicable."""
        try:
            # Check if file should have text replacements
            if src.suffix in self.TEXT_REPLACEMENT_FILES:
                # Text file - read, replace, and write
                try:
                    content = src.read_text(encoding='utf-8')
                    content = self.process_text(content, replacements)
                    dst.write_text(content, encoding='utf-8')
                except UnicodeDecodeError:
                    # Binary file - just copy
                    shutil.copy2(src, dst)
            else:
                # Binary file - just copy
                shutil.copy2(src, dst)
        except Exception as e:
            logger.error(f"Failed to copy {src}: {str(e)}")
            raise
    
    def list_files_to_clone(self) -> List[Dict]:
        """List files that will be cloned."""
        files = []
        for item in self.source_path.rglob('*'):
            if self.should_skip(item, is_dir=item.is_dir()):
                continue
            
            rel_path = item.relative_to(self.source_path)
            files.append({
                'path': str(rel_path),
                'size': item.stat().st_size if item.is_file() else 0,
                'is_dir': item.is_dir(),
                'will_replace_text': (
                    item.is_file() and item.suffix in self.TEXT_REPLACEMENT_FILES
                )
            })
        
        return files


def clone_amplify(source_path: str, dest_path: str, app_name: str) -> tuple[bool, Optional[str]]:
    """
    Convenience function to clone Amplify repository.
    
    Args:
        source_path: Path to source Amplify repository
        dest_path: Destination path for new clone
        app_name: Custom app name
        
    Returns:
        Tuple of (success, error_message)
    """
    try:
        cloner = RepositoryCloner(source_path)
        return cloner.clone_repo(dest_path, app_name)
    except Exception as e:
        logger.error(f"Clone error: {str(e)}")
        return False, str(e)
