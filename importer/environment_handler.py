"""
Environment token handler implementation.

This module provides a TokenHandler implementation for retrieving tokens from environment variables.
"""
import os
import sys
from pathlib import Path
from loguru import logger

# Add the parent directory to the Python path so that 'importer' can be found as a package
sys.path.insert(0, str(Path(__file__).parent.parent))

from importer.tokenmanager import TokenHandler


class EnvironmentTokenHandler(TokenHandler):
    """Token handler for retrieving tokens from environment variables."""

    def get_token(self, **kwargs) -> dict[str, str] | str:
        """
        Get a token from an environment variable.

        Args:
            **kwargs: Must include:
                - env_var_name (str): Name of the environment variable containing the token

        Returns:
            str: The token from the environment variable as a string

        Raises:
            KeyError: If the environment variable is not set or empty
        """
        env_var_name = kwargs.get('env_var_name')
        if not env_var_name:
            logger.error("env_var_name not provided")
            raise KeyError("env_var_name not provided")

        token = os.environ.get(env_var_name)
        if not token:
            logger.error(f"Environment variable {env_var_name} not set or empty")
            raise KeyError(f"Environment variable {env_var_name} not set or empty")

        logger.success(f"Successfully retrieved token from environment variable {env_var_name}")
        return token
