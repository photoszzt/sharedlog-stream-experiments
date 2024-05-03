#!/bin/bash
set -euo pipefail
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
flushes=(3 5 7 10)
modes=(epoch 2pc)

for ((i=0; i < ${#flushes[@]}; ++i)); do
  f=${flushes[i]}
  if [[ -d $SCRIPT_DIR/q8_boki/mem/4src_varflush/180s_0swarm_${f}ms_src${f}ms/ ]]; then
    python3 parse_e2e_latency.py \
    	--dir $SCRIPT_DIR/q8_boki/mem/4src_varflush/180s_0swarm_${f}ms_src${f}ms/ \
    	--out_stats $SCRIPT_DIR/../pub_data/micro/q8_varflush/epoch/${f}ms/ --app q8 --target epoch
  fi
  if [[ -d $SCRIPT_DIR/q8_boki/mem/4src_varflush/180s_0swarm_${f}ms_src${f}ms/ ]]; then
    python3 parse_e2e_latency.py \
    	--dir $SCRIPT_DIR/q8_boki/mem/4src_varflush/180s_0swarm_${f}ms_src${f}ms/ \
    	--out_stats $SCRIPT_DIR/../pub_data/micro/q8_varflush/2pc/${f}ms/ --app q8 --target 2pc
  fi
done

for ((i=0; i < ${#flushes[@]}; ++i)); do
  f=${flushes[i]}
  if [[ -d $SCRIPT_DIR/q8_boki/mem/4src_varflush/180s_0swarm_${f}ms_src${f}ms/ ]]; then
    python3 parse_stats_single_exp.py --dir $SCRIPT_DIR/q8_boki/mem/4src_varflush/180s_0swarm_${f}ms_src${f}ms/ --mode 2pc \
	    --app q8 --out_stats ../pub_data/micro/q8_varflush/2pc/${f}ms/
  fi
  if [[ -d $SCRIPT_DIR/q8_boki/mem/4src_varflush/180s_0swarm_${f}ms_src${f}ms/ ]]; then
    python3 parse_stats_single_exp.py --dir $SCRIPT_DIR/q8_boki/mem/4src_varflush/180s_0swarm_${f}ms_src${f}ms/ --mode epoch \
	    --app q8 --out_stats ../pub_data/micro/q8_varflush/epoch/${f}ms/
  fi
done
