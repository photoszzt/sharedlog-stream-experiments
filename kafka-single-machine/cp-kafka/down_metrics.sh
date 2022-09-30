#!/bin/bash

EXTERNAL_IP=$(hostname -I | awk '{print $1}') \
    SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd ) \
    docker-compose -f ./docker-compose-metrics.yml down
