#!/bin/bash
set -x
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
WORKSPACE_DIR=$(realpath $SCRIPT_DIR/../../)
$WORKSPACE_DIR/research-helper-scripts/microservice_helper start-machines --use-spot-instances

# TPS_PER_WORKER=(28000 32000)
TPS_PER_WORKER=(200 1000)
DURATION=180
WARM_DURATION=0
APP=(q8)
FLUSH_MS=10
NUM_INS=4
SRC_FLUSH_MS=10

for ((iter=0; iter<5; iter++)); do
    for ((j=0; j<${#APP[@]}; ++j)); do
        for ((idx=0; idx<${#TPS_PER_WORKER[@]}; ++idx)); do
    	TPS=$(expr ${TPS_PER_WORKER[idx]} \* ${NUM_INS})
    	EVENTS=$(expr ${TPS} \* $DURATION)
            echo ${APP[j]}, ${EVENTS} events, ${TPS} tps
    	subdir=${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS}ms_src${SRC_FLUSH_MS}ms
    
        # ./nexmark.sh --app ${APP[j]} \
        #     --exp_dir ./${APP[j]}/4src_ets/$subdir/${TPS_PER_WORKER[idx]}tps_${EVENTS}_alo/ \
        #     --nins 4 --nsrc 4 --serde msgp --duration $DURATION --nevents ${EVENTS} \
        #     --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS --src_flushms ${SRC_FLUSH_MS} --gua alo
    
        ./nexmark.sh --app ${APP[j]} \
            --exp_dir ./${APP[j]}/4src_test/$subdir/$iter/${TPS_PER_WORKER[idx]}tps_eo/ \
            --nins 4 --nsrc 4 --serde msgp --duration $DURATION --nevents ${EVENTS} \
            --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS --src_flushms ${SRC_FLUSH_MS} --gua eo
        done
    done
done

$WORKSPACE_DIR/research-helper-scripts/microservice_helper stop-machines
