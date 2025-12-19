"""OAuth authentication module for Vertex AI.

Supports two authentication methods:
1. Application Default Credentials (ADC) via google.auth.default()
2. Fallback to gcloud CLI token via subprocess
"""

import logging
import subprocess
from typing import Optional, Tuple

import google.auth
import google.auth.transport.requests
from google.auth.credentials import Credentials

logger = logging.getLogger(__name__)

# Required scope for Vertex AI
VERTEX_AI_SCOPE = "https://www.googleapis.com/auth/cloud-platform"


class AuthManager:
    """Manages OAuth authentication for Vertex AI."""

    def __init__(self):
        """Initialize the auth manager."""
        self._credentials: Optional[Credentials] = None
        self._project_id: Optional[str] = None

    def get_credentials(self) -> Tuple[Credentials, Optional[str]]:
        """Get valid credentials for Vertex AI.

        Tries ADC first, falls back to gcloud CLI if needed.

        Returns:
            Tuple of (credentials, project_id)

        Raises:
            RuntimeError: If authentication fails.
        """
        # Try ADC first
        try:
            credentials, project = self._get_adc_credentials()
            if credentials:
                self._credentials = credentials
                self._project_id = project
                logger.info("Authenticated via Application Default Credentials")
                return credentials, project
        except Exception as e:
            logger.warning(f"ADC authentication failed: {e}")

        # Fallback to gcloud CLI
        try:
            token = self._get_gcloud_token()
            if token:
                # Create credentials from token
                from google.oauth2.credentials import Credentials as OAuth2Credentials

                credentials = OAuth2Credentials(token=token)
                logger.info("Authenticated via gcloud CLI token")
                return credentials, None
        except Exception as e:
            logger.warning(f"gcloud CLI authentication failed: {e}")

        raise RuntimeError(
            "Failed to authenticate with Google Cloud. "
            "Please run 'gcloud auth application-default login' or ensure "
            "your service account is properly configured."
        )

    def _get_adc_credentials(self) -> Tuple[Optional[Credentials], Optional[str]]:
        """Get credentials using Application Default Credentials.

        Returns:
            Tuple of (credentials, project_id) or (None, None) if failed.
        """
        credentials, project = google.auth.default(scopes=[VERTEX_AI_SCOPE])

        # Refresh credentials to get a valid token
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)

        return credentials, project

    def _get_gcloud_token(self) -> Optional[str]:
        """Get access token from gcloud CLI.

        Returns:
            Access token string or None if failed.
        """
        try:
            result = subprocess.run(
                ["gcloud", "auth", "application-default", "print-access-token"],
                capture_output=True,
                text=True,
                check=True,
            )
            token = result.stdout.strip()
            if token:
                return token
        except subprocess.CalledProcessError as e:
            logger.error(f"gcloud command failed: {e.stderr}")
        except FileNotFoundError:
            logger.error("gcloud CLI not found in PATH")

        return None

    def refresh_if_needed(self) -> None:
        """Refresh credentials if they are expired or about to expire."""
        if self._credentials is None:
            self.get_credentials()
            return

        # Check if refresh is needed
        if hasattr(self._credentials, "expired") and self._credentials.expired:
            try:
                request = google.auth.transport.requests.Request()
                self._credentials.refresh(request)
                logger.debug("Credentials refreshed successfully")
            except Exception as e:
                logger.warning(f"Failed to refresh credentials: {e}")
                # Re-authenticate
                self.get_credentials()

    @property
    def project_id(self) -> Optional[str]:
        """Get the project ID from credentials."""
        return self._project_id

    @property
    def credentials(self) -> Optional[Credentials]:
        """Get the current credentials."""
        return self._credentials


# Global auth manager instance
_auth_manager: Optional[AuthManager] = None


def get_auth_manager() -> AuthManager:
    """Get the global auth manager instance.

    Returns:
        AuthManager singleton instance.
    """
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager
