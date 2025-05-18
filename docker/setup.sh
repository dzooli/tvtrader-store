#!/bin/bash

USER_NAME="${INFLUX_USER:-user}"
USER_PASSWORD="${INFLUX_PASSWORD:-userpassword}"
ORG="pricestore"
URL="http://localhost:8086"
TOKEN="${INFLUX_ADMIN_TOKEN:-admintoken}"
KEYCLOAK_URL="${KEYCLOAK_URL:-http://localhost:8080}"
KEYCLOAK_ADMIN="admin"
KEYCLOAK_ADMIN_PASSWORD="${KEYCLOAK_PASS:-admin_password}"
KEYCLOAK_REALM="tvtrader"

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

echo ">> Storing USER_TOKEN in Keycloak..."
# Get Keycloak access token
echo ">> Getting Keycloak access token..."
KC_ACCESS_TOKEN=$(curl -s \
  -d "client_id=admin-cli" \
  -d "username=$KEYCLOAK_ADMIN" \
  -d "password=$KEYCLOAK_ADMIN_PASSWORD" \
  -d "grant_type=password" \
  "${KEYCLOAK_URL}/realms/master/protocol/openid-connect/token" | jq -r '.access_token')

if [ -z "$KC_ACCESS_TOKEN" ] || [ "$KC_ACCESS_TOKEN" == "null" ]; then
  echo "Failed to get Keycloak access token. Check Keycloak credentials and connectivity."
else
  echo ">> Keycloak access token obtained successfully."

  # Check if realm exists, create if it doesn't
  REALM_EXISTS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $KC_ACCESS_TOKEN" \
    "${KEYCLOAK_URL}/admin/realms/$KEYCLOAK_REALM")

  if [ "$REALM_EXISTS" != "200" ]; then
    echo ">> Creating realm $KEYCLOAK_REALM..."
    curl -s -X POST \
      -H "Authorization: Bearer $KC_ACCESS_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"realm\":\"$KEYCLOAK_REALM\",\"enabled\":true}" \
      "${KEYCLOAK_URL}/admin/realms"
  fi

  # Store USER_TOKEN as a client secret
  # First check if client exists
  CLIENT_ID="tvtrader-influxdb"
  CLIENT_EXISTS=$(curl -s \
    -H "Authorization: Bearer $KC_ACCESS_TOKEN" \
    "${KEYCLOAK_URL}/admin/realms/$KEYCLOAK_REALM/clients" | jq -r ".[] | select(.clientId==\"$CLIENT_ID\") | .id")

  if [ -z "$CLIENT_EXISTS" ]; then
    echo ">> Creating client $CLIENT_ID..."
    CLIENT_EXISTS=$(curl -s -X POST \
      -H "Authorization: Bearer $KC_ACCESS_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"clientId\":\"$CLIENT_ID\",\"enabled\":true,\"clientAuthenticatorType\":\"client-secret\"}" \
      "${KEYCLOAK_URL}/admin/realms/$KEYCLOAK_REALM/clients" \
      -v 2>&1 | grep -oP 'Location: .*/\K[^/]+(?=\r)')
  fi

  if [ -n "$CLIENT_EXISTS" ]; then
    echo ">> Storing USER_TOKEN as client secret..."
    curl -s -X PUT \
      -H "Authorization: Bearer $KC_ACCESS_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"value\":\"$USER_TOKEN\"}" \
      "${KEYCLOAK_URL}/admin/realms/$KEYCLOAK_REALM/clients/$CLIENT_EXISTS/client-secret"

    echo ">> USER_TOKEN stored in Keycloak successfully."
  else
    echo "Failed to create or find client in Keycloak."
  fi
fi

echo "----------------------------"
echo "Admin token: $TOKEN"
echo "Read-Write user token on $ORG: $USER_TOKEN"
echo "Read-only token for $READONLY_USERNAME on $ORG: $READONLY_TOKEN"
echo "----------------------------"
