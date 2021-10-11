#!/bin/bash
set -euo pipefail
set -x

EXP_DIR=$1

BASE_DIR=`realpath $(dirname $0)`
SRC_DIR=/mnt/efs/workspace/kafka-streams-benchmark/wordcount/
HELPER_SCRIPT=/mnt/efs/workspace/research-helper-scripts/microservice_helper

MANAGER_HOST=`$HELPER_SCRIPT get-docker-manager-host --base-dir=$BASE_DIR`

scp -q $BASE_DIR/docker-compose-base.yml $MANAGER_HOST:~
$HELPER_SCRIPT generate-docker-compose --base-dir=$BASE_DIR
scp -q $BASE_DIR/docker-compose.yml $MANAGER_HOST:~

ssh -q $MANAGER_HOST -- docker stack rm kstreams-test || true
ssh -q $MANAGER_HOST -- docker service rm app || true
ssh -q $MANAGER_HOST -- docker service rm "kstreams-test_source" || true
ssh -q $MANAGER_HOST -- docker service rm "kstreams-test_wordcount" || true

sleep 40

ALL_BROKER_HOSTS=`$HELPER_SCRIPT get-machine-with-label --machine-label=broker_node`
FIRST_BROKER=""
for HOST in $ALL_BROKER_HOSTS; do
    if [ "$FIRST_BROKER" = "" ]; then
        FIRST_BROKER=$HOST
    fi
    ssh -q $HOST -oStrictHostKeyChecking=no -- sudo rm -rf /mnt/storage/kdata
    ssh -q $HOST -oStrictHostKeyChecking=no -- sudo mkdir -p /mnt/storage/kdata
    ssh -q $HOST -oStrictHostKeyChecking=no -- sudo chown ubuntu:ubuntu /mnt/storage/kdata
done

ssh -q $MANAGER_HOST -- docker network rm kstreams-test_default || true
ssh -q $MANAGER_HOST -- SRC_DIR=$SRC_DIR \
    docker stack deploy \
    -c ~/docker-compose-base.yml -c ~/docker-compose.yml kstreams-test
sleep 80

rm -rf $EXP_DIR
mkdir -p $EXP_DIR
ssh -q $MANAGER_HOST -- cat /proc/cmdline >>$EXP_DIR/kernel_cmdline
ssh -q $MANAGER_HOST -- uname -a >>$EXP_DIR/kernel_version

ssh -q $MANAGER_HOST -- "docker service create \
    --mount type=bind,source=/mnt/efs/workspace/sharedlog-stream,destination=/src \
    --constraint node.role==manager --network kstreams-test_default \
    --name kstreams-test_source --restart-condition none ubuntu:focal /src/bin/wordcount_genevents_kafka \
    -broker broker-1:9092 -in_fname /src/data/books.dat"

sleep 10

ssh -q $MANAGER_HOST -- "docker service create \
    --mount type=bind,source=/mnt/efs/workspace/kafka-streams-benchmark/wordcount,destination=/src \
    --constraint node.labels.app_node==true --env BOOTSTRAP_SERVER_CONFIG=$FIRST_BROKER:29092 \
    --network kstreams-test_default --restart-condition none \
    --name kstreams-test_wordcount openjdk:11.0.12-jre-slim-buster \
    bash -c 'java -jar /src/target/wordcount-1.0-SNAPSHOT-jar-with-dependencies.jar'"
