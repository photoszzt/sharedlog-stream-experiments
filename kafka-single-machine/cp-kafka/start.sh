#!/bin/bash

rm -rf /mnt/data/src/stream_workspace/kdata1/*
rm -rf /mnt/data/src/stream_workspace/kdata2/*
rm -rf /mnt/data/src/stream_workspace/kdata3/*
docker-compose -f ./docker-compose-local.yml up -d
