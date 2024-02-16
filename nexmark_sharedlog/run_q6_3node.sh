#!/bin/bash
set -x
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
WORKSPACE_DIR=$(realpath $SCRIPT_DIR/../../)

DIR=q6_boki/mem_3node
cd $DIR
$WORKSPACE_DIR/research-helper-scripts/microservice_helper start-machines --use-spot-instances
./update_docker.sh
cd ../..

# TPS_PER_WORKER=(250 500 750 1000 1250 1500)
TPS_PER_WORKER=(750)
NUM_WORKER=(4)
DURATION=180
WARM_DURATION=0
APP=q6
FLUSH_MS=100
SRC_FLUSH_MS=100
SNAPSHOT_S=10

cd ${DIR}
for ((iter=2; iter < 3; ++iter)); do
    for ((idx = 0; idx < ${#TPS_PER_WORKER[@]}; ++idx)); do
        for ((w = 0; w < ${#NUM_WORKER[@]}; ++w)); do
            TPS=$(expr ${TPS_PER_WORKER[idx]} \* ${NUM_WORKER[w]})
            EVENTS=$(expr $TPS \* $DURATION)
            echo ${APP}, ${DIR}, ${EVENTS} events, ${TPS} tps
            subdir=${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS}ms_src${SRC_FLUSH_MS}ms
            # ./run_once.sh --app ${APP} --exp_dir ./${NUM_WORKER[w]}src_cache/${subdir}/${TPS_PER_WORKER[idx]}tps_alo/ \
            #     --gua alo --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER[w]} \
            #     --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS --src_flushms $SRC_FLUSH_MS

            ./run_once.sh --app ${APP} \
                --exp_dir ./${NUM_WORKER[w]}src_2node_4ins/${subdir}/$iter/${TPS_PER_WORKER[idx]}tps_epoch/ \
                --gua epoch --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER[w]} \
                --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS --src_flushms $SRC_FLUSH_MS \
                --snapshot_s ${SNAPSHOT_S} --config_subpath 3node/4_ins/q6.json

            # ./run_once.sh --app ${APP} \
            #     --exp_dir ./${NUM_WORKER[w]}src_none_rds2/${subdir}/$iter/${TPS_PER_WORKER[idx]}tps_epoch/ \
            #     --gua none --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER[w]} \
            #     --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS --src_flushms $SRC_FLUSH_MS \
            #     --snapshot_s 0

            # ./run_once.sh --app ${APP} \
            #     --exp_dir ./${NUM_WORKER[w]}src_2pc/${subdir}/$iter/${TPS_PER_WORKER[idx]}tps_2pc/ \
            #     --gua 2pc --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER[w]} \
            #     --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS --src_flushms $SRC_FLUSH_MS \
            #     --snapshot_s $SNAPSHOT_S
        done
    done
done
cd -

cd $DIR
$WORKSPACE_DIR/research-helper-scripts/microservice_helper stop-machines
cd ../..
