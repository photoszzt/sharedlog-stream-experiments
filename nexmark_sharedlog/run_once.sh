#!/bin/bash
if [ "$1" = "" ]; then
    echo "should provide exp_dir"
    exit 1
fi

EXP_DIR=""
APP_NAME=""
GUA=""
DURATION=""
EVENTS_NUM=""
TPS=""
WARM_DURATION=""
FLUSH_MS=""
COMM_EVERY_MS=""
SRC_FLUSH_MS=""
NUM_WORKER=""
FAIL=""
SNAPSHOT_S=0
CONFIG_SUBPATH=""
BUF_MAX_SIZE=$(expr 128 \* 1024)
EXTRA_BYTES=0

while [ $# -gt 0 ]; do
    case "$1" in
        --app*)
            if [[ "$1" != *=* ]]; then shift; fi
            APP_NAME="${1#*=}"
            ;;
        --exp_dir*)
            if [[ "$1" != *=* ]]; then shift; fi
            EXP_DIR="${1#*=}"
            ;;
        --gua*)
            if [[ "$1" != *=* ]]; then shift; fi
            GUA="${1#*=}"
            ;;
        --nworker*)
            if [[ "$1" != *=* ]]; then shift; fi
            NUM_WORKER="${1#*=}"
            ;;
        --duration*)
            if [[ "$1" != *=* ]]; then shift; fi
            DURATION="${1#*=}"
            ;;
        --events_num*)
            if [[ "$1" != *=* ]]; then shift; fi
            EVENTS_NUM="${1#*=}"
            ;;
        --warm_duration*)
            if [[ "$1" != *=* ]]; then shift; fi
            WARM_DURATION="${1#*=}"
            ;;
        --tps*)
            if [[ "$1" != *=* ]]; then shift; fi
            TPS="${1#*=}"
            ;;
        --comm_everyMs*)
            if [[ "$1" != *=* ]]; then shift; fi
            COMM_EVERY_MS="${1#*=}"
            ;;
        --flushms*)
            if [[ "$1" != *=* ]]; then shift; fi
            FLUSH_MS="${1#*=}"
            ;;
        --src_flushms*)
            if [[ "$1" != *=* ]]; then shift; fi
            SRC_FLUSH_MS="${1#*=}"
            ;;
        --fail*)
            if [[ "$1" != *=* ]]; then shift; fi
            FAIL="${1#*=}"
            ;;
	    --snapshot_s*)
            if [[ "$1" != *=* ]]; then shift; fi
            SNAPSHOT_S="${1#*=}"
            ;;
	    --config_subpath*)
            if [[ "$1" != *=* ]]; then shift; fi
            CONFIG_SUBPATH="${1#*=}"
            ;;
        --buf_max_size*)
            if [[ "$1" != *=* ]]; then shift; fi
            BUF_MAX_SIZE="${1#*=}"
            ;;
        --extra_bytes*)
            if [[ "$1" != *=* ]]; then shift; fi
            EXTRA_BYTES="${1#*=}"
            ;;
        --help|-h)
            printf -- "--app <appname> one of q1,q2,q3,q5,q7,q8\n"
            printf -- "--exp_dir <exp_dir> required\n"
            printf -- "--tran <true or false>\n"
            printf -- "--duration <duration in sec>\n"
            printf -- "--events_num <number of events>\n"
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

if [[ "$EVENTS_NUM" = "" ]]; then
    echo "need to specify number of events"
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
if [[ "$FLUSH_MS" = "" ]]; then
    echo "need to specify flushms"
    exit 1
fi
if [[ "$SRC_FLUSH_MS" = "" ]]; then
    echo "need to specify src flushms"
    exit 1
fi
if [[ "$APP_NAME" = "" ]]; then
    echo "need to specify app name"
    exit 1
fi
if [[ "$EXP_DIR" = "" ]]; then
    echo "need to specify experiment dir"
    exit 1
fi
if [[ "$NUM_WORKER" = "" ]]; then
    echo "need to specify num worker"
    exit 1
fi
if [[ "$COMM_EVERY_MS" = "" ]]; then
    echo "need to specify commit every ms"
    exit 1
fi


echo "app: ${APP_NAME}, exp_dir: ${EXP_DIR}, guarantee: ${GUA}, duration: ${DURATION}, \
    events_num: ${EVENTS_NUM}, tps: ${TPS}, warmup time: ${WARM_DURATION}, flushms: ${FLUSH_MS}, \
    src_flushms: ${SRC_FLUSH_MS}, num_worker: ${NUM_WORKER}, fail_spec: ${FAIL_SPEC}, \
    snapshot_s: ${SNAPSHOT_S}, buf_max_size: ${BUF_MAX_SIZE}, extra_bytes: ${EXTRA_BYTES}"

SOURCE=${BASH_SOURCE[0]}
while [ -L "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
  SOURCE=$(readlink "$SOURCE")
  [[ $SOURCE != /* ]] && SOURCE=$DIR/$SOURCE # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
SCRIPT_DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )

BASE_DIR=$(realpath $(dirname $0))
WORKSPACE_DIR=$(realpath $SCRIPT_DIR/../../)
HELPER_SCRIPT=$WORKSPACE_DIR/research-helper-scripts/microservice_helper
SRC_DIR=$WORKSPACE_DIR/sharedlog-stream
MANAGER_HOST=$($HELPER_SCRIPT get-docker-manager-host --base-dir=$BASE_DIR)
CLIENT_HOST=$($HELPER_SCRIPT get-client-host --base-dir=$BASE_DIR)
ENTRY_HOST=$($HELPER_SCRIPT get-service-host --base-dir=$BASE_DIR --service=faas-gateway)

./run_once_common.sh

rm -rf $EXP_DIR
mkdir -p $EXP_DIR

ssh -q $MANAGER_HOST -- cat /proc/cmdline >>$EXP_DIR/kernel_cmdline
ssh -q $MANAGER_HOST -- uname -a >>$EXP_DIR/kernel_version
FAIL_SPEC_ARG=""
if [[ "$FAIL" = "true" ]]; then
    FAIL_SPEC_ARG="-fail_spec=$SRC_DIR/workload_config/4node/${NUM_WORKER}_ins/failure_config/${APP_NAME}.json"
fi

ALL_ENGINE_HOSTS=$($HELPER_SCRIPT get-machine-with-label --machine-label=engine_node)
mkdir -p $EXP_DIR/engine_sar/
for HOST in $ALL_ENGINE_HOSTS; do
    SSH_CMD="ssh -q $HOST -oStrictHostKeyChecking=no"
    $SSH_CMD -- 'ls -l /dev/nvme*' >>$EXP_DIR/engine_sar/${HOST}_dev
    $SSH_CMD -- sar -o /home/ubuntu/sar_st 1 >/dev/null 2>&1 &
    $SSH_CMD -- sleep 1 && rm -f /home/ubuntu/docker_stats.txt
    $SSH_CMD -- $SCRIPT_DIR/docker_stats.sh &
done

ALL_SEQUENCER_HOSTS=$($HELPER_SCRIPT get-machine-with-label --machine-label=sequencer_node)
ALL_STORAGE_HOSTS=$($HELPER_SCRIPT get-machine-with-label --machine-label=storage_node)
for HOST in $ALL_SEQUENCER_HOSTS; do
    echo $HOST >> $EXP_DIR/seqhosts
done

mkdir -p $EXP_DIR/storage_sar/
for HOST in $ALL_STORAGE_HOSTS; do
    SSH_CMD="ssh -q $HOST -oStrictHostKeyChecking=no"
    $SSH_CMD -- 'ls -l /dev/nvme*' >>$EXP_DIR/storage_sar/${HOST}_dev
    $SSH_CMD -- sar -o /home/ubuntu/sar_st 1 >/dev/null 2>&1 &
    $SSH_CMD -- 'sync'
done

WCONFIG=$SRC_DIR/workload_config/$CONFIG_SUBPATH
if [[ "$CONFIG_SUBPATH" = "" ]]; then
    WCONFIG=$SRC_DIR/workload_config/4node/${NUM_WORKER}_ins/${APP_NAME}.json
fi

ssh -q $CLIENT_HOST -- $SRC_DIR/bin/nexmark_client -app_name ${APP_NAME} \
    -faas_gateway $ENTRY_HOST:8080 -duration ${DURATION} -serde msgp \
    -guarantee $GUA -comm_everyMS ${COMM_EVERY_MS} -flushms ${FLUSH_MS} \
    -src_flushms ${SRC_FLUSH_MS} -events_num ${EVENTS_NUM} \
    -wconfig $WCONFIG -buf_max_size ${BUF_MAX_SIZE} \
    -stat_dir /home/ubuntu/${APP_NAME}/${EXP_DIR}/stats -waitForLast=true \
    -tps $TPS -warmup_time $WARM_DURATION $FAIL_SPEC_ARG \
    -snapshot_everyS=$SNAPSHOT_S -extraBytes=$EXTRA_BYTES >$EXP_DIR/results.log 2>&1

mkdir -p $EXP_DIR/docker_stats
for HOST in $ALL_STORAGE_HOSTS; do
    SSH_CMD="ssh -q $HOST -oStrictHostKeyChecking=no"
    redis_id=$($SSH_CMD -- docker ps --filter 'name=snapcache' --format '{{.ID}}')
    for id in $redis_id; do
        $SSH_CMD -- docker exec $id redis-cli INFO >$EXP_DIR/docker_stats/${HOST}_${id}_redis_info.txt 2>&1
        $SSH_CMD -- docker exec $id redis-cli MEMORY STATS >$EXP_DIR/docker_stats/${HOST}_${id}_redis_memory_stats.txt 2>&1
        $SSH_CMD -- docker exec $id redis-cli LATENCY HISTOGRAM >$EXP_DIR/docker_stats/${HOST}_${id}_redis_latency_hist.txt 2>&1
    done
done

for HOST in $ALL_ENGINE_HOSTS; do
    SSH_CMD="ssh -q $HOST -oStrictHostKeyChecking=no"
    $SSH_CMD -- pkill sar
    $SSH_CMD -- sync && pkill docker_stats.sh
    mkdir -p $EXP_DIR/engine_sar/$HOST
    scp $HOST:/home/ubuntu/sar_st $EXP_DIR/engine_sar/$HOST
    $SSH_CMD -- rm /home/ubuntu/sar_st
    scp $HOST:/home/ubuntu/docker_stats.txt $EXP_DIR/docker_stats/stats.txt
    mv $EXP_DIR/docker_stats/stats.txt $EXP_DIR/docker_stats/${HOST}_stats.txt
    # cat $EXP_DIR/docker_stats/stats.txt | jq '[inputs]' >> $EXP_DIR/docker_stats/${HOST}_stats.txt
    # rm $EXP_DIR/docker_stats/stats.txt
    $SSH_CMD -- rm /home/ubuntu/stats.txt
done

for HOST in $ALL_STORAGE_HOSTS; do
    SSH_CMD="ssh -q $HOST -oStrictHostKeyChecking=no"
    $SSH_CMD -- pkill sar
    mkdir -p $EXP_DIR/storage_sar/$HOST
    scp $HOST:/home/ubuntu/sar_st $EXP_DIR/storage_sar/$HOST
    $SSH_CMD -- rm /home/ubuntu/sar_st
    $SSH_CMD -- 'df -h' >>$EXP_DIR/storage_sar/${HOST}_disksize
done

mkdir $EXP_DIR/sequencer_netstats
for HOST in $ALL_SEQUENCER_HOSTS; do
    SSH_CMD="ssh -q $HOST -oStrictHostKeyChecking=no"
    NETDEVS=$(ssh -q $HOST -oStrictHostKeyChecking=no -- ls /sys/class/net | grep -e ^e)
    for NETDEV in $NETDEVS; do
        $SSH_CMD -- ethtool -S $NETDEV >>$EXP_DIR/sequencer_netstats/$HOST
    done
done

mkdir $EXP_DIR/engine_netstats
ALL_ENGINE_HOSTS=$($HELPER_SCRIPT get-machine-with-label --machine-label=engine_node)
for HOST in $ALL_ENGINE_HOSTS; do
    SSH_CMD="ssh -q $HOST -oStrictHostKeyChecking=no"
    NETDEVS=$(ssh -q $HOST -oStrictHostKeyChecking=no -- ls /sys/class/net | grep -e ^e)
    for NETDEV in $NETDEVS; do
        $SSH_CMD -- ethtool -S $NETDEV >>$EXP_DIR/engine_netstats/$HOST
    done
done

mkdir $EXP_DIR/storage_netstats
for HOST in $ALL_STORAGE_HOSTS; do
	NETDEVS=$(ssh -q $HOST -oStrictHostKeyChecking=no -- ls /sys/class/net | grep -e ^e)
	for NETDEV in $NETDEVS; do
		ssh -q $HOST -oStrictHostKeyChecking=no -- ethtool -S $NETDEV >>$EXP_DIR/storage_netstats/$HOST
	done
done

ssh -q $CLIENT_HOST -- "$WORKSPACE_DIR/sharedlog-stream-experiments/nexmark_sharedlog/zip_files.sh /home/ubuntu/${APP_NAME}/${EXP_DIR}/stats"
# ssh -q $CLIENT_HOST -- "$WORKSPACE_DIR/sharedlog-stream-experiments/nexmark_sharedlog/zip_files.sh /home/ubuntu/${APP_NAME}/${EXP_DIR}/dump"

scp -r $CLIENT_HOST:/home/ubuntu/${APP_NAME}/${EXP_DIR}/stats ${EXP_DIR}
# scp -r $CLIENT_HOST:/home/ubuntu/${APP_NAME}/${EXP_DIR}/dump ${EXP_DIR}

# $HELPER_SCRIPT collect-func-output --base-dir=$BASE_DIR --log-path=$EXP_DIR/logs
$HELPER_SCRIPT collect-container-logs --base-dir=$BASE_DIR --log-path=$EXP_DIR/logs
