"""
Base classes for token management.

This module provides the base classes for the token management system:
- TokenHandler: Abstract base class for token handlers
- TokenManager: Class that uses token handlers to retrieve tokens
"""

import abc
from typing import Dict, Optional


class TokenHandler(abc.ABC):
    """Abstract base class for token handlers."""

    @abc.abstractmethod
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
        self._tokens_cache: Dict[str, str] = {}

    def get_token(self, token_type: str, **kwargs) -> str:
        """
        Get a token of the specified type.

        Args:
            token_type (str): The type of token to retrieve
            **kwargs: Parameters to pass to the token handler

        Returns:
            str: The retrieved token

        Raises:
            KeyError: If there is an error while retrieving the token
        """
        # Check if we have a cached token
        if token_type in self._tokens_cache:
            return self._tokens_cache[token_type]

        # If it's a special token type that requires additional processing
        if token_type == "influxdb":
            # First, get the Keycloak token
            keycloak_token = self.get_token("keycloak", **kwargs)

            # Then use it to get the InfluxDB token
            from importer.token_manager.handlers.keycloak import KeycloakTokenHandler
            if isinstance(self.token_handler, KeycloakTokenHandler):
                influx_token = self.token_handler.get_client_secret(
                    access_token=keycloak_token,
                    server_url=kwargs.get('server_url'),
                    realm_name=kwargs.get('realm_name'),
                    client_secret_id=kwargs.get('client_secret_id')
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
