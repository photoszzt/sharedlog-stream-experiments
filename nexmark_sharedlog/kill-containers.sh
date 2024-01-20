#!/bin/bash
containers=$(docker ps | awk '{if(NR>1) print $1}')
# loop through all containers
for container in $containers; do
    ps awx | grep containerd-shim | grep $container | awk '{ print $1 }' | sudo xargs kill -9
done
