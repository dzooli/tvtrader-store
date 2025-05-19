#!/bin/sh
set -e

echo "🔧 Fixing permissions on /vault/data..."
chown -R vault:vault /vault/data

echo "🚀 Starting Vault server..."
exec "$@"
