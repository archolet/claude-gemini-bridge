"""Gemini API client wrapper for Vertex AI.

Provides high-level interface for text generation, chat, and image generation.
Includes automatic token refresh on authentication errors.
"""

import base64
import logging
import os
import uuid
from datetime import datetime
from functools import wraps
from pathlib import Path
import json
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, TypeVar

from google import genai
from google.genai import types

from .auth import get_auth_manager
from .config import GeminiConfig, get_config
from .frontend_presets import (
    FRONTEND_DESIGN_SYSTEM_PROMPT,
    build_style_guide,
    get_component_preset,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


class GeminiClient:
    """High-level client for Gemini API on Vertex AI.

    Includes automatic token refresh on authentication errors (401/403).
    """

    # Error messages that indicate token expiration
    AUTH_ERROR_PATTERNS = [
        "401",
        "403",
        "unauthorized",
        "unauthenticated",
        "token",
        "expired",
        "invalid_grant",
        "credentials",
    ]

    def __init__(self, config: Optional[GeminiConfig] = None):
        """Initialize the Gemini client.

        Args:
            config: Optional configuration. If not provided, loads from environment.
        """
        self.config = config or get_config()
        self._client: Optional[genai.Client] = None
        self._chat_sessions: Dict[str, Any] = {}
        self._auth_manager = get_auth_manager()

    def _is_auth_error(self, error: Exception) -> bool:
        """Check if an error is related to authentication/token issues.

        Args:
            error: The exception to check.

        Returns:
            True if this appears to be an authentication error.
        """
        error_str = str(error).lower()
        return any(pattern in error_str for pattern in self.AUTH_ERROR_PATTERNS)

    def _refresh_credentials_and_client(self) -> None:
        """Refresh credentials and recreate the client.

        This is called when an authentication error is detected.
        """
        logger.info("Refreshing credentials due to authentication error...")

        # Refresh credentials via AuthManager
        self._auth_manager.refresh_if_needed()

        # Force client recreation
        self._client = None
        logger.info("Client will be recreated on next request")

    @property
    def client(self) -> genai.Client:
        """Get or create the Gemini client.

        Returns:
            Initialized genai.Client for Vertex AI.
        """
        if self._client is None:
            # Ensure credentials are fresh before creating client
            self._auth_manager.refresh_if_needed()

            self._client = genai.Client(
                vertexai=True,
                project=self.config.project_id,
                location=self.config.location,
            )
            logger.info(
                f"Gemini client initialized for project '{self.config.project_id}' "
                f"in '{self.config.location}'"
            )
        return self._client

    async def generate_text(
        self,
        prompt: str,
        context: str = "",
        system_instruction: str = "",
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        thinking_level: str = "medium",
        stream: bool = True,
    ) -> Dict[str, Any]:
        """Generate text using Gemini 3.

        Args:
            prompt: The main prompt/question.
            context: Optional background context.
            system_instruction: Optional system-level instructions.
            model: Model ID to use. Defaults to config default.
            temperature: Generation temperature. Defaults to config default.
            max_tokens: Maximum tokens to generate. Defaults to config default.
            thinking_level: Gemini 3 reasoning depth (minimal, low, medium, high).
                           Higher = better quality but slower.
            stream: Whether to use streaming generation.

        Returns:
            Dict containing response text, model used, and usage stats.
        """
        model = model or self.config.default_model
        temperature = temperature if temperature is not None else self.config.default_temperature
        max_tokens = max_tokens or self.config.default_max_tokens

        # Build the full prompt with context
        full_prompt = prompt
        if context:
            full_prompt = f"Context:\n{context}\n\nQuestion/Task:\n{prompt}"

        # Configure generation with Gemini 3 thinking level
        # Gemini 3 uses thinking_level (LOW/HIGH) instead of thinking_budget
        # Map user-friendly levels to Gemini 3 API values
        thinking_level_map = {
            "minimal": None,  # No thinking mode
            "low": "low",
            "medium": "medium",
            "high": "high",
        }
        mapped_level = thinking_level_map.get(thinking_level, "medium")

        gen_config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        # Only add thinking config if level is not minimal
        if mapped_level:
            gen_config.thinking_config = types.ThinkingConfig(
                thinking_budget=32768,  # Max thinking budget for Gemini 3
            )
        if system_instruction:
            gen_config.system_instruction = system_instruction

        # Retry logic for authentication errors
        max_retries = 2
        last_error = None

        for attempt in range(max_retries):
            try:
                if stream:
                    # Streaming generation
                    response_text = ""
                    async for chunk in await self.client.aio.models.generate_content_stream(
                        model=model,
                        contents=full_prompt,
                        config=gen_config,
                    ):
                        if chunk.text:
                            response_text += chunk.text

                    return {
                        "model_used": model,
                        "response": response_text,
                        "streaming": True,
                    }
                else:
                    # Non-streaming generation
                    response = await self.client.aio.models.generate_content(
                        model=model,
                        contents=full_prompt,
                        config=gen_config,
                    )

                    return {
                        "model_used": model,
                        "response": response.text,
                        "streaming": False,
                        "usage": {
                            "input_tokens": getattr(response.usage_metadata, "prompt_token_count", None),
                            "output_tokens": getattr(response.usage_metadata, "candidates_token_count", None),
                        }
                        if hasattr(response, "usage_metadata")
                        else None,
                    }

            except Exception as e:
                last_error = e
                if self._is_auth_error(e) and attempt < max_retries - 1:
                    logger.warning(f"Authentication error detected (attempt {attempt + 1}): {e}")
                    self._refresh_credentials_and_client()
                    continue
                else:
                    logger.error(f"Text generation failed: {e}")
                    break

        raise RuntimeError(f"Failed to generate text: {last_error}")

    async def chat(
        self,
        message: str,
        chat_id: str = "default",
        model: Optional[str] = None,
        system_instruction: str = "",
    ) -> Dict[str, Any]:
        """Continue a multi-turn conversation with Gemini.

        Args:
            message: The message to send.
            chat_id: Unique identifier for the chat session.
            model: Model ID to use. Defaults to config default.
            system_instruction: System instructions for new sessions.

        Returns:
            Dict containing response and chat metadata.
        """
        model = model or self.config.default_model

        # Get or create chat session
        if chat_id not in self._chat_sessions:
            config = None
            if system_instruction:
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=self.config.default_temperature,
                )

            self._chat_sessions[chat_id] = self.client.chats.create(
                model=model,
                config=config,
            )
            logger.info(f"Created new chat session: {chat_id}")

        chat = self._chat_sessions[chat_id]

        # Retry logic for authentication errors
        max_retries = 2
        last_error = None

        for attempt in range(max_retries):
            try:
                # Send message with streaming
                response_text = ""
                for chunk in chat.send_message_stream(message):
                    if chunk.text:
                        response_text += chunk.text

                # Get history for context
                history = chat.get_history(curated=True)
                history_summary = [
                    {"role": item.role, "preview": item.parts[0].text[:100] + "..."}
                    for item in history[-5:]  # Last 5 messages
                    if item.parts
                ]

                return {
                    "model_used": model,
                    "chat_id": chat_id,
                    "response": response_text,
                    "history_length": len(history),
                    "recent_history": history_summary,
                }

            except Exception as e:
                last_error = e
                if self._is_auth_error(e) and attempt < max_retries - 1:
                    logger.warning(f"Chat auth error detected (attempt {attempt + 1}): {e}")
                    self._refresh_credentials_and_client()
                    # Recreate chat session after credential refresh
                    del self._chat_sessions[chat_id]
                    config = None
                    if system_instruction:
                        config = types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            temperature=self.config.default_temperature,
                        )
                    self._chat_sessions[chat_id] = self.client.chats.create(
                        model=model,
                        config=config,
                    )
                    chat = self._chat_sessions[chat_id]
                    continue
                else:
                    logger.error(f"Chat failed: {e}")
                    break

        raise RuntimeError(f"Failed to send chat message: {last_error}")

    def clear_chat(self, chat_id: str) -> bool:
        """Clear a chat session.

        Args:
            chat_id: The chat session ID to clear.

        Returns:
            True if session was cleared, False if not found.
        """
        if chat_id in self._chat_sessions:
            del self._chat_sessions[chat_id]
            logger.info(f"Cleared chat session: {chat_id}")
            return True
        return False

    async def generate_image(
        self,
        prompt: str,
        model: Optional[str] = None,
        aspect_ratio: str = "1:1",
        output_format: str = "base64",
        output_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate an image using Gemini or Imagen.

        Args:
            prompt: Text description of the image to generate.
            model: Model ID to use. Defaults to config default image model.
            aspect_ratio: Image aspect ratio (e.g., "1:1", "16:9", "9:16").
            output_format: "base64", "file", or "both".
            output_dir: Directory to save file output.

        Returns:
            Dict containing image data and/or file path.
        """
        model = model or self.config.default_image_model
        output_dir = output_dir or self.config.default_image_output_dir

        # Retry logic for authentication errors
        max_retries = 2
        last_error = None

        for attempt in range(max_retries):
            try:
                # Check if using Imagen standalone or Gemini with image capability
                if model.startswith("imagen"):
                    return await self._generate_with_imagen(
                        prompt, model, aspect_ratio, output_format, output_dir
                    )
                else:
                    return await self._generate_with_gemini_image(
                        prompt, model, aspect_ratio, output_format, output_dir
                    )

            except Exception as e:
                last_error = e
                if self._is_auth_error(e) and attempt < max_retries - 1:
                    logger.warning(f"Image gen auth error detected (attempt {attempt + 1}): {e}")
                    self._refresh_credentials_and_client()
                    continue
                else:
                    logger.error(f"Image generation failed: {e}")
                    break

        raise RuntimeError(f"Failed to generate image: {last_error}")

    async def _generate_with_gemini_image(
        self,
        prompt: str,
        model: str,
        aspect_ratio: str,
        output_format: str,
        output_dir: str,
    ) -> Dict[str, Any]:
        """Generate image using Gemini multimodal model.

        Note: Gemini requires responseModalities: ["TEXT", "IMAGE"]
        """
        gen_config = types.GenerateContentConfig(
            response_modalities=[types.Modality.TEXT, types.Modality.IMAGE],
        )

        response = await self.client.aio.models.generate_content(
            model=model,
            contents=prompt,
            config=gen_config,
        )

        result: Dict[str, Any] = {
            "model_used": model,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
        }

        # Extract image from response
        image_data = None
        text_response = ""

        for part in response.candidates[0].content.parts:
            if hasattr(part, "inline_data") and part.inline_data:
                image_data = part.inline_data.data
                result["mime_type"] = part.inline_data.mime_type
            elif hasattr(part, "text") and part.text:
                text_response += part.text

        if text_response:
            result["text_response"] = text_response

        if image_data:
            # Handle output format
            if output_format in ["base64", "both"]:
                if isinstance(image_data, bytes):
                    result["base64"] = base64.b64encode(image_data).decode("utf-8")
                else:
                    result["base64"] = image_data

            if output_format in ["file", "both"]:
                file_path = self._save_image(image_data, output_dir)
                result["file_path"] = file_path

        return result

    async def _generate_with_imagen(
        self,
        prompt: str,
        model: str,
        aspect_ratio: str,
        output_format: str,
        output_dir: str,
    ) -> Dict[str, Any]:
        """Generate image using Imagen standalone model."""
        config = types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio=aspect_ratio,
        )

        response = self.client.models.generate_images(
            model=model,
            prompt=prompt,
            config=config,
        )

        result: Dict[str, Any] = {
            "model_used": model,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
        }

        if response.generated_images:
            image = response.generated_images[0]
            image_data = image.image.image_bytes

            if output_format in ["base64", "both"]:
                result["base64"] = base64.b64encode(image_data).decode("utf-8")

            if output_format in ["file", "both"]:
                file_path = self._save_image(image_data, output_dir)
                result["file_path"] = file_path

        return result

    def _save_image(self, image_data: bytes, output_dir: str) -> str:
        """Save image data to file.

        Args:
            image_data: Raw image bytes.
            output_dir: Directory to save the file.

        Returns:
            Full path to saved file.
        """
        # Ensure directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        filename = f"gemini_image_{timestamp}_{unique_id}.png"
        file_path = os.path.join(output_dir, filename)

        # Write file
        if isinstance(image_data, str):
            # Base64 encoded
            image_bytes = base64.b64decode(image_data)
        else:
            image_bytes = image_data

        with open(file_path, "wb") as f:
            f.write(image_bytes)

        logger.info(f"Image saved to: {file_path}")
        return file_path

    async def design_component(
        self,
        component_type: str,
        design_spec: Dict[str, Any],
        style_guide: Optional[Dict[str, Any]] = None,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate frontend component HTML using Gemini 3 Pro.

        This method uses gemini-3-pro-preview exclusively for highest quality
        design output. It leverages high thinking budget for complex design
        reasoning and returns structured JSON with HTML and metadata.

        Args:
            component_type: Type of component (button, card, navbar, etc.)
            design_spec: Design specification containing:
                - context: Usage context (e.g., "Primary CTA for newsletter")
                - content_structure: Content to include in component
            style_guide: Visual style configuration from theme preset.
            constraints: Additional constraints like max_width, accessibility_level.

        Returns:
            Dict containing:
                - component_id: Unique identifier for the component
                - atomic_level: atom, molecule, or organism
                - html: Self-contained HTML with TailwindCSS classes
                - tailwind_classes_used: List of Tailwind classes used
                - accessibility_features: A11y features implemented
                - responsive_breakpoints: Responsive breakpoints used
                - dark_mode_support: Whether dark mode is supported
                - micro_interactions: Animation/transition classes
                - design_notes: Gemini's design decisions explanation
                - model_used: Model that generated the design
        """
        # Force Pro model for design quality
        model = "gemini-3-pro-preview"

        # Get component preset for context
        component_preset = get_component_preset(component_type)

        # Build structured JSON prompt (Gemini's recommended format)
        structured_prompt = {
            "task": "design_frontend_component",
            "component_type": component_type,
            "component_preset": component_preset,
            "context": design_spec.get("context", ""),
            "content_structure": design_spec.get("content_structure", {}),
            "style_guide": style_guide or {},
            "constraints": constraints or {},
        }

        prompt = f"""Design a {component_type} component with the following specification:

{json.dumps(structured_prompt, indent=2)}

Generate a high-quality, production-ready HTML component following all rules in your system instructions.
Respond ONLY with valid JSON."""

        # High thinking budget for design quality
        # max_output_tokens increased to 65536 (Gemini 3 max)
        gen_config = types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=65536,
            thinking_config=types.ThinkingConfig(
                thinking_budget=32768,  # Max thinking for best design quality
            ),
            system_instruction=FRONTEND_DESIGN_SYSTEM_PROMPT,
            response_mime_type="application/json",
        )

        # Retry logic for authentication errors
        max_retries = 2
        last_error = None

        for attempt in range(max_retries):
            try:
                response = await self.client.aio.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=gen_config,
                )

                # Parse JSON response
                response_text = response.text.strip()

                # Handle potential markdown code blocks
                if response_text.startswith("```"):
                    # Remove markdown code block markers
                    lines = response_text.split("\n")
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines[-1].strip() == "```":
                        lines = lines[:-1]
                    response_text = "\n".join(lines)

                result = json.loads(response_text)

                # Add model info to result
                result["model_used"] = model

                logger.info(
                    f"design_component completed: {component_type} -> {result.get('component_id', 'unknown')}"
                )
                return result

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse design response as JSON: {e}")
                logger.debug(f"Raw response: {response_text[:500]}...")
                return {
                    "error": f"Invalid JSON response: {e}",
                    "raw_response": response_text[:1000],
                    "model_used": model,
                    "component_type": component_type,
                }

            except Exception as e:
                last_error = e
                if self._is_auth_error(e) and attempt < max_retries - 1:
                    logger.warning(f"Design auth error detected (attempt {attempt + 1}): {e}")
                    self._refresh_credentials_and_client()
                    continue
                else:
                    logger.error(f"Design component failed: {e}")
                    break

        raise RuntimeError(f"Failed to design component: {last_error}")


# Global client instance
_gemini_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """Get the global Gemini client instance.

    Returns:
        GeminiClient singleton instance.
    """
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
