#!/bin/bash

EXP_DIR=$1

BASE_DIR=`realpath $(dirname $0)`
SRC_DIR=/mnt/efs/workspace/kafka-streams-benchmark
HELPER_SCRIPT=/mnt/efs/workspace/research-helper-scripts/microservice_helper

MANAGER_HOST=`$HELPER_SCRIPT get-docker-manager-host --base-dir=$BASE_DIR`

scp -q $BASE_DIR/docker-compose-base.yml $MANAGER_HOST:~
$HELPER_SCRIPT generate-docker-compose --base-dir=$BASE_DIR
scp -q $BASE_DIR/docker-compose.yml $MANAGER_HOST:~

ssh -q $MANAGER_HOST -- docker stack rm kstreams-test

sleep 40

# ALL_BROKER_HOSTS=`$HELPER_SCRIPT get-machine-with-label --machine-label=broker_node`
ssh -q $MANAGER_HOST -- docker network rm kstreams-test_default
ssh -q $MANAGER_HOST -- SRC_DIR=$SRC_DIR \
    docker stack deploy \
    -c ~/docker-compose-base.yml -c ~/docker-compose.yml kstreams-test
sleep 80

rm -rf $EXP_DIR
mkdir -p $EXP_DIR
ssh -q $MANAGER_HOST -- cat /proc/cmdline >>$EXP_DIR/kernel_cmdline
ssh -q $MANAGER_HOST -- uname -a >>$EXP_DIR/kernel_version