#!/bin/bash

cd q1_boki
/mnt/efs/workspace/research-helper-scripts/microservice_helper start-machines --use-spot-instances
cd ..
cp q1_boki/machines.json q2_boki
cp q1_boki/machines.json q3_boki/mem
cp q1_boki/machines.json q8_boki/mem

TPS=(1000 10000 100000 1000000)
DURATION=180
WARM_DURATION=60
EVENTS=(180000 1800000 18000000 180000000)

# q1
cd q1_boki
for ((idx=0; idx<${#TPS[@]}; ++idx)); do
    ./run_once.sh --app q1 --exp_dir ./4src_2xlarge/180s_60swarm/${TPS[idx]}tps_${EVENTS[idx]}/ \
        --tran false --duration $DURATION --events_num $EVENTS_NUM --use_mongodb false \
        -tps ${TPS[idx]} --warm_duration ${WARM_DURATION}
    ./run_once.sh --app q1 --exp_dir ./4src_2xlarge/180s_60swarm/${TPS[idx]}tps_${EVENTS}/ \
        --tran true --duration $DURATION --events_num $EVENTS_NUM --use_mongodb false \
        -tps ${TPS[idx]} --warm_duration ${WARM_DURATION}
done
cd ..

# q2
cd q2_boki
for ((idx=0; idx<${#TPS[@]}; ++idx)); do
    ./run_once.sh --app q2 --exp_dir ./4src_2xlarge/180s_60swarm/${TPS[idx]}tps_${EVENTS[idx]}/ \
        --tran false --duration $DURATION --events_num $EVENTS_NUM --use_mongodb false \
        -tps ${TPS[idx]} --warm_duration ${WARM_DURATION}
    ./run_once.sh --app q2 --exp_dir ./4src_2xlarge/180s_60swarm/${TPS[idx]}tps_${EVENTS}/ \
        --tran true --duration $DURATION --events_num $EVENTS_NUM --use_mongodb false \
        -tps ${TPS[idx]} --warm_duration ${WARM_DURATION}
done
cd ..

# cd q3_boki/mem
# for ((idx=0; idx<${#TPS[@]}; ++idx)); do
#     ./run_once.sh --app q3 --exp_dir ./4src_2xlarge/180s_60swarm/${TPS[idx]}tps_${EVENTS[idx]}/ \
#         --tran false --duration $DURATION --events_num $EVENTS_NUM --use_mongodb false \
#         -tps ${TPS[idx]} --warm_duration ${WARM_DURATION}
#     ./run_once.sh --app q3 --exp_dir ./4src_2xlarge/180s_60swarm/${TPS[idx]}tps_${EVENTS}/ \
#         --tran true --duration $DURATION --events_num $EVENTS_NUM --use_mongodb false \
#         -tps ${TPS[idx]} --warm_duration ${WARM_DURATION}
# done
# cd ../..
# 
# cd q8_boki/mem
# for ((idx=0; idx<${#TPS[@]}; ++idx)); do
#     ./run_once.sh --app q8 --exp_dir ./4src_2xlarge/180s_60swarm/${TPS[idx]}tps_${EVENTS[idx]}/ \
#         --tran false --duration $DURATION --events_num $EVENTS_NUM --use_mongodb false \
#         -tps ${TPS[idx]} --warm_duration ${WARM_DURATION}
#     ./run_once.sh --app q8 --exp_dir ./4src_2xlarge/180s_60swarm/${TPS[idx]}tps_${EVENTS}/ \
#         --tran true --duration $DURATION --events_num $EVENTS_NUM --use_mongodb false \
#         -tps ${TPS[idx]} --warm_duration ${WARM_DURATION}
# done
# cd ../..


cd q1_boki
/mnt/efs/workspace/research-helper-scripts/microservice_helper stop-machines
cd ..
rm q2_boki/machines.json