#!/bin/bash
set -x

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
WORKSPACE_DIR=$(realpath $SCRIPT_DIR/../../)

DIR=q8_boki/mem_4xlarge
DIRS=(q8_boki/mem_4xlarge q8_boki/mem_4node_8ins_4xlarge q8_boki/mem_4node_16ins_4xlarge q8_boki/mem_4node_32ins_4xlarge)

cd $DIR
$WORKSPACE_DIR/research-helper-scripts/microservice_helper start-machines --use-spot-instances
./update_docker.sh
cp machines.json ../mem_4node_8ins_4xlarge
cp machines.json ../mem_4node_16ins_4xlarge
cp machines.json ../mem_4node_32ins_4xlarge
cd ../..

# TPS_PER_WORKER=(4000 8000 12000 16000 20000 24000 28000 32000 36000)
TPS_PER_WORKER=(28000 14000 7000 3500)
NUM_WORKER=(4 8 16 32)
DURATION=180
WARM_DURATION=0
APP=q8
FLUSH_MS=100
SRC_FLUSH_MS=${FLUSH_MS}
SNAPSHOT_S=10
COMM_EVERY_MS=100
EXTRA_BYTES=(0)
modes=(2pc epoch align_chkpt)

for ((i=0; i < ${#EXTRA_BYTES[@]}; ++i)); do
    for ((w = 0; w < ${#NUM_WORKER[@]}; ++w)); do
        cd ${DIRS[w]}
        TPS=$(expr ${TPS_PER_WORKER[w]} \* ${NUM_WORKER[w]})
        EVENTS=$(expr $TPS \* $DURATION)
        echo ${APP}, ${DIRS[w]}, ${EVENTS} events, ${TPS} tps, ${EXTRA_BYTES[$i]} bytes
        subdir=${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS}ms_src${SRC_FLUSH_MS}ms
        exp_dir=${NUM_WORKER[w]}src_4node_${NUM_WORKER[w]}ins_${EXTRA_BYTES[$i]}extra_kvrocks
        for mode in ${modes[@]}; do
            for ((iter=0; iter < 1; ++iter)); do
                ./run_once.sh --app ${APP} \
                    --exp_dir ./${exp_dir}/${subdir}/$iter/${TPS_PER_WORKER[w]}tps_${mode}/ \
                    --gua $mode --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER[w]} \
                    --tps ${TPS} --warm_duration ${WARM_DURATION} \
                    --flushms ${FLUSH_MS[j]} --src_flushms $SRC_FLUSH_MS \
                    --snapshot_s ${SNAPSHOT_S} --config_subpath 4node/${NUM_WORKER[w]}_ins/q8.json \
                    --comm_everyMs ${COMM_EVERY_MS} --extra_bytes ${EXTRA_BYTES[$i]}
            done
        done
        cd -
    done
done

cd $DIR
$WORKSPACE_DIR/research-helper-scripts/microservice_helper stop-machines
rm ../mem_4node_8ins_4xlarge/machines.json || true
rm ../mem_4node_16ins_4xlarge/machines.json || true
rm ../mem_4node_32ins_4xlarge/machines.json || true
cd ../..
