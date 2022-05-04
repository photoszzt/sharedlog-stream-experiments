#!/bin/bash
NUM_EVENTS=25000000
/mnt/efs/workspace/research-helper-scripts/microservice_helper start-machines --use-spot-instances
./produce_bench.sh --exp_dir 1p_1t_1par_100b --ncon 1 --nprod 1 --duration 120 --events_num 25000000 --num_par 1 --payload payload-100b.data
./produce_bench.sh --exp_dir 1p_1t_1par_1kb --ncon 1 --nprod 1 --duration 120 --events_num 25000000 --num_par 1 --payload payload-1Kb.data
./produce_bench.sh --exp_dir 1p_1t_1par_4kb --ncon 1 --nprod 1 --duration 120 --events_num 25000000 --num_par 1 --payload payload-4Kb.data
./produce_bench.sh --exp_dir 1p_1t_1par_16kb --ncon 1 --nprod 1 --duration 120 --events_num 25000000 --num_par 1 --payload payload-16Kb.data
/mnt/efs/workspace/research-helper-scripts/microservice_helper stop-machines
