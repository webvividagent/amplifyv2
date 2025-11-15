import os
import logging
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class HardwareTier(str, Enum):
    LITE = "lite"
    STANDARD = "standard"
    PREMIUM = "premium"


class TierConfig:
    TIER_MODELS = {
        HardwareTier.LITE: {
            "general": "qwen3:4b",
            "code": "codellama:7b",
            "seer": None,
            "reasoning": None,
        },
        HardwareTier.STANDARD: {
            "general": "qwen3:8b",
            "code": "codellama:latest",
            "seer": "deepseek-r1:8b",
            "reasoning": None,
        },
        HardwareTier.PREMIUM: {
            "general": "qwen3:8b",
            "code": "codellama:latest",
            "seer": "deepseek-r1:8b",
            "reasoning": "llama3:latest",
        },
    }

    AMPLIFY_MODELS = {
        "amplify-general": {
            HardwareTier.LITE: "amplify-general",
            HardwareTier.STANDARD: "amplify-general",
            HardwareTier.PREMIUM: "amplify-general",
        },
        "amplify-code": {
            HardwareTier.LITE: "amplify-code",
            HardwareTier.STANDARD: "amplify-code",
            HardwareTier.PREMIUM: "amplify-code",
        },
        "amplify-seer": {
            HardwareTier.LITE: None,
            HardwareTier.STANDARD: "amplify-seer",
            HardwareTier.PREMIUM: "amplify-seer",
        },
        "amplify-reasoning": {
            HardwareTier.LITE: None,
            HardwareTier.STANDARD: None,
            HardwareTier.PREMIUM: "amplify-reasoning",
        },
    }

    def __init__(self):
        tier_env = os.getenv("HARDWARE_TIER", "standard").lower()
        try:
            self.tier = HardwareTier(tier_env)
        except ValueError:
            logger.warning(
                f"Invalid HARDWARE_TIER '{tier_env}', defaulting to 'standard'"
            )
            self.tier = HardwareTier.STANDARD

        logger.info(f"System tier: {self.tier}")

    def get_tier(self) -> HardwareTier:
        return self.tier

    def get_tier_str(self) -> str:
        return self.tier.value

    def get_models_for_tier(self) -> Dict[str, Optional[str]]:
        return self.TIER_MODELS[self.tier].copy()

    def get_amplify_models_for_tier(self) -> Dict[str, Optional[str]]:
        result = {}
        for model_name, tier_map in self.AMPLIFY_MODELS.items():
            model = tier_map.get(self.tier)
            if model:
                result[model_name] = model
        return result

    def get_model_for_purpose(self, purpose: str) -> Optional[str]:
        """Get the appropriate model for a specific purpose (general, code, seer, reasoning)."""
        return self.TIER_MODELS[self.tier].get(purpose)

    def get_amplify_model_for_purpose(self, purpose: str) -> Optional[str]:
        """Get the appropriate amplify model for a specific purpose."""
        model_key = f"amplify-{purpose}"
        if model_key in self.AMPLIFY_MODELS:
            return self.AMPLIFY_MODELS[model_key].get(self.tier)
        return None

    def is_lite(self) -> bool:
        return self.tier == HardwareTier.LITE

    def is_standard(self) -> bool:
        return self.tier == HardwareTier.STANDARD

    def is_premium(self) -> bool:
        return self.tier == HardwareTier.PREMIUM

    def supports_seer(self) -> bool:
        return self.tier != HardwareTier.LITE

    def supports_reasoning(self) -> bool:
        return self.tier == HardwareTier.PREMIUM


tier_config = TierConfig()
