from fastapi import APIRouter, HTTPException, status
from llm import OllamaProvider
from pydantic import BaseModel
from services.tier_config import tier_config, HardwareTier
from typing import Dict, Optional, List

router = APIRouter(prefix="/api/v1/models", tags=["models"])


class ModelInfo(BaseModel):
    name: str
    size: str
    modified: str


class TierInfo(BaseModel):
    tier: str
    models: Dict[str, Optional[str]]
    amplify_models: Dict[str, Optional[str]]
    supports_seer: bool
    supports_reasoning: bool


@router.get("/tier", response_model=TierInfo)
async def get_tier_info():
    """Get current system tier and tier-specific models."""
    try:
        return TierInfo(
            tier=tier_config.get_tier_str(),
            models=tier_config.get_models_for_tier(),
            amplify_models=tier_config.get_amplify_models_for_tier(),
            supports_seer=tier_config.supports_seer(),
            supports_reasoning=tier_config.supports_reasoning(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tier info: {str(e)}"
        )


@router.get("/available")
async def list_available_models():
    try:
        provider = OllamaProvider()
        models = await provider.list_available_models()
        tier_models = tier_config.get_amplify_models_for_tier()
        
        return {
            "models": models,
            "total": len(models),
            "tier": tier_config.get_tier_str(),
            "tier_models": tier_models,
            "recommended_code_models": provider.get_recommended_code_models(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch models: {str(e)}"
        )


@router.post("/pull/{model_name}")
async def pull_model(model_name: str):
    try:
        provider = OllamaProvider()
        success = await provider.pull_model(model_name)
        
        if success:
            return {
                "status": "success",
                "message": f"Model {model_name} pulled successfully",
                "model": model_name
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pull model: {str(e)}"
        )


@router.get("/health")
async def check_ollama_health():
    try:
        provider = OllamaProvider()
        models = await provider.list_available_models()
        
        return {
            "status": "healthy",
            "ollama_url": provider.base_url,
            "available_models": len(models),
            "models": models[:5],
            "tier": tier_config.get_tier_str(),
            "tier_models": tier_config.get_amplify_models_for_tier(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Ollama service is not available: {str(e)}"
        )
