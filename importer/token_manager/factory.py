"""
Token handler factory module.

This module provides a factory for creating token handlers based on their names.
"""

from typing import Dict, Type

from importer.token_manager.base import TokenHandler
from importer.token_manager.handlers.keycloak import KeycloakTokenHandler


class TokenHandlerFactory:
    """Factory for creating token handlers."""

    _handlers: Dict[str, Type[TokenHandler]] = {
        'keycloak': KeycloakTokenHandler
    }

    @classmethod
    def get_handler(cls, handler_name: str) -> TokenHandler:
        """
        Get a token handler by name.

        Args:
            handler_name (str): The name of the handler to get

        Returns:
            TokenHandler: An instance of the requested handler

        Raises:
            ValueError: If the handler name is not recognized
        """
        handler_class = cls._handlers.get(handler_name.lower())
        if not handler_class:
            raise ValueError(f"Unknown token handler: {handler_name}")

        return handler_class()

    @classmethod
    def register_handler(cls, name: str, handler_class: Type[TokenHandler]) -> None:
        """
        Register a new token handler.

        Args:
            name (str): The name to register the handler under
            handler_class (Type[TokenHandler]): The handler class to register
        """
        cls._handlers[name.lower()] = handler_class
