#!/bin/bash
/mnt/efs/workspace/research-helper-scripts/microservice_helper start-machines --use-spot-instances

TPS=(10 50 100)
DURATION=180
WARM_DURATION=0
WARM_EVENTS=(0 0 0)
payload=(16Kb)

for ((iter=0; iter<5; ++iter)); do
    for ((idx=0; idx<${#TPS[@]}; ++idx)); do
        for ((j=0; j<${#payload[@]}; ++j)); do
            EVENTS=$(expr $DURATION \* ${TPS[idx]})
            echo ${TPS[idx]}, ${payload[j]}, ${EVENTS}, ${WARM_EVENTS[idx]}
            ./produce_bench.sh --exp_dir 180s_0swarm/1p_1t_1par_${TPS[idx]}tps/$iter/${payload[j]} \
                --ncon 1 --nprod 1 --duration $DURATION \
                --events_num ${EVENTS} --num_par 1 --payload payload-${payload[j]}.data \
                --tps ${TPS[idx]} --warm_duration $WARM_DURATION --warm_events ${WARM_EVENTS[idx]}
        done
    done
done

/mnt/efs/workspace/research-helper-scripts/microservice_helper stop-machines
