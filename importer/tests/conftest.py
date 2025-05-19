import pytest
from unittest.mock import MagicMock, patch

from importer.tokenmanager import TokenHandler, TokenManager
from importer.config import Config
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


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


@pytest.fixture
def mock_config():
    """Fixture that provides a mock Config object."""
    config = MagicMock(spec=Config)
    config.influx_url = "http://influxdb:8086"
    config.influx_org = "pricestore"
    config.datasource_url = "http://localhost:3000"
    config.url_template = "{base}/api/v1/prices?ticker={ticker}&amount=10&broker={broker}&timeframe={tf}"
    config.tickers = ["FX:GBPUSD", "FX:EURUSD"]
    config.timeframes = ["4H", "1D"]
    config.influxdb_token = "test_influxdb_token"
    return config


@pytest.fixture
def mock_write_api():
    """Fixture that provides a mock InfluxDB write API."""
    write_api = MagicMock()
    write_api.write.return_value = None
    return write_api


@pytest.fixture
def mock_influxdb_client(mock_write_api):
    """Fixture that provides a mock InfluxDBClient."""
    client = MagicMock(spec=InfluxDBClient)
    client.write_api.return_value = mock_write_api
    return client


@pytest.fixture
def mock_requests_get():
    """Fixture that provides a mock for requests.get."""
    with patch('requests.get') as mock_get:
        response = MagicMock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "result": {
                "prices": [
                    {
                        "measurement": "price",
                        "ticker": "GBPUSD",
                        "broker": "FX",
                        "timeframe": "4H",
                        "open": 1.2345,
                        "high": 1.2456,
                        "low": 1.2234,
                        "close": 1.2400,
                        "volume": 1000,
                        "timestamp": 1609459200
                    }
                ]
            }
        }
        mock_get.return_value = response
        yield mock_get
