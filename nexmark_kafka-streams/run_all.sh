#!/bin/bash
../../workspace/research-helper-scripts/microservice_helper start-machines --use-spot-instances
DURATION=200
./nexmark.sh --app q1 --exp_dir ./q1/4src/4_2xlarge_tran_${DURATION}/ --nins 4 --nsrc 4 --serde msgp --duration $DURATION 
./nexmark.sh --app q2 --exp_dir ./q2/4src/4_2xlarge_tran_${DURATION}/ --nins 4 --nsrc 4 --serde msgp --duration $DURATION 
./nexmark.sh --app q3 --exp_dir ./q3/4src/4_2xlarge_tran_${DURATION}/ --nins 4 --nsrc 4 --serde msgp --duration $DURATION 
./nexmark.sh --app q5 --exp_dir ./q5/4src/4_2xlarge_tran_${DURATION}/ --nins 4 --nsrc 4 --serde msgp --duration $DURATION 
# ./nexmark.sh --app q7 --exp_dir ./q7/4src/4_2xlarge_tran/ --nins 4 --nsrc 4 --serde msgp --duration 300
./nexmark.sh --app q8 --exp_dir ./q8/4src/4_2xlarge_tran_${DURATION}/ --nins 4 --nsrc 4 --serde msgp --duration $DURATION

../../workspace/research-helper-scripts/microservice_helper stop-machines
