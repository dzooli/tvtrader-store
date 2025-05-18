FROM influxdb:2.7

ENV DOCKER_INFLUXDB_INIT_MODE=setup \
    DOCKER_INFLUXDB_INIT_USERNAME=admin \
    DOCKER_INFLUXDB_INIT_PASSWORD=adminpassword \
    DOCKER_INFLUXDB_INIT_ORG=pricestore \
    DOCKER_INFLUXDB_INIT_BUCKET=default \
    DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=admintoken

RUN apt-get update && apt-get install -y curl jq && apt-get clean

COPY setup.sh /docker-entrypoint-initdb.d/setup.sh
RUN chmod +x /docker-entrypoint-initdb.d/setup.sh
