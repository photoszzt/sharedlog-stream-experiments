#!/bin/bash
set -x

cd q6_boki
/mnt/efs/workspace/research-helper-scripts/microservice_helper start-machines --use-spot-instances
cd ..

TPS_PER_WORKER=(500)
NUM_WORKER=(4)
DURATION=180
WARM_DURATION=60
APP=(q6)
DIR=(q6_boki)
FLUSH_MS=10

for ((k=0; k<${#APP[@]}; ++k)); do
    cd ${DIR[k]}
    for ((idx=0; idx<${#TPS_PER_WORKER[@]}; ++idx)); do
        TPS=$(expr ${TPS_PER_WORKER[idx]} \* ${NUM_WORKER[idx]})
        EVENTS=$(expr $TPS \* $DURATION)
        echo ${APP[k]}, ${DIR[k]}, ${EVENTS[idx]} events, ${TPS} tps
        ./run_once.sh --app ${APP[k]} --exp_dir ./${NUM_WORKER}src_ets2/${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS}ms/${TPS_PER_WORKER[idx]}tps_alo/ \
            --gua alo --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER[idx]} \
            --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS
        ./run_once.sh --app ${APP[k]} --exp_dir ./${NUM_WORKER}src_ets2/${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS}ms/${TPS_PER_WORKER[idx]}tps_epoch/ \
            --gua epoch --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER[idx]} \
            --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS
        ./run_once.sh --app ${APP[k]} --exp_dir ./${NUM_WORKER}src_ets2/${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS}ms/${TPS_PER_WORKER[idx]}tps_2pc/ \
            --gua 2pc --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER[idx]} \
            --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS
    done
    cd -
done

cd q6_boki
/mnt/efs/workspace/research-helper-scripts/microservice_helper stop-machines
cd ..
