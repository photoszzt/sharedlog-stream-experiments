#!/bin/bash
/mnt/efs/workspace/research-helper-scripts/microservice_helper start-machines --use-spot-instances

TPS_PER_WORKER=(125 250 500)
DURATION=180
WARM_DURATION=0
APP=(q4 q6 q7)
FLUSH_MS=100
NUM_INS=4

for ((j=0; j<${#APP[@]}; ++j)); do
    for ((idx=0; idx<${#TPS_PER_WORKER[@]}; ++idx)); do
	TPS=$(expr ${TPS_PER_WORKER[idx]} \* ${NUM_INS})
	EVENTS=$(expr ${TPS} \* $DURATION)
        echo ${APP[j]}, ${EVENTS} events, ${TPS} tps
    	./nexmark.sh --app ${APP[j]} \
    	    --exp_dir ./${APP[j]}/4src_nocache/${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS}ms/${TPS_PER_WORKER[idx]}tps_${EVENTS}_alo/ \
    	    --nins 4 --nsrc 4 --serde msgp --duration $DURATION --nevents ${EVENTS} \
    	    --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS --gua alo --disable_cache true
    	./nexmark.sh --app ${APP[j]} \
    	    --exp_dir ./${APP[j]}/4src_nocache/${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS}ms/${TPS_PER_WORKER[idx]}tps_${EVENTS}_eo/ \
    	    --nins 4 --nsrc 4 --serde msgp --duration $DURATION --nevents ${EVENTS} \
    	    --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS --gua eo --disable_cache true
    done
done

/mnt/efs/workspace/research-helper-scripts/microservice_helper stop-machines
