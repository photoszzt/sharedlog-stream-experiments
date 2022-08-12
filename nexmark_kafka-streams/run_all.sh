#!/bin/bash
/mnt/efs/workspace/research-helper-scripts/microservice_helper start-machines --use-spot-instances

TPS=(500 1000)
DURATION=180
WARM_DURATION=0
APP=(q1 q2 q3 q4 q5 q6 q7 q8)
FLUSH_MS=100
SRC_FLUSH_MS=5

for ((j=0; j<${#APP[@]}; ++j)); do
    for ((idx=0; idx<${#TPS[@]}; ++idx)); do
	EVENTS=$(expr ${TPS[idx]} \* $DURATION)
        echo ${APP[j]}, ${EVENTS} events, ${TPS[idx]} tps
    	./nexmark.sh --app ${APP[j]} \
    	    --exp_dir ./${APP[j]}/4src_ets/${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS}ms/${TPS[idx]}tps_${EVENTS}_alo/ \
    	    --nins 4 --nsrc 4 --serde msgp --duration $DURATION --nevents ${EVENTS} \
    	    --tps ${TPS[idx]} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS \
			--src_flushms $SRC_FLUSH_MS --gua alo
    	./nexmark.sh --app ${APP[j]} \
    	    --exp_dir ./${APP[j]}/4src_ets/${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS}ms/${TPS[idx]}tps_${EVENTS}_eo/ \
    	    --nins 4 --nsrc 4 --serde msgp --duration $DURATION --nevents ${EVENTS} \
    	    --tps ${TPS[idx]} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS \
			--src_flushms $SRC_FLUSH_MS --gua eo
    done
done

/mnt/efs/workspace/research-helper-scripts/microservice_helper stop-machines
