"""Pytest fixtures for Claude Gemini Bridge tests."""

import pytest
from unittest.mock import MagicMock, AsyncMock


@pytest.fixture
def mock_genai_client():
    """Mock Google GenAI client."""
    client = MagicMock()
    client.aio = MagicMock()
    client.aio.models = MagicMock()
    client.aio.models.generate_content = AsyncMock()
    client.aio.models.generate_content_stream = AsyncMock()
    client.chats = MagicMock()
    client.chats.create = MagicMock()
    return client


@pytest.fixture
def mock_credentials():
    """Mock Google credentials."""
    creds = MagicMock()
    creds.valid = True
    creds.expired = False
    creds.token = "mock-token"
    return creds


@pytest.fixture
def sample_config():
    """Sample configuration for tests."""
    return {
        "project_id": "test-project",
        "location": "global",
        "default_model": "gemini-3-flash-preview",
        "default_image_model": "gemini-3-pro-image-preview",
    }
