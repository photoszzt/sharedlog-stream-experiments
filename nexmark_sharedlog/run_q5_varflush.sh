#!/bin/bash
set -x
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
WORKSPACE_DIR=$(realpath $SCRIPT_DIR/../../)
DIR=q5_boki/mem

cd $DIR
$WORKSPACE_DIR/research-helper-scripts/microservice_helper start-machines --use-spot-instances
./update_docker.sh
cd ../..

#TPS_PER_WORKER=(1000 8000 16000 24000 32000 40000 48000 56000 64000)
TPS_PER_WORKER=(48000)
NUM_WORKER=(4)
DURATION=180
WARM_DURATION=0
APP=q5
SRC_FLUSH_MS=(25 50 100)
SNAPSHOT_S=10
# FLUSH_MS=100
# COMM_EVERY_MS=100
# modes=(align_chkpt epoch 2pc none)
modes=(epoch 2pc)

cd ${DIR}
for ((idx = 0; idx < ${#TPS_PER_WORKER[@]}; ++idx)); do
    for ((s = 0; s < ${#SRC_FLUSH_MS[@]}; ++s)); do
        FLUSH_MS=${SRC_FLUSH_MS[$s]}
        COMM_EVERY_MS=${SRC_FLUSH_MS[$s]}
        for ((w = 0; w < ${#NUM_WORKER[@]}; ++w)); do
            TPS=$(expr ${TPS_PER_WORKER[idx]} \* ${NUM_WORKER[w]})
            EVENTS=$(expr $TPS \* $DURATION)
            echo ${APP}, ${DIR}, ${EVENTS} events, ${TPS} tps, $FLUSH_MS flush_ms, ${SRC_FLUSH_MS[$s]} srcflush_ms, $COMM_EVERY_MS comm_ms
            subdir=${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS}ms_src${SRC_FLUSH_MS[$s]}ms
            for mode in ${modes[@]}; do
                for ((iter=0; iter < 1; ++iter)); do
                    ./run_once.sh --app ${APP} \
                        --exp_dir ./${NUM_WORKER[w]}src_4/${subdir}/${iter}/${TPS_PER_WORKER[idx]}tps_${mode}/ \
                        --gua $mode --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER[w]} \
                        --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS \
		        --src_flushms $SRC_FLUSH_MS[$s] \
                        --snapshot_s ${SNAPSHOT_S} --comm_everyMs ${COMM_EVERY_MS}
                done
            done
        done
    done
done
cd -

cd $DIR
$WORKSPACE_DIR/research-helper-scripts/microservice_helper stop-machines
cd ../..
