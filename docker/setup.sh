#!/bin/bash

USER_NAME="${INFLUX_USER:-user}"
USER_PASSWORD="${INFLUX_PASSWORD:-userpassword}"
ORG="pricestore"
URL="http://localhost:8086"
TOKEN="${INFLUX_ADMIN_TOKEN:-admintoken}"
VAULT_URL="${VAULT_URL:-http://localhost:8200}"
VAULT_TOKEN="${VAULT_TOKEN:-admintoken}"

influx config create --config-name local \
    --host-url $URL \
    --org $ORG \
    --token $TOKEN \
    --active

echo "Creating buckets..."
influx bucket create --name prices_1m --org $ORG
influx bucket create --name prices_5m --org $ORG
influx bucket create --name prices_15m --org $ORG
influx bucket create --name prices_30m --org $ORG
influx bucket create --name prices_45m --org $ORG
influx bucket create --name prices_1h --org $ORG
influx bucket create --name prices_2h --org $ORG
influx bucket create --name prices_3h --org $ORG
influx bucket create --name prices_4h --org $ORG
influx bucket create --name prices_1d --org $ORG
influx bucket create --name prices_1w --org $ORG
influx bucket create --name prices_default --org $ORG

echo "Creating admin user for ${ORG}..."
set -x
USER_ID=$(influx user create --name $USER_NAME --org $ORG --password $USER_PASSWORD --json | jq -r '.id')
USER_TOKEN=$(influx auth create --read-buckets --write-buckets --user $USER_NAME --org $ORG --description "Read-Write user for the prices" --json | jq -r '.token')
READONLY_USERNAME="${READONLY_USERNAME:-readonly-user}"

set +x
echo ">> Creating read-only user: $READONLY_USERNAME"
influx user create --name "$READONLY_USERNAME"

echo ">> Creating read-only token..."
READONLY_TOKEN=$(influx auth create \
  --org $ORG \
  --read-buckets \
  --user "$READONLY_USERNAME" \
  --description "Read-only token for $READONLY_USERNAME" \
  --json | jq -r '.token')

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
# Create the secret path if it doesn't exist
set -x
VAULT_URL_CLEAN=${VAULT_URL%/}
curl -v -s -X POST \
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
echo "InfluxDB Setup finished."
