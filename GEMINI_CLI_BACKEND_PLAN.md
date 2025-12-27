# 🔌 GEMINI CLI BACKEND ENTEGRASYONu - UYGULAMA PLANI

## Versiyon: 1.0
## Tarih: 2025-12-25
## Hazırlayan: Claude (Opus 4.5 için yol haritası)

---

# 📋 İÇİNDEKİLER

1. [Özet](#1-özet)
2. [Mevcut Yapı Analizi](#2-mevcut-yapı-analizi)
3. [Hedef Mimari](#3-hedef-mimari)
4. [Dosya Değişiklikleri](#4-dosya-değişiklikleri)
5. [Detaylı Modül Planları](#5-detaylı-modül-planları)
6. [Entegrasyon Noktaları](#6-entegrasyon-noktaları)
7. [TODO Listesi](#7-todo-listesi)
8. [Test Senaryoları](#8-test-senaryoları)
9. [Konfigürasyon Örnekleri](#9-konfigürasyon-örnekleri)

---

# 1. ÖZET

## 1.1 Amaç
Mevcut Vertex AI backend'inin yanına **Gemini CLI backend** ekleyerek:
- Sabit fiyatlı Google AI Pro aboneliği kullanımı
- Vertex AI'ın pay-per-use modelinden bağımsız çalışma
- Kullanıcının backend seçebilmesi

## 1.2 Kısıtlamalar
- ⚠️ **SADECE Gemini 3 modelleri** desteklenecek (2.5 ve öncesi YOK)
- Vertex AI backend'i **AYNEN KALACAK** (hiç dokunulmayacak fonksiyonellik)
- CLI backend **EK SEÇenek** olarak eklenecek

## 1.3 Gemini CLI Özellikleri (Araştırma Sonucu)
```bash
# Non-interactive mod
gemini -p "prompt" --output-format json -m gemini-3-pro-preview

# Stdin ile
echo "prompt" | gemini --output-format json

# Model seçimi
gemini -p "..." -m gemini-3-flash-preview
```

**Desteklenen Flagler:**
- `-p, --prompt`: Non-interactive mod
- `--output-format json`: JSON çıktı
- `-m, --model`: Model seçimi
- `-y, --yolo`: Auto-approve (unattended)

---

# 2. MEVCUT YAPI ANALİZİ

## 2.1 Mevcut Dosya Yapısı
```
gemini_mcp/
├── auth.py          # Vertex AI OAuth (AuthManager)
├── cache.py         # DesignCache
├── client.py        # GeminiClient (Vertex AI ONLY)
├── config.py        # GeminiConfig (Vertex AI ONLY)
├── server.py        # MCP tools, get_gemini_client()
└── ...
```

## 2.2 Kritik Bağımlılıklar

### config.py
```python
@dataclass
class GeminiConfig:
    project_id: str      # Vertex AI zorunlu
    location: str        # Vertex AI zorunlu
    default_model: str
    ...
```

### client.py
```python
class GeminiClient:
    def __init__(self, config: GeminiConfig):
        self._client = genai.Client(
            vertexai=True,  # <-- Vertex AI hardcoded
            project=self.config.project_id,
            location=self.config.location,
        )
```

### auth.py
```python
class AuthManager:
    # Sadece Vertex AI / Google Cloud auth
    # ADC veya gcloud CLI token
```

### server.py
```python
def get_gemini_client() -> GeminiClient:
    # Tek bir client tipi döner
    return GeminiClient(get_config())
```

## 2.3 Dokunulacak Dosyalar
| Dosya | Değişiklik Tipi |
|-------|-----------------|
| `config.py` | **MODIFY** - Backend enum ekle |
| `client.py` | **REFACTOR** - Abstract base class |
| `auth.py` | **EXTEND** - CLI auth ekle |
| `server.py` | **MODIFY** - Backend seçimi |
| `backends/__init__.py` | **NEW** |
| `backends/base.py` | **NEW** |
| `backends/vertex_ai.py` | **NEW** (mevcut client.py'den taşı) |
| `backends/gemini_cli.py` | **NEW** |

---

# 3. HEDEF MİMARİ

## 3.1 Yeni Dosya Yapısı
```
gemini_mcp/
├── backends/                    # YENİ KLASÖR
│   ├── __init__.py             # Public exports
│   ├── base.py                 # BaseGeminiBackend (ABC)
│   ├── vertex_ai.py            # VertexAIBackend (mevcut logic)
│   └── gemini_cli.py           # GeminiCLIBackend (YENİ)
├── auth.py                      # EXTEND - CLI auth desteği
├── cache.py                     # DEĞİŞMEZ
├── client.py                    # REFACTOR - Factory pattern
├── config.py                    # MODIFY - Backend enum
├── server.py                    # MODIFY - Backend seçimi
└── ...
```

## 3.2 Sınıf Hiyerarşisi
```
                    ┌─────────────────────┐
                    │  BaseGeminiBackend  │  (ABC)
                    │  ─────────────────  │
                    │  + generate_text()  │
                    │  + generate_image() │
                    │  + design_component │
                    └──────────┬──────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                                     │
            ▼                                     ▼
┌─────────────────────┐             ┌─────────────────────┐
│  VertexAIBackend    │             │  GeminiCLIBackend   │
│  ─────────────────  │             │  ─────────────────  │
│  genai.Client(      │             │  subprocess.run(    │
│    vertexai=True)   │             │    ['gemini', ...]) │
└─────────────────────┘             └─────────────────────┘
```

## 3.3 Veri Akışı (Backend Seçimi)
```
┌─────────────┐
│   User      │
│ Config/Env  │
└──────┬──────┘
       │ GEMINI_BACKEND=cli veya vertex_ai
       ▼
┌─────────────────┐
│  config.py      │
│  BackendType    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────────┐
│  client.py      │────▶│  get_backend()      │
│  GeminiClient   │     │  Factory Function   │
└────────┬────────┘     └──────────┬──────────┘
         │                         │
         │         ┌───────────────┴───────────────┐
         │         │                               │
         ▼         ▼                               ▼
┌─────────────────────┐             ┌─────────────────────┐
│  VertexAIBackend    │             │  GeminiCLIBackend   │
│  (Mevcut mantık)    │             │  (Yeni mantık)      │
└─────────────────────┘             └─────────────────────┘
```

---

# 4. DOSYA DEĞİŞİKLİKLERİ

## 4.1 config.py - MODIFY

### Mevcut Kod
```python
@dataclass
class GeminiConfig:
    project_id: str = field(default_factory=lambda: os.getenv("GOOGLE_CLOUD_PROJECT", ""))
    location: str = field(default_factory=lambda: os.getenv("GOOGLE_CLOUD_LOCATION", "global"))
    default_model: str = field(default_factory=lambda: os.getenv("GEMINI_DEFAULT_MODEL", "gemini-3-flash-preview"))
    ...
```

### Yeni Kod
```python
from enum import Enum

class BackendType(Enum):
    """Gemini API backend seçenekleri."""
    VERTEX_AI = "vertex_ai"
    GEMINI_CLI = "gemini_cli"


@dataclass
class GeminiConfig:
    """Configuration settings for Gemini MCP Server."""
    
    # ========================================
    # BACKEND SEÇİMİ (YENİ)
    # ========================================
    backend: BackendType = field(
        default_factory=lambda: BackendType(
            os.getenv("GEMINI_BACKEND", "vertex_ai")
        )
    )
    
    # ========================================
    # VERTEX AI SETTINGS (MEVCUT)
    # ========================================
    project_id: str = field(
        default_factory=lambda: os.getenv("GOOGLE_CLOUD_PROJECT", "")
    )
    location: str = field(
        default_factory=lambda: os.getenv("GOOGLE_CLOUD_LOCATION", "global")
    )
    
    # ========================================
    # GEMINI CLI SETTINGS (YENİ)
    # ========================================
    cli_path: str = field(
        default_factory=lambda: os.getenv("GEMINI_CLI_PATH", "gemini")
    )
    cli_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY", None)
    )
    cli_use_oauth: bool = field(
        default_factory=lambda: os.getenv("GEMINI_CLI_USE_OAUTH", "true").lower() == "true"
    )
    cli_timeout_seconds: int = field(
        default_factory=lambda: int(os.getenv("GEMINI_CLI_TIMEOUT", "120"))
    )
    cli_auto_approve: bool = field(
        default_factory=lambda: os.getenv("GEMINI_CLI_AUTO_APPROVE", "true").lower() == "true"
    )
    
    # ========================================
    # MODEL DEFAULTS (MEVCUT - GÜNCELLENMİŞ)
    # ========================================
    default_model: str = field(
        default_factory=lambda: os.getenv("GEMINI_DEFAULT_MODEL", "gemini-3-flash-preview")
    )
    default_image_model: str = field(
        default_factory=lambda: os.getenv("GEMINI_IMAGE_MODEL", "gemini-3-pro-image-preview")
    )
    
    # ========================================
    # GENERATION DEFAULTS (MEVCUT)
    # ========================================
    default_temperature: float = 0.7
    default_max_tokens: int = 8192
    default_image_output_dir: str = field(
        default_factory=lambda: os.getenv("GEMINI_IMAGE_OUTPUT_DIR", "./images")
    )

    def __post_init__(self):
        """Validate configuration after initialization."""
        
        # Backend-specific validation
        if self.backend == BackendType.VERTEX_AI:
            if not self.project_id:
                raise ValueError(
                    "GOOGLE_CLOUD_PROJECT environment variable is required for Vertex AI backend. "
                    "Set it with: export GOOGLE_CLOUD_PROJECT=your-project-id\n"
                    "Or switch to CLI backend: export GEMINI_BACKEND=gemini_cli"
                )
        
        elif self.backend == BackendType.GEMINI_CLI:
            # CLI backend - OAuth veya API key gerekli
            if not self.cli_use_oauth and not self.cli_api_key:
                raise ValueError(
                    "GEMINI_API_KEY required when GEMINI_CLI_USE_OAUTH=false. "
                    "Set it with: export GEMINI_API_KEY=your-api-key\n"
                    "Or use OAuth: export GEMINI_CLI_USE_OAUTH=true"
                )
        
        # Model validation - SADECE Gemini 3
        if not self._is_gemini_3_model(self.default_model):
            raise ValueError(
                f"Invalid model: {self.default_model}. "
                "Only Gemini 3 models are supported: gemini-3-pro-preview, gemini-3-flash-preview"
            )
    
    @staticmethod
    def _is_gemini_3_model(model: str) -> bool:
        """Check if model is Gemini 3 family."""
        return model.startswith("gemini-3") or model.startswith("imagen-4")
    
    @classmethod
    def from_env(cls) -> "GeminiConfig":
        """Create configuration from environment variables."""
        return cls()


# ========================================
# AVAILABLE MODELS - GEMINI 3 ONLY
# ========================================
AVAILABLE_MODELS = {
    "text": [
        {
            "id": "gemini-3-flash-preview",
            "name": "Gemini 3 Flash",
            "description": "Pro-grade reasoning at Flash-level speed",
            "backends": ["vertex_ai", "gemini_cli"],  # YENİ ALAN
        },
        {
            "id": "gemini-3-pro-preview",
            "name": "Gemini 3 Pro",
            "description": "Latest reasoning-first model",
            "backends": ["vertex_ai", "gemini_cli"],
        },
    ],
    "image": [
        {
            "id": "gemini-3-pro-image-preview",
            "name": "Gemini 3 Pro Image",
            "description": "High-fidelity image generation",
            "backends": ["vertex_ai"],  # CLI image gen sınırlı olabilir
        },
        {
            "id": "imagen-4.0-ultra-generate-001",
            "name": "Imagen 4 Ultra",
            "description": "Highest quality image generation",
            "backends": ["vertex_ai"],  # Sadece Vertex AI
        },
    ],
}


def get_config() -> GeminiConfig:
    """Get the current configuration."""
    return GeminiConfig.from_env()


def get_available_models_for_backend(backend: BackendType) -> dict:
    """Get models available for a specific backend."""
    result = {"text": [], "image": []}
    
    for category, models in AVAILABLE_MODELS.items():
        for model in models:
            if backend.value in model.get("backends", []):
                result[category].append(model)
    
    return result
```

---

## 4.2 backends/__init__.py - NEW

```python
"""
Gemini Backend Implementations.

Provides pluggable backends for Gemini API access:
- VertexAIBackend: Google Cloud Vertex AI (pay-per-use)
- GeminiCLIBackend: Gemini CLI (subscription-based)
"""

from .base import BaseGeminiBackend, BackendCapabilities
from .vertex_ai import VertexAIBackend
from .gemini_cli import GeminiCLIBackend

__all__ = [
    "BaseGeminiBackend",
    "BackendCapabilities",
    "VertexAIBackend",
    "GeminiCLIBackend",
]
```

---

## 4.3 backends/base.py - NEW

```python
"""
Abstract Base Class for Gemini Backends.

Defines the interface that all backends must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class BackendCapabilities:
    """Describes what a backend can do."""
    
    supports_text_generation: bool = True
    supports_image_generation: bool = True
    supports_vision: bool = True
    supports_streaming: bool = False
    supports_thinking_level: bool = True
    supports_function_calling: bool = False
    max_concurrent_requests: int = 1
    
    # CLI-specific
    requires_subprocess: bool = False
    has_process_overhead: bool = False


@dataclass
class GenerationResult:
    """Standardized result from any backend."""
    
    text: str = ""
    model_used: str = ""
    backend_used: str = ""
    
    # Optional fields
    thinking_level: Optional[str] = None
    thought_signature: Optional[str] = None
    usage_stats: Optional[Dict[str, Any]] = None
    
    # Image generation
    image_base64: Optional[str] = None
    image_path: Optional[str] = None
    
    # Error info
    error: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


class BaseGeminiBackend(ABC):
    """
    Abstract base class for Gemini API backends.
    
    All backends must implement these core methods to ensure
    consistent behavior across Vertex AI and CLI implementations.
    """
    
    # Class-level capabilities (override in subclasses)
    capabilities = BackendCapabilities()
    backend_name = "base"
    
    def __init__(self, config: "GeminiConfig"):
        """
        Initialize the backend.
        
        Args:
            config: GeminiConfig instance
        """
        self.config = config
        self._initialized = False
    
    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the backend (auth, client creation, etc.)
        
        Called lazily on first use.
        """
        pass
    
    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 8192,
        thinking_level: str = "none",
        system_instruction: Optional[str] = None,
    ) -> GenerationResult:
        """
        Generate text from a prompt.
        
        Args:
            prompt: The input prompt
            model: Model ID (defaults to config default)
            temperature: Sampling temperature
            max_tokens: Maximum output tokens
            thinking_level: "none", "low", "medium", "high"
            system_instruction: Optional system prompt
        
        Returns:
            GenerationResult with text and metadata
        """
        pass
    
    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        model: Optional[str] = None,
        aspect_ratio: str = "1:1",
        output_format: str = "base64",
        output_dir: Optional[str] = None,
    ) -> GenerationResult:
        """
        Generate an image from a prompt.
        
        Args:
            prompt: Image description
            model: Model ID for image generation
            aspect_ratio: Image aspect ratio
            output_format: "base64", "file", or "both"
            output_dir: Directory for file output
        
        Returns:
            GenerationResult with image data
        """
        pass
    
    async def design_component(
        self,
        component_type: str,
        design_spec: Dict[str, Any],
        style_guide: Optional[Dict[str, Any]] = None,
        project_context: str = "",
        content_language: str = "tr",
    ) -> Dict[str, Any]:
        """
        Design a frontend component.
        
        This is a higher-level method that uses generate_text internally.
        Default implementation provided, can be overridden.
        
        Args:
            component_type: Type of component (button, card, etc.)
            design_spec: Design specification dict
            style_guide: Optional style guide
            project_context: Project context string
            content_language: Content language code
        
        Returns:
            Dict with html, css, design_tokens, etc.
        """
        from gemini_mcp.prompt_builder import build_design_prompt
        
        # Build the prompt
        prompt = build_design_prompt(
            component_type=component_type,
            context=design_spec.get("context", ""),
            theme=style_guide.get("theme", "modern-minimal") if style_guide else "modern-minimal",
            content_structure=str(design_spec.get("content_structure", {})),
            project_context=project_context,
            content_language=content_language,
        )
        
        # Generate
        result = await self.generate_text(
            prompt=prompt,
            thinking_level="medium",
        )
        
        if result.error:
            return {"error": result.error, "model_used": result.model_used}
        
        # Parse response
        return self._parse_design_response(result.text, result)
    
    def _parse_design_response(
        self, 
        text: str, 
        result: GenerationResult
    ) -> Dict[str, Any]:
        """
        Parse design response text into structured output.
        
        Uses error_recovery module for robust parsing.
        """
        from gemini_mcp.error_recovery import (
            repair_json_response,
            extract_html_fallback,
            ResponseValidator,
        )
        
        # Try JSON parse first
        parsed = repair_json_response(text)
        
        if parsed:
            parsed["model_used"] = result.model_used
            parsed["backend_used"] = self.backend_name
            return parsed
        
        # Fallback to HTML extraction
        html = extract_html_fallback(text)
        
        return {
            "html": html or text,
            "model_used": result.model_used,
            "backend_used": self.backend_name,
            "_parse_fallback": True,
        }
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Check backend health/connectivity.
        
        Returns:
            Dict with status, latency, errors
        """
        pass
    
    async def close(self) -> None:
        """
        Cleanup resources (optional override).
        """
        pass
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} initialized={self._initialized}>"
```

---

## 4.4 backends/vertex_ai.py - NEW (Mevcut client.py'den taşınacak)

```python
"""
Vertex AI Backend Implementation.

This is the original GeminiClient logic, extracted into a backend class.
Uses Google Cloud Vertex AI for API access (pay-per-use).
"""

import base64
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

from gemini_mcp.auth import get_auth_manager
from gemini_mcp.config import GeminiConfig
from gemini_mcp.error_recovery import (
    RecoveryStrategy,
    repair_json_response,
    extract_html_fallback,
)

from .base import BaseGeminiBackend, BackendCapabilities, GenerationResult

logger = logging.getLogger(__name__)


class VertexAIBackend(BaseGeminiBackend):
    """
    Vertex AI backend for Gemini API.
    
    Uses Google Cloud Vertex AI with pay-per-use billing.
    Supports all Gemini features including image generation.
    """
    
    capabilities = BackendCapabilities(
        supports_text_generation=True,
        supports_image_generation=True,
        supports_vision=True,
        supports_streaming=True,
        supports_thinking_level=True,
        supports_function_calling=True,
        max_concurrent_requests=10,
        requires_subprocess=False,
        has_process_overhead=False,
    )
    
    backend_name = "vertex_ai"
    
    # Error patterns for auth retry
    AUTH_ERROR_PATTERNS = [
        "401", "403", "unauthorized", "unauthenticated",
        "token", "expired", "invalid_grant", "credentials",
    ]
    
    def __init__(self, config: GeminiConfig):
        super().__init__(config)
        self._client: Optional[genai.Client] = None
        self._auth_manager = get_auth_manager()
        self._recovery_strategy = RecoveryStrategy(
            max_retries=2,
            base_delay_seconds=1.0,
            exponential_backoff=True,
        )
    
    async def initialize(self) -> None:
        """Initialize Vertex AI client."""
        if self._initialized:
            return
        
        self._auth_manager.refresh_if_needed()
        
        self._client = genai.Client(
            vertexai=True,
            project=self.config.project_id,
            location=self.config.location,
        )
        
        self._initialized = True
        logger.info(f"VertexAIBackend initialized for project {self.config.project_id}")
    
    @property
    def client(self) -> genai.Client:
        """Get the initialized client."""
        if self._client is None:
            raise RuntimeError("Backend not initialized. Call initialize() first.")
        return self._client
    
    def _is_auth_error(self, error: Exception) -> bool:
        """Check if error is authentication related."""
        error_str = str(error).lower()
        return any(p in error_str for p in self.AUTH_ERROR_PATTERNS)
    
    def _refresh_credentials(self) -> None:
        """Refresh credentials and recreate client."""
        logger.info("Refreshing credentials...")
        self._auth_manager.refresh_if_needed()
        self._client = None
        self._initialized = False
    
    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 8192,
        thinking_level: str = "none",
        system_instruction: Optional[str] = None,
    ) -> GenerationResult:
        """Generate text using Vertex AI."""
        
        await self.initialize()
        
        model = model or self.config.default_model
        
        # Build generation config
        gen_config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        
        # Add thinking config for Gemini 3
        if thinking_level != "none":
            thinking_config = types.ThinkingConfig(
                thinking_budget=self._thinking_level_to_budget(thinking_level)
            )
            gen_config.thinking_config = thinking_config
        
        if system_instruction:
            gen_config.system_instruction = system_instruction
        
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
                
                response_text = response.text.strip() if response.text else ""
                
                # Extract thought signature if present
                thought_signature = self._extract_thought_signature(response)
                
                return GenerationResult(
                    text=response_text,
                    model_used=model,
                    backend_used=self.backend_name,
                    thinking_level=thinking_level,
                    thought_signature=thought_signature,
                )
                
            except Exception as e:
                last_error = e
                if self._is_auth_error(e) and attempt < max_retries - 1:
                    logger.warning(f"Auth error (attempt {attempt + 1}): {e}")
                    self._refresh_credentials()
                    await self.initialize()
                    continue
                else:
                    break
        
        return GenerationResult(
            error=str(last_error),
            model_used=model,
            backend_used=self.backend_name,
        )
    
    async def generate_image(
        self,
        prompt: str,
        model: Optional[str] = None,
        aspect_ratio: str = "1:1",
        output_format: str = "base64",
        output_dir: Optional[str] = None,
    ) -> GenerationResult:
        """Generate image using Vertex AI."""
        
        await self.initialize()
        
        model = model or self.config.default_image_model
        output_dir = output_dir or self.config.default_image_output_dir
        
        # ... (mevcut _generate_with_imagen ve _generate_with_gemini_image logic'i)
        # Bu kısım mevcut client.py'den aynen taşınacak
        
        # Placeholder
        return GenerationResult(
            error="Image generation - implement from existing client.py",
            model_used=model,
            backend_used=self.backend_name,
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Vertex AI connectivity."""
        import time
        
        start = time.time()
        
        try:
            await self.initialize()
            
            # Simple test call
            result = await self.generate_text(
                prompt="Say 'OK'",
                max_tokens=10,
            )
            
            latency = time.time() - start
            
            return {
                "status": "healthy" if not result.error else "unhealthy",
                "backend": self.backend_name,
                "latency_ms": round(latency * 1000),
                "error": result.error,
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "backend": self.backend_name,
                "error": str(e),
            }
    
    def _thinking_level_to_budget(self, level: str) -> int:
        """Convert thinking level to token budget."""
        budgets = {
            "none": 0,
            "low": 1024,
            "medium": 4096,
            "high": 8192,
        }
        return budgets.get(level, 0)
    
    def _extract_thought_signature(self, response) -> Optional[str]:
        """Extract thought signature from response."""
        if hasattr(response, "thought_signature"):
            return response.thought_signature
        
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "thought_signature"):
                return candidate.thought_signature
        
        return None
```

---

## 4.5 backends/gemini_cli.py - NEW (ANA YENİLİK)

```python
"""
Gemini CLI Backend Implementation.

Uses the Gemini CLI tool for API access via subprocess.
Supports Google AI Pro subscription for fixed-price usage.

Key Features:
- Non-interactive mode via -p flag
- JSON output parsing
- OAuth or API key authentication
- Gemini 3 model support
"""

import asyncio
import json
import logging
import os
import shutil
import subprocess
from typing import Any, Dict, Optional

from gemini_mcp.config import GeminiConfig

from .base import BaseGeminiBackend, BackendCapabilities, GenerationResult

logger = logging.getLogger(__name__)


class GeminiCLIBackend(BaseGeminiBackend):
    """
    Gemini CLI backend for Gemini API.
    
    Uses subprocess to call the Gemini CLI tool.
    Ideal for Google AI Pro subscription users (fixed monthly cost).
    
    Requirements:
        - Gemini CLI installed: npm install -g @google/gemini-cli
        - Authentication: OAuth login or GEMINI_API_KEY
        - Preview features enabled for Gemini 3
    """
    
    capabilities = BackendCapabilities(
        supports_text_generation=True,
        supports_image_generation=False,  # CLI image gen sınırlı
        supports_vision=False,  # CLI vision desteği yok
        supports_streaming=False,
        supports_thinking_level=True,
        supports_function_calling=False,
        max_concurrent_requests=1,  # Sequential for CLI
        requires_subprocess=True,
        has_process_overhead=True,
    )
    
    backend_name = "gemini_cli"
    
    def __init__(self, config: GeminiConfig):
        super().__init__(config)
        self._cli_path: Optional[str] = None
        self._env: Dict[str, str] = {}
    
    async def initialize(self) -> None:
        """Initialize CLI backend - verify CLI is available."""
        if self._initialized:
            return
        
        # Find CLI executable
        cli_path = self.config.cli_path
        
        # Check if CLI exists
        full_path = shutil.which(cli_path)
        if not full_path:
            raise RuntimeError(
                f"Gemini CLI not found at '{cli_path}'. "
                "Install it with: npm install -g @google/gemini-cli"
            )
        
        self._cli_path = full_path
        
        # Setup environment
        self._env = os.environ.copy()
        
        # API key if provided and not using OAuth
        if not self.config.cli_use_oauth and self.config.cli_api_key:
            self._env["GEMINI_API_KEY"] = self.config.cli_api_key
        
        # Verify CLI works
        try:
            result = await self._run_cli_command(["--version"])
            logger.info(f"Gemini CLI initialized: {result.get('version', 'unknown')}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Gemini CLI: {e}")
        
        self._initialized = True
    
    async def _run_cli_command(
        self,
        args: list,
        input_text: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Run a Gemini CLI command.
        
        Args:
            args: Command line arguments
            input_text: Optional stdin input
            timeout: Command timeout in seconds
        
        Returns:
            Parsed JSON output or raw text
        """
        timeout = timeout or self.config.cli_timeout_seconds
        
        cmd = [self._cli_path] + args
        
        logger.debug(f"Running CLI command: {' '.join(cmd)}")
        
        # Run in thread pool to not block event loop
        loop = asyncio.get_event_loop()
        
        def _run_subprocess():
            try:
                result = subprocess.run(
                    cmd,
                    input=input_text,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    env=self._env,
                )
                return result
            except subprocess.TimeoutExpired as e:
                raise RuntimeError(f"CLI command timed out after {timeout}s")
        
        result = await loop.run_in_executor(None, _run_subprocess)
        
        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or "Unknown error"
            raise RuntimeError(f"CLI command failed: {error_msg}")
        
        # Parse output
        output = result.stdout.strip()
        
        # Try JSON parse
        if output.startswith("{") or output.startswith("["):
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                pass
        
        return {"text": output, "raw": True}
    
    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 8192,
        thinking_level: str = "none",
        system_instruction: Optional[str] = None,
    ) -> GenerationResult:
        """Generate text using Gemini CLI."""
        
        await self.initialize()
        
        model = model or self.config.default_model
        
        # Build CLI arguments
        args = [
            "-p", prompt,  # Non-interactive mode
            "--output-format", "json",
            "-m", model,
        ]
        
        # Auto-approve if configured
        if self.config.cli_auto_approve:
            args.append("-y")
        
        # Note: CLI doesn't have direct temperature/max_tokens control
        # These are handled by the model defaults
        
        # System instruction via environment or prepend
        if system_instruction:
            prompt = f"System: {system_instruction}\n\nUser: {prompt}"
            args[1] = prompt  # Update prompt in args
        
        try:
            result = await self._run_cli_command(args)
            
            # Parse response
            if isinstance(result, dict):
                if "response" in result:
                    text = result["response"]
                elif "text" in result:
                    text = result["text"]
                else:
                    text = json.dumps(result)
                
                # Extract stats if available
                usage_stats = result.get("stats", {})
                
                return GenerationResult(
                    text=text,
                    model_used=model,
                    backend_used=self.backend_name,
                    thinking_level=thinking_level,
                    usage_stats=usage_stats,
                    raw_response=result,
                )
            else:
                return GenerationResult(
                    text=str(result),
                    model_used=model,
                    backend_used=self.backend_name,
                )
                
        except Exception as e:
            logger.error(f"CLI generation failed: {e}")
            return GenerationResult(
                error=str(e),
                model_used=model,
                backend_used=self.backend_name,
            )
    
    async def generate_image(
        self,
        prompt: str,
        model: Optional[str] = None,
        aspect_ratio: str = "1:1",
        output_format: str = "base64",
        output_dir: Optional[str] = None,
    ) -> GenerationResult:
        """
        Generate image using Gemini CLI.
        
        Note: CLI image generation support is limited.
        Consider using Vertex AI backend for image generation.
        """
        return GenerationResult(
            error="Image generation not supported in CLI backend. Use Vertex AI backend for images.",
            model_used=model or "N/A",
            backend_used=self.backend_name,
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check CLI availability and authentication."""
        import time
        
        start = time.time()
        
        try:
            await self.initialize()
            
            # Test with simple prompt
            result = await self.generate_text(
                prompt="Respond with only the word OK",
                max_tokens=10,
            )
            
            latency = time.time() - start
            
            return {
                "status": "healthy" if not result.error else "unhealthy",
                "backend": self.backend_name,
                "cli_path": self._cli_path,
                "latency_ms": round(latency * 1000),
                "error": result.error,
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "backend": self.backend_name,
                "error": str(e),
            }
    
    async def close(self) -> None:
        """Cleanup (nothing needed for CLI)."""
        pass
```

---

## 4.6 client.py - REFACTOR (Factory Pattern)

```python
"""
Gemini Client - Backend Factory.

Provides a unified interface for accessing Gemini API through
different backends (Vertex AI or CLI).
"""

import logging
from typing import Optional, Union

from .config import GeminiConfig, BackendType, get_config
from .backends import BaseGeminiBackend, VertexAIBackend, GeminiCLIBackend

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Unified Gemini Client with pluggable backends.
    
    This is a wrapper that delegates to the appropriate backend
    based on configuration.
    
    Usage:
        # Automatic backend selection from config
        client = GeminiClient()
        
        # Explicit backend
        client = GeminiClient(backend_type=BackendType.GEMINI_CLI)
    """
    
    def __init__(
        self,
        config: Optional[GeminiConfig] = None,
        backend_type: Optional[BackendType] = None,
    ):
        """
        Initialize the client.
        
        Args:
            config: Optional configuration (uses env if not provided)
            backend_type: Override backend from config
        """
        self.config = config or get_config()
        
        # Determine backend
        self._backend_type = backend_type or self.config.backend
        self._backend: Optional[BaseGeminiBackend] = None
        
        logger.info(f"GeminiClient initialized with backend: {self._backend_type.value}")
    
    @property
    def backend(self) -> BaseGeminiBackend:
        """Get or create the backend instance."""
        if self._backend is None:
            self._backend = self._create_backend()
        return self._backend
    
    def _create_backend(self) -> BaseGeminiBackend:
        """Create the appropriate backend based on type."""
        if self._backend_type == BackendType.VERTEX_AI:
            return VertexAIBackend(self.config)
        elif self._backend_type == BackendType.GEMINI_CLI:
            return GeminiCLIBackend(self.config)
        else:
            raise ValueError(f"Unknown backend type: {self._backend_type}")
    
    # ========================================
    # DELEGATED METHODS
    # ========================================
    
    async def generate_text(self, *args, **kwargs):
        """Generate text - delegates to backend."""
        return await self.backend.generate_text(*args, **kwargs)
    
    async def generate_image(self, *args, **kwargs):
        """Generate image - delegates to backend."""
        return await self.backend.generate_image(*args, **kwargs)
    
    async def design_component(self, *args, **kwargs):
        """Design component - delegates to backend."""
        return await self.backend.design_component(*args, **kwargs)
    
    async def health_check(self):
        """Health check - delegates to backend."""
        return await self.backend.health_check()
    
    @property
    def capabilities(self):
        """Get backend capabilities."""
        return self.backend.capabilities
    
    @property
    def backend_name(self) -> str:
        """Get current backend name."""
        return self._backend_type.value


# ========================================
# GLOBAL CLIENT MANAGEMENT
# ========================================

_gemini_client: Optional[GeminiClient] = None


def get_gemini_client(
    backend_type: Optional[BackendType] = None,
    force_new: bool = False,
) -> GeminiClient:
    """
    Get or create the global Gemini client.
    
    Args:
        backend_type: Override backend type
        force_new: Force create new client (ignore cached)
    
    Returns:
        GeminiClient instance
    """
    global _gemini_client
    
    if force_new or _gemini_client is None:
        _gemini_client = GeminiClient(backend_type=backend_type)
    
    return _gemini_client


def reset_client() -> None:
    """Reset the global client (for testing or config changes)."""
    global _gemini_client
    _gemini_client = None
```

---

## 4.7 server.py - MODIFY

```python
# server.py içinde değişiklikler

# Import ekle
from .config import BackendType

# Mevcut get_gemini_client import'unu güncelle
from .client import get_gemini_client, GeminiClient


# Yeni MCP tool ekle
@mcp.tool()
async def get_backend_info() -> Dict[str, Any]:
    """
    Get information about the current Gemini backend.
    
    Returns backend type, capabilities, and health status.
    """
    client = get_gemini_client()
    health = await client.health_check()
    
    return {
        "backend": client.backend_name,
        "capabilities": {
            "text_generation": client.capabilities.supports_text_generation,
            "image_generation": client.capabilities.supports_image_generation,
            "vision": client.capabilities.supports_vision,
            "streaming": client.capabilities.supports_streaming,
            "thinking_level": client.capabilities.supports_thinking_level,
        },
        "health": health,
    }


@mcp.tool()
async def switch_backend(backend: str) -> Dict[str, Any]:
    """
    Switch to a different Gemini backend.
    
    Args:
        backend: "vertex_ai" or "gemini_cli"
    
    Returns:
        New backend information
    """
    from .client import reset_client
    
    try:
        backend_type = BackendType(backend)
    except ValueError:
        return {
            "error": f"Invalid backend: {backend}. Use 'vertex_ai' or 'gemini_cli'",
            "available_backends": [b.value for b in BackendType],
        }
    
    # Reset and create new client with specified backend
    reset_client()
    client = get_gemini_client(backend_type=backend_type)
    
    # Test the new backend
    health = await client.health_check()
    
    return {
        "switched_to": backend,
        "health": health,
    }
```

---

# 5. DETAYLI MODÜL PLANLARI

## 5.1 Auth Modülü Genişletmesi (auth.py)

```python
# auth.py'ye eklenecek CLI auth desteği

class CLIAuthManager:
    """
    Authentication manager for Gemini CLI.
    
    Supports:
    - OAuth via browser (gemini login)
    - API key via environment
    """
    
    def __init__(self):
        self._authenticated = False
    
    def check_auth_status(self) -> Dict[str, Any]:
        """Check if CLI is authenticated."""
        # Run: gemini auth status (veya benzeri)
        pass
    
    def trigger_oauth_login(self) -> bool:
        """Trigger browser-based OAuth login."""
        # Run: gemini auth login
        pass


def get_cli_auth_manager() -> CLIAuthManager:
    """Get CLI auth manager singleton."""
    pass
```

---

# 6. ENTEGRASYON NOKTALARI

## 6.1 Environment Variables

```bash
# Backend seçimi
export GEMINI_BACKEND=gemini_cli  # veya vertex_ai

# Vertex AI (mevcut)
export GOOGLE_CLOUD_PROJECT=your-project
export GOOGLE_CLOUD_LOCATION=global

# Gemini CLI (yeni)
export GEMINI_CLI_PATH=gemini  # veya /usr/local/bin/gemini
export GEMINI_API_KEY=your-api-key  # OAuth kullanılmıyorsa
export GEMINI_CLI_USE_OAUTH=true
export GEMINI_CLI_TIMEOUT=120
export GEMINI_CLI_AUTO_APPROVE=true

# Ortak
export GEMINI_DEFAULT_MODEL=gemini-3-flash-preview
```

## 6.2 MCP Tool'ları ile Entegrasyon

Tüm mevcut tool'lar (`design_frontend`, `design_page`, vb.) **DEĞİŞMEYECEK**.

Backend seçimi şeffaf olacak - `get_gemini_client()` çağrısı otomatik olarak doğru backend'i döndürecek.

---

# 7. TODO LİSTESİ

## 🔴 Faz 1: Altyapı (Öncelik: Kritik)

### 1.1 Config Güncellemesi
- [ ] `config.py`'ye `BackendType` enum ekle
- [ ] `GeminiConfig`'e CLI alanları ekle
- [ ] Backend validation logic ekle
- [ ] `get_available_models_for_backend()` ekle

### 1.2 Backends Klasörü
- [ ] `backends/` klasörü oluştur
- [ ] `backends/__init__.py` oluştur
- [ ] `backends/base.py` oluştur - ABC tanımla
- [ ] `GenerationResult` dataclass oluştur
- [ ] `BackendCapabilities` dataclass oluştur

## 🟠 Faz 2: Vertex AI Backend (Öncelik: Yüksek)

### 2.1 Mevcut Logic Taşıma
- [ ] `backends/vertex_ai.py` oluştur
- [ ] `client.py`'den `GeminiClient` içeriğini taşı
- [ ] `VertexAIBackend` class'ını implement et
- [ ] `generate_text()` implement et
- [ ] `generate_image()` implement et (mevcut logic)
- [ ] `health_check()` implement et
- [ ] Auth retry logic'i taşı

### 2.2 Test
- [ ] Vertex AI backend unit test
- [ ] Mevcut functionality'nin çalıştığını doğrula

## 🟡 Faz 3: Gemini CLI Backend (Öncelik: Yüksek)

### 3.1 CLI Backend Implementation
- [ ] `backends/gemini_cli.py` oluştur
- [ ] `GeminiCLIBackend` class'ını implement et
- [ ] `_run_cli_command()` async wrapper yaz
- [ ] `generate_text()` implement et
- [ ] `generate_image()` - "not supported" döndür
- [ ] `health_check()` implement et
- [ ] JSON output parsing yaz
- [ ] Error handling ekle

### 3.2 CLI Auth
- [ ] OAuth check logic ekle
- [ ] API key environment handling
- [ ] Auth error mesajları

## 🟢 Faz 4: Client Factory (Öncelik: Orta)

### 4.1 Client Refactor
- [ ] `client.py`'yi factory pattern'e çevir
- [ ] `GeminiClient` wrapper class yaz
- [ ] `get_gemini_client()` güncelle
- [ ] `reset_client()` ekle

### 4.2 Server Entegrasyonu
- [ ] `server.py`'ye `get_backend_info` tool ekle
- [ ] `server.py`'ye `switch_backend` tool ekle
- [ ] Import'ları güncelle

## 🔵 Faz 5: Test & Dokümantasyon (Öncelik: Orta)

### 5.1 Integration Tests
- [ ] Backend switching test
- [ ] CLI backend full flow test
- [ ] Vertex AI backend regression test
- [ ] Error handling tests

### 5.2 Dokümantasyon
- [ ] README.md güncelle
- [ ] Environment variables dokümantasyonu
- [ ] Backend karşılaştırma tablosu

---

# 8. TEST SENARYOLARI

## Test 1: CLI Backend ile Text Generation
```python
# Config
os.environ["GEMINI_BACKEND"] = "gemini_cli"
os.environ["GEMINI_CLI_USE_OAUTH"] = "true"

# Test
client = get_gemini_client()
result = await client.generate_text("Hello, write a haiku")

assert result.backend_used == "gemini_cli"
assert result.text != ""
assert result.error is None
```

## Test 2: Backend Switching
```python
# Start with Vertex AI
os.environ["GEMINI_BACKEND"] = "vertex_ai"
client1 = get_gemini_client()
assert client1.backend_name == "vertex_ai"

# Switch to CLI
from gemini_mcp.client import reset_client
reset_client()
os.environ["GEMINI_BACKEND"] = "gemini_cli"
client2 = get_gemini_client()
assert client2.backend_name == "gemini_cli"
```

## Test 3: CLI Image Generation Fallback
```python
client = get_gemini_client(backend_type=BackendType.GEMINI_CLI)
result = await client.generate_image("A cat")

assert result.error is not None  # CLI doesn't support images
assert "not supported" in result.error.lower()
```

---

# 9. KONFİGÜRASYON ÖRNEKLERİ

## 9.1 Gemini CLI Backend (Önerilen - Sabit Fiyat)
```bash
# .env veya shell
export GEMINI_BACKEND=gemini_cli
export GEMINI_CLI_USE_OAUTH=true
export GEMINI_DEFAULT_MODEL=gemini-3-flash-preview
export GEMINI_CLI_TIMEOUT=120
```

## 9.2 Vertex AI Backend (Pay-per-use)
```bash
export GEMINI_BACKEND=vertex_ai
export GOOGLE_CLOUD_PROJECT=my-project
export GOOGLE_CLOUD_LOCATION=global
export GEMINI_DEFAULT_MODEL=gemini-3-pro-preview
```

## 9.3 Hybrid Setup (CLI for text, Vertex for images)
```python
# Python'da runtime'da seçim
from gemini_mcp.client import get_gemini_client, reset_client
from gemini_mcp.config import BackendType

# Text için CLI
text_client = get_gemini_client(backend_type=BackendType.GEMINI_CLI)
text_result = await text_client.generate_text("...")

# Image için Vertex AI
reset_client()
image_client = get_gemini_client(backend_type=BackendType.VERTEX_AI)
image_result = await image_client.generate_image("...")
```

---

# 📎 ÖZET

## Değişiklik Matrisi

| Dosya | Durum | Açıklama |
|-------|-------|----------|
| `config.py` | MODIFY | BackendType enum, CLI settings |
| `client.py` | REFACTOR | Factory pattern, wrapper |
| `auth.py` | EXTEND | CLI auth desteği |
| `server.py` | MODIFY | Yeni tool'lar |
| `backends/__init__.py` | NEW | Exports |
| `backends/base.py` | NEW | ABC, dataclasses |
| `backends/vertex_ai.py` | NEW | Mevcut logic taşıma |
| `backends/gemini_cli.py` | NEW | CLI subprocess |

## Tahmini Metrikler
- **Süre**: 2-3 gün
- **Yeni Kod**: ~1500 satır
- **Değişen Kod**: ~300 satır
- **Test**: ~500 satır

## Risk Analizi
| Risk | Olasılık | Etki | Mitigasyon |
|------|----------|------|------------|
| CLI JSON parse hataları | Orta | Düşük | Robust parsing |
| CLI timeout | Orta | Orta | Configurable timeout |
| Gemini 3 preview değişiklikleri | Düşük | Yüksek | Model validation |
| Image gen CLI'da yok | Kesin | Orta | Clear error message |

---

*Plan Sonu - Versiyon 1.0*
*Tahmini Geliştirme Süresi: 2-3 gün*
