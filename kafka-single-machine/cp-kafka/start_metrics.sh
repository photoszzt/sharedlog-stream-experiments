#!/bin/bash

rm -rf /mnt/data/src/stream_workspace/kdata1/*
rm -rf /mnt/data/src/stream_workspace/kdata2/*
rm -rf /mnt/data/src/stream_workspace/kdata3/*

EXTERNAL_IP=$(hostname -I | awk '{print $1}') \
    SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd ) \
    docker-compose -f ./docker-compose-metrics.yml up -d
