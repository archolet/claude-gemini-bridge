"""Configuration management for Gemini MCP Server."""

import os
from dataclasses import dataclass, field


@dataclass
class GeminiConfig:
    """Configuration settings for Gemini MCP Server."""

    # Google Cloud settings
    project_id: str = field(default_factory=lambda: os.getenv("GOOGLE_CLOUD_PROJECT", ""))
    # IMPORTANT: Gemini 3 models require "global" location
    location: str = field(default_factory=lambda: os.getenv("GOOGLE_CLOUD_LOCATION", "global"))

    # Model defaults - Gemini 3 ONLY
    default_model: str = field(default_factory=lambda: os.getenv("GEMINI_DEFAULT_MODEL", "gemini-3-flash-preview"))
    default_image_model: str = field(default_factory=lambda: os.getenv("GEMINI_IMAGE_MODEL", "gemini-3-pro-image-preview"))

    # Generation defaults
    default_temperature: float = 0.7
    default_max_tokens: int = 8192

    # Image output settings
    default_image_output_dir: str = field(default_factory=lambda: os.getenv("GEMINI_IMAGE_OUTPUT_DIR", "./images"))

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.project_id:
            raise ValueError(
                "GOOGLE_CLOUD_PROJECT environment variable is required. "
                "Set it with: export GOOGLE_CLOUD_PROJECT=your-project-id"
            )

    @classmethod
    def from_env(cls) -> "GeminiConfig":
        """Create configuration from environment variables."""
        return cls()


# Available models for reference - GEMINI 3 ONLY
AVAILABLE_MODELS = {
    "text": [
        {
            "id": "gemini-3-flash-preview",
            "name": "Gemini 3 Flash",
            "description": "Pro-grade reasoning at Flash-level speed, best for complex multimodal understanding",
            "max_tokens": 65536,
            "context_window": "1M tokens",
            "features": ["thinking_level", "adaptive reasoning", "agentic workflows"],
        },
        {
            "id": "gemini-3-pro-preview",
            "name": "Gemini 3 Pro",
            "description": "Latest reasoning-first model for complex agentic workflows and coding",
            "max_tokens": 65536,
            "context_window": "1M tokens",
            "features": ["thinking_level", "grounding", "multimodal problem solving"],
        },
    ],
    "image": [
        {
            "id": "gemini-3-pro-image-preview",
            "name": "Gemini 3 Pro Image",
            "description": "High-fidelity image generation with reasoning-enhanced composition (4096px)",
            "max_resolution": "4096x4096",
            "features": ["legible text", "multi-turn editing", "character consistency", "14 reference inputs"],
        },
        {
            "id": "imagen-4.0-ultra-generate-001",
            "name": "Imagen 4 Ultra",
            "description": "Highest quality image generation with ultra-high fidelity for print media",
            "max_resolution": "2K",
            "price": "$0.06/image",
            "features": ["ultra-high fidelity", "complex prompts", "SynthID watermark", "1-4 images per request"],
        },
        {
            "id": "imagen-4.0-generate-001",
            "name": "Imagen 4",
            "description": "High-quality image generation for general tasks",
            "max_resolution": "2K",
            "price": "$0.04/image",
            "features": ["high quality", "SynthID watermark", "1-4 images per request"],
        },
        {
            "id": "imagen-4.0-fast-generate-001",
            "name": "Imagen 4 Fast",
            "description": "Fast image generation for quick iterations",
            "max_resolution": "2K",
            "price": "$0.02/image",
            "features": ["fast generation", "SynthID watermark", "best with simple prompts"],
        },
    ],
}


def get_config() -> GeminiConfig:
    """Get the current configuration.

    Returns:
        GeminiConfig instance with current settings.

    Raises:
        ValueError: If required configuration is missing.
    """
    return GeminiConfig.from_env()
