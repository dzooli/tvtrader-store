FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y supervisor && \
    pip install influxdb-client loguru python-keycloak requests tomli && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create importer directory for package structure
RUN mkdir -p /app/importer

COPY ./import_prices.py /app
COPY ./config.toml /app
COPY ./run_hourly.sh /app
COPY ./config.py /app/importer/
COPY ./importer.py /app/importer/
COPY token_manager /app/importer/token_manager

# Create __init__.py in importer directory to make it a package
RUN touch /app/importer/__init__.py

RUN chmod +x /app/run_hourly.sh

COPY supervisord.conf /etc/supervisor/supervisord.conf

CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]
