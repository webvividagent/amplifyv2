import logging
from typing import Optional
from llm import OllamaProvider
from .tier_config import tier_config

logger = logging.getLogger(__name__)


class ModelSelector:
    """Tier-aware model selection service."""

    def __init__(self):
        self.provider = OllamaProvider()
        self.available_models = []
        self.amplify_models = []

    async def initialize(self):
        """Load available models from Ollama on startup."""
        try:
            self.available_models = await self.provider.list_available_models()
            self.amplify_models = [m for m in self.available_models if m.startswith("amplify-")]
            logger.info(f"Loaded {len(self.available_models)} models from Ollama")
            logger.info(f"Amplify models: {self.amplify_models}")
        except Exception as e:
            logger.error(f"Failed to initialize ModelSelector: {e}")

    def get_model_for_purpose(self, purpose: str) -> Optional[str]:
        """Get the best available model for a specific purpose.
        
        Purpose can be: 'general', 'code', 'seer', 'reasoning'
        """
        amplify_model = tier_config.get_amplify_model_for_purpose(purpose)
        
        if amplify_model and amplify_model in self.available_models:
            logger.info(f"Using amplify model for {purpose}: {amplify_model}")
            return amplify_model
        
        fallback_model = tier_config.get_model_for_purpose(purpose)
        if fallback_model and fallback_model in self.available_models:
            logger.info(f"Using fallback model for {purpose}: {fallback_model}")
            return fallback_model
        
        if self.available_models:
            logger.warning(f"No model available for purpose '{purpose}', using first available: {self.available_models[0]}")
            return self.available_models[0]
        
        logger.warning(f"No model available for purpose '{purpose}', using default")
        return self.provider.model

    def get_code_model(self) -> str:
        """Get tier-appropriate code generation model."""
        model = self.get_model_for_purpose("code")
        return model or self.provider.model

    def get_general_model(self) -> str:
        """Get tier-appropriate general purpose model."""
        model = self.get_model_for_purpose("general")
        return model or self.provider.model

    def get_seer_model(self) -> Optional[str]:
        """Get tier-appropriate review/synthesis model (None if not supported)."""
        if not tier_config.supports_seer():
            return None
        return self.get_model_for_purpose("seer")

    def get_reasoning_model(self) -> Optional[str]:
        """Get tier-appropriate reasoning model (None if not supported)."""
        if not tier_config.supports_reasoning():
            return None
        return self.get_model_for_purpose("reasoning")

    def is_model_available(self, model_name: str) -> bool:
        """Check if a specific model is available."""
        return model_name in self.available_models

    def get_available_amplify_models(self) -> list:
        """Get list of available amplify models for this tier."""
        tier_amplify_models = tier_config.get_amplify_models_for_tier()
        available = []
        for model_name in tier_amplify_models.values():
            if model_name and model_name in self.available_models:
                available.append(model_name)
        return available


model_selector = ModelSelector()
