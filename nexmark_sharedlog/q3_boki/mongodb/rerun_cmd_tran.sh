#!/bin/bash
if [ "$1" = "" ]; then
	echo "should provide exp_dir"
	exit 1
fi
EXP_DIR=$1

SRC_DIR=/mnt/efs/workspace/sharedlog-stream
BASE_DIR=`realpath $(dirname $0)`
CLIENT_HOST=`$HELPER_SCRIPT get-client-host --base-dir=$BASE_DIR`
ENTRY_HOST=`$HELPER_SCRIPT get-service-host --base-dir=$BASE_DIR --service=faas-gateway`

ssh -q $CLIENT_HOST -- $SRC_DIR/bin/nexmark_client -app_name q3 \
    -faas_gateway $ENTRY_HOST:8080 -duration 60 -serde msgp -tran -comm_every_niter 100 \
    -tab_type mongodb -mongo_addr mongodb://mongodb-primary:27017,mongodb-secondary-0:27017,mongodb-secondary-1:27017/?replicaSet=replicaset \
    -wconfig $SRC_DIR/workload_config/q3.json >$EXP_DIR/results.log


$HELPER_SCRIPT collect-container-logs --base-dir=$BASE_DIR --log-path=$EXP_DIR/logs