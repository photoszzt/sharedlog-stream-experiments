#!/bin/bash
/mnt/efs/workspace/research-helper-scripts/microservice_helper start-machines --use-spot-instances

TPS=(100)
DURATION=180
EVENTS=(18000 180000 1800000)
payload=(100b)
for ((idx=0; idx<${#TPS[@]}; ++idx)); do
    for ((j=0; j<${#payload[@]}; ++j)); do
        EVENTS=$(expr ${TPS[idx]} \* $DURATION)
        echo ${TPS[idx]}, ${payload[j]}, ${EVENTS}
        ./produce_bench.sh --exp_dir 180s_0swarm/1p_1t_1par_${TPS[idx]}tps/${payload[j]} \
            --ncon 1 --nprod 1 --duration $DURATION \
            --events_num ${EVENTS} --num_par 1 --payload payload-${payload[j]}.data \
            --tps ${TPS[idx]}
    done
done
/mnt/efs/workspace/research-helper-scripts/microservice_helper stop-machines
