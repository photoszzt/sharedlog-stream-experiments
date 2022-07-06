#!/bin/bash
set -x

cd q1_boki
/mnt/efs/workspace/research-helper-scripts/microservice_helper start-machines --use-spot-instances
cd ..
cp q1_boki/machines.json q2_boki
cp q1_boki/machines.json q3_boki/mem
cp q1_boki/machines.json q4_boki
cp q1_boki/machines.json q5_boki/mem
cp q1_boki/machines.json q7_boki/mem
cp q1_boki/machines.json q8_boki/mem

TPS_PER_WORKER=(500)
NUM_WORKER=(4)
DURATION=180
WARM_DURATION=60
APP=(q1 q2 q3 q4 q5 q7 q8)
DIR=(q1_boki q2_boki q3_boki/mem q4_boki q5_boki/mem q7_boki/mem q8_boki/mem)
FLUSH_MS=5

for ((k=0; k<${#APP[@]}; ++k)); do
    cd ${DIR[k]}
    for ((idx=0; idx<${#TPS_PER_WORKER[@]}; ++idx)); do
        TPS=$(expr ${TPS_PER_WORKER[idx]} \* ${NUM_WORKER[idx]})
        EVENTS=$(expr $TPS \* $DURATION)
        echo ${APP[k]}, ${DIR[k]}, ${EVENTS[idx]} events, ${TPS} tps
        ./run_once.sh --app ${APP[k]} --exp_dir ./${NUM_WORKER}src_2xlarge/${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS}ms/${TPS_PER_WORKER[idx]}tps_alo/ \
            --gua alo --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER[idx]} \
            --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS
        ./run_once.sh --app ${APP[k]} --exp_dir ./${NUM_WORKER}src_2xlarge/${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS}ms/${TPS_PER_WORKER[idx]}tps_epoch/ \
            --gua epoch --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER[idx]} \
            --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS
        ./run_once.sh --app ${APP[k]} --exp_dir ./${NUM_WORKER}src_2xlarge/${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS}ms/${TPS_PER_WORKER[idx]}tps_2pc/ \
            --gua 2pc --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER[idx]} \
            --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS
    done
    cd -
done

cd q1_boki
/mnt/efs/workspace/research-helper-scripts/microservice_helper stop-machines
cd ..
rm q2_boki/machines.json
rm q3_boki/mem/machines.json
rm q4_boki/machines.json
rm q5_boki/mem/machines.json
rm q7_boki/mem/machines.json
rm q8_boki/mem/machines.json
