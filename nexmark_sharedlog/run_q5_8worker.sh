#!/bin/bash
set -x
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
WORKSPACE_DIR=$(realpath $SCRIPT_DIR/../../)
DIR=q5_boki/mem_2xlarge

cd $DIR
$WORKSPACE_DIR/research-helper-scripts/microservice_helper start-machines --use-spot-instances
./update_docker.sh
cd ../..

# TPS_PER_WORKER=(1000 8000 16000 24000 32000 40000 48000 56000 64000)
TPS_PER_WORKER=(64000)
NUM_WORKER=(4)
DURATION=180
WARM_DURATION=0
APP=q5
FLUSH_MS=100
SRC_FLUSH_MS=100
SNAPSHOT_S=10
COMM_EVERY_MS=100

cd ${DIR}
for ((iter=2; iter < 3; ++iter)); do
    for ((idx = 0; idx < ${#TPS_PER_WORKER[@]}; ++idx)); do
        for ((w = 0; w < ${#NUM_WORKER[@]}; ++w)); do
            TPS=$(expr ${TPS_PER_WORKER[idx]} \* 4)
            EVENTS=$(expr $TPS \* $DURATION)
            echo ${APP}, ${DIR}, ${EVENTS} events, ${TPS} tps
            subdir=${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS}ms_src${SRC_FLUSH_MS}ms

            ./run_once.sh --app ${APP} \
                --exp_dir ./${NUM_WORKER[w]}src_8ins_2cpu2gm/${subdir}/${iter}/${TPS_PER_WORKER[idx]}tps_epoch/ \
                --gua epoch --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER[w]} \
                --tps ${TPS} --warm_duration ${WARM_DURATION} \
                --flushms $FLUSH_MS --src_flushms $SRC_FLUSH_MS \
                --snapshot_s ${SNAPSHOT_S} --config_subpath 4node/8_ins/q5.json  --comm_everyMs ${COMM_EVERY_MS}
        done
    done
done
cd -

cd $DIR
$WORKSPACE_DIR/research-helper-scripts/microservice_helper stop-machines
cd ../..
