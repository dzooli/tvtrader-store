"""
Unit tests for the TokenHandler class.

This module contains tests for the TokenHandler abstract base class.
"""

import pytest

from importer.tokenmanager import TokenHandler


class ConcreteTokenHandler(TokenHandler):
    """A concrete implementation of TokenHandler for testing."""

    def get_token(self, **kwargs) -> str:
        """
        Get a token from the token store.

        Args:
            **kwargs: Handler-specific parameters

        Returns:
            str: The retrieved token

        Raises:
            KeyError: If there is an error
        """
        if 'fail' in kwargs and kwargs['fail']:
            raise KeyError("Failed to get token")
        return "test_token"


class TestTokenHandler:
    """Test cases for the TokenHandler class."""

    def test_get_token_success(self):
        """Test that get_token returns a token successfully."""
        handler = ConcreteTokenHandler()
        token = handler.get_token()
        assert token == "test_token"

    def test_get_token_failure(self):
        """Test that get_token raises KeyError when it fails."""
        handler = ConcreteTokenHandler()
        with pytest.raises(KeyError):
            handler.get_token(fail=True)

    def test_token_handler_is_abstract(self):
        """Test that TokenHandler cannot be instantiated directly."""
        with pytest.raises(TypeError):
            TokenHandler()
