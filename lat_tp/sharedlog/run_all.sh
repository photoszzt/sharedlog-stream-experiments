#!/bin/bash
/mnt/efs/workspace/research-helper-scripts/microservice_helper start-machines --use-spot-instances

TPS=(100 1000 10000)
DURATION=180
WARM_DURATION=60
WARM_EVENTS=(6000 60000 600000)
EVENTS=(18000 180000 1800000)
payload=(100b 1Kb 4Kb 16Kb)
for ((idx=0; idx<${#TPS[@]}; ++idx)); do
    for ((j=0; j<${#payload[@]}; ++j)); do
        ./run_once.sh --exp_dir 180s_60swarm/1prod_1t_1par_5ms_${TPS[idx]}/${payload[j]} \
            --tps "${TPS[idx]}" --warm_duration $WARM_DURATION --warm_events ${WARM_EVENTS[idx]} \
            --duration $DURATION --events_num "${EVENTS[idx]}" \
            --npar 1 --nprod 1 --payload "payload-${payload[j]}.data"
    done
done
/mnt/efs/workspace/research-helper-scripts/microservice_helper stop-machines
