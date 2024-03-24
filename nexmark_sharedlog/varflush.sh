#!/bin/bash
set -euo pipefail
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
flushes=(100 50 25 10)
modes=(epoch 2pc)

for ((i=0; i < ${#flushes[@]}; ++i)); do
  f=${flushes[i]}
  if [[ -d $SCRIPT_DIR/q6_boki/4src_4/180s_0swarm_${f}ms_src${f}ms/ ]]; then
    python3 parse_e2e_latency.py \
    	--dir $SCRIPT_DIR/q6_boki/4src_4/180s_0swarm_${f}ms_src${f}ms/ \
    	--out_stats $SCRIPT_DIR/../pub_data/micro/q6_varflush/epoch/${f}ms/ --app q6 --target epoch
  fi
  if [[ -d $SCRIPT_DIR/q6_boki/4src_5/180s_0swarm_${f}ms_src${f}ms/ ]]; then
    python3 parse_e2e_latency.py \
    	--dir $SCRIPT_DIR/q6_boki/4src_5/180s_0swarm_${f}ms_src${f}ms/ \
    	--out_stats $SCRIPT_DIR/../pub_data/micro/q6_varflush/2pc/${f}ms/ --app q6 --target 2pc
  fi
  if [[ -d $SCRIPT_DIR/q4_boki/4src_4/180s_0swarm_${f}ms_src${f}ms/ ]]; then
    python3 parse_e2e_latency.py \
    	--dir $SCRIPT_DIR/q4_boki/4src_4/180s_0swarm_${f}ms_src${f}ms/ \
    	--out_stats $SCRIPT_DIR/../pub_data/micro/q4_varflush/epoch/${f}ms/ --app q4 --target epoch
  fi
  if [[ -d $SCRIPT_DIR/q4_boki/4src_5/180s_0swarm_${f}ms_src${f}ms/ ]]; then
    python3 parse_e2e_latency.py \
    	--dir $SCRIPT_DIR/q4_boki/4src_5/180s_0swarm_${f}ms_src${f}ms/ \
    	--out_stats $SCRIPT_DIR/../pub_data/micro/q4_varflush/2pc/${f}ms/ --app q4 --target 2pc
  fi
done
