#!/bin/bash
cd q5_boki
cd mem
../../../workspace/research-helper-scripts/microservice_helper start-machines --use-spot-instances
mkdir -p 4src/4_2xlarge_tran
mkdir -p 4src/4_2xlarge
./run_once.sh ./4src/4_2xlarge_tran/ true && ./run_once.sh ./4src/4_2xlarge false
../../../workspace/research-helper-scripts/microservice_helper stop-machines
cd ..
cd mongodb
../../../workspace/research-helper-scripts/microservice_helper start-machines --use-spot-instances
mkdir -p 4src/4_2xlarge_tran
mkdir -p 4src/4_2xlarge
./run_once.sh ./4src/4_2xlarge_tran/ true && ./run_once.sh ./4src/4_2xlarge false
../../../workspace/research-helper-scripts/microservice_helper stop-machines
cd ..
cd ..
