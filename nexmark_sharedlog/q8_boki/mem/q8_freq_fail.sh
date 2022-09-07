#!/bin/bash
SOURCE=${BASH_SOURCE[0]}
while [ -L "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
  SOURCE=$(readlink "$SOURCE")
  [[ $SOURCE != /* ]] && SOURCE=$DIR/$SOURCE # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
SCRIPT_DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )

WORKSPACE_DIR=$(realpath $SCRIPT_DIR/../../../../)
HELPER_SCRIPT=$WORKSPACE_DIR/research-helper-scripts/microservice_helper

ALL_ENGINE_HOSTS=$($HELPER_SCRIPT get-machine-with-label --machine-label=engine_node)
for HOST in $ALL_ENGINE_HOSTS; do
	container_names=$(ssh -q $HOST -oStrictHostKeyChecking=no -- "docker ps --format "{{.Names}}"")
	for h in $container_names; do
		spl=(${h//./ })
		task_slot=${spl[1]}
		name=${spl[0]}
		if [[ $name = "faas-test_faas-engine" ]] && [[ ${task_slot} -gt 4 ]]; then
			pid=$(ssh -q $HOST -oStrictHostKeyChecking=no -- "pgrep -f func_id=50")
			echo "found pid: $pid"
			ssh -q $HOST -oStrictHostKeyChecking=no -- "ps aux | grep [f]unc_id=50"
			ssh -q $HOST -oStrictHostKeyChecking=no -- "docker ps"
			ssh -q $HOST -oStrictHostKeyChecking=no -- "sudo kill -9 $pid"
			echo "after kill"
			ssh -q $HOST -oStrictHostKeyChecking=no -- "docker ps"
			exit 0
		fi
	done
done
