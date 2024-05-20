#!/bin/bash
set -x
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
WORKSPACE_DIR=$(realpath $SCRIPT_DIR/../../)
DIR=fanout_boki
cd $DIR
$WORKSPACE_DIR/research-helper-scripts/microservice_helper start-machines --use-spot-instances
./update_docker.sh
cd ..

TPS_PER_WORKER=(6000)
NUM_WORKER=4
DURATION=180
WARM_DURATION=0
APP=fanout
FLUSH_MS=50
COMM_EVERY_MS=50
SRC_FLUSH_MS=50
SNAPSHOT_S=0
# modes=(epoch none 2pc align_chkpt)
modes=(remote_2pc epoch)
EXTRA_BYTES=0
workload_dirs=(4node/4_ins/fanout_4.json 4node/4_ins/fanout_8.json 4node/4_ins/fanout_16.json)
# workload_dirs=(4node/4_ins/fanout_128.json)


cd ${DIR}
for ((idx = 0; idx < ${#TPS_PER_WORKER[@]}; ++idx)); do
    for ((j=0; j < ${#workload_dirs[@]}; ++j)); do
	WORKLOAD=${workload_dirs[$j]}
	wname=$(basename $WORKLOAD .json)
        TPS=$(expr ${TPS_PER_WORKER[$idx]} \* ${NUM_WORKER})
        EVENTS=$(expr $TPS \* $DURATION)
        echo ${APP}, ${DIR}, ${EVENTS} events, ${TPS} tps, ${WORKLOAD}
        subdir=${DURATION}s_${WARM_DURATION}swarm_${FLUSH_MS}ms_src${SRC_FLUSH_MS}ms
        for mode in ${modes[@]}; do
            for ((iter=0; iter < 2; ++iter)); do
                ./run_once.sh --app ${APP} \
                    --exp_dir ./${NUM_WORKER}src_1024byte_16384buf/${subdir}/${iter}/${TPS_PER_WORKER[$idx]}tps_${mode}_${wname}/ \
                    --gua $mode --duration $DURATION --events_num ${EVENTS} --nworker ${NUM_WORKER} \
                    --tps ${TPS} --warm_duration ${WARM_DURATION} --flushms $FLUSH_MS --src_flushms $SRC_FLUSH_MS \
                    --snapshot_s ${SNAPSHOT_S} --comm_everyMs ${COMM_EVERY_MS} --config_subpath ${WORKLOAD} \
		    --buf_max_size 16384
            done
        done
    done
done
cd -

cd $DIR
$WORKSPACE_DIR/research-helper-scripts/microservice_helper stop-machines
cd ..
