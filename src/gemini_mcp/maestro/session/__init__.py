"""MAESTRO Session Management Module.

Provides production-ready session management with:
- Automatic expiration (TTL)
- Concurrent session limits
- Lazy cleanup on access
"""

from gemini_mcp.maestro.session.manager import SessionManager

__all__ = ["SessionManager"]
