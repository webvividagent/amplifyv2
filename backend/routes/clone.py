"""
API routes for repository cloning functionality.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import logging
import os
from pathlib import Path

from services.cloner import clone_amplify, RepositoryCloner

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/clone", tags=["clone"])


class CloneRequest(BaseModel):
    """Request to clone Amplify repository."""
    app_name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Name for the new application"
    )
    dest_path: str = Field(
        default="~/amplify_clone",
        description="Destination path for cloned repository"
    )


class CloneResponse(BaseModel):
    """Response from clone operation."""
    success: bool
    message: str
    dest_path: str = None
    files_cloned: int = None
    error: str = None


class ValidationRequest(BaseModel):
    """Request to validate app name."""
    app_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="App name to validate"
    )


class ValidationResponse(BaseModel):
    """Response from validation."""
    valid: bool
    app_name: str
    error: str = None
    suggested_names: list = []
    preview: dict = None


@router.post("/validate", response_model=ValidationResponse)
async def validate_app_name(req: ValidationRequest):
    """
    Validate app name for cloning.
    
    Returns validation status and suggestions if invalid.
    """
    try:
        cloner = RepositoryCloner(os.getcwd())
        is_valid, error = cloner.validate_app_name(req.app_name)
        
        if is_valid:
            replacements = cloner.generate_replacements(req.app_name)
            return ValidationResponse(
                valid=True,
                app_name=req.app_name,
                preview=replacements
            )
        else:
            # Generate suggestions
            suggestions = generate_suggestions(req.app_name)
            return ValidationResponse(
                valid=False,
                app_name=req.app_name,
                error=error,
                suggested_names=suggestions
            )
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )


@router.post("/estimate", response_model=dict)
async def estimate_clone(req: CloneRequest):
    """
    Estimate clone size and file count without actually cloning.
    """
    try:
        # Validate app name first
        cloner = RepositoryCloner(os.getcwd())
        is_valid, error = cloner.validate_app_name(req.app_name)
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        
        files = cloner.list_files_to_clone()
        
        total_size = sum(f['size'] for f in files)
        total_files = len([f for f in files if not f['is_dir']])
        total_dirs = len([f for f in files if f['is_dir']])
        text_files = len([f for f in files if f['will_replace_text']])
        
        return {
            'total_files': total_files,
            'total_dirs': total_dirs,
            'text_files': text_files,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / 1024 / 1024, 2),
            'destination': os.path.expanduser(req.dest_path),
            'app_name': req.app_name
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Estimation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Estimation failed: {str(e)}"
        )


@router.post("/execute", response_model=CloneResponse)
async def execute_clone(req: CloneRequest):
    """
    Execute the repository clone with custom app name.
    
    This operation:
    1. Validates the app name
    2. Expands the destination path
    3. Clones the repository
    4. Replaces all references to 'Amplify' with the new app name
    5. Returns the path to the new repository
    """
    try:
        # Validate app name
        cloner = RepositoryCloner(os.getcwd())
        is_valid, error = cloner.validate_app_name(req.app_name)
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        
        # Expand destination path
        dest = os.path.expanduser(req.dest_path)
        
        # Check if destination parent exists
        dest_parent = Path(dest).parent
        if not dest_parent.exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Destination parent directory does not exist: {dest_parent}"
            )
        
        # Execute clone
        logger.info(f"Starting clone: {req.app_name} → {dest}")
        success, error_msg = clone_amplify(
            os.getcwd(),
            dest,
            req.app_name
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )
        
        # Count files in cloned repository
        cloned_files = sum(
            1 for _ in Path(dest).rglob('*') if _.is_file()
        )
        
        return CloneResponse(
            success=True,
            message=f"Successfully cloned Amplify as '{req.app_name}'",
            dest_path=dest,
            files_cloned=cloned_files
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Clone execution error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Clone failed: {str(e)}"
        )


@router.get("/status")
async def clone_status():
    """Get cloning feature status."""
    return {
        'available': True,
        'version': '1.0',
        'features': [
            'Clone with custom app name',
            'Automatic text replacement',
            'Preserve directory structure',
            'Skip unnecessary files',
            'Validation and estimation'
        ]
    }


def generate_suggestions(invalid_name: str) -> list:
    """Generate suggested app names based on invalid input."""
    suggestions = []
    
    # Remove invalid characters
    cleaned = ''.join(c for c in invalid_name if c.isalnum() or c in ' -_')
    
    if cleaned and cleaned != invalid_name:
        suggestions.append(cleaned)
    
    # Add some generic suggestions
    if len(invalid_name) > 0:
        suggestions.extend([
            f"{invalid_name.title()}",
            f"My{invalid_name.title()}",
            f"{invalid_name.lower()}_app",
            f"{invalid_name.replace(' ', '-')}",
        ])
    
    return list(dict.fromkeys(suggestions))[:5]  # Dedupe and limit
