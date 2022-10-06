#!/bin/bash
set -x

NAME=""
EXP_DIR=""
NUM_INSTANCE=""
NUM_SRC_INSTANCE=""
SERDE=""
DURATION=""
NUM_EVENTS=""
WARM_DURATION=""
TPS=""
FLUSH_MS=""
SRC_FLUSH_MS=""
GUARANTEE=""
DISABLE_CACHE=""

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
    --warm_duration*)
        if [[ "$1" != *=* ]]; then shift; fi
        WARM_DURATION="${1#*=}"
        ;;
    --tps*)
        if [[ "$1" != *=* ]]; then shift; fi
        TPS="${1#*=}"
        ;;
    --serde*)
        if [[ "$1" != *=* ]]; then shift; fi
        SERDE="${1#*=}"
        ;;
    --duration*)
        if [[ "$1" != *=* ]]; then shift; fi
        DURATION="${1#*=}"
        ;;
    --nevents*)
        if [[ "$1" != *=* ]]; then shift; fi
        NUM_EVENTS="${1#*=}"
        ;;
    --flushms*)
        if [[ "$1" != *=* ]]; then shift; fi
        FLUSH_MS="${1#*=}"
        ;;
    --src_flushms*)
        if [[ "$1" != *=* ]]; then shift; fi
        SRC_FLUSH_MS="${1#*=}"
        ;;
    --gua*)
        if [[ "$1" != *=* ]]; then shift; fi
        GUARANTEE="${1#*=}"
        ;;
    --disable_cache*)
        if [[ "$1" != *=* ]]; then shift; fi
        DISABLE_CACHE="${1#*=}"
        ;;
    --help | -h)
        printf -- "--app <appname> one of q1,q2,q3,q4,q5,q6,q7,q8\n"
        printf -- "--exp_dir <exp_dir> required\n"
        printf -- "--nins <nins> number of instance\n"
        printf -- "--nsrc <nsrc> number of source\n"
        printf -- "--serde <json or msgp>\n"
        printf -- "--duration <duration in sec>\n"
        printf -- "--warm_duration <duration in sec>\n"
        printf -- "--tps <events per sec>\n"
        printf -- "--flushms <flush interval in ms>\n"
        printf -- "--gua <guarantee; alo or eo>\n"
	printf -- "--disable_cache <true or false>\n"
        exit 0
        ;;
    *)
        printf >&2 "Error: invalid argument"
        exit 1
        ;;
    esac
    shift
done

if [[ "$EXP_DIR" = "" ]] || [[ "$NUM_INSTANCE" = "" ]] || [[ "$NAME" = "" ]]; then
    echo "should provide app name, exp_dir and number of instance"
    exit 1
fi

if [[ "$NUM_EVENTS" = "" ]]; then
    echo "should provide num events"
    exit 1
fi

if [[ "$SERDE" = "" ]]; then
    echo "should provide serde"
    exit 1
fi
if [[ "$NUM_SRC_INSTANCE" = "" ]]; then
    echo "should provide num src instance"
    exit 1
fi
if [[ "$DURATION" = "" ]]; then
    echo "should provide duration"
    exit 1
fi

if [[ "$TPS" = "" ]]; then
    echo "should provide tps"
    exit 1
fi
if [[ "$WARM_DURATION" = "" ]]; then
    echo "should provide warm duration"
    exit 1
fi

if [[ "$FLUSH_MS" = "" ]]; then
    echo "should provide flushms"
    exit 1
fi
if [[ "$SRC_FLUSH_MS" = "" ]]; then
    echo "should provide src flushms"
    exit 1
fi

if [[ "$GUARANTEE" = "" ]]; then
    echo "should provide guarantee"
    exit 1
fi

CACHE_ARG=""

if [[ "$DISABLE_CACHE" = "true" ]]; then
	CACHE_ARG="--disable_cache"
fi

echo "app: $NAME, exp_dir: $EXP_DIR, num_instance: $NUM_INSTANCE, num events: $NUM_EVENTS, \
	num_src: $NUM_SRC_INSTANCE, serde: $SERDE, duration: $DURATION, tps: $TPS, \
	warm duration: $WARM_DURATION, flushMs: $FLUSH_MS, guarantee: $GUARANTEE, \
	disable_cache: ${DISABLE_CACHE}, cache_arg: ${CACHE_ARG}, src_flush_ms: ${SRC_FLUSH_MS}"

BASE_DIR=$(realpath $(dirname $0))
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
HELPER_SCRIPT=$(realpath $SCRIPT_DIR/../../research-helper-scripts/microservice_helper)
WORKSPACE_DIR=$(realpath $SCRIPT_DIR/../../)

MANAGER_HOST=$($HELPER_SCRIPT get-docker-manager-host --base-dir=$BASE_DIR)
CLIENT_HOST=$($HELPER_SCRIPT get-client-host --base-dir=$BASE_DIR)

scp -q $BASE_DIR/docker-compose-base.yml $MANAGER_HOST:~
$HELPER_SCRIPT generate-docker-compose --base-dir=$BASE_DIR
scp -q $BASE_DIR/docker-compose.yml $MANAGER_HOST:~

ssh -q $MANAGER_HOST -oStrictHostKeyChecking=no -- docker service rm "kstreams-test_source" || true
ssh -q $MANAGER_HOST -oStrictHostKeyChecking=no -- docker service rm "kstreams-test_nexmark" || true
for ((i=0; i<$NUM_SRC_INSTANCE; i++)); do
    ssh -q $MANAGER_HOST -- docker service rm "kstreams-test_source-${i}" || true
done
for ((i=0; i<$NUM_INSTANCE; i++)); do
    ssh -q $MANAGER_HOST -- docker service rm "kstreams-test_nexmark-${i}" || true
done
ssh -q $MANAGER_HOST -- docker stack rm kstreams-test || true

sleep 40

PROMETHEUS_HOST=$($HELPER_SCRIPT get-machine-with-label --machine-label=prometheus_node)
ssh -q $PROMETHEUS_HOST -oStrictHostKeyChecking=no -- \
    "sudo rm -rf /mnt/storage/prometheus && sudo mkdir /mnt/storage/prometheus && sudo chown \
    ubuntu:ubuntu /mnt/storage/prometheus && sudo chmod -R 777 /mnt/storage/prometheus"

ALL_BROKER_HOSTS=$($HELPER_SCRIPT get-machine-with-label --machine-label=broker_node)
FIRST_BROKER=""
for HOST in ${ALL_BROKER_HOSTS[@]}; do
    if [ "$FIRST_BROKER" = "" ]; then
        FIRST_BROKER=$HOST
    fi
    ssh -q $HOST -oStrictHostKeyChecking=no -- sudo rm -rf /mnt/storage/kdata
    ssh -q $HOST -oStrictHostKeyChecking=no -- sudo mkdir -p /mnt/storage/kdata
    ssh -q $HOST -oStrictHostKeyChecking=no -- sudo chown ubuntu:ubuntu /mnt/storage/kdata
done

ssh -q $MANAGER_HOST -oStrictHostKeyChecking=no -- docker network rm kstreams-test_default || true
ssh -q $MANAGER_HOST -oStrictHostKeyChecking=no -- docker stack deploy \
    -c ~/docker-compose-base.yml -c ~/docker-compose.yml kstreams-test
sleep 40

FIRST_BROKER_CONTAINER_IP=""
for HOST in ${ALL_BROKER_HOSTS[@]}; do
    echo $HOST
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
echo "first broker container ip: $FIRST_BROKER_CONTAINER_IP"

rm -rf $EXP_DIR
mkdir -p $EXP_DIR
echo "app: $NAME, exp_dir: $EXP_DIR, num_instance: $NUM_INSTANCE, num events: $NUM_EVENTS, num_src: $NUM_SRC_INSTANCE, \
	serde: $SERDE, duration: $DURATION, tps: $TPS, warm duration: $WARM_DURATION, \
	flushMs: $FLUSH_MS, guarantee: ${GUARANTEE}, disable_cache: ${DISABLE_CACHE}, src_flushms: ${SRC_FLUSH_MS}">$EXP_DIR/params

ssh -q $MANAGER_HOST -oStrictHostKeyChecking=no -- cat /proc/cmdline >>$EXP_DIR/kernel_cmdline
ssh -q $MANAGER_HOST -oStrictHostKeyChecking=no -- uname -a >>$EXP_DIR/kernel_version

for ((j=0; j<$NUM_SRC_INSTANCE; j++)); do
    PORT=$(expr 8000 + $j)
    ssh -q $MANAGER_HOST -oStrictHostKeyChecking=no -- "docker service create \
        --mount type=bind,source=$WORKSPACE_DIR/sharedlog-stream,destination=/src \
        --constraint node.labels.source_node==true --network kstreams-test_default \
        --name kstreams-test_source-${j} --restart-condition none --replicas=1 \
        --replicas-max-per-node=1 --hostname=source-${j} --publish mode=host,published=$PORT,target=$PORT \
        --env IID=$j ubuntu:focal /src/bin/nexmark_genevents_kafka \
        -broker $FIRST_BROKER_CONTAINER_IP:9092 -duration ${DURATION} -npar 4 -serde $SERDE \
        -srcIns $NUM_SRC_INSTANCE -events_num $NUM_EVENTS -tps $TPS -port $PORT -flushms $SRC_FLUSH_MS" &
done

for ((k=0; k<$NUM_INSTANCE; k++)); do
    PORT=$(expr 7000 + $k)
    ssh -q $MANAGER_HOST -oStrictHostKeyChecking=no -- "docker service create \
        --mount type=bind,source=$WORKSPACE_DIR/nexmark/nexmark-kafka-streams,destination=/src \
        --mount type=bind,source=$WORKSPACE_DIR/sharedlog-stream-experiments/nexmark_kafka-streams/shared-assets/jmx-exporter,destination=/usr/share/jmx-exporter \
        --constraint node.labels.app_node==true \
        --env BOOTSTRAP_SERVER_CONFIG=$FIRST_BROKER_CONTAINER_IP:9092 \
        --network kstreams-test_default --restart-condition none --replicas=1 \
        --replicas-max-per-node=1 --hostname=nexmark-${k} \
        --name kstreams-test_nexmark-${k} --publish mode=host,published=$PORT,target=$PORT \
        --publish mode=host,published=12345,target=12345 \
        openjdk:11.0.12-jre-slim-buster \
        bash -c 'java -javaagent:/usr/share/jmx-exporter/jmx_prometheus_javaagent-0.16.1.jar=12345:/usr/share/jmx-exporter/kafka_streams.yml \
        -cp /src/build/libs/nexmark-kafka-streams-0.2-SNAPSHOT-uber.jar \
        com.github.nexmark.kafka.queries.RunQuery \
        --name $NAME --serde $SERDE --conf  /src/workload_config/${NAME}.properties \
        --duration $DURATION --port $PORT  \
        --flushms ${FLUSH_MS} --warmup_time ${WARM_DURATION} --guarantee ${GUARANTEE} \
        --stats_dir /tmp/stats ${CACHE_ARG}'" &
done

sleep 20

ALL_SOURCE_HOSTS=$($HELPER_SCRIPT get-machine-with-label --machine-label=source_node)
ALL_APP_HOSTS=$($HELPER_SCRIPT get-machine-with-label --machine-label=app_node)

# for HOST in $ALL_BROKER_HOSTS; do
# 	ssh -q $HOST -oStrictHostKeyChecking=no -- sar -o /home/ubuntu/sar_st 1 >/dev/null 2>&1 &
# done
# 
# for HOST in $ALL_SOURCE_HOSTS; do
# 	ssh -q $HOST -oStrictHostKeyChecking=no -- sar -o /home/ubuntu/sar_st 1 >/dev/null 2>&1 &
# done
# 
# for HOST in $ALL_APP_HOSTS; do
# 	ssh -q $HOST -oStrictHostKeyChecking=no -- sar -o /home/ubuntu/sar_st 1 >/dev/null 2>&1 &
# done

pids=()
i=0
for ((j=0; j<$NUM_SRC_INSTANCE; j++)); do
    NODE=$(ssh -q $MANAGER_HOST -oStrictHostKeyChecking=no -- "docker service ps --format '{{.Node}}' kstreams-test_source-$j")
    HOST=$(ssh -q $MANAGER_HOST -oStrictHostKeyChecking=no -- "docker node inspect $NODE --format '{{ .Status.Addr }}'")
    PORT=$(expr 8000 + $j)
    ssh -q $CLIENT_HOST -oStrictHostKeyChecking=no -- "curl $HOST:$PORT/kproduce" &
    pids[$i]=$!
    i=$(expr $i + 1)
done

for ((jj=0; jj<$NUM_INSTANCE; jj++)); do
    NODE=$(ssh -q $MANAGER_HOST -oStrictHostKeyChecking=no -- "docker service ps --format '{{.Node}}' kstreams-test_nexmark-${jj}")
    HOST=$(ssh -q $MANAGER_HOST -oStrictHostKeyChecking=no -- "docker node inspect $NODE --format '{{ .Status.Addr }}'")
    PORT=$(expr 7000 + ${jj})
    ssh -q $CLIENT_HOST -oStrictHostKeyChecking=no -- "curl $HOST:$PORT/run" &
    pids[$i]=$!
    i=$(expr $i + 1)
done

for pid in ${pids[*]}; do
    wait $pid
done

# for HOST in $ALL_BROKER_HOSTS; do
# 	ssh -q $HOST -oStrictHostKeyChecking=no -- pkill sar
# 	mkdir -p $EXP_DIR/broker_sar/$HOST
# 	scp $HOST:/home/ubuntu/sar_st $EXP_DIR/broker_sar/$HOST
# 	ssh -q $HOST -oStrictHostKeyChecking=no -- rm /home/ubuntu/sar_st
# done
# 
# for HOST in $ALL_SOURCE_HOSTS; do
# 	ssh -q $HOST -oStrictHostKeyChecking=no -- pkill sar
# 	mkdir -p $EXP_DIR/source_sar/$HOST
# 	scp $HOST:/home/ubuntu/sar_st $EXP_DIR/source_sar/$HOST
# 	ssh -q $HOST -oStrictHostKeyChecking=no -- rm /home/ubuntu/sar_st
# done
# 
# for HOST in $ALL_APP_HOSTS; do
# 	ssh -q $HOST -oStrictHostKeyChecking=no -- pkill sar
# 	mkdir -p $EXP_DIR/app_sar/$HOST
# 	scp $HOST:/home/ubuntu/sar_st $EXP_DIR/app_sar/$HOST
# 	ssh -q $HOST -oStrictHostKeyChecking=no -- rm /home/ubuntu/sar_st
# done

ssh -q $PROMETHEUS_HOST -oStrictHostKeyChecking=no -- curl -XPOST http://localhost:9090/api/v1/admin/tsdb/snapshot
scp -r $PROMETHEUS_HOST:/mnt/storage/prometheus/snapshots $EXP_DIR/snapshots

mkdir $EXP_DIR/broker_netstats
for HOST in ${ALL_BROKER_HOSTS[@]}; do
	NETDEVS=$(ssh -q $HOST -oStrictHostKeyChecking=no -- ls /sys/class/net | grep -e ^e)
	for NETDEV in $NETDEVS; do
		ssh -q $HOST -oStrictHostKeyChecking=no -- ethtool -S $NETDEV >>$EXP_DIR/broker_netstats/$HOST
	done
done

mkdir $EXP_DIR/source_netstats
for HOST in ${ALL_SOURCE_HOSTS[@]}; do
	NETDEVS=$(ssh -q $HOST -oStrictHostKeyChecking=no -- ls /sys/class/net | grep -e ^e)
	for NETDEV in $NETDEVS; do
		ssh -q $HOST -oStrictHostKeyChecking=no -- ethtool -S $NETDEV >>$EXP_DIR/source_netstats/$HOST
	done
done

mkdir $EXP_DIR/app_netstats
for HOST in ${ALL_SOURCE_HOSTS[@]}; do
	NETDEVS=$(ssh -q $HOST -oStrictHostKeyChecking=no -- ls /sys/class/net | grep -e ^e)
	for NETDEV in $NETDEVS; do
		ssh -q $HOST -oStrictHostKeyChecking=no -- ethtool -S $NETDEV >>$EXP_DIR/app_netstats/$HOST
	done
done

$HELPER_SCRIPT collect-container-logs --base-dir=$BASE_DIR --log-path=$EXP_DIR/logs
