#!/bin/bash
set -x

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
WORKSPACE_DIR=$(realpath $SCRIPT_DIR/../../)
DIR=q8_boki/mem_scale

cd $DIR
$WORKSPACE_DIR/research-helper-scripts/microservice_helper start-machines --use-spot-instances
./update_docker.sh
cd ../..

TPS_PER_WORKER=(24000)
BEFORE_SCALE=10
AFTER_SCALE=10
WARM_DURATION=0
APP=q8
FLUSH_MS=100
SRC_FLUSH_MS=100
SNAPSHOT_S=10
INIT_NUM_WORKER=2
SCALE_SCENE=2_to_4_ins

cd ${DIR}
for ((iter=0; iter < 1; ++iter)); do
    for ((idx = 0; idx < ${#TPS_PER_WORKER[@]}; ++idx)); do
        DURATION=$(expr $BEFORE_SCALE + $AFTER_SCALE)
        TPS=$(expr ${TPS_PER_WORKER[idx]} \* 4)
        EVENTS=$(expr $TPS \* $DURATION)
        echo ${APP}, ${DIR}, ${EVENTS} events, ${TPS} tps
        topdir=2src_scaleup2_${BEFORE_SCALE}_${AFTER_SCALE}_${TPS_PER_WORKER}
        subdir=${DURATION}s_${FLUSH_MS}ms_src${SRC_FLUSH_MS}ms	

        ./run_once_scale.sh --app ${APP} \
            --exp_dir ./${topdir}/$subdir/$iter/${TPS_PER_WORKER[idx]}tps_epoch/ \
            --beforeScale ${BEFORE_SCALE} --afterScale ${AFTER_SCALE} --events_num ${EVENTS} \
            --tps ${TPS} --flushms $FLUSH_MS --src_flushms $SRC_FLUSH_MS \
            --snapshot_s ${SNAPSHOT_S} --init_nworker $INIT_NUM_WORKER --scale_scene $SCALE_SCENE
    done
done
cd -

cd $DIR
$WORKSPACE_DIR/research-helper-scripts/microservice_helper stop-machines
cd ../..
