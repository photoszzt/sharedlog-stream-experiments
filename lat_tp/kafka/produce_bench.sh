#!/bin/bash

EXP_DIR=""
NUM_PRODUCER=""
DURATION=""
NUM_EVENTS=""
NUM_PARTITION=""
PAYLOAD=""

while [ $# -gt 0 ]; do
    case "$1" in
        --exp_dir*)
            if [[ "$1" != *=* ]]; then shift; fi
            EXP_DIR="${1#*=}"
            ;;
        --nprod*)
            if [[ "$1" != *=* ]]; then shift; fi
            NUM_PRODUCER="${1#*=}"
            ;;
        --duration*)
            if [[ "$1" != *=* ]]; then shift; fi
            DURATION="${1#*=}"
            ;;
        --events_num*)
            if [[ "$1" != *=* ]]; then shift; fi
            NUM_EVENTS="${1#*=}"
            ;;
        --num_par*)
            if [[ "$1" != *=* ]]; then shift; fi
            NUM_PARTITION="${1#*=}"
            ;;
        --payload*)
            if [[ "$1" != *=* ]]; then shift; fi
            PAYLOAD="${1#*=}"
            ;;
        --help|-h)
            printf -- "--exp_dir <exp_dir> required\n"
            printf -- "--nprod <num> required\n"
            printf -- "--duration <duration in sec>\n"
            printf -- "--events_num <number of events>\n"
            printf -- "--num_par <num partition>\n"
            exit 0
            ;;
        *)
            >&2 printf "Error: invalid argument"
            exit 1
            ;;
    esac
    shift
done

DURATION=${DURATION:-60}

if [[ "$NUM_EVENTS" = "" ]]; then
    echo "need to specify number of events"
    exit 1
fi
if [[ "$EXP_DIR" = "" ]]; then
    echo "need to specify experiment dir"
    exit 1
fi
if [[ "$NUM_PRODUCER" = "" ]]; then
    echo "need to specify number of producer"
    exit 1
fi
if [[ "$NUM_PARTITION" = "" ]]; then
    echo "need to specify number of partition"
    exit 1
fi
if [[ "$PAYLOAD" = "" ]]; then
    echo "need to specify the payload"
    exit 1
fi

echo "exp_dir: $EXP_DIR, num_producer: $NUM_PRODUCER, duration: $DURATION, num partition: $NUM_PARTITION, payload: $PAYLOAD"

BASE_DIR=`realpath $(dirname $0)`
HELPER_SCRIPT=/mnt/efs/workspace/research-helper-scripts/microservice_helper

MANAGER_HOST=`$HELPER_SCRIPT get-docker-manager-host --base-dir=$BASE_DIR`

scp -q $BASE_DIR/docker-compose-base.yml $MANAGER_HOST:~
$HELPER_SCRIPT generate-docker-compose --base-dir=$BASE_DIR
scp -q $BASE_DIR/docker-compose.yml $MANAGER_HOST:~

ssh -q $MANAGER_HOST -- docker service rm "kstreams-test_prod" || true
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

ssh -q $MANAGER_HOST -- "docker service create \
    --mount type=bind,source=/mnt/efs/workspace/sharedlog-stream,destination=/src \
    --constraint node.labels.app_node==true --network kstreams-test_default \
    --name kstreams-test_prod --restart-condition none --replicas=$NUM_PRODUCER \
    --replicas-max-per-node=1 --hostname='prod-{{.Task.Slot}}' ubuntu:focal /src/bin/kafka_produce_bench \
    -broker $FIRST_BROKER_CONTAINER_IP:9092 -duration ${DURATION} -events_num ${NUM_EVENTS} -npar ${NUM_PARTITION} \
    -payload /src/data/$PAYLOAD

sleep $DURATION

$HELPER_SCRIPT collect-container-logs --base-dir=$BASE_DIR --log-path=$EXP_DIR/logs
