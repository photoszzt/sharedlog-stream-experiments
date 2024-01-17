#!/bin/bash
set -x

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
WORKSPACE_DIR=$(realpath $SCRIPT_DIR/../../)
DIR=q8_boki/mem
cd $DIR
$WORKSPACE_DIR/research-helper-scripts/microservice_helper start-machines --use-spot-instances
cd ../..

TPS_PER_WORKER=(4000 8000 12000 16000 20000 24000 28000 32000 36000)
# TPS_PER_WORKER=(12000 16000 20000 28000 32000)
# TPS_PER_WORKER=(36000)
NUM_WORKER=(4)
DURATION=180
WARM_DURATION=0
APP=q8
FLUSH_MS=100
SNAPSHOT_S=10
SRC_FLUSH_MS=${FLUSH_MS}
modes=(alo epoch none 2pc align_chkpt)

for ((iter=0; iter < 3; ++iter)); do
    cd ${DIR}
    for ((idx = 0; idx < ${#TPS_PER_WORKER[@]}; ++idx)); do
        for ((w = 0; w < ${#NUM_WORKER[@]}; ++w)); do
            TPS=$(expr ${TPS_PER_WORKER[idx]} \* ${NUM_WORKER[w]})
            EVENTS=$(expr $TPS \* $DURATION)
            echo ${APP}, ${DIR}, ${EVENTS} events, ${TPS} tps
            subdir=${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS[j]}ms_src${SRC_FLUSH_MS}ms
            for mode in ${modes[@]}; do
                ./run_once.sh --app ${APP} 
                    --exp_dir ./${NUM_WORKER[w]}src_1/${subdir}/${iter}/${TPS_PER_WORKER[idx]}tps_${mode}/ \
                    --gua $mode --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER[w]} \
                    --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS --src_flushms $SRC_FLUSH_MS \
                    --snapshot_s ${SNAPSHOT_S}
            done
        done
    done
    cd -
done

cd $DIR
$WORKSPACE_DIR/research-helper-scripts/microservice_helper stop-machines
cd ../..
