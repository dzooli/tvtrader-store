"""
Unit tests for the TokenManager class.

This module contains tests for the TokenManager class.
"""

from unittest.mock import MagicMock, patch

import pytest

import os
from importer.tokenmanager import TokenManager
from importer.vault_handler import VaultTokenHandler


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

    def test_get_influxdb_token_not_vault_handler(self, token_manager):
        """Test that get_token raises NotImplementedError for influxdb when not using VaultTokenHandler."""
        with pytest.raises((NotImplementedError, KeyError)):
            token_manager.get_token("influxdb")

    def test_get_influxdb_token_from_environment(self):
        """Test that get_token gets the influxdb token from the environment."""
        # Create a mock with spec=VaultTokenHandler
        mock_vault_handler = MagicMock(spec=VaultTokenHandler)

        # Create a TokenManager with the mock VaultTokenHandler
        token_manager = TokenManager(mock_vault_handler)

        # Set the environment variable
        with patch.dict(os.environ, {"INFLUXDB_TOKEN": "env_influx_token"}):
            # Get influxdb token
            token = token_manager.get_token("influxdb")

            # Verify vault token was not requested
            mock_vault_handler.get_token.assert_not_called()

            # Verify the token is from the environment
            assert token == "env_influx_token"
            assert token_manager._tokens_cache["influxdb"] == "env_influx_token"
