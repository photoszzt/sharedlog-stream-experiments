#!/bin/bash
set -x
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
WORKSPACE_DIR=$(realpath $SCRIPT_DIR/../../)
cd q1_boki
$WORKSPACE_DIR/research-helper-scripts/microservice_helper start-machines --use-spot-instances
cd ..

TPS_PER_WORKER=(4000 16000 32000 48000 64000 80000 88000)
#  TPS_PER_WORKER=(1000 )
NUM_WORKER=4
DURATION=180
WARM_DURATION=0
APP=q1
DIR=q1_boki
FLUSH_MS=100
SRC_FLUSH_MS=10
SNAPSHOT_S=0
modes=(alo epoch none 2pc align_chkpt)

for ((iter=0; iter < 3; ++iter)); do
    cd ${DIR}
    for ((idx = 0; idx < ${#TPS_PER_WORKER[@]}; ++idx)); do
        TPS=$(expr ${TPS_PER_WORKER[idx]} \* ${NUM_WORKER})
        EVENTS=$(expr $TPS \* $DURATION)
        echo ${APP}, ${DIR}, ${EVENTS} events, ${TPS} tps
        subdir=${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS}ms_src${SRC_FLUSH_MS}ms
        for mode in ${modes[@]}; do
            ./run_once.sh --app ${APP} \
                --exp_dir ./${NUM_WORKER}src_1/${subdir}/${iter}/${TPS_PER_WORKER[idx]}tps_${mode}/ \
                --gua $mode --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER} \
                --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS --src_flushms $SRC_FLUSH_MS \
                --snapshot_s ${SNAPSHOT_S}
        done
    done
    cd -
done

cd q1_boki
$WORKSPACE_DIR/research-helper-scripts/microservice_helper stop-machines
cd ..
