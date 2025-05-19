# tvtrader-store

Storage solution for the TvTrader stack based on InfluxDB for time-series data storage.

## Overview

This directory contains the configuration and code for the storage component of the TvTrader system. It consists of:

1. **InfluxDB** - A time-series database for storing financial price data
2. **Vault** - A secrets management service for secure token storage
3. **Keycloak** - An identity and access management service (legacy, being replaced by Vault)
4. **Importer** - A service that periodically imports price data from an external source

## Components

### InfluxDB

The InfluxDB service is configured to store financial price data with:
- Multiple buckets for different timeframes (4h, 1d)
- User access control with admin, read-write, and read-only users
- Persistent storage using Docker volumes

### Vault

The Vault service provides:
- Secure storage for authentication tokens and secrets
- Fine-grained access control
- Integration with the setup process to store InfluxDB tokens
- Persistent storage using Docker volumes

During the setup process, the InfluxDB read-write and read-only tokens are automatically stored in Vault. The importer service authenticates with Vault to retrieve these tokens when needed, providing a secure approach for managing sensitive credentials.

### Keycloak (Legacy)

The Keycloak service was previously used for:
- Secure storage for authentication tokens
- Identity and access management
- Integration with the setup process to store InfluxDB tokens
- Persistent storage using Docker volumes

Note: Keycloak is being phased out in favor of Vault for secret management. It is kept for backward compatibility.

### Importer

The importer service:
- Runs on an hourly schedule
- Fetches price data for currency pairs (GBPUSD, EURUSD)
- Supports multiple timeframes (4H, 1D)
- Writes data to the appropriate InfluxDB buckets

## Configuration

The system is configured using environment variables in the `.env` file. An example configuration is provided in `.env.example`.

Key configuration parameters:
- `INFLUX_USER` - Username for the InfluxDB read-write user
- `INFLUX_PASSWORD` - Password for the InfluxDB read-write user
- `READONLY_USERNAME` - Username for the InfluxDB read-only user
- `DATASOURCE_URL` - URL of the data source API
- `INFLUXDB_URL` - URL of the InfluxDB instance
- `INFLUXDB_ORG` - Organization name in InfluxDB
- `VAULT_TOKEN` - Root token for the Vault server
- `VAULT_URL` - URL of the Vault instance
- `KEYCLOAK_PASS` - Password for the Keycloak admin user (legacy)
- `KEYCLOAK_URL` - URL of the Keycloak instance (legacy)

Note: The InfluxDB tokens are not directly specified in the environment variables. Instead, they are automatically generated during setup and stored securely in Vault. The importer service retrieves these tokens from Vault when needed.

## Usage

### Starting the Services

To start all services:

```bash
docker-compose up -d
```

This will start all three services: InfluxDB, Keycloak, and the importer.

### Accessing InfluxDB

InfluxDB is accessible on port 8086. You can access the InfluxDB UI at:

```
http://localhost:8086
```

### Accessing Keycloak

Keycloak is accessible on port 8080. You can access the Keycloak admin console at:

```
http://localhost:8080/admin/
```

Login with:
- Username: admin
- Password: The value of KEYCLOAK_PASS from your .env file

### Data Structure

Price data is stored in the following buckets:
- `prices_4h` - 4-hour price data
- `prices_1d` - Daily price data

Each data point contains:
- Tags: ticker, broker, timeframe
- Fields: open, high, low, close, volume
- Timestamp

## Development

### Directory Structure

- `docker/` - Contains Dockerfile and setup script for InfluxDB, Vault, and Keycloak integration
- `importer/` - Contains code for the data importer service
  - `import_prices.py` - Main script for importing price data
  - `config.toml` - Configuration for the importer (tickers, timeframes)
  - `vault_handler.py` - Handler for retrieving tokens from Vault
  - `keycloak_handler.py` - Handler for retrieving tokens from Keycloak (legacy)
  - `run_hourly.sh` - Script to run the importer on an hourly schedule
  - `supervisord.conf` - Supervisor configuration for managing the importer process
- `.env.example` - Example environment configuration including Vault and Keycloak settings
- `docker-compose.yml` - Docker Compose configuration for all services (InfluxDB, Vault, Keycloak, Importer)

### Adding New Data Sources

To add new data sources, modify the `config.toml` file in the importer directory:
1. Add new tickers to the `tickers` list in the format `"BROKER:TICKER"` (e.g., `"FX:GBPUSD"`)
2. Add new timeframes to the `timeframes` list if needed

The system supports multiple timeframes including:
- `1m`, `5m`, `15m`, `30m`, `45m` - Minute-based timeframes
- `1h`, `2h`, `3h`, `4h` - Hour-based timeframes
- `1D` - Daily timeframe
- `1W` - Weekly timeframe

Each timeframe will be stored in a corresponding bucket (e.g., `prices_4h`, `prices_1d`). If you add a new timeframe, make sure to create the corresponding bucket in the setup script.
