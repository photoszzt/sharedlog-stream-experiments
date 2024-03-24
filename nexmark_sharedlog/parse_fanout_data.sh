#!/bin/bash 
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd $SCRIPT_DIR
python3 parse_stats_single_exp.py --dir $SCRIPT_DIR/fanout_boki/4src_1/180s_0swarm_100ms_src10ms/ --mode epoch --app fanout --out_stats $SCRIPT_DIR../pub_data/micro/fanout/
python3 parse_stats_single_exp.py --dir $SCRIPT_DIR/fanout_boki/4src_1/180s_0swarm_100ms_src10ms/ --mode 2pc --app fanout --out_stats $SCRIPT_DIR../pub_data/micro/fanout/
python3 parse_fanout.py --dir $SCRIPT_DIR/fanout_boki/4src_1/180s_0swarm_100ms_src10ms/ --out_stats $SCRIPT_DIR../pub_data/micro/fanout/ --target 2pc
python3 parse_fanout.py --dir $SCRIPT_DIR/fanout_boki/4src_1/180s_0swarm_100ms_src10ms/ --out_stats $SCRIPT_DIR../pub_data/micro/fanout/ --target epoch
cd -
