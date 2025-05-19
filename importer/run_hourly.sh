#!/bin/bash
set -e

while true; do
    echo "[INFO] Awakening..."
    sleep 120
    echo "[INFO] Running price importer at $(date)"
    cd /app/importer && python import_prices.py
    echo "[INFO] Sleeping..."
    sleep 3180
done
