#!/bin/bash
set -x

if [ "$1" = "" ]; then
    echo "should provide exp_dir"
    exit 1
fi

EXP_DIR=""
APP_NAME=""
TRAN=""
DURATION=""
EVENTS_NUM=""
USE_MONGODB=""
TPS=""
WARM_DURATION=""
FLUSH_MS=""

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
        --tran*)
            if [[ "$1" != *=* ]]; then shift; fi
            TRAN="${1#*=}"
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
        --use_mongodb*)
            if [[ "$1" != *=* ]]; then shift; fi
            USE_MONGODB="${1#*=}"
            ;;
        --flushms*)
            if [[ "$1" != *=* ]]; then shift; fi
            FLUSH_MS="${1#*=}"
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

TRAN=${TRAN:-false}
DURATION=${DURATION:-60}
USE_MONGODB=${USE_MONGODB:-false}

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
if [[ "FLUSH_MS" = "" ]]; then
    echo "need to specify flushms"
    exit 1
fi
if [[ "APP_NAME" = "" ]]; then
    echo "need to specify app name"
    exit 1
fi
if [[ "EXP_DIR" = "" ]]; then
    echo "need to specify experiment dir"
    exit 1
fi

echo "app: ${APP_NAME}, exp_dir: ${EXP_DIR}, tran: ${TRAN}, duration: ${DURATION}, events_num: ${EVENTS_NUM}, use_mongodb: ${USE_MONGODB}, tps: ${TPS}, warmup time: ${WARM_DURATION}, flushms: ${FLUSH_MS}"

HELPER_SCRIPT=/mnt/efs/workspace/research-helper-scripts/microservice_helper
BASE_DIR=$(realpath $(dirname $0))
SRC_DIR=/mnt/efs/workspace/sharedlog-stream
MANAGER_HOST=$($HELPER_SCRIPT get-docker-manager-host --base-dir=$BASE_DIR)
CLIENT_HOST=$($HELPER_SCRIPT get-client-host --base-dir=$BASE_DIR)
ENTRY_HOST=$($HELPER_SCRIPT get-service-host --base-dir=$BASE_DIR --service=faas-gateway)

if [ "${USE_MONGODB}" = "true" ]; then
    ./run_once_mongodb.sh
else
    ./run_once_common.sh
fi

rm -rf $EXP_DIR
mkdir -p $EXP_DIR

ssh -q $MANAGER_HOST -- cat /proc/cmdline >>$EXP_DIR/kernel_cmdline
ssh -q $MANAGER_HOST -- uname -a >>$EXP_DIR/kernel_version

if [ "$USE_MONGODB" = "true" ]; then
    if [ "$TRAN" = "true" ]; then
        ssh -q $CLIENT_HOST -- $SRC_DIR/bin/nexmark_client -app_name ${APP_NAME} \
            -faas_gateway $ENTRY_HOST:8080 -duration ${DURATION} -serde msgp \
            -tran -comm_every_niter 0 -comm_everyMS ${FLUSH_MS} --flushms ${FLUSH_MS} -events_num ${EVENTS_NUM} \
            -tab_type mongodb -mongo_addr mongodb://mongodb-0:27017,mongodb-1:27017,mongodb-2:27017/?replicaSet=replicaset \
            -wconfig $SRC_DIR/workload_config/${APP_NAME}.json -tps $TPS -warmup_time $WARM_DURATION \
            -stat_dir /home/ubuntu/${EXP_DIR}/stats >$EXP_DIR/results.log 2>&1
    else
        ssh -q $CLIENT_HOST -- $SRC_DIR/bin/nexmark_client -app_name ${APP_NAME} \
            -faas_gateway $ENTRY_HOST:8080 -duration ${DURATION} --flushms ${FLUSH_MS} -serde msgp -events_num ${EVENTS_NUM} \
            -tab_type mongodb -mongo_addr mongodb://mongodb-0:27017,mongodb-1:27017,mongodb-2:27017/?replicaSet=replicaset \
            -wconfig $SRC_DIR/workload_config/${APP_NAME}.json -tps $TPS -warmup_time $WARM_DURATION \
            -stat_dir /home/ubuntu/${EXP_DIR}/stats >$EXP_DIR/results.log 2>&1
    fi
else
    if [ "$TRAN" = "true" ]; then
        ssh -q $CLIENT_HOST -- $SRC_DIR/bin/nexmark_client -app_name ${APP_NAME} \
            -faas_gateway $ENTRY_HOST:8080 -duration ${DURATION} -serde msgp \
            -tran -comm_every_niter 0 -comm_everyMS ${FLUSH_MS} -flushms ${FLUSH_MS} -events_num ${EVENTS_NUM} \
            -wconfig $SRC_DIR/workload_config/${APP_NAME}.json \
            -stat_dir /home/ubuntu/${APP_NAME}/${EXP_DIR}/stats \
            -tps $TPS -warmup_time $WARM_DURATION >$EXP_DIR/results.log 2>&1
    else
        ssh -q $CLIENT_HOST -- $SRC_DIR/bin/nexmark_client -app_name ${APP_NAME} \
            -faas_gateway $ENTRY_HOST:8080 -duration ${DURATION} --flushms ${FLUSH_MS} -events_num ${EVENTS_NUM} -serde msgp \
            -wconfig $SRC_DIR/workload_config/${APP_NAME}.json -tps $TPS -warmup_time $WARM_DURATION \
            -stat_dir /home/ubuntu/${APP_NAME}/${EXP_DIR}/stats >$EXP_DIR/results.log 2>&1
    fi
fi

ssh -q $CLIENT_HOST -- "/mnt/efs/experiments/nexmark_sharedlog/zip_files.sh /home/ubuntu/${APP_NAME}/${EXP_DIR}/stats"

scp -r $CLIENT_HOST:/home/ubuntu/${APP_NAME}/${EXP_DIR}/stats ${EXP_DIR}

$HELPER_SCRIPT collect-container-logs --base-dir=$BASE_DIR --log-path=$EXP_DIR/logs
