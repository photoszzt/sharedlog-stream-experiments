#!/bin/bash
set -x
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
WORKSPACE_DIR=$(realpath $SCRIPT_DIR/../../)
DIR=q2_boki

cd $DIR
$WORKSPACE_DIR/research-helper-scripts/microservice_helper start-machines --use-spot-instances
./update_docker.sh
cd ..

# TPS_PER_WORKER=(4000 16000 32000 48000 64000 80000 88000)
TPS_PER_WORKER=(64000)
NUM_WORKER=4
DURATION=180
WARM_DURATION=0
APP=q2
FLUSH_MSES=(10 25 50)
SRC_FLUSH_MS=10
SNAPSHOT_S=0
modes=(remote_2pc epoch)

cd ${DIR}
for ((idx = 0; idx < ${#TPS_PER_WORKER[@]}; ++idx)); do
    for ((s = 0; s < ${#FLUSH_MSES[@]}; ++s)); do
        FLUSH_MS=${FLUSH_MSES[$s]}
        COMM_EVERY_MS=${FLUSH_MSES[$s]}
        TPS=$(expr ${TPS_PER_WORKER[idx]} \* ${NUM_WORKER})
        EVENTS=$(expr $TPS \* $DURATION)
        echo ${APP}, ${DIR}, ${EVENTS} events, ${TPS} tps
        subdir=${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS}ms_src${SRC_FLUSH_MS}ms
        for mode in ${modes[@]}; do
            for ((iter=0; iter < 3; ++iter)); do
                ./run_once.sh --app ${APP} \
                    --exp_dir ./${NUM_WORKER}src_varflush/${subdir}/${iter}/${TPS_PER_WORKER[idx]}tps_${mode}/ \
                    --gua $mode --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER} \
                    --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS --src_flushms $SRC_FLUSH_MS \
                    --snapshot_s ${SNAPSHOT_S} --comm_everyMs ${COMM_EVERY_MS}
            done
        done
    done
done
cd -

cd $DIR
$WORKSPACE_DIR/research-helper-scripts/microservice_helper stop-machines
cd ..
