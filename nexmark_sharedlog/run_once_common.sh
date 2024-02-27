#!/bin/bash
set -x
SOURCE=${BASH_SOURCE[0]}
while [ -L "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
  SOURCE=$(readlink "$SOURCE")
  [[ $SOURCE != /* ]] && SOURCE=$DIR/$SOURCE # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
SCRIPT_DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )

BASE_DIR=$(realpath $(dirname $0))
WORKSPACE_DIR=$(realpath $SCRIPT_DIR/../../)
SRC_DIR=$WORKSPACE_DIR/sharedlog-stream
EXP_DIR=$WORKSPACE_DIR/sharedlog-stream-experiments
FAAS_DIR=$WORKSPACE_DIR/boki
FAAS_BUILD_TYPE=release
# FAAS_BUILD_TYPE=debug
HELPER_SCRIPT=$WORKSPACE_DIR/research-helper-scripts/microservice_helper
USE_CACHE=1

MANAGER_HOST=$($HELPER_SCRIPT get-docker-manager-host --base-dir=$BASE_DIR)
ALL_HOSTS=$($HELPER_SCRIPT get-all-server-hosts --base-dir=$BASE_DIR)

ssh -q $MANAGER_HOST -- docker stack rm faas-test
sleep 40
for HOST in $ALL_HOSTS; do
    SSH_CMD="ssh -q $HOST -oStrictHostKeyChecking=no"
    scp -q $SCRIPT_DIR/kill-containers.sh $HOST:
    $SSH_CMD -- ./kill-containers.sh
done

scp -q $BASE_DIR/docker-compose-base.yml $MANAGER_HOST:~
# $HELPER_SCRIPT generate-docker-compose --base-dir=$BASE_DIR
scp -q $BASE_DIR/docker-compose.yml $MANAGER_HOST:~
scp -q $SCRIPT_DIR/docker-stack-wait.sh $MANAGER_HOST:~


ALL_SEQUENCER_HOSTS=$($HELPER_SCRIPT get-machine-with-label --machine-label=sequencer_node)
for HOST in $ALL_SEQUENCER_HOSTS; do
    SSH_CMD="ssh -q $HOST -oStrictHostKeyChecking=no"
    $SSH_CMD -- "sudo rm -rf /mnt/inmem/log_seq; \
	    sudo mkdir -p /mnt/inmem/log_seq; \
	    sudo rm -rf /mnt/storage_seq/journal; \
	    sudo mkdir -p /mnt/storage_seq/journal"
done

ALL_ENGINE_HOSTS=$($HELPER_SCRIPT get-machine-with-label --machine-label=engine_node)
for HOST in $ALL_ENGINE_HOSTS; do
    SSH_CMD="ssh -q $HOST -oStrictHostKeyChecking=no"
    $SSH_CMD -- "sudo rm -rf /mnt/inmem/log; sudo mkdir -p /mnt/inmem/log; \
	    sudo rm -rf /mnt/inmem/faas; sudo mkdir -p /mnt/inmem/faas; \
	    sudo mkdir -p /mnt/inmem/faas/output /mnt/inmem/faas/ipc"
done

ALL_STORAGE_HOSTS=$($HELPER_SCRIPT get-machine-with-label --machine-label=storage_node)
for HOST in $ALL_STORAGE_HOSTS; do
    SSH_CMD="ssh -q $HOST -oStrictHostKeyChecking=no"
    $SSH_CMD -- "sudo rm -rf /mnt/inmem/log || true; sudo mkdir -p /mnt/inmem/log; \
	    sudo rm -rf /mnt/storage/logdata; sudo mkdir -p /mnt/storage/logdata; \
	    sudo rm -rf /mnt/storage/journal; sudo mkdir -p /mnt/storage/journal;"
    $SSH_CMD -- 'sudo rm -rf /mnt/storage/redis; sudo mkdir -p /mnt/storage/redis; sudo chown $(id -u):$(id -g) /mnt/storage/redis' || true
    $SSH_CMD -- 'for ((i=1; i <=8; i++)); do sudo mkdir -p /mnt/storage/redis/$i; done'
done

ssh -q $MANAGER_HOST -- docker network rm faas-test_default
ssh -q $MANAGER_HOST -- SRC_DIR=$SRC_DIR FAAS_DIR=$FAAS_DIR EXP_DIR=$EXP_DIR USE_CACHE=${USE_CACHE} FAAS_BUILD_TYPE=$FAAS_BUILD_TYPE \
    docker stack deploy -c ~/docker-compose-base.yml -c ~/docker-compose.yml faas-test
ssh -q $MANAGER_HOST -- ./docker-stack-wait.sh faas-test
sleep 100

# for HOST in $ALL_ENGINE_HOSTS; do
#     ENGINE_CONTAINER_ID=$($HELPER_SCRIPT get-container-id --service faas-engine --machine-host $HOST)
#     echo 4096 | ssh -q $HOST -- sudo tee /sys/fs/cgroup/cpu,cpuacct/docker/$ENGINE_CONTAINER_ID/cpu.shares
# done
