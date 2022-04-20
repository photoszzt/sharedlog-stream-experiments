#!/bin/bash
cd q1_boki
../../workspace/research-helper-scripts/microservice_helper start-machines --use-spot-instances
./run_once.sh ./4src/4_2xlarge_tran_0_12.5M/ true 0 12500000
./run_once.sh ./4src/4_2xlarge_0_12.5M/ false 0 12500000
# ../../workspace/research-helper-scripts/microservice_helper stop-machines
# cd ..
# cd ..
