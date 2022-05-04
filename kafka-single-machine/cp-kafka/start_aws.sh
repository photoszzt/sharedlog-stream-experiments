#!/bin/bash

rm -rf /mnt/efs/workspace/kdata1/*
rm -rf /mnt/efs/workspace/kdata2/*
rm -rf /mnt/efs/workspace/kdata3/*
mkdir -p /mnt/efs/workspace/kdata3 
mkdir -p /mnt/efs/workspace/kdata2 
mkdir -p /mnt/efs/workspace/kdata1 
sudo chmod g+w,o+w /mnt/efs/workspace/kdata3 /mnt/efs/workspace/kdata2 /mnt/efs/workspace/kdata1
docker-compose -f ./docker-compose-aws.yml up
