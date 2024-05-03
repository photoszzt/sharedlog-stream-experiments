#!/bin/bash
set -euo pipefail
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
flushes=(50 25 10)
modes=(epoch 2pc)

q6_out_dir=$SCRIPT_DIR/../pub_data/micro/q6_varflush_16384buf/
q4_out_dir=$SCRIPT_DIR/../pub_data/micro/q4_varflush_16384buf/
for ((i=0; i < ${#flushes[@]}; ++i)); do
  f=${flushes[i]}
  q6_in_dir=$SCRIPT_DIR/q6_boki/4src_7/180s_0swarm_${f}ms_src${f}ms/
  for ((m=0; m < ${#modes[@]}; ++m)); do
    mode=${modes[m]}
    if [[ -d $q6_in_dir ]]; then
      python3 parse_e2e_latency.py \
      	--dir $q6_in_dir \
      	--out_stats $q6_out_dir/${mode}/${f}ms/ --app q6 --target ${mode}
      python3 parse_stats_single_exp.py \
      	--dir $q6_in_dir/ \
      	--out_stats $q6_out_dir/${mode}/${f}ms/ --app q6 --mode ${mode}
    fi
  done
done

for ((i=0; i < ${#flushes[@]}; ++i)); do
  f=${flushes[i]}
  q4_in_dir=$SCRIPT_DIR/q4_boki/4src_varflush_16384buf/180s_0swarm_${f}ms_src${f}ms/
  for ((m=0; m < ${#modes[@]}; ++m)); do
    mode=${modes[m]}
    if [[ -d $q4_in_dir ]]; then
      python3 parse_e2e_latency.py \
      	--dir $q4_in_dir \
      	--out_stats $q4_out_dir/${mode}/${f}ms/ --app q4 --target ${mode}
      python3 parse_stats_single_exp.py --dir $q4_in_dir/ --mode ${mode} \
              --app q4 --out_stats $q4_out_dir/${mode}/${f}ms/
    fi
  done
done
