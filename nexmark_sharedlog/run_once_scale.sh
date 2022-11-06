#!/bin/bash
set -x

if [ "$1" = "" ]; then
    echo "should provide exp_dir"
    exit 1
fi

EXP_DIR=""
APP_NAME=""
GUA="epoch"
BEF_DUR=""
AF_DUR=""
EVENTS_NUM=""
TPS=""
FLUSH_MS=""
SRC_FLUSH_MS=""
SNAPSHOT_S=0
SCALE_SCENE=""
INIT_NUM_WORKER=""

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
        --init_nworker*)
            if [[ "$1" != *=* ]]; then shift; fi
            INIT_NUM_WORKER="${1#*=}"
            ;;
        --beforeScale*)
            if [[ "$1" != *=* ]]; then shift; fi
            BEF_DUR="${1#*=}"
            ;;
        --afterScale*)
            if [[ "$1" != *=* ]]; then shift; fi
            AF_DUR="${1#*=}"
            ;;
        --events_num*)
            if [[ "$1" != *=* ]]; then shift; fi
            EVENTS_NUM="${1#*=}"
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
	--snapshot_s*)
            if [[ "$1" != *=* ]]; then shift; fi
            SNAPSHOT_S="${1#*=}"
            ;;
	--scale_scene*)
            if [[ "$1" != *=* ]]; then shift; fi
            SCALE_SCENE="${1#*=}"
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

if [[ "$EVENTS_NUM" = "" ]]; then
    echo "need to specify number of events"
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
if [[ "$SCALE_SCENE" = "" ]]; then
    echo "need to specify scale scene"
    exit 1
fi
if [[ "$INIT_NUM_WORKER" = "" ]]; then
    echo "need to specify num worker"
    exit 1
fi

echo "app: ${APP_NAME}, exp_dir: ${EXP_DIR}, dur before scale: ${BEF_DUR}, dur after scale: ${AF_DUR} \
    events_num: ${EVENTS_NUM}, tps: ${TPS}, flushms: ${FLUSH_MS}, \
    src_flushms: ${SRC_FLUSH_MS}, num_worker: ${INIT_NUM_WORKER}, \
    snapshot_s: ${SNAPSHOT_S}, scale_scene: ${SCALE_SCENE}"

SOURCE=${BASH_SOURCE[0]}
while [ -L "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
  SOURCE=$(readlink "$SOURCE")
  # if $SOURCE was a relative symlink, we need to resolve 
  # it relative to the path where the symlink file was located
  [[ $SOURCE != /* ]] && SOURCE=$DIR/$SOURCE 
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

ALL_ENGINE_HOSTS=$($HELPER_SCRIPT get-machine-with-label --machine-label=engine_node)
for HOST in $ALL_ENGINE_HOSTS; do
	ssh -q $HOST -oStrictHostKeyChecking=no -- sar -o /home/ubuntu/sar_st 1 >/dev/null 2>&1 &
done

ssh -q $CLIENT_HOST -- $SRC_DIR/bin/nexmark_scale -app_name ${APP_NAME} \
    -faas_gateway $ENTRY_HOST:8080 -durBF ${BEF_DUR} -durAF ${AF_DUR} -serde msgp \
    -guarantee epoch -comm_everyMS ${FLUSH_MS} -flushms ${FLUSH_MS} \
    -src_flushms ${SRC_FLUSH_MS} -events_num ${EVENTS_NUM} \
    -wconfig $SRC_DIR/workload_config/${INIT_NUM_WORKER}_ins/${APP_NAME}.json \
    -scconfig $SRC_DIR/scale_to_src_unchanged/${SCALE_SCENE}/${APP_NAME}.json \
    -stat_dir /home/ubuntu/${APP_NAME}/${EXP_DIR}/stats -waitForLast=true \
    -tps $TPS -snapshot_everyS=$SNAPSHOT_S >$EXP_DIR/results.log 2>&1

for HOST in $ALL_ENGINE_HOSTS; do
	ssh -q $HOST -oStrictHostKeyChecking=no -- pkill sar
	mkdir -p $EXP_DIR/engine_sar/$HOST
	scp $HOST:/home/ubuntu/sar_st $EXP_DIR/engine_sar/$HOST
	ssh -q $HOST -oStrictHostKeyChecking=no -- rm /home/ubuntu/sar_st
done

mkdir $EXP_DIR/sequencer_netstats
ALL_SEQUENCER_HOSTS=$($HELPER_SCRIPT get-machine-with-label --machine-label=sequencer_node)
for HOST in $ALL_SEQUENCER_HOSTS; do
	NETDEVS=$(ssh -q $HOST -oStrictHostKeyChecking=no -- ls /sys/class/net | grep -e ^e)
	for NETDEV in $NETDEVS; do
		ssh -q $HOST -oStrictHostKeyChecking=no -- ethtool -S $NETDEV >>$EXP_DIR/sequencer_netstats/$HOST
	done
done

mkdir $EXP_DIR/engine_netstats
ALL_ENGINE_HOSTS=$($HELPER_SCRIPT get-machine-with-label --machine-label=engine_node)
for HOST in $ALL_ENGINE_HOSTS; do
	NETDEVS=$(ssh -q $HOST -oStrictHostKeyChecking=no -- ls /sys/class/net | grep -e ^e)
	for NETDEV in $NETDEVS; do
		ssh -q $HOST -oStrictHostKeyChecking=no -- ethtool -S $NETDEV >>$EXP_DIR/engine_netstats/$HOST
	done
done

mkdir $EXP_DIR/storage_netstats
ALL_STORAGE_HOSTS=$($HELPER_SCRIPT get-machine-with-label --machine-label=storage_node)
for HOST in $ALL_STORAGE_HOSTS; do
	NETDEVS=$(ssh -q $HOST -oStrictHostKeyChecking=no -- ls /sys/class/net | grep -e ^e)
	for NETDEV in $NETDEVS; do
		ssh -q $HOST -oStrictHostKeyChecking=no -- ethtool -S $NETDEV >>$EXP_DIR/storage_netstats/$HOST
	done
done

ssh -q $CLIENT_HOST -- "$WORKSPACE_DIR/sharedlog-stream-experiments/nexmark_sharedlog/zip_files.sh /home/ubuntu/${APP_NAME}/${EXP_DIR}/stats"

scp -r $CLIENT_HOST:/home/ubuntu/${APP_NAME}/${EXP_DIR}/stats ${EXP_DIR}

# $HELPER_SCRIPT collect-func-output --base-dir=$BASE_DIR --log-path=$EXP_DIR/logs
$HELPER_SCRIPT collect-container-logs --base-dir=$BASE_DIR --log-path=$EXP_DIR/logs
