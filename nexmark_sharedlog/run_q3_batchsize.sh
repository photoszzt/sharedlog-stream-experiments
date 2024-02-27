#!/bin/bash
set -x

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
WORKSPACE_DIR=$(realpath $SCRIPT_DIR/../../)
DIR=q3_boki/mem

cd $DIR
$WORKSPACE_DIR/research-helper-scripts/microservice_helper start-machines --use-spot-instances
./update_docker.sh
cd ../..

# TPS_PER_WORKER=(8000 16000 32000 48000 64000 80000 96000 112000 128000)
TPS_PER_WORKER=(80000 96000)
NUM_WORKER=4
DURATION=180
WARM_DURATION=0
APP=q3
FLUSH_MS=100
SRC_FLUSH_MS=100
SNAPSHOT_S=10
BUF_MAX_SIZES=(65536 131072 262144)
COMM_EVERY_MS=100

cd $DIR
for ((idx = 0; idx < ${#TPS_PER_WORKER[@]}; ++idx)); do
    for BUF_MAX_SIZE in "${BUF_MAX_SIZES[@]}"; do
        TPS=$(expr ${TPS_PER_WORKER[idx]} \* ${NUM_WORKER})
        EVENTS=$(expr $TPS \* $DURATION)
        echo $APP, $DIR, ${EVENTS} events, ${TPS} tps, ${batch_size} batch_size
        subdir=${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS}ms_src${SRC_FLUSH_MS}ms
        for ((iter=0; iter < 3; ++iter)); do
            # ./run_once.sh --app ${APP} \
            #     --exp_dir ./${NUM_WORKER}src_generics/$subdir/${TPS_PER_WORKER[idx]}tps_alo/ \
            #     --gua alo --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER} \
            #     --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS \
            #     --src_flushms $SRC_FLUSH_MS --comm_everyMs ${COMM_EVERY_MS}

            ./run_once.sh --app ${APP} \
                --exp_dir ./${NUM_WORKER}src_${BUF_MAX_SIZE}/$subdir/$iter/${TPS_PER_WORKER[idx]}tps_epoch/ \
                --gua epoch --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER} \
                --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS --src_flushms $SRC_FLUSH_MS \
                --snapshot_s ${SNAPSHOT_S} --buf_max_size ${BUF_MAX_SIZE} --comm_everyMs ${COMM_EVERY_MS}

            # ./run_once.sh --app ${APP} \
            #     --exp_dir ./${NUM_WORKER}src_none_gm1/$subdir/$iter/${TPS_PER_WORKER[idx]}tps_epoch/ \
            #     --gua none --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER} \
            #     --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS --src_flushms $SRC_FLUSH_MS \
            #     --snapshot_s 0 --comm_everyMs ${COMM_EVERY_MS}

            # ./run_once.sh --app ${APP} \
            #     --exp_dir ./${NUM_WORKER}src_ets2/$subdir/$iter/${TPS_PER_WORKER[idx]}tps_2pc/ \
            #     --gua 2pc --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER} \
            #     --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS --src_flushms $SRC_FLUSH_MS \
            #     --snapshot_s 0 --comm_everyMs ${COMM_EVERY_MS}
        done
    done
done
cd -

cd $DIR
$WORKSPACE_DIR/research-helper-scripts/microservice_helper stop-machines
cd ../..
