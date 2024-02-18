#!/bin/bash
set -x

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
WORKSPACE_DIR=$(realpath $SCRIPT_DIR/../../)

DIR=q8_boki/mem
DIRS=(q8_boki/mem q8_boki/mem_4node_8ins q8_boki/mem_4node_16ins)

cd $DIR
$WORKSPACE_DIR/research-helper-scripts/microservice_helper start-machines --use-spot-instances
./update_docker.sh
cp machines.json ../q8_boki/mem_4node_8ins
cp machines.json ../q8_boki/mem_4node_16ins
cd ../..

# TPS_PER_WORKER=(4000 8000 12000 16000 20000 24000 28000 32000 36000)
# TPS_PER_WORKER=(12000 16000 20000 28000 32000)
TPS_PER_WORKER=(24000)
NUM_WORKER=(4 8 16)
DURATION=180
WARM_DURATION=0
APP=q8
FLUSH_MS=100
SRC_FLUSH_MS=${FLUSH_MS}
SNAPSHOT_S=10
modes=(align_chkpt epoch 2pc)

for ((idx = 0; idx < ${#TPS_PER_WORKER[@]}; ++idx)); do
    for ((w = 0; w < ${#NUM_WORKER[@]}; ++w)); do
        cd ${DIRS[w]}
        TPS=$(expr ${TPS_PER_WORKER[idx]} \* ${NUM_WORKER[w]})
        EVENTS=$(expr $TPS \* $DURATION)
        echo ${APP}, ${DIRS[w]}, ${EVENTS} events, ${TPS} tps
        subdir=${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS[j]}ms_src${SRC_FLUSH_MS}ms
        exp_dir=${NUM_WORKER[w]}src_4node_${NUM_WORKER[w]}ins
        for mode in ${modes[@]}; do
            for ((iter=0; iter < 1; ++iter)); do
                ./run_once.sh --app ${APP} \
                    --exp_dir ./${exp_dir}/${subdir}/$iter/${TPS_PER_WORKER[idx]}tps_${mode}/ \
                    --gua $mode --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER[w]} \
                    --tps ${TPS} --warm_duration ${WARM_DURATION} \
                    --flushms ${FLUSH_MS[j]} --src_flushms $SRC_FLUSH_MS \
                    --snapshot_s ${SNAPSHOT_S} --config_subpath 4node/${NUM_WORKER[w]}_ins/q8.json
            done
        done
        cd -
    done
done

cd $DIR
$WORKSPACE_DIR/research-helper-scripts/microservice_helper stop-machines
cd ../..
