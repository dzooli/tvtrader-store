#!/bin/bash
set -e

while true; do
  echo "[INFO] Running price importer at $(date)"
  python import_prices.py
  echo "[INFO] Sleeping for 1 hour"
  sleep 3600
done
