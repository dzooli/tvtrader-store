import os
import sys
from pathlib import Path
from typing import List

import tomli
from loguru import logger

# Configure loguru to write to standard output
logger.remove()  # Remove default handler
logger.add(sys.stdout, format="{time} | {level} | {message}")


class Config:
    """Class to handle configuration loading and access."""

    def __init__(self, config_path: Path = None):
        """
        Initialize configuration from config file and environment variables.

        Args:
            config_path: Path to the configuration file. If None, uses a default path.
        """
        if config_path is None:
            config_path = Path(__file__).parent / "config.toml"

        with open(config_path, "rb") as f:
            self._config = tomli.load(f)

        # URL template for API requests
        self.url_template = "{base}/api/v1/prices?ticker={ticker}&amount=10&broker={broker}&timeframe={tf}"

        # Load and validate required configuration
        self._load_datasource_url()
        self._load_keycloak_password()
        self._load_influxdb_token()
        self._load_vault_token()

    def _load_datasource_url(self):
        """Load datasource URL from environment or config file."""
        self.datasource_url = os.environ.get("DATASOURCE_URL")
        if not self.datasource_url:
            # If not in environment, try config file
            if "datasource_url" in self._config["general"]:
                self.datasource_url = self._config["general"]["datasource_url"]
            else:
                # If not in the config file either, raise an exception
                logger.error("DATASOURCE_URL not found in environment variables or config file")
                raise ValueError("DATASOURCE_URL not found in environment variables or config file")

    def _load_keycloak_password(self):
        """Load Keycloak password from the environment."""
        self.keycloak_password = os.environ.get("KEYCLOAK_PASS")
        if not self.keycloak_password:
            logger.error("KEYCLOAK_PASS environment variable is not set")
            raise ValueError("KEYCLOAK_PASS environment variable is not set. Please set it to the Keycloak admin password.")

    def _load_influxdb_token(self):
        """Load InfluxDB token from the environment."""
        self._influxdb_token = os.environ.get("INFLUXDB_TOKEN")
        if not self._influxdb_token:
            logger.warning("INFLUXDB_TOKEN environment variable is not set. Will try to get it from Vault.")

    def _load_vault_token(self):
        """Load Vault token from the environment."""
        self._vault_token = os.environ.get("VAULT_TOKEN")
        if not self._vault_token:
            logger.warning("VAULT_TOKEN environment variable is not set. This is required for Vault authentication.")

    @property
    def influx_url(self) -> str:
        """Get InfluxDB URL."""
        return self._config["general"]["influx_url"]

    @property
    def influx_org(self) -> str:
        """Get InfluxDB organization."""
        return self._config["general"]["influx_org"]

    @property
    def keycloak_url(self) -> str:
        """Get Keycloak URL."""
        return self._config["general"]["keycloak_url"]

    @property
    def keycloak_realm(self) -> str:
        """Get Keycloak realm."""
        return self._config["general"]["keycloak_realm"]

    @property
    def keycloak_client_id(self) -> str:
        """Get Keycloak client ID."""
        return self._config["general"]["keycloak_client_id"]

    @property
    def keycloak_username(self) -> str:
        """Get Keycloak username."""
        return self._config["general"]["keycloak_username"]

    @property
    def keycloak_user_attribute(self) -> str:
        """Get Keycloak user attribute name for InfluxDB token."""
        return self._config["general"]["keycloak_user_attribute"]

    @property
    def tickers(self) -> List[str]:
        """Get a list of tickers."""
        return self._config["data"]["tickers"]

    @property
    def timeframes(self) -> List[str]:
        """Get a list of timeframes."""
        return self._config["data"]["timeframes"]

    @property
    def vault_url(self) -> str:
        """Get Vault URL."""
        return self._config["general"].get("vault_url", "http://vault:8200")

    @property
    def vault_secret_path(self) -> str:
        """Get Vault secret path for InfluxDB token."""
        return self._config["general"].get("vault_secret_path", "secret/influxdb")

    @property
    def vault_secret_key(self) -> str:
        """Get Vault secret key for InfluxDB token."""
        return self._config["general"].get("vault_secret_key", "token")

    @property
    def vault_token(self) -> str:
        """Get Vault token."""
        return self._vault_token

    @property
    def influxdb_token(self) -> str:
        """Get InfluxDB token."""
        return self._influxdb_token
