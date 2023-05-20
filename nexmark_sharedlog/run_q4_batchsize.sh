#!/bin/bash
set -x
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
WORKSPACE_DIR=$(realpath $SCRIPT_DIR/../../)

cd q4_boki
$WORKSPACE_DIR/research-helper-scripts/microservice_helper start-machines --use-spot-instances
cd ..

TPS_PER_WORKER=(1000 1250)
# TPS_PER_WORKER=(250 500 750 1000 1250 1500 1750 2000)
NUM_WORKER=4
DURATION=180
WARM_DURATION=0
APP=q4
DIR=q4_boki
FLUSH_MS=100
SRC_FLUSH_MS=100
SNAPSHOT_S=10
BUF_MAX_SIZES=(65536 131072 262144)

for ((iter=0; iter < 3; ++iter)); do
    cd $DIR
    for ((idx = 0; idx < ${#TPS_PER_WORKER[@]}; ++idx)); do
        for BUF_MAX_SIZE in "${BUF_MAX_SIZES[@]}"; do
            TPS=$(expr ${TPS_PER_WORKER[idx]} \* ${NUM_WORKER})
            EVENTS=$(expr $TPS \* $DURATION)
            echo ${APP}, ${DIR}, ${EVENTS} events, ${TPS} tps
            subdir=${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS}ms_src${SRC_FLUSH_MS}ms
            # ./run_once.sh --app ${APP} \
            #       --exp_dir ./${NUM_WORKER}src_cache/${subdir}/${TPS_PER_WORKER[idx]}tps_alo/ \
            # 	--gua alo --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER} \
            # 	--tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS --src_flushms $SRC_FLUSH_MS

            ./run_once.sh --app ${APP} \
                --exp_dir ./${NUM_WORKER}src_${BUF_MAX_SIZE}/${subdir}/$iter/${TPS_PER_WORKER[idx]}tps_epoch/ \
                --gua epoch --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER} \
                --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS --src_flushms $SRC_FLUSH_MS \
                --snapshot_s ${SNAPSHOT_S} --buf_max_size ${BUF_MAX_SIZE}

            # ./run_once.sh --app ${APP} \
            #     --exp_dir ./${NUM_WORKER}src_none_gm1/${subdir}/$iter/${TPS_PER_WORKER[idx]}tps_epoch/ \
            #     --gua none --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER} \
            #     --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS --src_flushms $SRC_FLUSH_MS \
            #     --snapshot_s 0

            # ./run_once.sh --app ${APP} \
            #     --exp_dir ./${NUM_WORKER}src_ets2/${subdir}/$iter/${TPS_PER_WORKER[idx]}tps_2pc/ \
            #     --gua 2pc --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER} \
            #     --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS --src_flushms $SRC_FLUSH_MS \
            #     --snapshot_s 0
        done
    done
    cd -
done

cd q4_boki
$WORKSPACE_DIR/research-helper-scripts/microservice_helper stop-machines
cd ..
