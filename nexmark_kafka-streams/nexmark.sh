#!/bin/bash
set -euo pipefail
set -x

NAME=""
EXP_DIR=""
NUM_INSTANCE=""
NUM_SRC_INSTANCE=""
SERDE=""
DURATION=""

while [ $# -gt 0 ]; do
    case "$1" in
        --app*)
            if [[ "$1" != *=* ]]; then shift; fi
            NAME="${1#*=}"
            ;;
        --exp_dir*)
            if [[ "$1" != *=* ]]; then shift; fi
            EXP_DIR="${1#*=}"
            ;;
        --nins*)
            if [[ "$1" != *=* ]]; then shift; fi
            NUM_INSTANCE="${1#*=}"
            ;;
        --nsrc*)
            if [[ "$1" != *=* ]]; then shift; fi
            NUM_SRC_INSTANCE="${1#*=}"
            ;;
        --serde*)
            if [[ "$1" != *=* ]]; then shift; fi
            SERDE="${1#*=}"
            ;;
        --duration*)
            if [[ "$1" != *=* ]]; then shift; fi
            DURATION="${1#*=}"
            ;;
        --help|-h)
            printf -- "--app <appname> one of q1,q2,q3,q5,q7,q8\n"
            printf -- "--exp_dir <exp_dir> required\n"
            printf -- "--nins <nins> number of instance\n"
            printf -- "--nsrc <nsrc> number of source\n"
            printf -- "--serde <json or msgp>\n"
            printf -- "--duration <duration in sec>\n"
            exit 0
            ;;
        *)
            >&2 printf "Error: invalid argument"
            exit 1
            ;;
    esac
    shift
done

if [[ "$EXP_DIR" = "" ]] || [[ "$NUM_INSTANCE" = "" ]] || [[ "$NAME" = "" ]]; then
    echo "should provide app name, exp_dir and number of instance"
    exit 1
fi

echo "app: $NAME, exp_dir: $EXP_DIR, num_instance: $NUM_INSTANCE, num_src: $NUM_SRC_INSTANCE, serde: $SERDE, duration: $DURATION"

NUM_SRC_INSTANCE=${NUM_SRC_INSTANCE:-1}
SERDE=${SERDE:-json}
DURATION=${DURATION:-60}

BASE_DIR=`realpath $(dirname $0)`
HELPER_SCRIPT=/mnt/efs/workspace/research-helper-scripts/microservice_helper

MANAGER_HOST=`$HELPER_SCRIPT get-docker-manager-host --base-dir=$BASE_DIR`

scp -q $BASE_DIR/docker-compose-base.yml $MANAGER_HOST:~
$HELPER_SCRIPT generate-docker-compose --base-dir=$BASE_DIR
scp -q $BASE_DIR/docker-compose.yml $MANAGER_HOST:~

ssh -q $MANAGER_HOST -- docker service rm "kstreams-test_source" || true
ssh -q $MANAGER_HOST -- docker service rm "kstreams-test_nexmark" || true
ssh -q $MANAGER_HOST -- docker stack rm kstreams-test || true

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
ssh -q $MANAGER_HOST -- docker stack deploy \
    -c ~/docker-compose-base.yml -c ~/docker-compose.yml kstreams-test
sleep 80

FIRST_BROKER_CONTAINER_IP=""
for HOST in $ALL_BROKER_HOSTS; do
    container_id=$(ssh -q $HOST -oStrictHostKeyChecking=no -- "docker ps -f name=kstreams-test_broker --format "{{.ID}}"")
    docker_ip_outside=$(ssh -q $HOST -oStrictHostKeyChecking=no -- "docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $container_id")
    docker_ip_inside=$(ssh -q $HOST -oStrictHostKeyChecking=no -- "docker exec $container_id hostname -i")
    if [ $docker_ip_inside != $docker_ip_outside ]; then
        echo "container $HOST ip observed from outside: $docker_ip_outside, from inside: $docker_ip_inside are different"
        exit -1
    fi
    if [ $HOST = $FIRST_BROKER ]; then
        FIRST_BROKER_CONTAINER_IP=$docker_ip_outside
    fi
done

rm -rf $EXP_DIR
mkdir -p $EXP_DIR
ssh -q $MANAGER_HOST -- cat /proc/cmdline >>$EXP_DIR/kernel_cmdline
ssh -q $MANAGER_HOST -- uname -a >>$EXP_DIR/kernel_version

SRC_DURATION=$(expr $DURATION + 10)
ssh -q $MANAGER_HOST -- "docker service create \
    --mount type=bind,source=/mnt/efs/workspace/sharedlog-stream,destination=/src \
    --constraint node.labels.app_node==true --network kstreams-test_default \
    --name kstreams-test_source --restart-condition none --replicas=$NUM_SRC_INSTANCE \
    --replicas-max-per-node=1 --hostname='source-{{.Task.Slot}}' ubuntu:focal /src/bin/nexmark_genevents_kafka \
    -broker $FIRST_BROKER_CONTAINER_IP:9092 -duration ${SRC_DURATION} -npar 4 -serde $SERDE" -srcIns $NUM_SRC_INSTANCE

sleep 10

ssh -q $MANAGER_HOST -- "docker service create \
    --mount type=bind,source=/mnt/efs/workspace/nexmark/nexmark-kafka-streams,destination=/src \
    --constraint node.labels.app_node==true --env BOOTSTRAP_SERVER_CONFIG=$FIRST_BROKER_CONTAINER_IP:9092 \
    --network kstreams-test_default --restart-condition none --replicas=$NUM_INSTANCE \
    --replicas-max-per-node=1 --hostname='nexmark-{{.Task.Slot}}' \
    --name kstreams-test_nexmark openjdk:11.0.12-jre-slim-buster \
    bash -c 'java -cp /src/build/libs/nexmark-kafka-streams-0.2-SNAPSHOT-uber.jar com.github.nexmark.kafka.queries.RunQuery --name $NAME --serde $SERDE --duration $DURATION --conf  /src/workload_config/${NAME}.properties'"

sleep $DURATION

$HELPER_SCRIPT collect-container-logs --base-dir=$BASE_DIR --log-path=$EXP_DIR/logs
