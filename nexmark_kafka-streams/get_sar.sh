#!/bin/bash
DIR=$1
APP=$2
it=(app source broker)
for ((j=0; j<${#it[@]}; j++)); do 
    mkdir -p ./sar_stats/$APP/${it[j]}
    for ((i=0; i<3; i++)); do 
        python3 parse_sar.py \
            --dir $DIR/$i \
            --target_dir ${it[j]}_sar --out_dir ./sar_stats/$APP/${it[j]}/
    done
done
