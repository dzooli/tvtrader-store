"""
Unit tests for the EnvironmentTokenHandler class.

This module contains tests for the EnvironmentTokenHandler class.
"""
import os
from unittest.mock import patch

import pytest

from importer.environment_handler import EnvironmentTokenHandler


class TestEnvironmentTokenHandler:
    """Test cases for the EnvironmentTokenHandler class."""

    def test_get_token_success(self):
        """Test that get_token returns a token successfully."""
        # Setup
        handler = EnvironmentTokenHandler()
        env_var_name = "TEST_TOKEN"
        token_value = "test_token_value"

        # Mock the environment variable
        with patch.dict(os.environ, {env_var_name: token_value}):
            # Execute
            token = handler.get_token(env_var_name=env_var_name)

            # Verify
            assert token == token_value

    def test_get_token_missing_env_var_name(self):
        """Test that get_token raises KeyError when env_var_name is not provided."""
        # Setup
        handler = EnvironmentTokenHandler()

        # Execute and verify
        with pytest.raises(KeyError) as excinfo:
            handler.get_token()

        assert "env_var_name not provided" in str(excinfo.value)

    def test_get_token_missing_env_var(self):
        """Test that get_token raises KeyError when the environment variable is not set."""
        # Setup
        handler = EnvironmentTokenHandler()
        env_var_name = "NONEXISTENT_ENV_VAR"

        # Ensure the environment variable is not set
        if env_var_name in os.environ:
            del os.environ[env_var_name]

        # Execute and verify
        with pytest.raises(KeyError) as excinfo:
            handler.get_token(env_var_name=env_var_name)

        assert f"Environment variable {env_var_name} not set or empty" in str(excinfo.value)
