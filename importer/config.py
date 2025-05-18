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
    def keycloak_client_secret(self) -> str:
        """Get Keycloak client secret."""
        return self._config["general"]["keycloak_client_secret"]

    @property
    def tickers(self) -> List[str]:
        """Get a list of tickers."""
        return self._config["data"]["tickers"]

    @property
    def timeframes(self) -> List[str]:
        """Get a list of timeframes."""
        return self._config["data"]["timeframes"]
