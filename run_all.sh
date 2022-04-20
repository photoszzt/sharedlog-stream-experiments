#!/bin/bash

DURATION=1500
EVENTS_NUM=6250000
TRAN_DIR=4_2xlarge_tran_${DURATION}_6.25M
NORM_DIR=4_2xlarge_${DURATION}_6.25M
cd q3_boki
cd mongodb
../../../workspace/research-helper-scripts/microservice_helper start-machines --use-spot-instances
cd ..
cp mongodb/machines.json mem
cd ..
cp q3_boki/mongodb/machines.json ./q1_boki/
cp q3_boki/mongodb/machines.json ./q2_boki/
cp q3_boki/mongodb/machines.json ./q5_boki/mem
cp q3_boki/mongodb/machines.json ./q5_boki/mongodb
cp q3_boki/mongodb/machines.json ./q7_boki/mem
cp q3_boki/mongodb/machines.json ./q7_boki/mongodb
cp q3_boki/mongodb/machines.json ./q8_boki/mem
cp q3_boki/mongodb/machines.json ./q8_boki/mongodb

# cd q1_boki
# ./run_once.sh ./4src/$NORM_DIR false $DURATION $EVENTS_NUM
# ./run_once.sh ./4src/$TRAN_DIR/ true $DURATION $EVENTS_NUM
# cd ..
# 
# cd q2_boki
# ./run_once.sh ./4src/$NORM_DIR false $DURATION $EVENTS_NUM
# ./run_once.sh ./4src/$TRAN_DIR/ true $DURATION $EVENTS_NUM
# cd ..

cd q3_boki
cd mem
./run_once.sh ./4src/$NORM_DIR false $DURATION $EVENTS_NUM
./run_once.sh ./4src/$TRAN_DIR/ true $DURATION $EVENTS_NUM
cd ..
cd mongodb
./run_once.sh ./4src/$NORM_DIR false $DURATION $EVENTS_NUM
./run_once.sh ./4src/$TRAN_DIR/ true $DURATION $EVENTS_NUM
cd ..
cd ..

cd q5_boki
cd mem
./run_once.sh ./4src/${NORM_DIR}/ false $DURATION $EVENTS_NUM
./run_once.sh ./4src/${TRAN_DIR}/ true $DURATION $EVENTS_NUM
cd ..
cd mongodb
./run_once.sh ./4src/${NORM_DIR}/ false $DURATION $EVENTS_NUM
./run_once.sh ./4src/${TRAN_DIR}/ true $DURATION $EVENTS_NUM
cd ..
cd ..

# cd q7_boki
# cd mem
# ./run_once.sh ./4src/${NORM_DIR}/ false
# ./run_once.sh ./4src/${TRAN_DIR}/ true
# cd ..
# cd mongodb
# ./run_once.sh ./4src/${NORM_DIR}/ false
# ./run_once.sh ./4src/${TRAN_DIR}/ true
# cd ..
# cd ..

cd q8_boki
cd mem
./run_once.sh ./4src/${NORM_DIR} false $DURATION $EVENTS_NUM
./run_once.sh ./4src/${TRAN_DIR}/ true $DURATION $EVENTS_NUM
cd ..
cd mongodb
./run_once.sh ./4src/$NORM_DIR false $DURATION $EVENTS_NUM
./run_once.sh ./4src/$TRAN_DIR/ true $DURATION $EVENTS_NUM
cd ..
cd ..

cd q3_boki
cd mongodb
../../../workspace/research-helper-scripts/microservice_helper stop-machines
cd ..
rm mem/machines.json
cd ..

rm q1_boki/machines.json
rm q2_boki/machines.json

rm q5_boki/mem/machines.json
rm q5_boki/mongodb/machines.json

rm q7_boki/mem/machines.json
rm q7_boki/mongodb/machines.json

rm q8_boki/mem/machines.json
rm q8_boki/mongodb/machines.json
