#!/bin/bash
set -euo pipefail
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
flushes=(50 25 10)
modes=(epoch remote_2pc)

parse_varflush() {
  out_dir=$2
  in_path=$1
  app=$3
  for ((i=0; i < ${#flushes[@]}; ++i)); do
    f=${flushes[i]}
    in_dir=$in_path/180s_0swarm_${f}ms_src${f}ms/
    for ((m=0; m < ${#modes[@]}; ++m)); do
      mode=${modes[m]}
      if [[ -d $in_dir ]]; then
        python3 parse_e2e_latency.py \
        	--dir $in_dir \
        	--out_stats $out_dir/${mode}/${f}ms/ --app $app --target ${mode}
        # python3 parse_stats_single_exp.py --dir $in_dir/ --mode ${mode} \
        #         --app $app --out_stats $out_dir/${mode}/${f}ms/
      fi
    done
  done
}

parse_varflush_q12() {
  out_dir=$2
  in_path=$1
  app=$3
  for ((i=0; i < ${#flushes[@]}; ++i)); do
    f=${flushes[i]}
    in_dir=$in_path/180s_0swarm_${f}ms_src10ms/
    for ((m=0; m < ${#modes[@]}; ++m)); do
      mode=${modes[m]}
      if [[ -d $in_dir ]]; then
        python3 parse_e2e_latency.py \
        	--dir $in_dir \
        	--out_stats $out_dir/${mode}/${f}ms/ --app $app --target ${mode}
        # python3 parse_stats_single_exp.py --dir $in_dir/ --mode ${mode} \
        #         --app $app --out_stats $out_dir/${mode}/${f}ms/
      fi
    done
  done
}

# q1_out_dir=$SCRIPT_DIR/../pub_data/micro/q1_varflush/
# q1_in=$SCRIPT_DIR/q1_boki/4src_varflush/
# parse_varflush $q1_in $q1_out_dir q1

q2_out_dir=$SCRIPT_DIR/../pub_data/micro/q2_varflush/
q2_in=$SCRIPT_DIR/q2_boki/4src_varflush/
parse_varflush_q12 $q2_in $q2_out_dir q2

q3_out_dir=$SCRIPT_DIR/../pub_data/micro/q3_varflush/
q3_in=$SCRIPT_DIR/q3_boki/mem/4src_varflush/
parse_varflush $q3_in $q3_out_dir q3

q4_out_dir=$SCRIPT_DIR/../pub_data/micro/q4_varflush/
q4_in=$SCRIPT_DIR/q4_boki/4src_varflush
parse_varflush $q4_in $q4_out_dir q4

q5_out_dir=$SCRIPT_DIR/../pub_data/micro/q5_varflush/
q5_in=$SCRIPT_DIR/q5_boki/mem/4src_varflush/
parse_varflush $q5_in $q5_out_dir q5

q6_out_dir=$SCRIPT_DIR/../pub_data/micro/q6_varflush/
parse_varflush $SCRIPT_DIR/q6_boki/4src_varflush $q6_out_dir q6

q7_out_dir=$SCRIPT_DIR/../pub_data/micro/q7_varflush/
q7_in=$SCRIPT_DIR/q7_boki/mem/4src_varflush
parse_varflush $q7_in $q7_out_dir q7

q8_out_dir=$SCRIPT_DIR/../pub_data/micro/q8_varflush/
q8_in=$SCRIPT_DIR/q8_boki/mem/4src_varflush
parse_varflush $q8_in $q8_out_dir q8
