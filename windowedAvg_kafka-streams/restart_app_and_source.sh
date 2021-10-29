#!/bin/bash
set -euo pipefail

EXP_DIR=$1
NUM_INSTANCE=$2

BASE_DIR=`realpath $(dirname $0)`
SRC_DIR=/mnt/efs/workspace/kafka-streams-benchmark/wordcount/
HELPER_SCRIPT=/mnt/efs/workspace/research-helper-scripts/microservice_helper

MANAGER_HOST=`$HELPER_SCRIPT get-docker-manager-host --base-dir=$BASE_DIR`

ssh -q $MANAGER_HOST -- docker service rm "kstreams-test_source" || true
ssh -q $MANAGER_HOST -- docker service rm "kstreams-test_windowedAvg" || true

sleep 40

ALL_BROKER_HOSTS=(`$HELPER_SCRIPT get-machine-with-label --machine-label=broker_node`)
FIRST_BROKER=${ALL_BROKER_HOSTS[0]}
container_id=$(ssh -q $FIRST_BROKER -oStrictHostKeyChecking=no -- "docker ps -f name=kstreams-test_broker --format "{{.ID}}"")
FIRST_BROKER_CONTAINER_IP=$(ssh -q $FIRST_BROKER -oStrictHostKeyChecking=no -- "docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $container_id")

ssh -q $MANAGER_HOST -- "docker service create \
    --mount type=bind,source=/mnt/efs/workspace/sharedlog-stream,destination=/src \
    --constraint node.labels.source_node==true --network kstreams-test_default \
    --name kstreams-test_source --restart-condition none ubuntu:focal /src/bin/nexmark_genevents_kafka \
    -broker $FIRST_BROKER_CONTAINER_IP:9092 -num_events 100000"

sleep 30

ssh -q $MANAGER_HOST -- "docker service create \
    --mount type=bind,source=/mnt/efs/workspace/nexmark/nexmark-kafka-streams,destination=/src \
    --constraint node.labels.app_node==true --env BOOTSTRAP_SERVER_CONFIG=$FIRST_BROKER_CONTAINER_IP:9092 \
    --network kstreams-test_default --restart-condition none --replicas=$NUM_INSTANCE \
    --replicas-max-per-node=1 --hostname='windowedAvg-{{.Task.Slot}}' \
    --name kstreams-test_windowedAvg openjdk:11.0.12-jre-slim-buster \
    bash -c 'java -cp /src/build/libs/nexmark-kafka-streams-0.2-SNAPSHOT-uber.jar com.github.nexmark.kafka.queries.RunQuery 9'"

sleep 60

$HELPER_SCRIPT collect-container-logs --base-dir=$BASE_DIR --log-path=$EXP_DIR/logs
