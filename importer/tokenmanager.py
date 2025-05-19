"""
Base classes for token management.

This module provides the base classes for the token management system:
- TokenHandler: Abstract base class for token handlers
- TokenManager: Class that uses token handlers to retrieve tokens
"""

import abc
import sys
from pathlib import Path
from typing import Dict, Optional, Union

# Add the parent directory to the Python path so that 'importer' can be found as a package
sys.path.insert(0, str(Path(__file__).parent.parent))


class TokenHandler(abc.ABC):
    """Abstract base class for token handlers."""

    @abc.abstractmethod
    def get_token(self, **kwargs) -> dict[str, str] | str:
        """
        Get a token from the token store.

        Args:
            **kwargs: Handler-specific parameters

        Returns:
            dict[str, str] | str: The retrieved token, either as a dictionary or a string

        Raises:
            KeyError: If there is an error
        """
        pass


class TokenManager:
    """
    Token manager that uses token handlers to retrieve tokens.

    This class provides a unified interface for token management,
    allowing different token handlers to be used interchangeably.
    """

    def __init__(self, token_handler: TokenHandler):
        """
        Initialize the token manager with a token handler.

        Args:
            token_handler (TokenHandler): The token handler to use
        """
        self.token_handler = token_handler
        self._tokens_cache: Dict[str, Union[dict[str, str], str]] = {}

    def get_token(self, token_type: str, **kwargs) -> dict[str, str] | str:
        """
        Get a token of the specified type.

        Args:
            token_type (str): The type of token to retrieve
            **kwargs: Parameters to pass to the token handler

        Returns:
            dict[str, str] | str: The retrieved token, either as a dictionary or a string
                                 depending on the token type and handler

        Raises:
            KeyError: If there is an error while retrieving the token
        """
        # Check if we have a cached token
        if token_type in self._tokens_cache:
            return self._tokens_cache[token_type]

        # If it's a special token type that requires additional processing
        if token_type == "influxdb":
            # First try to get the token from environment
            from importer.environment_handler import EnvironmentTokenHandler
            env_handler = EnvironmentTokenHandler()
            try:
                influx_token = env_handler.get_token(env_var_name="INFLUXDB_TOKEN")
                self._tokens_cache[token_type] = influx_token
                return influx_token
            except KeyError:
                # If not available in environment, fall back to Vault
                from importer.vault_handler import VaultTokenHandler
                if isinstance(self.token_handler, VaultTokenHandler):
                    influx_token = self.token_handler.get_token(
                        vault_url=kwargs.get('vault_url'),
                        vault_token=kwargs.get('vault_token'),
                        secret_path=kwargs.get('secret_path'),
                        secret_key=kwargs.get('secret_key')
                    )
                    self._tokens_cache[token_type] = influx_token
                    return influx_token
                else:
                    raise NotImplementedError(f"Token handler {type(self.token_handler)} does not support getting InfluxDB tokens")

        # For regular token types, use the handler
        token = self.token_handler.get_token(**kwargs)
        self._tokens_cache[token_type] = token
        return token

    def clear_cache(self, token_type: Optional[str] = None) -> None:
        """
        Clear the token cache.

        Args:
            token_type (str, optional): The type of token to clear from the cache.
                If None, clears all tokens from the cache.
        """
        if token_type:
            if token_type in self._tokens_cache:
                del self._tokens_cache[token_type]
        else:
            self._tokens_cache.clear()
