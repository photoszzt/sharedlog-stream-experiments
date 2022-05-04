#!/bin/bash
/mnt/efs/workspace/research-helper-scripts/microservice_helper start-machines --use-spot-instances

// tps 100
TPS=100
DURATION=180
WARM_DURATION=60
WARM_EVENTS=6000
EVENTS=18000
./produce_bench.sh --exp_dir 180s_60swarm/1p_1t_1par_5ms_${TPS}tps/100b --ncon 1 --nprod 1 --duration $DURATION \
    --events_num $EVENTS --num_par 1 --payload payload-100b.data --tps $TPS \
    --warm_duration $WARM_DURATION --warm_events $WARM_EVENTS
./produce_bench.sh --exp_dir 180s_60swarm/1p_1t_1par_5ms_${TPS}tps/1kb --ncon 1 --nprod 1 --duration $DURATION \
    --events_num $EVENTS --num_par 1 --payload payload-1Kb.data --tps $TPS \
    --warm_duration $WARM_DURATION --warm_events $WARM_EVENTS
./produce_bench.sh --exp_dir 180s_60swarm/1p_1t_1par_5ms_${TPS}tps/4kb --ncon 1 --nprod 1 --duration $DURATION \
    --events_num $EVENTS --num_par 1 --payload payload-4Kb.data --tps $TPS \
    --warm_duration $WARM_DURATION --warm_events $WARM_EVENTS
./produce_bench.sh --exp_dir 180s_60swarm/1p_1t_1par_5ms_${TPS}tps/16kb --ncon 1 --nprod 1 --duration $DURATION \
    --events_num $EVENTS --num_par 1 --payload payload-16Kb.data --tps $TPS \
    --warm_duration $WARM_DURATION --warm_events $WARM_EVENTS

// tps 1000
TPS=1000
DURATION=180
WARM_DURATION=60
WARM_EVENTS=60000
EVENTS=180000
./produce_bench.sh --exp_dir 180s_60swarm/1p_1t_1par_5ms_${TPS}tps/100b --ncon 1 --nprod 1 --duration $DURATION \
    --events_num $EVENTS --num_par 1 --payload payload-100b.data --tps $TPS \
    --warm_duration $WARM_DURATION --warm_events $WARM_EVENTS
./produce_bench.sh --exp_dir 180s_60swarm/1p_1t_1par_5ms_${TPS}tps/1kb --ncon 1 --nprod 1 --duration $DURATION \
    --events_num $EVENTS --num_par 1 --payload payload-1Kb.data --tps $TPS \
    --warm_duration $WARM_DURATION --warm_events $WARM_EVENTS
./produce_bench.sh --exp_dir 180s_60swarm/1p_1t_1par_5ms_${TPS}tps/4kb --ncon 1 --nprod 1 --duration $DURATION \
    --events_num $EVENTS --num_par 1 --payload payload-4Kb.data --tps $TPS \
    --warm_duration $WARM_DURATION --warm_events $WARM_EVENTS
./produce_bench.sh --exp_dir 180s_60swarm/1p_1t_1par_5ms_${TPS}tps/16kb --ncon 1 --nprod 1 --duration $DURATION \
    --events_num $EVENTS --num_par 1 --payload payload-16Kb.data --tps $TPS \
    --warm_duration $WARM_DURATION --warm_events $WARM_EVENTS

// tps 10000
TPS=10000
DURATION=180
WARM_DURATION=60
WARM_EVENTS=600000
EVENTS=1800000
./produce_bench.sh --exp_dir 180s_60swarm/1p_1t_1par_5ms_${TPS}tps/100b --ncon 1 --nprod 1 --duration $DURATION \
    --events_num $EVENTS --num_par 1 --payload payload-100b.data --tps $TPS \
    --warm_duration $WARM_DURATION --warm_events $WARM_EVENTS
./produce_bench.sh --exp_dir 180s_60swarm/1p_1t_1par_5ms_${TPS}tps/1kb --ncon 1 --nprod 1 --duration $DURATION \
    --events_num $EVENTS --num_par 1 --payload payload-1Kb.data --tps $TPS \
    --warm_duration $WARM_DURATION --warm_events $WARM_EVENTS
./produce_bench.sh --exp_dir 180s_60swarm/1p_1t_1par_5ms_${TPS}tps/4kb --ncon 1 --nprod 1 --duration $DURATION \
    --events_num $EVENTS --num_par 1 --payload payload-4Kb.data --tps $TPS \
    --warm_duration $WARM_DURATION --warm_events $WARM_EVENTS
./produce_bench.sh --exp_dir 180s_60swarm/1p_1t_1par_5ms_${TPS}tps/16kb --ncon 1 --nprod 1 --duration $DURATION \
    --events_num $EVENTS --num_par 1 --payload payload-16Kb.data --tps $TPS \
    --warm_duration $WARM_DURATION --warm_events $WARM_EVENTS

/mnt/efs/workspace/research-helper-scripts/microservice_helper stop-machines
