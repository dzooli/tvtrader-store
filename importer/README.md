# Price Importer

This directory contains scripts for importing price data into InfluxDB.

## Configuration

The importer is configured using a TOML configuration file (`config.toml`). This file contains:

- General configuration (datasource URL, InfluxDB URL, etc.)
- Vault configuration for retrieving the InfluxDB token
- Data configuration (tickers and timeframes to import)

### Example Configuration

```toml
# Configuration for import_prices.py

[general]
# Data source URL
datasource_url = "http://localhost:3000"

# InfluxDB configuration
influx_url = "http://influxdb:8086"
influx_org = "pricestore"

# Vault configuration
vault_url = "http://vault:8200"
vault_secret_path = "secret/influxdb"
vault_secret_key = "token"
# vault_secret_key can also be "readonly_token" to access the read-only token

[data]
# Tickers to fetch prices for
tickers = [
    "GBPUSD",
    "EURUSD"
]

# Timeframes to fetch prices for
timeframes = [
    "4H",
    "1D"
]
```

## Environment Variables

The script requires the following environment variables:

- `VAULT_TOKEN` - Token for authenticating with Vault (used to retrieve the InfluxDB tokens)
- `INFLUXDB_TOKEN` - (Optional) Token for InfluxDB. If not set, it will be retrieved from Vault

During the setup process, both the read-write token (`USER_TOKEN`) and read-only token (`READONLY_TOKEN`) are stored in Vault at the path specified in the configuration. The importer can access either token by specifying the appropriate key in the configuration.

## Project Structure

The project is organized into modules:

- `config.py` - Contains the `Config` class for handling configuration loading and access
- `importer.py` - Contains the `PriceImporter` class for handling the price import process
- `import_prices.py` - Main script that uses the above modules to run the import process
- `vault_handler.py` - Handler for retrieving tokens from Vault
- `tokenmanager.py` - Contains the `TokenManager` class for managing authentication tokens
- `tokenhandler_factory.py` - Factory for creating token handlers

## Usage

The main script is `import_prices.py`, which:

1. Reads configuration from `config.toml` using the `Config` class
2. Authenticates with Vault to retrieve the InfluxDB tokens (if not provided via environment variable)
3. Fetches price data for the configured tickers and timeframes using the `PriceImporter` class
4. Writes the data to InfluxDB

The script uses the `VaultTokenHandler` to retrieve tokens from Vault.

To run the script:

```bash
python import_prices.py
```

The script can also be run on a schedule using the `run_hourly.sh` script, which is configured to run via supervisord.
