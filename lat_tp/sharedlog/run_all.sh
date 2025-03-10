#!/bin/bash
set -x
/mnt/efs/workspace/research-helper-scripts/microservice_helper start-machines --use-spot-instances

TPS=(10 50 100)
DURATION=180
WARM_DURATION=0
WARM_EVENTS=(0 0 0)
payload=(16Kb)
for ((iter=0; iter<5; iter++)); do
    for ((idx=0; idx<${#TPS[@]}; ++idx)); do
        for ((j=0; j<${#payload[@]}; ++j)); do
            EVENTS=$(expr $DURATION \* ${TPS[idx]})
            ./run_once.sh --exp_dir ${DURATION}s_${WARM_DURATION}swarm_2/1prod_1t_1par_${TPS[idx]}/$iter/${payload[j]} \
                --tps "${TPS[idx]}" --warm_duration $WARM_DURATION --warm_events ${WARM_EVENTS[idx]} \
                --duration $DURATION --events_num "${EVENTS}" \
                --npar 1 --nprod 1 --payload "payload-${payload[j]}.data"
        done
    done
done

/mnt/efs/workspace/research-helper-scripts/microservice_helper stop-machines
