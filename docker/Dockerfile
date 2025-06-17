FROM influxdb:2.7

ENV DOCKER_INFLUXDB_INIT_MODE=setup \
    DOCKER_INFLUXDB_INIT_USERNAME=admin \
    DOCKER_INFLUXDB_INIT_PASSWORD=adminpassword \
    DOCKER_INFLUXDB_INIT_ORG=pricestore \
    DOCKER_INFLUXDB_INIT_BUCKET=default \
    DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=admintoken

COPY setup.sh /docker-entrypoint-initdb.d/setup.sh
COPY refresh_password.sh /refresh_password.sh

RUN apt-get update && apt-get install -y curl jq && apt-get clean \
&& chmod +x /docker-entrypoint-initdb.d/setup.sh /refresh_password.sh \
&& echo '#!/bin/bash\n\
# Run the password refresh script in the background\n\
(sleep 10 && /refresh_password.sh) &\n\
\n\
# Execute the original entrypoint\n\
exec /entrypoint.sh "$@"' > /custom-entrypoint.sh \
&& chmod +x /custom-entrypoint.sh

ENTRYPOINT ["/custom-entrypoint.sh"]
