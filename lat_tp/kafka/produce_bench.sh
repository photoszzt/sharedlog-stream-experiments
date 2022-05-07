#!/bin/bash
set -x

EXP_DIR=""
NUM_PRODUCER=""
NUM_CONSUMER=""
DURATION=""
NUM_EVENTS=""
NUM_PARTITION=""
PAYLOAD=""
WARM_DURATION=""
WARM_EVENTS=""
TPS=""

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
        --ncon*)
            if [[ "$1" != *=* ]]; then shift; fi
            NUM_CONSUMER="${1#*=}"
            ;;
        --duration*)
            if [[ "$1" != *=* ]]; then shift; fi
            DURATION="${1#*=}"
            ;;
        --warm_duration*)
            if [[ "$1" != *=* ]]; then shift; fi
            WARM_DURATION="${1#*=}"
            ;;
        --warm_events*)
            if [[ "$1" != *=* ]]; then shift; fi
            WARM_EVENTS="${1#*=}"
            ;;
        --tps*)
            if [[ "$1" != *=* ]]; then shift; fi
            TPS="${1#*=}"
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
            printf -- "--ncon <num> required\n"
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
if [[ "$NUM_CONSUMER" = "" ]]; then
    echo "need to specify number of consumer"
    exit 1
fi
if [[ "$PAYLOAD" = "" ]]; then
    echo "need to specify the payload"
    exit 1
fi
if [[ "$WARM_EVENTS" = "" ]]; then
    echo "need to specify number of warmup events"
    exit 1
fi
if [[ "$WARM_DURATION" = "" ]]; then
    echo "need to specify warmup duration"
    exit 1
fi
if [[ "$TPS" = "" ]]; then
    echo "need to specify tps"
    exit 1
fi

echo "exp_dir: $EXP_DIR, num_producer: $NUM_PRODUCER, num_consumer: $NUM_CONSUMER, duration: $DURATION, num partition: $NUM_PARTITION, payload: $PAYLOAD, warm_duration: $WARM_DURATION, warm_events: $WARM_EVENTS, tps: $TPS"

BASE_DIR=`realpath $(dirname $0)`
HELPER_SCRIPT=/mnt/efs/workspace/research-helper-scripts/microservice_helper

MANAGER_HOST=`$HELPER_SCRIPT get-docker-manager-host --base-dir=$BASE_DIR`
CLIENT_HOST=$($HELPER_SCRIPT get-client-host --base-dir=$BASE_DIR)

scp -q $BASE_DIR/docker-compose-base.yml $MANAGER_HOST:~
$HELPER_SCRIPT generate-docker-compose --base-dir=$BASE_DIR
scp -q $BASE_DIR/docker-compose.yml $MANAGER_HOST:~

ssh -q $MANAGER_HOST -- docker service rm "kstreams-test_produce" || true
ssh -q $MANAGER_HOST -- docker service rm "kstreams-test_consume" || true
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

CONSUME_DURATION=$(expr ${DURATION} + 5)
ssh -q $MANAGER_HOST -- "docker service create \
    --mount type=bind,source=/mnt/efs/workspace/sharedlog-stream,destination=/src \
    --constraint node.labels.consume_node==true --network kstreams-test_default \
    --name kstreams-test_consume --restart-condition none --replicas=$NUM_CONSUMER \
    --replicas-max-per-node=1 --publish published=8090,target=8090 ubuntu:focal /src/bin/kafka_consume_bench \
    -broker $FIRST_BROKER_CONTAINER_IP:9092 -duration ${CONSUME_DURATION} -events_num ${NUM_EVENTS} \
    -warmup_time ${WARM_DURATION} -warmup_events ${WARM_EVENTS}" &

ssh -q $MANAGER_HOST -- "docker service create \
    --mount type=bind,source=/mnt/efs/workspace/sharedlog-stream,destination=/src \
    --constraint node.labels.produce_node==true --network kstreams-test_default \
    --name kstreams-test_produce --restart-condition none --replicas=$NUM_PRODUCER \
    --replicas-max-per-node=1 --publish published=8080,target=8080 ubuntu:focal /src/bin/kafka_produce_bench \
    -broker $FIRST_BROKER_CONTAINER_IP:9092 -duration ${DURATION} -events_num ${NUM_EVENTS} -npar ${NUM_PARTITION} \
    -payload /src/data/$PAYLOAD -tps $TPS"

sleep 10

PRODUCE_HOSTS=$($HELPER_SCRIPT get-machine-with-label --machine-label produce_node)
CONSUME_HOSTS=$($HELPER_SCRIPT get-machine-with-label --machine-label consume_node)

pids=()
i=0
for HOST in $PRODUCE_HOSTS; do
    ssh -q $CLIENT_HOST -- "curl $HOST:8080/produce" &
    pids[$i]=$!
    i=$(expr $i + 1)
done

for HOST in $CONSUME_HOSTS; do
    ssh -q $CLIENT_HOST -- "curl $HOST:8090/consume" &
    pids[$i]=$!
    i=$(expr $i + 1)
done

for pid in ${pids[*]}; do
    wait $pid
done

$HELPER_SCRIPT collect-container-logs --base-dir=$BASE_DIR --log-path=$EXP_DIR/logs
