#!/bin/bash
set -x

cp -r $1 /tmp
dir_name=$(basename $1)
chmod 777 /tmp/${dir_name}
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
docker run --rm -d -p 9090:9090 -v /tmp/${dir_name}/:/prometheus prom/prometheus \
    --config.file=/etc/prometheus/prometheus.yml  --storage.tsdb.path=/prometheus
docker run --rm -d -p 5000:3000 -v ${SCRIPT_DIR}/assets/grafana/provisioning:/etc/grafana/provisioning \
    -e GF_SECURITY_ADMIN_USER=admin -e GF_SECURITY_ADMIN_PASSWORD=password -e GF_USERS_ALLOW_SIGN_UP=false \
    grafana/grafana:8.1.3
