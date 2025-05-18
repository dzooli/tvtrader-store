import sys
from loguru import logger

from importer.config import Config
from importer.importer import PriceImporter
from importer.token_manager import TokenManager, TokenHandlerFactory

# Configure loguru to write to standard output
logger.remove()  # Remove default handler
logger.add(sys.stdout, format="{time} | {level} | {message}")


def main():
    """Main function to run the price import process."""
    # Load configuration
    config = Config()

    # Initialize token handler and manager using factory
    token_handler = TokenHandlerFactory.get_handler('keycloak')
    token_manager = TokenManager(token_handler)

    # Get InfluxDB token using TokenManager
    logger.info(f"Getting tokens from {config.keycloak_url}...")
    influx_token = token_manager.get_token(
        "influxdb",
        server_url=config.keycloak_url,
        client_id=config.keycloak_client_id,
        username=config.keycloak_username,
        password=config.keycloak_password,
        realm_name=config.keycloak_realm,
        client_secret_id=config.keycloak_client_secret
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
