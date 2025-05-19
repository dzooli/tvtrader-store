#!/bin/bash

# This script changes the password for INFLUX_USER and stores the token in Vault on every container startup

USER_NAME="${INFLUX_USER:-user}"
USER_PASSWORD="${INFLUX_PASSWORD:-userpassword}"
ORG="pricestore"
URL="http://localhost:8086"
TOKEN="${INFLUX_ADMIN_TOKEN:-admintoken}"
VAULT_URL="${VAULT_URL:-http://localhost:8200}"
VAULT_TOKEN="${VAULT_TOKEN:-admintoken}"

echo ">> Refreshing password for user ${USER_NAME}..."

# Configure influx CLI
influx config create --config-name local \
    --host-url $URL \
    --org $ORG \
    --token $TOKEN \
    --active

# Change the password for the user
influx user password -n $USER_NAME -p $USER_PASSWORD

# Create a new token for the user
USER_TOKEN=$(influx auth create --read-buckets --write-buckets --user $USER_NAME --org $ORG --description "Read-Write user for the prices" --json | jq -r '.token')

# Get the read-only token (assuming it already exists)
READONLY_USERNAME="${READONLY_USERNAME:-readonly-user}"
# Create a new token for the user
READONLY_TOKEN=$(influx auth create --read-buckets --write-buckets --user $READONLY_USERNAME --org $ORG --description "Read-Only user for the prices" --json | jq -r '.token')

echo ">> Waiting for Vault..."
TIMEOUT=300
VAULT_URL_CLEAN=${VAULT_URL%/}
while ! curl -s "$VAULT_URL_CLEAN/v1/sys/health" > /dev/null; do
    if [ "$TIMEOUT" -le 0 ]; then
        echo "Timeout waiting for Vault to be ready"
        exit 1
    fi
    echo "Waiting for Vault to be ready... ${TIMEOUT}s remaining"
    sleep 5
    TIMEOUT=$((TIMEOUT-5))
done

echo ">> Storing USER_TOKEN and READONLY_TOKEN in Vault..."
# Store the tokens in Vault
VAULT_URL_CLEAN=${VAULT_URL%/}
curl -s -X POST \
  -H "X-Vault-Token: $VAULT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"data\":{\"token\":\"$USER_TOKEN\",\"readonly_token\":\"$READONLY_TOKEN\"}}" \
  -L "$VAULT_URL_CLEAN/v1/secret/data/influxdb" \
&& echo ">> USER_TOKEN and READONLY_TOKEN stored in Vault successfully." \
|| echo ">> Failed to store the tokens!"

echo "----------------------------"
echo "Admin token: $TOKEN"
echo "Read-Write user token on $ORG: $USER_TOKEN"
echo "Read-only token for $READONLY_USERNAME on $ORG: $READONLY_TOKEN"
echo "----------------------------"

echo ""
echo "InfluxDB Password Refresh finished."
