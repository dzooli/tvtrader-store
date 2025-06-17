FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y supervisor && \
    pip install hvac influxdb-client  loguru python-keycloak requests tomli  && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create proper Python package structure
RUN mkdir -p /app/importer

# Copy all files to maintain the correct package structure
COPY ./import_prices.py /app/importer/
COPY ./config.toml /app/importer/
COPY ./run_hourly.sh /app/
COPY config.py /app/importer/
COPY importer.py /app/importer/
COPY environment_handler.py /app/importer/
COPY vault_handler.py /app/importer/
COPY tokenhandler_factory.py /app/importer/
COPY tokenmanager.py /app/importer/
COPY environment_handler.py /app/importer
COPY vault_handler.py /app/importer
COPY ./__init__.py /app/importer/

# Make sure the Python path includes the parent directory
ENV PYTHONPATH=/app

RUN chmod +x /app/run_hourly.sh

COPY supervisord.conf /etc/supervisor/supervisord.conf

CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]
