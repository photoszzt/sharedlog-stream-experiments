#!/bin/bash
set -x
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
WORKSPACE_DIR=$(realpath $SCRIPT_DIR/../../)
cd q2_measure_epoch
$WORKSPACE_DIR/research-helper-scripts/microservice_helper start-machines --use-spot-instances
./update_docker.sh
cd ..

TPS_PER_WORKER=(10)
#  TPS_PER_WORKER=(1000 )
NUM_WORKER=(1)
DURATION=180
WARM_DURATION=0
APP=(q2)
DIR=(q2_measure_epoch)
FLUSH_MS=100
SRC_FLUSH_MS=10
SNAPSHOT_S=0
COMM_EVERY_MS=100

for ((iter=0; iter < 1; ++iter)); do
    for ((k = 0; k < ${#APP[@]}; ++k)); do
        cd ${DIR[k]}
        for ((idx = 0; idx < ${#TPS_PER_WORKER[@]}; ++idx)); do
            for ((w = 0; w < ${#NUM_WORKER[@]}; ++w)); do
                TPS=$(expr ${TPS_PER_WORKER[idx]} \* ${NUM_WORKER[w]})
                EVENTS=$(expr $TPS \* $DURATION)
                echo ${APP[k]}, ${DIR[k]}, ${EVENTS} events, ${TPS} tps
                subdir=${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS}ms_src${SRC_FLUSH_MS}ms
                ./run_once.sh --app ${APP[k]} --exp_dir ./${NUM_WORKER[w]}src_mea1/$subdir/$iter/${TPS_PER_WORKER[idx]}tps_epoch/ \
                    --gua epoch --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER[w]} \
                    --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS --src_flushms $SRC_FLUSH_MS \
                    --snapshot_s ${SNAPSHOT_S} --comm_everyMs ${COMM_EVERY_MS}
            done
        done
        cd -
    done
done

cd q2_measure_epoch
$WORKSPACE_DIR/research-helper-scripts/microservice_helper stop-machines
cd ..
