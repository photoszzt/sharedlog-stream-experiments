#!/bin/bash
set -x
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
WORKSPACE_DIR=$(realpath $SCRIPT_DIR/../../)
DIR=q5_boki/mem_3node

cd $DIR
$WORKSPACE_DIR/research-helper-scripts/microservice_helper start-machines --use-spot-instances
cd ../..

TPS_PER_WORKER=(60000)
NUM_WORKER=6
DURATION=180
WARM_DURATION=0
APP=q5
FLUSH_MS=100
SRC_FLUSH_MS=100
SNAPSHOT_S=10
TPS=240000
EVENTS=$(expr $TPS \* $DURATION)
echo ${APP}, ${DIR}, ${EVENTS} events, ${TPS} tps

for ((iter=0; iter < 2; ++iter)); do
    cd ${DIR}
    for ((idx = 0; idx < ${#TPS_PER_WORKER[@]}; ++idx)); do
        subdir=${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS}ms_src${SRC_FLUSH_MS}ms
        ./run_once.sh --app ${APP} \
            --exp_dir ./${NUM_WORKER}src_6ins_3node/${subdir}/${iter}/${TPS_PER_WORKER[idx]}tps_epoch/ \
            --gua epoch --duration $DURATION --events_num ${EVENTS} \
            --tps ${TPS} --warm_duration ${WARM_DURATION} --nworker ${NUM_WORKER} \
            --flushms $FLUSH_MS --src_flushms $SRC_FLUSH_MS \
            --snapshot_s ${SNAPSHOT_S} --config_subpath 3node/6_ins/q5.json
    done
    cd -
done

cd $DIR
$WORKSPACE_DIR/research-helper-scripts/microservice_helper stop-machines
cd ../..
