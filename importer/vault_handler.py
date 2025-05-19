"""
Vault token handler implementation.

This module provides a TokenHandler implementation for retrieving tokens from HashiCorp Vault.
"""
import os
import sys
from pathlib import Path
from typing import Dict, Union
from loguru import logger

import hvac

# Add the parent directory to the Python path so that 'importer' can be found as a package
sys.path.insert(0, str(Path(__file__).parent.parent))

from importer.tokenmanager import TokenHandler


class VaultTokenHandler(TokenHandler):
    """Token handler for retrieving tokens from HashiCorp Vault."""

    def __init__(self):
        """Initialize the Vault token handler."""
        self.client = None

    def _connect_to_vault(self, **kwargs) -> None:
        """
        Connect to Vault server.

        Args:
            **kwargs: Must include:
                - vault_url (str): URL of the Vault server
                - vault_token (str): Token for authenticating with Vault

        Raises:
            KeyError: If required parameters are missing or invalid
            ConnectionError: If connection to Vault fails
        """
        vault_url = kwargs.get('vault_url')
        vault_token = kwargs.get('vault_token')

        if not vault_url:
            logger.error("vault_url not provided")
            raise KeyError("vault_url not provided")

        if not vault_token:
            logger.error("vault_token not provided")
            raise KeyError("vault_token not provided")

        try:
            self.client = hvac.Client(url=vault_url, token=vault_token)
            if not self.client.is_authenticated():
                logger.error("Failed to authenticate with Vault")
                raise ConnectionError("Failed to authenticate with Vault")
            logger.success(f"Successfully connected to Vault at {vault_url}")
        except Exception as e:
            logger.error(f"Error connecting to Vault: {str(e)}")
            raise ConnectionError(f"Error connecting to Vault: {str(e)}")

    def get_token(self, **kwargs) -> Union[Dict[str, str], str]:
        """
        Get a token from Vault.

        Args:
            **kwargs: Must include:
                - vault_url (str): URL of the Vault server
                - vault_token (str): Token for authenticating with Vault
                - secret_path (str): Path to the secret in Vault
                - secret_key (str): Key of the secret to retrieve

        Returns:
            str: The token retrieved from Vault

        Raises:
            KeyError: If required parameters are missing or the secret is not found
            ConnectionError: If connection to Vault fails
        """
        # Connect to Vault if not already connected
        if not self.client or not self.client.is_authenticated():
            self._connect_to_vault(**kwargs)

        secret_path = kwargs.get('secret_path')
        secret_key = kwargs.get('secret_key')

        if not secret_path:
            logger.error("secret_path not provided")
            raise KeyError("secret_path not provided")

        if not secret_key:
            logger.error("secret_key not provided")
            raise KeyError("secret_key not provided")

        try:
            # Read the secret from Vault
            secret_response = self.client.secrets.kv.v2.read_secret_version(
                path=secret_path
            )

            # Extract the token from the secret
            if not secret_response or 'data' not in secret_response or 'data' not in secret_response['data']:
                logger.error(f"Secret not found at path {secret_path}")
                raise KeyError(f"Secret not found at path {secret_path}")

            secret_data = secret_response['data']['data']
            if secret_key not in secret_data:
                logger.error(f"Key {secret_key} not found in secret at path {secret_path}")
                raise KeyError(f"Key {secret_key} not found in secret at path {secret_path}")

            token = secret_data[secret_key]
            logger.success(f"Successfully retrieved token from Vault at path {secret_path}, key {secret_key}")
            return token
        except Exception as e:
            logger.error(f"Error retrieving token from Vault: {str(e)}")
            raise KeyError(f"Error retrieving token from Vault: {str(e)}")
