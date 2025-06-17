"""
Unit tests for the VaultTokenHandler class.
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

from pathlib import Path

# Add the parent directory to the Python path so that 'importer' can be found as a package
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from importer.vault_handler import VaultTokenHandler


class TestVaultTokenHandler(unittest.TestCase):
    """Test cases for the VaultTokenHandler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.handler = VaultTokenHandler()

    @patch('hvac.Client')
    def test_connect_to_vault_success(self, mock_client):
        """Test successful connection to Vault."""
        # Configure the mock
        mock_instance = mock_client.return_value
        mock_instance.is_authenticated.return_value = True

        # Call the method
        self.handler._connect_to_vault(
            vault_url="http://vault:8200",
            vault_token="test_token"
        )

        # Verify the mock was called with the correct arguments
        mock_client.assert_called_once_with(
            url="http://vault:8200",
            token="test_token"
        )
        mock_instance.is_authenticated.assert_called_once()

    @patch('hvac.Client')
    def test_connect_to_vault_missing_url(self, mock_client):
        """Test connection to Vault with missing URL."""
        # Call the method and expect an exception
        with self.assertRaises(KeyError):
            self.handler._connect_to_vault(
                vault_token="test_token"
            )

        # Verify the mock was not called
        mock_client.assert_not_called()

    @patch('hvac.Client')
    def test_connect_to_vault_missing_token(self, mock_client):
        """Test connection to Vault with missing token."""
        # Call the method and expect an exception
        with self.assertRaises(KeyError):
            self.handler._connect_to_vault(
                vault_url="http://vault:8200"
            )

        # Verify the mock was not called
        mock_client.assert_not_called()

    @patch('hvac.Client')
    def test_connect_to_vault_authentication_failure(self, mock_client):
        """Test connection to Vault with authentication failure."""
        # Configure the mock
        mock_instance = mock_client.return_value
        mock_instance.is_authenticated.return_value = False

        # Call the method and expect an exception
        with self.assertRaises(ConnectionError):
            self.handler._connect_to_vault(
                vault_url="http://vault:8200",
                vault_token="test_token"
            )

        # Verify the mock was called with the correct arguments
        mock_client.assert_called_once_with(
            url="http://vault:8200",
            token="test_token"
        )
        mock_instance.is_authenticated.assert_called_once()

    @patch('hvac.Client')
    def test_get_token_success(self, mock_client):
        """Test successful token retrieval from Vault."""
        # Configure the mock
        mock_instance = mock_client.return_value
        mock_instance.is_authenticated.return_value = True
        mock_instance.secrets.kv.v2.read_secret_version.return_value = {
            'data': {
                'data': {
                    'token': 'test_influxdb_token'
                }
            }
        }

        # Call the method
        token = self.handler.get_token(
            vault_url="http://vault:8200",
            vault_token="test_token",
            secret_path="secret/influxdb",
            secret_key="token"
        )

        # Verify the result
        self.assertEqual(token, 'test_influxdb_token')

        # Verify the mock was called with the correct arguments
        mock_client.assert_called_once_with(
            url="http://vault:8200",
            token="test_token"
        )
        mock_instance.is_authenticated.assert_called_once()
        mock_instance.secrets.kv.v2.read_secret_version.assert_called_once_with(
            path="secret/influxdb"
        )

    @patch('hvac.Client')
    def test_get_token_missing_path(self, mock_client):
        """Test token retrieval from Vault with missing path."""
        # Configure the mock
        mock_instance = mock_client.return_value
        mock_instance.is_authenticated.return_value = True

        # Call the method and expect an exception
        with self.assertRaises(KeyError):
            self.handler.get_token(
                vault_url="http://vault:8200",
                vault_token="test_token",
                secret_key="token"
            )

    @patch('hvac.Client')
    def test_get_token_missing_key(self, mock_client):
        """Test token retrieval from Vault with missing key."""
        # Configure the mock
        mock_instance = mock_client.return_value
        mock_instance.is_authenticated.return_value = True

        # Call the method and expect an exception
        with self.assertRaises(KeyError):
            self.handler.get_token(
                vault_url="http://vault:8200",
                vault_token="test_token",
                secret_path="secret/influxdb"
            )

    @patch('hvac.Client')
    def test_get_token_secret_not_found(self, mock_client):
        """Test token retrieval from Vault with secret not found."""
        # Configure the mock
        mock_instance = mock_client.return_value
        mock_instance.is_authenticated.return_value = True
        mock_instance.secrets.kv.v2.read_secret_version.return_value = None

        # Call the method and expect an exception
        with self.assertRaises(KeyError):
            self.handler.get_token(
                vault_url="http://vault:8200",
                vault_token="test_token",
                secret_path="secret/influxdb",
                secret_key="token"
            )

    @patch('hvac.Client')
    def test_get_token_key_not_found(self, mock_client):
        """Test token retrieval from Vault with key not found in secret."""
        # Configure the mock
        mock_instance = mock_client.return_value
        mock_instance.is_authenticated.return_value = True
        mock_instance.secrets.kv.v2.read_secret_version.return_value = {
            'data': {
                'data': {
                    'other_key': 'test_value'
                }
            }
        }

        # Call the method and expect an exception
        with self.assertRaises(KeyError):
            self.handler.get_token(
                vault_url="http://vault:8200",
                vault_token="test_token",
                secret_path="secret/influxdb",
                secret_key="token"
            )


if __name__ == '__main__':
    unittest.main()
