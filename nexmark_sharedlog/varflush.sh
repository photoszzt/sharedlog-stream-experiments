#!/bin/bash
set -euo pipefail
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
flushes=(100 50 25 10)
modes=(epoch 2pc)

for ((i=0; i < ${#flushes[@]}; ++i)); do
  f=${flushes[i]}
  for ((j=0; j < ${#modes[@]}; ++j)); do
    m=${modes[j]}
    if [[ -d $SCRIPT_DIR/q6_boki/4src_4/180s_0swarm_${f}ms_src${f}ms/ ]]; then
      python3 parse_e2e_latency.py \
      	--dir $SCRIPT_DIR/q6_boki/4src_4/180s_0swarm_${f}ms_src${f}ms/ \
      	--out_stats $SCRIPT_DIR/../pub_data/micro/q6_varflush/${m}/${f}ms/ --app q6 --target ${m}
    fi
    if [[ -d $SCRIPT_DIR/q4_boki/4src_4/180s_0swarm_${f}ms_src${f}ms/ ]]; then
      python3 parse_e2e_latency.py \
      	--dir $SCRIPT_DIR/q4_boki/4src_4/180s_0swarm_${f}ms_src${f}ms/ \
      	--out_stats $SCRIPT_DIR/../pub_data/micro/q4_varflush/${m}/${f}ms/ --app q4 --target ${m}
    fi
    if [[ -d $SCRIPT_DIR/q7_boki/mem_nosync/4src_4/180s_0swarm_${f}ms_src${f}ms_comm${f}ms/ ]]; then
      python3 parse_e2e_latency.py \
      	--dir $SCRIPT_DIR/q7_boki/mem_nosync/4src_4/180s_0swarm_${f}ms_src${f}ms_comm${f}ms/ \
      	--out_stats $SCRIPT_DIR/../pub_data/micro/q7_varflush/${m}/${f}ms/ --app q7 --target ${m}
    fi
  done
done
