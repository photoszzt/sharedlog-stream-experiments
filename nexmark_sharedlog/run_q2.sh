#!/bin/bash
DURATION=600
EVENTS_NUM=12500000
TRAN_DIR=4_2xlarge_tran_${DURATION}_12.5M
NORM_DIR=4_2xlarge_${DURATION}_12.5M

cd q2_boki
../../workspace/research-helper-scripts/microservice_helper start-machines --use-spot-instances
./run_once.sh --app q2 --exp_dir ./4src/$NORM_DIR/ --tran false --duration $DURATION --events_num $EVENTS_NUM --use_mongodb false
./run_once.sh --app q2 --exp_dir ./4src/$TRAN_DIR/ --tran true  --duration $DURATION --events_num $EVENTS_NUM --use_mongodb false
../../workspace/research-helper-scripts/microservice_helper stop-machines
cd ..
