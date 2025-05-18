# Price Importer

This directory contains scripts for importing price data into InfluxDB.

## Configuration

The importer is configured using a TOML configuration file (`config.toml`). This file contains:

- General configuration (datasource URL, InfluxDB URL, etc.)
- Keycloak configuration for retrieving the InfluxDB token
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

# Keycloak configuration
keycloak_url = "http://keycloak:8080"
keycloak_realm = "tvtrader"
keycloak_client_id = "admin-cli"
keycloak_username = "admin"
keycloak_client_secret = "tvtrader-influxdb"

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

- `KEYCLOAK_PASS` - Password for the Keycloak admin user (used to retrieve the InfluxDB token)

## Project Structure

The project is organized into modules:

- `config.py` - Contains the `Config` class for handling configuration loading and access
- `importer.py` - Contains the `PriceImporter` class for handling the price import process
- `import_prices.py` - Main script that uses the above modules to run the import process
- `token_manager/` - Package for handling authentication tokens

## Usage

The main script is `import_prices.py`, which:

1. Reads configuration from `config.toml` using the `Config` class
2. Authenticates with Keycloak to retrieve the InfluxDB token
3. Fetches price data for the configured tickers and timeframes using the `PriceImporter` class
4. Writes the data to InfluxDB

To run the script:

```bash
python import_prices.py
```

The script can also be run on a schedule using the `run_hourly.sh` script, which is configured to run via supervisord.
