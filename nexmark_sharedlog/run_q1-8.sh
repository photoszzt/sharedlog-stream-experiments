#!/bin/bash
set -x

cd q1_boki
/mnt/efs/workspace/research-helper-scripts/microservice_helper start-machines --use-spot-instances
cd ..
cp q1_boki/machines.json q2_boki
cp q1_boki/machines.json q3_boki/mem
cp q1_boki/machines.json q5_boki/mem
cp q1_boki/machines.json q8_boki/mem

TPS=(1000 10000 100000 200000)
DURATION=180
WARM_DURATION=60
EVENTS=(180000 1800000 18000000 36000000)
APP=(q1 q2 q3 q5 q8)
DIR=(q1_boki q2_boki q3_boki/mem q5_boki/mem q8_boki/mem)
FLUSH_MS=100

for ((k=0; k<${#APP[@]}; ++k)); do
    cd ${DIR[k]}
    for ((idx=0; idx<${#TPS[@]}; ++idx)); do
        echo ${APP[k]}, ${DIR[k]}, ${EVENTS[idx]}, ${TPS[idx]}
        ./run_once.sh --app ${APP[k]} --exp_dir ./4src_2xlarge/${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS}ms/${TPS[idx]}tps_${EVENTS[idx]}/ \
            --tran false --duration $DURATION --events_num ${EVENTS[idx]} --use_mongodb false \
            --tps ${TPS[idx]} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS
        ./run_once.sh --app ${APP[k]} --exp_dir ./4src_2xlarge/${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS}ms/${TPS[idx]}tps_${EVENTS[idx]}_tran/ \
            --tran true --duration $DURATION --events_num ${EVENTS[idx]} --use_mongodb false \
            --tps ${TPS[idx]} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS
    done
    cd -
done

cd q1_boki
/mnt/efs/workspace/research-helper-scripts/microservice_helper stop-machines
cd ..
rm q2_boki/machines.json
rm q3_boki/mem/machines.json
rm q5_boki/mem/machines.json
rm q8_boki/mem/machines.json
