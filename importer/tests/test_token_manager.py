"""
Unit tests for the TokenManager class.

This module contains tests for the TokenManager class.
"""

from unittest.mock import MagicMock, patch

import pytest

from importer.token_manager.base import TokenManager
from importer.token_manager.handlers.keycloak import KeycloakTokenHandler


class TestTokenManager:
    """Test cases for the TokenManager class."""

    def test_init(self, mock_token_handler):
        """Test that TokenManager initializes correctly."""
        manager = TokenManager(mock_token_handler)
        assert manager.token_handler == mock_token_handler
        assert manager._tokens_cache == {}

    def test_get_token_no_cache(self, token_manager, mock_token_handler):
        """Test that get_token calls the handler when no cached token exists."""
        token = token_manager.get_token("test_type", param1="value1")

        mock_token_handler.get_token.assert_called_once_with(param1="value1")
        assert token == "test_token"
        assert token_manager._tokens_cache["test_type"] == "test_token"

    def test_get_token_from_cache(self, token_manager, mock_token_handler):
        """Test that get_token returns cached token when available."""
        # First call to populate cache
        token_manager.get_token("test_type", param1="value1")

        # Reset mock to verify it's not called again
        mock_token_handler.get_token.reset_mock()

        # Second call should use cache
        token = token_manager.get_token("test_type", param1="value1")

        mock_token_handler.get_token.assert_not_called()
        assert token == "test_token"

    def test_clear_cache_specific_token(self, token_manager):
        """Test that clear_cache removes a specific token from cache."""
        # Populate cache
        token_manager.get_token("type1")
        token_manager.get_token("type2")

        # Clear specific token
        token_manager.clear_cache("type1")

        assert "type1" not in token_manager._tokens_cache
        assert "type2" in token_manager._tokens_cache

    def test_clear_cache_all_tokens(self, token_manager):
        """Test that clear_cache removes all tokens from cache when no type is specified."""
        # Populate cache
        token_manager.get_token("type1")
        token_manager.get_token("type2")

        # Clear all tokens
        token_manager.clear_cache()

        assert token_manager._tokens_cache == {}

    def test_get_influxdb_token(self):
        """Test that get_token handles the influxdb token type correctly."""
        # Create a mock with spec=KeycloakTokenHandler
        mock_keycloak_handler = MagicMock(spec=KeycloakTokenHandler)
        mock_keycloak_handler.get_token.return_value = "test_token"
        mock_keycloak_handler.get_client_secret.return_value = "influx_token"

        # Create a TokenManager with the mock KeycloakTokenHandler
        token_manager = TokenManager(mock_keycloak_handler)

        # Patch isinstance to make it return True when checking if our mock is a KeycloakTokenHandler
        with patch("importer.token_manager.base.isinstance", return_value=True):
            # Get influxdb token
            token = token_manager.get_token(
                "influxdb",
                server_url="http://keycloak",
                realm_name="master",
                client_secret_id="influxdb"
            )

            # Verify keycloak token was requested first
            mock_keycloak_handler.get_token.assert_called_with(
                server_url="http://keycloak",
                realm_name="master",
                client_secret_id="influxdb"
            )

            # Verify client secret was requested with keycloak token
            mock_keycloak_handler.get_client_secret.assert_called_with(
                access_token="test_token",
                server_url="http://keycloak",
                realm_name="master",
                client_secret_id="influxdb"
            )

            assert token == "influx_token"
            assert token_manager._tokens_cache["influxdb"] == "influx_token"

    def test_get_influxdb_token_not_keycloak_handler(self, token_manager):
        """Test that get_token raises NotImplementedError for influxdb when not using KeycloakTokenHandler."""
        with pytest.raises((NotImplementedError, KeyError)):
            token_manager.get_token("influxdb")
