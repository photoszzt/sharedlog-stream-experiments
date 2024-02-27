#!/bin/bash
set -x
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
WORKSPACE_DIR=$(realpath $SCRIPT_DIR/../../)
DIR=q8_boki/mem

cd $DIR
$WORKSPACE_DIR/research-helper-scripts/microservice_helper start-machines --use-spot-instances
./update_docker.sh
cd ../..

TPS_PER_WORKER=(20000 24000 28000)
NUM_WORKER=(4)
DURATION=330
WARM_DURATION=0
APP=q8
FLUSH_MS=100
SRC_FLUSH_MS=100
SNAPSHOT_S=10
COMM_EVERY_MS=100

cd ${DIR}
for ((i = 0; i < 1; ++i)); do
    for ((idx = 0; idx < ${#TPS_PER_WORKER[@]}; ++idx)); do
        for ((w = 0; w < ${#NUM_WORKER[@]}; ++w)); do
            TPS=$(expr ${TPS_PER_WORKER[idx]} \* ${NUM_WORKER[w]})
            EVENTS=$(expr $TPS \* $DURATION)
            echo ${APP[k]}, ${DIR[k]}, ${EVENTS} events, ${TPS} tps
            subdir=${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS}ms_src${SRC_FLUSH_MS}ms
            ./run_once.sh --app ${APP[k]} \
                --exp_dir ./${NUM_WORKER[w]}src_snapshot_300_gm2/$subdir/$i/${TPS_PER_WORKER[idx]}tps_epoch/ \
                --gua epoch --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER[w]} \
                --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS \
                --src_flushms $SRC_FLUSH_MS --fail true --snapshot_s ${SNAPSHOT_S} --comm_everyMs ${COMM_EVERY_MS}
        done
    done
done
cd -

cd $DIR
$WORKSPACE_DIR/research-helper-scripts/microservice_helper stop-machines
cd ../..
