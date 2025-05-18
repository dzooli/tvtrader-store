"""
Unit tests for the KeycloakTokenHandler class.

This module contains tests for the KeycloakTokenHandler class.
"""
from unittest.mock import MagicMock, patch

import pytest

from importer.token_manager.handlers.keycloak import KeycloakTokenHandler


class TestKeycloakTokenHandler:
    """Test cases for the KeycloakTokenHandler class."""

    @patch("importer.token_manager.handlers.keycloak.KeycloakOpenID")
    def test_get_token_success(self, mock_keycloak_openid_class, mock_keycloak_openid):
        """Test that get_token returns a token successfully."""
        # Setup
        mock_keycloak_openid_class.return_value = mock_keycloak_openid
        handler = KeycloakTokenHandler()

        # Execute
        token = handler.get_token(
            server_url="http://keycloak",
            client_id="test_client",
            username="test_user",
            password="test_password",
            realm_name="test_realm"
        )

        # Verify
        mock_keycloak_openid_class.assert_called_once_with(
            server_url="http://keycloak",
            client_id="test_client",
            realm_name="test_realm"
        )
        mock_keycloak_openid.token.assert_called_once_with(
            username="test_user",
            password="test_password",
            grant_type="password"
        )
        assert token == "test_access_token"

    @patch("importer.token_manager.handlers.keycloak.KeycloakOpenID")
    def test_get_token_failure(self, mock_keycloak_openid_class):
        """Test that get_token raises KeyError when it fails."""
        # Setup
        mock_keycloak_openid = MagicMock()
        mock_keycloak_openid.token.side_effect = Exception("Token error")
        mock_keycloak_openid_class.return_value = mock_keycloak_openid
        handler = KeycloakTokenHandler()

        # Execute and verify
        with pytest.raises(KeyError) as excinfo:
            handler.get_token(
                server_url="http://keycloak",
                client_id="test_client",
                username="test_user",
                password="test_password"
            )

        assert "Failed to get Keycloak token" in str(excinfo.value)

    @patch("importer.token_manager.handlers.keycloak.KeycloakAdmin")
    def test_get_client_secret_success(self, mock_keycloak_admin_class, mock_keycloak_admin):
        """Test that get_client_secret returns a client secret successfully."""
        # Setup
        mock_keycloak_admin_class.return_value = mock_keycloak_admin
        handler = KeycloakTokenHandler()

        # Execute
        client_secret = handler.get_client_secret(
            access_token="test_access_token",
            server_url="http://keycloak",
            realm_name="test_realm",
            client_secret_id="test_client"
        )

        # Verify
        mock_keycloak_admin_class.assert_called_once_with(
            server_url="http://keycloak",
            realm_name="test_realm",
            token={'access': "test_access_token"}
        )
        mock_keycloak_admin.get_clients.assert_called_once()
        mock_keycloak_admin.get_client_secrets.assert_called_once_with("test_client_id")
        assert client_secret == "test_client_secret"

    @patch("importer.token_manager.handlers.keycloak.KeycloakAdmin")
    def test_get_client_secret_client_not_found(self, mock_keycloak_admin_class, mock_keycloak_admin):
        """Test that get_client_secret raises AttributeError when client is not found."""
        # Setup
        mock_keycloak_admin_class.return_value = mock_keycloak_admin
        handler = KeycloakTokenHandler()

        # Execute and verify
        with pytest.raises(AttributeError) as excinfo:
            handler.get_client_secret(
                access_token="test_access_token",
                server_url="http://keycloak",
                realm_name="test_realm",
                client_secret_id="nonexistent_client"
            )

        assert "Client nonexistent_client not found" in str(excinfo.value)

    @patch("importer.token_manager.handlers.keycloak.KeycloakAdmin")
    def test_get_clients_failure(self, mock_keycloak_admin_class):
        """Test that get_clients raises KeyError when API call fails."""
        # Setup
        mock_keycloak_admin = MagicMock()
        mock_keycloak_admin.get_clients.side_effect = Exception("API error")
        mock_keycloak_admin_class.return_value = mock_keycloak_admin
        handler = KeycloakTokenHandler()

        # Execute and verify
        with pytest.raises(Exception) as excinfo:
            handler.get_client_secret(
                access_token="test_access_token",
                server_url="http://keycloak",
                realm_name="test_realm",
                client_secret_id="test_client"
            )

        assert "API error" in str(excinfo.value)
