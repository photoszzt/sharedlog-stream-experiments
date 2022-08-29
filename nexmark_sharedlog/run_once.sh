#!/bin/bash
set -x

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
SRC_FLUSH_MS=""
NUM_WORKER=""

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
        --flushms*)
            if [[ "$1" != *=* ]]; then shift; fi
            FLUSH_MS="${1#*=}"
            ;;
        --src_flushms*)
            if [[ "$1" != *=* ]]; then shift; fi
            SRC_FLUSH_MS="${1#*=}"
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


echo "app: ${APP_NAME}, exp_dir: ${EXP_DIR}, guarantee: ${GUA}, duration: ${DURATION}, \
    events_num: ${EVENTS_NUM}, tps: ${TPS}, warmup time: ${WARM_DURATION}, flushms: ${FLUSH_MS}, \
    src_flushms: ${SRC_FLUSH_MS}, num_worker: ${NUM_WORKER}"

BASE_DIR=$(realpath $(dirname $0))
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
WORKSPACE_DIR=$(realpath $SCRIPT_DIR/../../)
HELPER_SCRIPT=$($WORKSPACE_DIR/research-helper-scripts/microservice_helper)
SRC_DIR=$WORKSPACE_DIR/sharedlog-stream
MANAGER_HOST=$($HELPER_SCRIPT get-docker-manager-host --base-dir=$BASE_DIR)
CLIENT_HOST=$($HELPER_SCRIPT get-client-host --base-dir=$BASE_DIR)
ENTRY_HOST=$($HELPER_SCRIPT get-service-host --base-dir=$BASE_DIR --service=faas-gateway)

./run_once_common.sh

rm -rf $EXP_DIR
mkdir -p $EXP_DIR

ssh -q $MANAGER_HOST -- cat /proc/cmdline >>$EXP_DIR/kernel_cmdline
ssh -q $MANAGER_HOST -- uname -a >>$EXP_DIR/kernel_version

ssh -q $CLIENT_HOST -- $SRC_DIR/bin/nexmark_client -app_name ${APP_NAME} \
    -faas_gateway $ENTRY_HOST:8080 -duration ${DURATION} -serde msgp \
    -guarantee $GUA -comm_everyMS ${FLUSH_MS} -flushms ${FLUSH_MS} \
    -src_flushms ${SRC_FLUSH_MS} -events_num ${EVENTS_NUM} \
    -wconfig $SRC_DIR/workload_config/${NUM_WORKER}_ins/${APP_NAME}.json \
    -stat_dir /home/ubuntu/${APP_NAME}/${EXP_DIR}/stats -waitForLast=true \
    -tps $TPS -warmup_time $WARM_DURATION >$EXP_DIR/results.log 2>&1

ssh -q $CLIENT_HOST -- "/mnt/efs/experiments/nexmark_sharedlog/zip_files.sh /home/ubuntu/${APP_NAME}/${EXP_DIR}/stats"

scp -r $CLIENT_HOST:/home/ubuntu/${APP_NAME}/${EXP_DIR}/stats ${EXP_DIR}

# $HELPER_SCRIPT collect-func-output --base-dir=$BASE_DIR --log-path=$EXP_DIR/logs
$HELPER_SCRIPT collect-container-logs --base-dir=$BASE_DIR --log-path=$EXP_DIR/logs
