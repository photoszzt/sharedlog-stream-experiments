#!/bin/bash
set -euo pipefail
set -x

if [ "$1" = "" ]; then
    echo "should provide exp_dir"
    exit 1
fi

EXP_DIR=""
DURATION=""
EVENTS_NUM=""
NUM_PARTITION=""
NUM_PRODUCER=""
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
    --duration*)
        if [[ "$1" != *=* ]]; then shift; fi
        DURATION="${1#*=}"
        ;;
    --events_num*)
        if [[ "$1" != *=* ]]; then shift; fi
        EVENTS_NUM="${1#*=}"
        ;;
    --npar*)
        if [[ "$1" != *=* ]]; then shift; fi
        NUM_PARTITION="${1#*=}"
        ;;
    --nprod*)
        if [[ "$1" != *=* ]]; then shift; fi
        NUM_PRODUCER="${1#*=}"
        ;;
    --payload*)
        if [[ "$1" != *=* ]]; then shift; fi
        PAYLOAD="${1#*=}"
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
    --help | -h)
        printf -- "--exp_dir <exp_dir> required\n"
        printf -- "--duration <duration in sec>\n"
        printf -- "--events_num <number of events>\n"
        exit 0
        ;;
    *)
        printf >&2 "Error: invalid argument"
        exit 1
        ;;
    esac
    shift
done

DURATION=${DURATION:-60}
echo "exp_dir: $EXP_DIR, num_producer: $NUM_PRODUCER, duration: $DURATION, num partition: $NUM_PARTITION, payload: $PAYLOAD"

if [[ "$EVENTS_NUM" = "" ]]; then
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


echo "exp_dir: $EXP_DIR, num_producer: $NUM_PRODUCER, duration: $DURATION, num partition: $NUM_PARTITION, payload: $PAYLOAD, warm_duration: $WARM_DURATION, warm_events: $WARM_EVENTS, tps: $TPS"

HELPER_SCRIPT=/mnt/efs/workspace/research-helper-scripts/microservice_helper
BASE_DIR=$(realpath $(dirname $0))
SRC_DIR=/mnt/efs/workspace/sharedlog-stream
MANAGER_HOST=$($HELPER_SCRIPT get-docker-manager-host --base-dir=$BASE_DIR)
CLIENT_HOST=$($HELPER_SCRIPT get-client-host --base-dir=$BASE_DIR)
ENTRY_HOST=$($HELPER_SCRIPT get-service-host --base-dir=$BASE_DIR --service=faas-gateway)

./run_once_common.sh

rm -rf $EXP_DIR
mkdir -p $EXP_DIR

ssh -q $MANAGER_HOST -- cat /proc/cmdline >>$EXP_DIR/kernel_cmdline
ssh -q $MANAGER_HOST -- uname -a >>$EXP_DIR/kernel_version

ssh -q $CLIENT_HOST -- $SRC_DIR/bin/sharedlog_bench_client \
    -faas_gateway $ENTRY_HOST:8080 -duration ${DURATION} -events_num ${EVENTS_NUM} -serde msgp \
    -npar ${NUM_PARTITION} -nprod ${NUM_PRODUCER} \
    -payload /src/data/${PAYLOAD} -tps $TPS -warmup_events $WARM_EVENTS 
    -warm_time $WARM_DURATION \ >$EXP_DIR/results.log 2>&1

$HELPER_SCRIPT collect-container-logs --base-dir=$BASE_DIR --log-path=$EXP_DIR/logs
