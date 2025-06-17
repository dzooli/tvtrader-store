# InfluxDB Container with Password Refresh

This directory contains the Dockerfile and scripts for the InfluxDB container used in the tvtrader project.

## Features

- Initial setup of InfluxDB with admin user, organization, and buckets
- Creation of a read-write user and a read-only user
- Password refresh for the read-write user on every container startup
- Storage of user tokens in Vault for secure access

## How It Works

1. The container is built from the official InfluxDB 2.7 image
2. During the first startup, the `setup.sh` script is executed to:
   - Create the initial buckets
   - Create the admin user
   - Create the read-write user (from INFLUX_USER environment variable)
   - Create the read-only user (from READONLY_USERNAME environment variable)
   - Store the tokens in Vault

3. On every subsequent startup, the `refresh_password.sh` script is executed to:
   - Change the password for the read-write user to the value in INFLUX_PASSWORD
   - Create a new token for the user
   - Store the updated token in Vault

## Environment Variables

- `INFLUX_USER`: The username for the read-write user (default: "user")
- `INFLUX_PASSWORD`: The password for the read-write user (default: "userpassword")
- `READONLY_USERNAME`: The username for the read-only user (default: "readonly-user")
- `INFLUX_ADMIN_TOKEN`: The admin token for InfluxDB (default: "admintoken")
- `VAULT_URL`: The URL of the Vault server (default: "http://localhost:8200")
- `VAULT_TOKEN`: The token for authenticating with Vault (default: "admintoken")

## Testing

To test the password refresh functionality:

1. Start the containers using docker-compose:
   ```
   docker-compose up -d
   ```

2. Check the logs to verify that the password refresh script ran successfully:
   ```
   docker-compose logs influxdb
   ```

3. You should see output indicating that the password was refreshed and the tokens were stored in Vault.

4. To verify that the tokens are stored in Vault, you can use the Vault CLI:
   ```
   export VAULT_ADDR=http://localhost:8200
   export VAULT_TOKEN=myroot
   vault kv get secret/influxdb
   ```

5. You should see the updated tokens for both the read-write user and the read-only user.
