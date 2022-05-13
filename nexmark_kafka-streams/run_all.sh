#!/bin/bash
/mnt/efs/workspace/research-helper-scripts/microservice_helper start-machines --use-spot-instances

TPS=(1000 10000 100000 200000)
DURATION=120
WARM_DURATION=0
EVENTS=(180000 1800000 18000000 36000000)
APP=(q1 q2 q3 q5 q8)


for ((j=0; j<${#APP[@]}; ++j)); do
    for ((idx=0; idx<${#TPS[@]}; ++idx)); do
    ./nexmark.sh --app ${APP[j]} \
        --exp_dir ./${APP[j]}/4src_2xlarge/${DURATION}s_${WARM_DURATION}swarm/${TPS[idx]}tps_${EVENTS[idx]}/ \
        --nins 4 --nsrc 4 --serde msgp --duration $DURATION --nevents ${EVENTS[idx]} \
        --tps ${TPS[idx]} --warm_duration ${WARM_DURATION}
    done
done

/mnt/efs/workspace/research-helper-scripts/microservice_helper stop-machines
