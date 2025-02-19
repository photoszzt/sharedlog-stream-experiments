#!/bin/bash
set -euo pipefail
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
OUT_DIR=$SCRIPT_DIR/../pub_data/fig10_fig11/q38_rerun/align_chkpt_kvrocks2/
mkdir -p $OUT_DIR

# mkdir -p $OUT_DIR/q1-180s-0swarm-100ms-src10ms/
# rm -rf $OUT_DIR/q1-180s-0swarm-100ms-src10ms/*
# mkdir -p $OUT_DIR/q2-180s-0swarm-100ms-src10ms/
# rm -rf $OUT_DIR/q2-180s-0swarm-100ms-src10ms/*
# for ((i=3; i <= 8; i++)); do
#   mkdir -p $OUT_DIR/q${i}-180s-0swarm-100ms-src100ms/
#   rm -rf $OUT_DIR/q${i}-180s-0swarm-100ms-src100ms/*
# done

function update_mtime() {
  sub_in_dir=$(ls -d -- $INDIR/*/)
  for d in $sub_in_dir; do
    touch $d
    sleep 1
  done
}

for ((i=0; i < 6; i++)); do
  # INDIR=$SCRIPT_DIR/q1_boki/4src_3/180s_0swarm_100ms_src10ms/$i
  # [[ -d $INDIR ]] && update_mtime
  # INDIR=$SCRIPT_DIR/q2_boki/4src_3/180s_0swarm_100ms_src10ms/$i
  # [[ -d $INDIR ]] && update_mtime
  INDIR=$SCRIPT_DIR/q3_boki/mem/4src_3/180s_0swarm_100ms_src100ms/$i/
  [[ -d $INDIR ]] && update_mtime
  INDIR=$SCRIPT_DIR/q4_boki/4src_3/180s_0swarm_100ms_src100ms/$i
  [[ -d $INDIR ]] && update_mtime
  INDIR=$SCRIPT_DIR/q5_boki/mem/4src_3/180s_0swarm_100ms_src100ms/$i
  [[ -d $INDIR ]] && update_mtime
  INDIR=$SCRIPT_DIR/q6_boki/4src_3/180s_0swarm_100ms_src100ms/$i
  [[ -d $INDIR ]] && update_mtime
  INDIR=$SCRIPT_DIR/q7_boki/mem_nosync/4src_3/180s_0swarm_100ms_src100ms_comm100ms/$i
  [[ -d $INDIR ]] && update_mtime
  INDIR=$SCRIPT_DIR/q8_boki/mem/4src_3/180s_0swarm_100ms_src100ms/$i
  [[ -d $INDIR ]] && update_mtime
done
