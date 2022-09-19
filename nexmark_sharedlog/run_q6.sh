#!/bin/bash
set -x
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
WORKSPACE_DIR=$(realpath $SCRIPT_DIR/../../)

cd q6_boki
$WORKSPACE_DIR/research-helper-scripts/microservice_helper start-machines --use-spot-instances
cd ..

TPS_PER_WORKER=(250 500 750 1000 1250 1500 1750 2000)
NUM_WORKER=(4)
DURATION=180
WARM_DURATION=0
APP=(q6)
DIR=(q6_boki)
FLUSH_MS=100
SRC_FLUSH_MS=100
SNAPSHOT_S=10

for ((iter=0; iter < 5; ++iter)); do
    for ((k = 0; k < ${#APP[@]}; ++k)); do
        cd ${DIR[k]}
        for ((idx = 0; idx < ${#TPS_PER_WORKER[@]}; ++idx)); do
            for ((w = 0; w < ${#NUM_WORKER[@]}; ++w)); do
                TPS=$(expr ${TPS_PER_WORKER[idx]} \* ${NUM_WORKER[w]})
                EVENTS=$(expr $TPS \* $DURATION)
                echo ${APP[k]}, ${DIR[k]}, ${EVENTS} events, ${TPS} tps
                subdir=${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS}ms_src${SRC_FLUSH_MS}ms
                # ./run_once.sh --app ${APP[k]} --exp_dir ./${NUM_WORKER[w]}src_cache/${subdir}/${TPS_PER_WORKER[idx]}tps_alo/ \
                #     --gua alo --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER[w]} \
                #     --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS --src_flushms $SRC_FLUSH_MS
                ./run_once.sh --app ${APP[k]} --exp_dir ./${NUM_WORKER[w]}src_gm1/${subdir}/$iter/${TPS_PER_WORKER[idx]}tps_epoch/ \
                    --gua epoch --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER[w]} \
                    --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS --src_flushms $SRC_FLUSH_MS \
                    --snapshot_s ${SNAPSHOT_S}
                # ./run_once.sh --app ${APP[k]} --exp_dir ./${NUM_WORKER[w]}src_ets2/${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS}ms/${TPS_PER_WORKER[idx]}tps_2pc/ \
                #     --gua 2pc --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER[w]} \
                #     --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS --src_flushms $SRC_FLUSH_MS
            done
        done
        cd -
    done
done

cd q6_boki
$WORKSPACE_DIR/research-helper-scripts/microservice_helper stop-machines
cd ..
