import pytest
from unittest.mock import MagicMock

from importer.token_manager import TokenHandler, TokenManager


@pytest.fixture
def mock_keycloak_openid():
    """Fixture that provides a mock KeycloakOpenID."""
    mock = MagicMock()
    mock.token.return_value = {"access_token": "test_access_token"}
    return mock


@pytest.fixture
def mock_keycloak_admin():
    """Fixture that provides a mock KeycloakAdmin."""
    mock = MagicMock()
    mock.get_clients.return_value = [
        {"clientId": "test_client", "id": "test_client_id"},
        {"clientId": "another_client", "id": "another_client_id"}
    ]
    mock.get_client_secrets.return_value = ["test_client_secret"]
    return mock


@pytest.fixture
def mock_token_handler():
    """Fixture that provides a mock TokenHandler."""
    handler = MagicMock(spec=TokenHandler)
    handler.get_token.return_value = "test_token"
    return handler


@pytest.fixture
def token_manager(mock_token_handler):
    """Fixture that provides a TokenManager with a mock TokenHandler."""
    return TokenManager(mock_token_handler)
