"""Gemini API client wrapper for Vertex AI.

Design-focused client providing high-level interface for frontend design and
image generation. Includes automatic token refresh on authentication errors.
"""

import base64
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
import json
from typing import Any, Dict, List, Optional, TypeVar

from google import genai
from google.genai import types

from .auth import get_auth_manager
from .config import GeminiConfig, get_config
from .frontend_presets import (
    build_refinement_prompt,
    build_section_prompt,
    build_system_prompt,
    extract_design_tokens,
    get_component_preset,
    get_section_info,
)
from .schemas import (
    DesignTokens,
    DesignSystemState,
    validate_design_response,
    validate_design_tokens,
    get_language_config,
)
from .cache import DesignCache, get_design_cache
from .error_recovery import (
    RecoveryStrategy,
    repair_json_response,
    extract_html_fallback,
    create_fallback_response,
    ResponseValidator,
)
from .few_shot_examples import get_few_shot_examples_for_prompt

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
        self._auth_manager = get_auth_manager()
        # Design system state for consistency across components
        self._design_systems: Dict[str, DesignSystemState] = {}
        # Cache for design results
        self._cache: DesignCache = get_design_cache(ttl_hours=24, max_entries=100)
        # Error recovery strategy
        self._recovery_strategy = RecoveryStrategy(
            max_retries=2,
            base_delay_seconds=1.0,
            exponential_backoff=True,
        )

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

    # =========================================================================
    # Generic Text Generation (Used by Agents)
    # =========================================================================

    async def generate_text(
        self,
        prompt: str,
        system_instruction: str = "",
        temperature: float = 1.0,
        max_output_tokens: int = 8192,
        thinking_level: str = "high",
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate text using Gemini API with Gemini 3 optimizations.

        This method is used by pipeline agents for text generation tasks.
        It supports Gemini 3's thought signatures and thinking configuration.

        IMPORTANT: Gemini 3 requires temperature=1.0 for optimal performance.
        Lower values may cause response loops.

        Args:
            prompt: The text prompt to send to the model.
            system_instruction: System-level instructions for the model.
            temperature: Generation temperature (default 1.0 for Gemini 3).
            max_output_tokens: Maximum tokens in response.
            thinking_level: Thinking depth - "high", "low", or "minimal".
                - "high": 32768 budget for complex tasks
                - "low": 8192 budget for simple tasks
                - "minimal": 1024 budget for trivial tasks
            model: Model to use (defaults to gemini-3-pro-preview).

        Returns:
            Dict containing:
                - text: The generated text response
                - thought_signature: Gemini 3 thought signature (if available)
                - model_used: Model that generated the response
                - thinking_level: Thinking level used
        """
        model = model or "gemini-3-pro-preview"

        # Map thinking level to budget
        thinking_budgets = {
            "high": 32768,
            "low": 8192,
            "minimal": 1024,
        }
        thinking_budget = thinking_budgets.get(thinking_level, 32768)

        # Build config with Gemini 3 optimizations
        gen_config = types.GenerateContentConfig(
            temperature=temperature,  # Should be 1.0 for Gemini 3
            max_output_tokens=max_output_tokens,
            thinking_config=types.ThinkingConfig(
                thinking_budget=thinking_budget,
            ),
        )

        # Add system instruction if provided
        if system_instruction:
            gen_config.system_instruction = system_instruction

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

                # Extract text from response
                response_text = response.text.strip() if response.text else ""

                # Build result
                result: Dict[str, Any] = {
                    "text": response_text,
                    "model_used": model,
                    "thinking_level": thinking_level,
                }

                # === GEMINI 3 THOUGHT SIGNATURE EXTRACTION ===
                # Thought signatures maintain reasoning continuity across API calls.
                # They are REQUIRED for multi-turn conversations with Gemini 3.
                thought_signature = None

                # Try to extract from response metadata
                if hasattr(response, "thought_signature"):
                    thought_signature = response.thought_signature
                elif hasattr(response, "candidates") and response.candidates:
                    candidate = response.candidates[0]
                    # Check candidate for thought signature
                    if hasattr(candidate, "thought_signature"):
                        thought_signature = candidate.thought_signature
                    elif hasattr(candidate, "grounding_metadata"):
                        # Some responses store it in grounding metadata
                        metadata = candidate.grounding_metadata
                        if hasattr(metadata, "thought_signature"):
                            thought_signature = metadata.thought_signature

                if thought_signature:
                    result["thought_signature"] = thought_signature
                    logger.debug(f"Extracted thought signature: {thought_signature[:50]}...")

                logger.info(
                    f"generate_text completed: {len(response_text)} chars, "
                    f"thinking_level={thinking_level}"
                )
                return result

            except Exception as e:
                last_error = e
                if self._is_auth_error(e) and attempt < max_retries - 1:
                    logger.warning(f"Text gen auth error (attempt {attempt + 1}): {e}")
                    self._refresh_credentials_and_client()
                    continue
                else:
                    logger.error(f"Text generation failed: {e}")
                    break

        raise RuntimeError(f"Failed to generate text: {last_error}")

    # =========================================================================
    # Image Generation
    # =========================================================================

    async def generate_image(
        self,
        prompt: str,
        model: Optional[str] = None,
        aspect_ratio: str = "1:1",
        output_format: str = "base64",
        output_dir: Optional[str] = None,
        number_of_images: int = 1,
        output_resolution: str = "1K",
    ) -> Dict[str, Any]:
        """Generate an image using Gemini or Imagen.

        Args:
            prompt: Text description of the image to generate.
            model: Model ID to use. Defaults to config default image model.
            aspect_ratio: Image aspect ratio (e.g., "1:1", "16:9", "9:16", "3:4", "4:3").
            output_format: "base64", "file", or "both".
            output_dir: Directory to save file output.
            number_of_images: Number of images to generate (1-4, Imagen only).
            output_resolution: Output resolution "1K" or "2K" (Imagen 4 only).

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
                        prompt, model, aspect_ratio, output_format, output_dir,
                        number_of_images, output_resolution
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
        number_of_images: int = 1,
        output_resolution: str = "1K",
    ) -> Dict[str, Any]:
        """Generate image using Imagen standalone model.

        Supports Imagen 4 family:
        - imagen-4.0-generate-001: Standard quality
        - imagen-4.0-ultra-generate-001: Ultra high quality
        - imagen-4.0-fast-generate-001: Fast generation
        """
        # Clamp number_of_images to valid range (1-4)
        number_of_images = max(1, min(4, number_of_images))

        # Build config for Imagen 4
        config = types.GenerateImagesConfig(
            number_of_images=number_of_images,
            aspect_ratio=aspect_ratio,
            output_mime_type="image/png",
        )

        # Add output resolution for Imagen 4 models (1K or 2K)
        if "imagen-4" in model and output_resolution in ["1K", "2K"]:
            # Note: The SDK may use different attribute name
            # This might need adjustment based on actual SDK version
            pass  # output_resolution is set via API, SDK support may vary

        # Use async API for proper async handling
        response = await self.client.aio.models.generate_images(
            model=model,
            prompt=prompt,
            config=config,
        )

        result: Dict[str, Any] = {
            "model_used": model,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "number_of_images": number_of_images,
        }

        if response.generated_images:
            # Handle multiple images
            if number_of_images == 1:
                # Single image - return as before for backwards compatibility
                image = response.generated_images[0]
                image_data = image.image.image_bytes

                if output_format in ["base64", "both"]:
                    result["base64"] = base64.b64encode(image_data).decode("utf-8")

                if output_format in ["file", "both"]:
                    file_path = self._save_image(image_data, output_dir)
                    result["file_path"] = file_path
            else:
                # Multiple images - return as list
                result["images"] = []
                for i, image in enumerate(response.generated_images):
                    image_data = image.image.image_bytes
                    img_result = {}

                    if output_format in ["base64", "both"]:
                        img_result["base64"] = base64.b64encode(image_data).decode("utf-8")

                    if output_format in ["file", "both"]:
                        file_path = self._save_image(image_data, output_dir)
                        img_result["file_path"] = file_path

                    result["images"].append(img_result)

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

    # =========================================================================
    # Design System State Management
    # =========================================================================

    def get_or_create_design_system(
        self,
        design_system_id: str,
        name: str = "",
        theme: str = "modern-minimal",
    ) -> DesignSystemState:
        """Get or create a design system for maintaining consistency.

        Design systems track components designed within a project and ensure
        visual consistency by sharing design tokens across components.

        Args:
            design_system_id: Unique identifier for the design system.
            name: Human-readable name for the design system.
            theme: Base theme to use.

        Returns:
            DesignSystemState instance.
        """
        if design_system_id not in self._design_systems:
            self._design_systems[design_system_id] = DesignSystemState(
                id=design_system_id,
                name=name,
                theme=theme,
            )
            logger.info(f"Created design system: {design_system_id}")
        return self._design_systems[design_system_id]

    def _validate_and_log_response(
        self,
        response: Dict[str, Any],
        response_type: str = "design",
    ) -> Dict[str, Any]:
        """Validate response using Pydantic schemas and log warnings.

        This method performs optional validation - it logs warnings for
        invalid responses but still returns the original data.

        Args:
            response: The response dictionary to validate.
            response_type: Type of response ("design", "vision", "tokens").

        Returns:
            The original response (validation is for logging only).
        """
        try:
            if response_type == "design":
                is_valid, _, error = validate_design_response(response)
                if not is_valid:
                    logger.warning(f"Design response validation warning: {error}")
            elif response_type == "tokens":
                tokens = response.get("design_tokens", {})
                if tokens:
                    is_valid, _, error = validate_design_tokens(tokens)
                    if not is_valid:
                        logger.warning(f"Design tokens validation warning: {error}")
        except Exception as e:
            logger.debug(f"Validation check failed: {e}")

        return response

    async def design_component(
        self,
        component_type: str,
        design_spec: Dict[str, Any],
        style_guide: Optional[Dict[str, Any]] = None,
        constraints: Optional[Dict[str, Any]] = None,
        project_context: str = "",
        design_system_id: str = "",
        content_language: str = "tr",
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
            project_context: Optional project context describing the project's
                purpose, target audience, industry, and design philosophy.
                This helps Gemini understand the project's "spirit" for consistent design.
            design_system_id: Optional design system ID for maintaining consistency
                across multiple components in the same project.
            content_language: Language code for generated content (tr, en, de).
                Default is "tr" (Turkish).

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

        # Create cache key parameters
        cache_params = {
            "component_type": component_type,
            "design_spec": design_spec,
            "style_guide": style_guide,
            "constraints": constraints,
            "content_language": content_language,
        }

        # Check cache first
        cached = self._cache.get(**cache_params)
        if cached:
            logger.info(f"Cache hit for {component_type}")
            return cached

        # Get component preset for context
        component_preset = get_component_preset(component_type)

        # Get language configuration
        lang_config = get_language_config(content_language)

        # Get design system context if ID provided
        design_system_context = ""
        design_system = None
        if design_system_id:
            design_system = self.get_or_create_design_system(design_system_id)
            design_system_context = design_system.get_context()

        # Build structured JSON prompt (Gemini's recommended format)
        structured_prompt = {
            "task": "design_frontend_component",
            "component_type": component_type,
            "component_preset": component_preset,
            "context": design_spec.get("context", ""),
            "content_structure": design_spec.get("content_structure", {}),
            "style_guide": style_guide or {},
            "constraints": constraints or {},
            "content_language": {
                "code": lang_config.code,
                "name": lang_config.name,
                "cta_examples": lang_config.cta_primary[:3],
                "common_phrases": lang_config.common_phrases,
            },
        }

        # Build prompt with language instruction
        lang_instruction = f"Generate ALL text content in {lang_config.name} ({lang_config.code})."

        # Get few-shot examples for better output quality
        few_shot_context = get_few_shot_examples_for_prompt(component_type)

        prompt = f"""Design a {component_type} component with the following specification:

{json.dumps(structured_prompt, indent=2)}

{design_system_context}

{few_shot_context}

{lang_instruction}

Generate a high-quality, production-ready HTML component following all rules in your system instructions.
Respond ONLY with valid JSON."""

        # Build system prompt with project context
        system_prompt = build_system_prompt(project_context)

        # High thinking budget for design quality
        # max_output_tokens increased to 65536 (Gemini 3 max)
        gen_config = types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=65536,
            thinking_config=types.ThinkingConfig(
                thinking_budget=32768,  # Max thinking for best design quality
            ),
            system_instruction=system_prompt,
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

                # Add model info and language to result
                result["model_used"] = model
                result["content_language"] = content_language

                # Validate response (logs warnings, doesn't block)
                self._validate_and_log_response(result, "design")

                # Register with design system if provided
                if design_system and result.get("component_id"):
                    design_tokens = None
                    if result.get("design_tokens"):
                        try:
                            design_tokens = DesignTokens(**result["design_tokens"])
                        except Exception:
                            pass
                    design_system.register_component(
                        component_id=result["component_id"],
                        component_type=component_type,
                        atomic_level=result.get("atomic_level", "molecule"),
                        html=result.get("html", ""),
                        design_tokens=design_tokens,
                    )

                # Cache successful result
                self._cache.set(result, **cache_params)

                logger.info(
                    f"design_component completed: {component_type} -> {result.get('component_id', 'unknown')}"
                )
                return result

            except json.JSONDecodeError as e:
                logger.warning(f"JSON parse failed, attempting repair: {e}")

                # Try to repair malformed JSON
                repaired = repair_json_response(response_text)
                if repaired:
                    logger.info("JSON repair successful")
                    repaired["model_used"] = model
                    repaired["content_language"] = content_language
                    repaired["_repaired"] = True

                    # Validate and repair missing fields
                    repaired = ResponseValidator.repair(repaired, "design", component_type)

                    # Cache even repaired results
                    self._cache.set(repaired, **cache_params)
                    return repaired

                # Try to extract HTML as fallback
                html_fallback = extract_html_fallback(response_text)
                if html_fallback:
                    logger.info("Extracted HTML from malformed response")
                    fallback_result = {
                        "html": html_fallback,
                        "component_id": f"recovered_{component_type}",
                        "model_used": model,
                        "content_language": content_language,
                        "_recovered_html": True,
                    }
                    return fallback_result

                logger.error(f"Failed to parse or repair design response: {e}")
                return create_fallback_response(component_type, e)

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

    async def refine_component(
        self,
        previous_html: str,
        modifications: str,
        project_context: str = "",
    ) -> Dict[str, Any]:
        """Refine an existing component design based on feedback.

        This method takes a previously generated HTML component and applies
        modifications based on natural language instructions. It preserves
        the overall structure unless explicitly asked to change it.

        Args:
            previous_html: The HTML code from a previous design that needs refinement.
            modifications: Natural language description of the changes to make.
                Examples: "Buton rengini maviden yeşile çevir",
                         "Header'ı daha kompakt yap",
                         "Dark mode desteği ekle"
            project_context: Optional project context to maintain design consistency.

        Returns:
            Dict containing:
                - html: The refined HTML component
                - modifications_applied: Description of changes made
                - model_used: Model that generated the refinement
                - design_notes: Explanation of refinement decisions
        """
        # Force Pro model for design quality
        model = "gemini-3-pro-preview"

        # Build refinement prompt
        system_prompt = build_refinement_prompt(
            previous_html=previous_html,
            modifications=modifications,
            project_context=project_context,
        )

        prompt = f"""Refine the following HTML component based on these modification requests:

## Modification Requests:
{modifications}

## Current HTML to Refine:
```html
{previous_html}
```

Apply the requested modifications while:
1. Preserving the overall structure unless explicitly asked to change
2. Maintaining consistency with existing style choices
3. Keeping all existing accessibility features
4. Returning the COMPLETE modified HTML, not just changed parts

Respond with valid JSON containing:
- html: The complete refined HTML
- modifications_applied: List of changes made
- design_notes: Brief explanation of refinement decisions"""

        # High thinking budget for quality refinement
        gen_config = types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=65536,
            thinking_config=types.ThinkingConfig(
                thinking_budget=32768,
            ),
            system_instruction=system_prompt,
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
                    f"refine_component completed: {len(modifications)} char modifications applied"
                )
                return result

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse refinement response as JSON: {e}")
                logger.debug(f"Raw response: {response_text[:500]}...")
                return {
                    "error": f"Invalid JSON response: {e}",
                    "raw_response": response_text[:1000],
                    "model_used": model,
                }

            except Exception as e:
                last_error = e
                if self._is_auth_error(e) and attempt < max_retries - 1:
                    logger.warning(f"Refinement auth error detected (attempt {attempt + 1}): {e}")
                    self._refresh_credentials_and_client()
                    continue
                else:
                    logger.error(f"Refine component failed: {e}")
                    break

        raise RuntimeError(f"Failed to refine component: {last_error}")

    async def analyze_reference_image(
        self,
        image_path: str,
        extract_only: bool = True,
    ) -> Dict[str, Any]:
        """Analyze a reference image and extract design tokens using Gemini Vision.

        This method takes a screenshot or design reference image and uses
        Gemini's vision capabilities to extract style tokens that can be
        used to create similar designs.

        Args:
            image_path: Path to the reference image file (PNG, JPG, WEBP).
            extract_only: If True, only extract tokens without generating HTML.
                         If False, also generate a brief design description.

        Returns:
            Dict containing:
                - design_tokens: Extracted design tokens
                    - colors: Color palette with hex codes
                    - typography: Font sizes, weights, line heights
                    - spacing: Padding, margin, gap patterns
                    - borders: Border radius, border styles
                    - shadows: Shadow styles
                    - layout: Grid/flex patterns detected
                - aesthetic: Overall design aesthetic (minimal, bold, etc.)
                - component_hints: Detected UI component types
                - design_description: Brief description (if extract_only=False)
                - model_used: Model that analyzed the image

        Example:
            >>> tokens = await client.analyze_reference_image("screenshot.png")
            >>> print(tokens["design_tokens"]["colors"])
            {"primary": "#3B82F6", "secondary": "#1E40AF", ...}
        """
        model = "gemini-3-pro-preview"

        # Read and encode the image
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()

            # Determine MIME type
            ext = Path(image_path).suffix.lower()
            mime_types = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".webp": "image/webp",
                ".gif": "image/gif",
            }
            mime_type = mime_types.get(ext, "image/png")

            image_base64 = base64.b64encode(image_data).decode("utf-8")

        except FileNotFoundError:
            return {
                "error": f"Image file not found: {image_path}",
                "model_used": model,
            }
        except Exception as e:
            return {
                "error": f"Failed to read image: {e}",
                "model_used": model,
            }

        # Build the vision analysis prompt
        analysis_prompt = """Analyze this UI screenshot/design reference and extract detailed design tokens.

Return a JSON object with the following structure:
{
  "design_tokens": {
    "colors": {
      "primary": "#hex",
      "secondary": "#hex",
      "accent": "#hex",
      "background": "#hex",
      "surface": "#hex",
      "text_primary": "#hex",
      "text_secondary": "#hex",
      "border": "#hex"
    },
    "typography": {
      "heading_size": "text-4xl or similar",
      "body_size": "text-base or similar",
      "font_weight_heading": "font-bold or similar",
      "font_weight_body": "font-normal or similar",
      "line_height": "leading-relaxed or similar"
    },
    "spacing": {
      "section_padding": "py-20 or similar",
      "element_gap": "gap-8 or similar",
      "container_padding": "px-6 or similar"
    },
    "borders": {
      "radius": "rounded-xl or similar",
      "width": "border or border-2",
      "style": "solid, dashed, etc."
    },
    "shadows": {
      "card": "shadow-lg or similar",
      "button": "shadow-md or similar",
      "hover": "hover:shadow-xl or similar"
    },
    "layout": {
      "max_width": "max-w-7xl or similar",
      "grid_cols": "grid-cols-3 or similar",
      "flex_direction": "flex-row or flex-col"
    }
  },
  "aesthetic": "modern-minimal | brutalist | glassmorphism | neo-brutalism | corporate | gradient | cyberpunk | retro | pastel",
  "component_hints": ["detected component types like hero, navbar, card, etc."],
  "mood": "professional | playful | elegant | bold | minimal | warm | cool",
  "special_effects": ["gradient overlays", "blur effects", "animations visible", etc.]
}

Be precise with Tailwind class suggestions. Analyze colors accurately using hex codes.
Focus on extractable, reusable design patterns."""

        if not extract_only:
            analysis_prompt += """

Also include a "design_description" field with a 2-3 sentence description of the overall design approach and what makes it distinctive."""

        # Create multimodal content with image
        contents = [
            types.Part.from_bytes(
                data=image_data,
                mime_type=mime_type,
            ),
            types.Part.from_text(analysis_prompt),
        ]

        # Configure for vision analysis
        gen_config = types.GenerateContentConfig(
            temperature=0.3,  # Lower temperature for more accurate analysis
            max_output_tokens=8192,
            thinking_config=types.ThinkingConfig(
                thinking_budget=16384,  # Medium thinking for analysis
            ),
            response_mime_type="application/json",
        )

        # Retry logic
        max_retries = 2
        last_error = None

        for attempt in range(max_retries):
            try:
                response = await self.client.aio.models.generate_content(
                    model=model,
                    contents=contents,
                    config=gen_config,
                )

                # Parse JSON response
                response_text = response.text.strip()

                # Handle markdown code blocks
                if response_text.startswith("```"):
                    lines = response_text.split("\n")
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines[-1].strip() == "```":
                        lines = lines[:-1]
                    response_text = "\n".join(lines)

                result = json.loads(response_text)
                result["model_used"] = model
                result["image_analyzed"] = image_path

                logger.info(f"analyze_reference_image completed: {image_path}")
                return result

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse vision analysis as JSON: {e}")
                return {
                    "error": f"Invalid JSON response: {e}",
                    "raw_response": response_text[:1000] if 'response_text' in locals() else None,
                    "model_used": model,
                }

            except Exception as e:
                last_error = e
                if self._is_auth_error(e) and attempt < max_retries - 1:
                    logger.warning(f"Vision auth error (attempt {attempt + 1}): {e}")
                    self._refresh_credentials_and_client()
                    continue
                else:
                    logger.error(f"Vision analysis failed: {e}")
                    break

        raise RuntimeError(f"Failed to analyze reference image: {last_error}")

    async def design_from_reference(
        self,
        image_path: str,
        component_type: str,
        instructions: str = "",
        context: str = "",
        project_context: str = "",
        content_language: str = "tr",
    ) -> Dict[str, Any]:
        """Design a component based on a reference image.

        This method combines vision analysis with design generation:
        1. Analyzes the reference image to extract design tokens
        2. Uses those tokens to generate a similar component

        Args:
            image_path: Path to the reference image file.
            component_type: Type of component to design (hero, navbar, card, etc.)
            instructions: Additional instructions like "but make it blue" or
                         "simpler version" or "with more spacing".
            context: Usage context for the component.
            project_context: Project context for design consistency.
            content_language: Language code for content (default: "tr").

        Returns:
            Dict containing:
                - extracted_tokens: Design tokens from the reference image
                - html: Generated HTML component matching the style
                - design_notes: How the reference was interpreted
                - modifications: Changes made based on instructions
                - model_used: Model that generated the design

        Example:
            >>> result = await client.design_from_reference(
            ...     image_path="reference_hero.png",
            ...     component_type="hero",
            ...     instructions="Similar style but with dark background"
            ... )
        """
        model = "gemini-3-pro-preview"

        # Step 1: Analyze the reference image
        analysis = await self.analyze_reference_image(image_path, extract_only=False)

        if "error" in analysis:
            return analysis

        design_tokens = analysis.get("design_tokens", {})
        aesthetic = analysis.get("aesthetic", "modern-minimal")
        design_description = analysis.get("design_description", "")

        # Step 2: Build the design prompt with reference context
        system_prompt = build_system_prompt(project_context)

        # Add reference-specific instructions to system prompt
        reference_context = f"""
## Reference Image Analysis
The user provided a reference image. Here are the extracted design tokens:

### Design Tokens to Match:
{json.dumps(design_tokens, indent=2)}

### Detected Aesthetic: {aesthetic}
### Design Description: {design_description}

### User Modifications: {instructions if instructions else "None - match the reference closely"}

IMPORTANT: Your design should closely match the visual style of the reference image.
Use the extracted colors, typography, spacing, and effects.
Apply any user modifications on top of the reference style.
"""

        # Get component preset and language config
        component_preset = get_component_preset(component_type)
        lang_config = get_language_config(content_language)

        structured_prompt = {
            "task": "design_from_reference",
            "component_type": component_type,
            "component_preset": component_preset,
            "context": context,
            "reference_tokens": design_tokens,
            "reference_aesthetic": aesthetic,
            "user_modifications": instructions,
            "content_language": {
                "code": lang_config.code,
                "name": lang_config.name,
                "cta_examples": lang_config.cta_primary[:3],
                "common_phrases": lang_config.common_phrases,
            },
        }

        prompt = f"""Design a {component_type} component that matches the style from a reference image.

{json.dumps(structured_prompt, indent=2)}

{reference_context}

Generate HTML that closely matches the reference image style while implementing a functional {component_type}.
Respond ONLY with valid JSON containing:
- html: Complete HTML with TailwindCSS classes matching the reference style
- design_notes: How you interpreted and applied the reference
- modifications_applied: Changes made based on user instructions
- tailwind_classes_used: Array of main Tailwind classes
- accessibility_features: Array of a11y features
- dark_mode_support: Boolean"""

        # High thinking budget for reference matching
        gen_config = types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=65536,
            thinking_config=types.ThinkingConfig(
                thinking_budget=32768,
            ),
            system_instruction=system_prompt,
            response_mime_type="application/json",
        )

        # Retry logic
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

                # Handle markdown code blocks
                if response_text.startswith("```"):
                    lines = response_text.split("\n")
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines[-1].strip() == "```":
                        lines = lines[:-1]
                    response_text = "\n".join(lines)

                result = json.loads(response_text)

                # Add metadata
                result["model_used"] = model
                result["extracted_tokens"] = design_tokens
                result["reference_aesthetic"] = aesthetic
                result["reference_image"] = image_path
                result["content_language"] = content_language

                # Validate response
                self._validate_and_log_response(result, "reference_design")

                logger.info(f"design_from_reference completed: {component_type} from {image_path}")
                return result

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse design response as JSON: {e}")
                return {
                    "error": f"Invalid JSON response: {e}",
                    "raw_response": response_text[:1000] if 'response_text' in locals() else None,
                    "model_used": model,
                    "extracted_tokens": design_tokens,
                }

            except Exception as e:
                last_error = e
                if self._is_auth_error(e) and attempt < max_retries - 1:
                    logger.warning(f"Reference design auth error (attempt {attempt + 1}): {e}")
                    self._refresh_credentials_and_client()
                    continue
                else:
                    logger.error(f"Design from reference failed: {e}")
                    break

        raise RuntimeError(f"Failed to design from reference: {last_error}")

    async def design_section(
        self,
        section_type: str,
        context: str = "",
        previous_html: str = "",
        design_tokens: Optional[Dict[str, Any]] = None,
        content_structure: Optional[Dict[str, Any]] = None,
        theme: str = "modern-minimal",
        project_context: str = "",
        content_language: str = "tr",
    ) -> Dict[str, Any]:
        """Design a single page section that matches previous sections.

        This method is designed for building large pages section-by-section,
        where each section maintains visual consistency with previous ones.
        It extracts design tokens from previous HTML and passes them to Gemini
        for style matching.

        Args:
            section_type: Type of section to design. Supported types:
                - hero: Hero/banner section with headline and CTA
                - features: Feature showcase grid/list
                - pricing: Pricing tiers/cards
                - testimonials: Customer testimonials/reviews
                - cta: Call-to-action section
                - footer: Page footer with links
                - stats: Statistics/metrics display
                - faq: FAQ accordion
                - team: Team members grid
                - contact: Contact form section
                - gallery: Image/portfolio gallery
                - newsletter: Newsletter signup
            context: Usage context describing where/how the section will be used.
            previous_html: HTML from previous section for style matching.
                When provided, Gemini will extract and match:
                - Color palette
                - Typography choices
                - Spacing patterns
                - Border radius
                - Shadow styles
                - Animation patterns
            design_tokens: Explicit design tokens to use. If not provided but
                previous_html is given, tokens will be extracted automatically.
                Structure: {colors: {}, typography: {}, spacing: {}, style: {}}
            content_structure: Content to include in the section (JSON dict).
            theme: Visual theme preset (modern-minimal, brutalist, etc.)
            project_context: Project context for design consistency.
            content_language: Language code for generated content (tr, en, de).
                Default is "tr" (Turkish).

        Returns:
            Dict containing:
                - section_type: Type of section designed
                - html: Self-contained HTML with TailwindCSS classes
                - design_tokens: Extracted design tokens for next section
                - tailwind_classes_used: List of Tailwind classes used
                - accessibility_features: A11y features implemented
                - responsive_breakpoints: Responsive breakpoints used
                - dark_mode_support: Whether dark mode is supported
                - design_notes: Gemini's design decisions explanation
                - model_used: Model that generated the design

        Example workflow for building a full landing page:
            >>> # 1. Design hero section first
            >>> hero = await client.design_section("hero", context="SaaS landing")
            >>>
            >>> # 2. Features section matching hero style
            >>> features = await client.design_section(
            ...     "features",
            ...     previous_html=hero["html"],
            ...     design_tokens=hero["design_tokens"]
            ... )
            >>>
            >>> # 3. Continue chain...
            >>> pricing = await client.design_section(
            ...     "pricing",
            ...     previous_html=features["html"],
            ...     design_tokens=features["design_tokens"]
            ... )
            >>>
            >>> # 4. Combine all sections
            >>> full_page = hero["html"] + features["html"] + pricing["html"]
        """
        # Force Pro model for design quality
        model = "gemini-3-pro-preview"

        # Get section info for better context
        section_info = get_section_info(section_type)
        if not section_info:
            section_info = {
                "description": f"A {section_type} section",
                "typical_elements": [],
            }

        # Auto-extract design tokens from previous HTML if not provided
        if previous_html and not design_tokens:
            design_tokens = extract_design_tokens(previous_html)

        # Get language configuration
        lang_config = get_language_config(content_language)

        # Build section-aware prompt
        system_prompt = build_section_prompt(
            section_type=section_type,
            context=context,
            previous_html=previous_html,
            design_tokens=design_tokens,
            project_context=project_context,
        )

        # Build content structure for prompt
        structured_content = {
            "task": "design_page_section",
            "section_type": section_type,
            "section_info": section_info,
            "context": context,
            "content_structure": content_structure or {},
            "theme": theme,
            "has_previous_section": bool(previous_html),
            "content_language": {
                "code": lang_config.code,
                "name": lang_config.name,
                "cta_examples": lang_config.cta_primary[:3],
            },
        }

        if design_tokens:
            structured_content["design_tokens_to_match"] = design_tokens

        # Build prompt with language instruction
        lang_instruction = f"Generate ALL text content in {lang_config.name} ({lang_config.code})."

        prompt = f"""Design a {section_type} section with the following specification:

{json.dumps(structured_content, indent=2)}

{lang_instruction}

Generate a high-quality, production-ready HTML section following all rules in your system instructions.
{"IMPORTANT: Match the design patterns from the previous section exactly." if previous_html else ""}

Respond ONLY with valid JSON containing:
- html: Self-contained HTML with TailwindCSS classes
- design_notes: Brief explanation of design decisions
- tailwind_classes_used: Array of main Tailwind classes used
- accessibility_features: Array of a11y features implemented
- responsive_breakpoints: Array of breakpoints used
- dark_mode_support: Boolean
- micro_interactions: Array of animation/transition classes used"""

        # High thinking budget for design quality
        gen_config = types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=65536,
            thinking_config=types.ThinkingConfig(
                thinking_budget=32768,
            ),
            system_instruction=system_prompt,
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
                    lines = response_text.split("\n")
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines[-1].strip() == "```":
                        lines = lines[:-1]
                    response_text = "\n".join(lines)

                result = json.loads(response_text)

                # Extract design tokens from generated HTML for chain continuity
                if result.get("html"):
                    result["design_tokens"] = extract_design_tokens(result["html"])

                # Add metadata
                result["section_type"] = section_type
                result["model_used"] = model
                result["content_language"] = content_language

                # Validate response (logs warnings, doesn't block)
                self._validate_and_log_response(result, "design")

                logger.info(
                    f"design_section completed: {section_type} "
                    f"(chain_mode={'yes' if previous_html else 'no'})"
                )
                return result

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse section response as JSON: {e}")
                logger.debug(f"Raw response: {response_text[:500]}...")
                return {
                    "error": f"Invalid JSON response: {e}",
                    "raw_response": response_text[:1000],
                    "model_used": model,
                    "section_type": section_type,
                }

            except Exception as e:
                last_error = e
                if self._is_auth_error(e) and attempt < max_retries - 1:
                    logger.warning(f"Section design auth error (attempt {attempt + 1}): {e}")
                    self._refresh_credentials_and_client()
                    continue
                else:
                    logger.error(f"Design section failed: {e}")
                    break

        raise RuntimeError(f"Failed to design section: {last_error}")


def fix_js_fallbacks(html: str) -> tuple[str, list[str]]:
    """Post-process HTML to ensure JS graceful degradation.

    Analyzes Gemini output and fixes common JS-only patterns that break
    when Alpine.js doesn't load.

    Args:
        html: The HTML string from Gemini.

    Returns:
        Tuple of (fixed_html, list_of_fixes_applied).
    """
    import re

    fixes_applied = []
    fixed_html = html

    # Pattern 1: x-text without fallback content
    # BAD:  <span x-text="variable"></span>
    # GOOD: <span x-text="variable">Fallback Text</span>
    xtext_empty_pattern = r'(<[^>]+x-text="([^"]+)"[^>]*>)\s*</(\w+)>'

    def add_xtext_fallback(match):
        opening_tag = match.group(1)
        variable = match.group(2)
        closing_tag = match.group(3)

        # Generate a sensible fallback based on variable name
        fallback_map = {
            'currentWord': 'İçerik Yükleniyor...',
            'text': 'Metin',
            'title': 'Başlık',
            'message': 'Mesaj',
            'count': '0',
            'value': '0',
            'selected': 'Seçiniz',
            'item': 'Öğe',
            'name': 'İsim',
            'email': 'E-posta',
        }

        # Try to find a matching fallback
        fallback = 'İçerik'
        for key, val in fallback_map.items():
            if key.lower() in variable.lower():
                fallback = val
                break

        fixes_applied.append(f"Added fallback '{fallback}' for x-text=\"{variable}\"")
        return f'{opening_tag}{fallback}</{closing_tag}>'

    fixed_html = re.sub(xtext_empty_pattern, add_xtext_fallback, fixed_html)

    # Pattern 2: x-show hiding critical content without CSS fallback
    # Look for x-show on elements that don't have style="display: none;"
    # This ensures hidden-by-default elements stay hidden without JS
    xshow_pattern = r'(<[^>]+)(x-show="[^"]+")([^>]*>)'

    def ensure_display_none(match):
        before = match.group(1)
        xshow = match.group(2)
        after = match.group(3)

        # Skip if already has style with display
        if 'style=' in before and 'display' in before:
            return match.group(0)
        if 'style=' in after and 'display' in after:
            return match.group(0)

        # Skip if it's a non-critical element (already visible)
        # We only add display:none to modals, dropdowns etc.
        if any(keyword in match.group(0).lower() for keyword in ['modal', 'dropdown', 'menu', 'popup', 'dialog', 'overlay']):
            if 'style="display: none;"' not in match.group(0):
                fixes_applied.append("Added style=\"display: none;\" for x-show element")
                return f'{before}{xshow} style="display: none;"{after}'

        return match.group(0)

    fixed_html = re.sub(xshow_pattern, ensure_display_none, fixed_html)

    # Pattern 3: Ensure @keyframes are defined for animate-* classes
    # Check if common animations are used but not defined
    custom_animations = ['animate-blob', 'animate-float', 'animate-fade-in-up', 'animate-shimmer']
    animations_used = [anim for anim in custom_animations if anim in fixed_html]

    keyframes_defined = '@keyframes' in fixed_html

    if animations_used and not keyframes_defined:
        # Add style block with keyframes
        keyframes_css = '''
<style>
  @keyframes blob {
    0%, 100% { transform: translate(0, 0) scale(1); }
    33% { transform: translate(30px, -50px) scale(1.1); }
    66% { transform: translate(-20px, 20px) scale(0.9); }
  }
  @keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-20px); }
  }
  @keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }
  @keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
  }
  .animate-blob { animation: blob 7s infinite; }
  .animate-float { animation: float 6s ease-in-out infinite; }
  .animate-fade-in-up { animation: fadeInUp 0.6s ease-out forwards; }
  .animate-shimmer { animation: shimmer 2s infinite; }
  .animation-delay-2000 { animation-delay: 2s; }
  .animation-delay-4000 { animation-delay: 4s; }
</style>
'''
        # Insert at the beginning of HTML
        fixed_html = keyframes_css + fixed_html
        fixes_applied.append(f"Added @keyframes definitions for: {', '.join(animations_used)}")

    # Pattern 4: Check for x-intersect without CSS fallback
    # x-intersect is for scroll animations - ensure element is visible by default
    if 'x-intersect' in fixed_html:
        # Elements with x-intersect often start with opacity-0
        # Add a noscript or ensure they have animation-fill-mode: forwards
        xintersect_pattern = r'(<[^>]+x-intersect[^>]+class="[^"]*)(opacity-0)([^"]*"[^>]*>)'

        def fix_intersect_opacity(match):
            before = match.group(1)
            opacity = match.group(2)
            after = match.group(3)

            # Add CSS animation that makes it visible even without JS
            # Using animation with forwards fill-mode
            if 'animate-' not in match.group(0):
                fixes_applied.append("Added fallback animation for x-intersect element with opacity-0")
                return f'{before}{opacity} animate-fade-in-up{after}'
            return match.group(0)

        fixed_html = re.sub(xintersect_pattern, fix_intersect_opacity, fixed_html)

    return fixed_html, fixes_applied


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
