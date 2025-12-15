import sys
import os
from pathlib import Path

# Add the parent directory to the Python path so that 'importer' can be found as a package
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

from importer.importer import Config
from importer.importer import PriceImporter
from importer.tokenmanager import TokenManager
from importer.tokenhandler_factory import TokenHandlerFactory

# Configure loguru to write to standard output
logger.remove()  # Remove default handler
logger.add(sys.stdout, format="{time} | {level} | {message}")


def main():
    """Main function to run the price import process."""
    # Load configuration
    config = Config()

    # Initialize token handler and manager using factory
    token_handler = TokenHandlerFactory.get_handler("vault")
    token_manager = TokenManager(token_handler)

    # Try to get InfluxDB token from environment first
    logger.info("Getting InfluxDB token...")
    influx_token = config.influxdb_token

    # If not available in environment, use TokenManager to get it from Vault
    if not influx_token:
        logger.info(f"InfluxDB token not found in environment, getting from {config.vault_url}...")
        influx_token = token_manager.get_token(
            "influxdb",
            vault_url=config.vault_url,
            vault_token=config.vault_token,
            secret_path=config.vault_secret_path,
            secret_key=config.vault_secret_key,
        )

    # Initialize price importer
    importer = PriceImporter(config)

    try:
        # Connect to InfluxDB
        importer.connect_to_influxdb(influx_token)

        # Fetch and store prices
        importer.fetch_and_store_prices()
    finally:
        # Ensure the connection is closed
        importer.close()


if __name__ == "__main__":
    main()
