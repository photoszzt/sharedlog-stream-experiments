#!/bin/bash
set -x

BASE_DIR=$(realpath $(dirname $0))
SRC_DIR=/mnt/efs/workspace/sharedlog-stream
FAAS_DIR=/mnt/efs/workspace/boki
FAAS_BUILD_TYPE=release
# FAAS_BUILD_TYPE=debug
HELPER_SCRIPT=/mnt/efs/workspace/research-helper-scripts/microservice_helper

MANAGER_HOST=$($HELPER_SCRIPT get-docker-manager-host --base-dir=$BASE_DIR)
CLIENT_HOST=$($HELPER_SCRIPT get-client-host --base-dir=$BASE_DIR)
ENTRY_HOST=$($HELPER_SCRIPT get-service-host --base-dir=$BASE_DIR --service=faas-gateway)
ALL_HOSTS=$($HELPER_SCRIPT get-all-server-hosts --base-dir=$BASE_DIR)


scp -q $BASE_DIR/docker-compose-base.yml $MANAGER_HOST:~
$HELPER_SCRIPT generate-docker-compose --base-dir=$BASE_DIR
scp -q $BASE_DIR/docker-compose.yml $MANAGER_HOST:~

ssh -q $MANAGER_HOST -- docker stack rm faas-test

sleep 40

MONGO_HOSTS=$($HELPER_SCRIPT get-machine-with-label --base-dir=$BASE_DIR --machine-label=mongo_node)
for HOST in $MONGO_HOSTS; do
    ssh -q $HOST -- sudo rm -rf /mnt/storage/mdata
    ssh -q $HOST -- sudo mkdir -p /mnt/storage/mdata 
    ssh -q $HOST -- sudo chown ubuntu:ubuntu /mnt/storage/mdata
    ssh -q $HOST -- sudo chmod g+w,o+w /mnt/storage/mdata
    ssh -q $HOST -- echo "ubuntu hard fsize unlimited" | sudo tee -a /etc/security/limits.conf
    ssh -q $HOST -- echo "ubuntu soft fsize unlimited" | sudo tee -a /etc/security/limits.conf
    ssh -q $HOST -- echo "ubuntu hard cpu unlimited" | sudo tee -a /etc/security/limits.conf
    ssh -q $HOST -- echo "ubuntu soft cpu unlimited" | sudo tee -a /etc/security/limits.conf
    ssh -q $HOST -- echo "ubuntu soft as unlimited" | sudo tee -a /etc/security/limits.conf
    ssh -q $HOST -- echo "ubuntu hard as unlimited" | sudo tee -a /etc/security/limits.conf
    ssh -q $HOST -- echo "ubuntu soft memlock unlimited" | sudo tee -a /etc/security/limits.conf
    ssh -q $HOST -- echo "ubuntu hard memlock unlimited" | sudo tee -a /etc/security/limits.conf
    ssh -q $HOST -- echo "ubuntu hard nofile 64000" | sudo tee -a /etc/security/limits.conf
    ssh -q $HOST -- echo "ubuntu soft nofile 64000" | sudo tee -a /etc/security/limits.conf
    ssh -q $HOST -- echo "ubuntu hard nproc 64000" | sudo tee -a /etc/security/limits.conf
    ssh -q $HOST -- echo "ubuntu soft nproc 64000" | sudo tee -a /etc/security/limits.conf
done

ALL_SEQUENCER_HOSTS=$($HELPER_SCRIPT get-machine-with-label --machine-label=sequencer_node)
for HOST in $ALL_SEQUENCER_HOSTS; do
    ssh -q $HOST -- sudo rm -rf /mnt/inmem/log
    ssh -q $HOST -- sudo mkdir -p /mnt/inmem/log
    ssh -q $HOST -- sudo rm -rf /mnt/storage/journal
    ssh -q $HOST -- sudo mkdir -p /mnt/storage/journal
done

ALL_ENGINE_HOSTS=$($HELPER_SCRIPT get-machine-with-label --machine-label=engine_node)
for HOST in $ALL_ENGINE_HOSTS; do
    ssh -q $HOST -- sudo rm -rf /mnt/inmem/log
    ssh -q $HOST -- sudo mkdir -p /mnt/inmem/log
    ssh -q $HOST -- sudo rm -rf /mnt/inmem/faas
    ssh -q $HOST -- sudo mkdir -p /mnt/inmem/faas
    ssh -q $HOST -- sudo mkdir -p /mnt/inmem/faas/output /mnt/inmem/faas/ipc
done

ALL_STORAGE_HOSTS=$($HELPER_SCRIPT get-machine-with-label --machine-label=storage_node)
for HOST in $ALL_STORAGE_HOSTS; do
    ssh -q $HOST -- sudo rm -rf /mnt/inmem/log
    ssh -q $HOST -- sudo mkdir -p /mnt/inmem/log
    ssh -q $HOST -- sudo rm -rf /mnt/storage/logdata
    ssh -q $HOST -- sudo mkdir -p /mnt/storage/logdata
    ssh -q $HOST -- sudo rm -rf /mnt/storage/journal
    ssh -q $HOST -- sudo mkdir -p /mnt/storage/journal
done

ssh -q $MANAGER_HOST -- docker network rm faas-test_default
ssh -q $MANAGER_HOST -- SRC_DIR=$SRC_DIR FAAS_DIR=$FAAS_DIR FAAS_BUILD_TYPE=$FAAS_BUILD_TYPE \
    docker stack deploy \
    -c ~/docker-compose-base.yml -c ~/docker-compose.yml faas-test
sleep 100

for HOST in $ALL_ENGINE_HOSTS; do
    ENGINE_CONTAINER_ID=$($HELPER_SCRIPT get-container-id --service faas-engine --machine-host $HOST)
    echo 4096 | ssh -q $HOST -- sudo tee /sys/fs/cgroup/cpu,cpuacct/docker/$ENGINE_CONTAINER_ID/cpu.shares
done

sleep 10
