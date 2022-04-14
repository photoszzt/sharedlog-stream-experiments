#!/bin/bash
cd q8_boki
cd mongodb
../../../workspace/research-helper-scripts/microservice_helper start-machines --use-spot-instances
cd ..
cp mongodb/machines.json mem
cd mem
mkdir -p 4src/4_2xlarge_tran
mkdir -p 4src/4_2xlarge
./run_once.sh ./4src/4_2xlarge_tran/ true && ./run_once.sh ./4src/4_2xlarge false
cd ..
cd mongodb
mkdir -p 4src/4_2xlarge_tran
mkdir -p 4src/4_2xlarge
./run_once.sh ./4src/4_2xlarge_tran/ true && ./run_once.sh ./4src/4_2xlarge false
../../../workspace/research-helper-scripts/microservice_helper stop-machines
cd ..
rm mem/machines.json
cd ..
