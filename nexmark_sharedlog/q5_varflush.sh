#!/bin/bash
set -euo pipefail
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
flushes=(25 10 5)
modes=(epoch 2pc)

for ((i=0; i < ${#flushes[@]}; ++i)); do
  f=${flushes[i]}
  if [[ -d $SCRIPT_DIR/q5_boki/mem/4src_5/180s_0swarm_${f}ms_src${f}ms/ ]]; then
    python3 parse_e2e_latency.py \
    	--dir $SCRIPT_DIR/q5_boki/mem/4src_5/180s_0swarm_${f}ms_src${f}ms/ \
    	--out_stats $SCRIPT_DIR/../pub_data/micro/q5_varflush/epoch/${f}ms/ --app q5 --target epoch
  fi
  if [[ -d $SCRIPT_DIR/q5_boki/mem/4src_5/180s_0swarm_${f}ms_src${f}ms/ ]]; then
    python3 parse_e2e_latency.py \
    	--dir $SCRIPT_DIR/q5_boki/mem/4src_5/180s_0swarm_${f}ms_src${f}ms/ \
    	--out_stats $SCRIPT_DIR/../pub_data/micro/q5_varflush/2pc/${f}ms/ --app q5 --target 2pc
  fi
done

for ((i=0; i < ${#flushes[@]}; ++i)); do
  f=${flushes[i]}
  if [[ -d $SCRIPT_DIR/q5_boki/mem/4src_5/180s_0swarm_${f}ms_src${f}ms/ ]]; then
    python3 parse_stats_single_exp.py --dir $SCRIPT_DIR/q5_boki/mem/4src_5/180s_0swarm_${f}ms_src${f}ms/ --mode 2pc \
	    --app q5 --out_stats ../pub_data/micro/q5_varflush/2pc/${f}ms/
  fi
  if [[ -d $SCRIPT_DIR/q5_boki/mem/4src_5/180s_0swarm_${f}ms_src${f}ms/ ]]; then
    python3 parse_stats_single_exp.py --dir $SCRIPT_DIR/q5_boki/mem/4src_5/180s_0swarm_${f}ms_src${f}ms/ --mode epoch \
	    --app q5 --out_stats ../pub_data/micro/q5_varflush/epoch/${f}ms/
  fi
done
