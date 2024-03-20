#!/bin/bash
set -euo pipefail
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
flushes=(100 50 25)
modes=(epoch 2pc)

for ((i=0; i < ${#flushes[@]}; ++i)); do
  f=${flushes[i]}
  for ((j=0; j < ${#modes[@]}; ++j)); do
    m=${modes[j]}
    python3 parse_e2e_latency.py \
    	--dir $SCRIPT_DIR/q6_boki/4src_4/180s_0swarm_${f}ms_src${f}ms/ \
    	--out_stats $SCRIPT_DIR/../pub_data/micro/q6_varflush/${m}/${f}ms/ --app q6 --target ${m}
  done
done
