#!/bin/bash
set -euo pipefail
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
OUT_DIR=$SCRIPT_DIR/../pub_data/fig10_fig11/q38_rerun/align_chkpt_kvrocks/
mkdir -p $OUT_DIR

mkdir -p $OUT_DIR/q1-180s-0swarm-100ms-src10ms/
mkdir -p $OUT_DIR/q2-180s-0swarm-100ms-src10ms/
mkdir -p $OUT_DIR/q3-180s-0swarm-100ms-src100ms/
mkdir -p $OUT_DIR/q4-180s-0swarm-100ms-src100ms/
mkdir -p $OUT_DIR/q5-180s-0swarm-100ms-src100ms/
mkdir -p $OUT_DIR/q6-180s-0swarm-100ms-src100ms/
mkdir -p $OUT_DIR/q7-180s-0swarm-100ms-src100ms/
mkdir -p $OUT_DIR/q8-180s-0swarm-100ms-src100ms/

for ((i=0; i < 3; i++)); do
  latency scan --prefix query1 --suffix .json.gz --output $OUT_DIR/q1-180s-0swarm-10ms-src10ms/ $SCRIPT_DIR/q1_boki/4src_2/180s_0swarm_100ms_src10ms/$i || true
  latency scan --prefix query2 --suffix .json.gz --output $OUT_DIR/q2-180s-0swarm-10ms-src10ms/ $SCRIPT_DIR/q2_boki/4src_2/180s_0swarm_100ms_src10ms/$i || true
  latency scan --prefix q3JoinTable --suffix .json.gz --output $OUT_DIR/q3-180s-0swarm-100ms-src100ms/ $SCRIPT_DIR/q3_boki/mem/4src_2/180s_0swarm_100ms_src100ms/$i/ || true
  latency scan --prefix q4Avg --suffix .json.gz --output $OUT_DIR/q4-180s-0swarm-100ms-src100ms/ $SCRIPT_DIR/q4_boki/4src_2/180s_0swarm_100ms_src100ms/$i || true
  latency scan --prefix q5maxbid --suffix .json.gz --output $OUT_DIR/q5-180s-0swarm-100ms-src100ms/ $SCRIPT_DIR/q5_boki/mem/4src_2/180s_0swarm_100ms_src100ms/$i || true
  latency scan --prefix q6Avg --suffix .json.gz --output $OUT_DIR/q6-180s-0swarm-100ms-src100ms/ $SCRIPT_DIR/q6_boki/4src_2/180s_0swarm_100ms_src100ms/$i || true
  # # latency scan --prefix q7JoinMaxBid --suffix .json.gz --output $OUT_DIR/q7-180s-0swarm-100ms-src100ms/ $SCRIPT_DIR/q7_boki/mem/4src_2/180s_0swarm_100ms_src100ms/$i
  latency scan --prefix q8JoinStream --suffix .json.gz --output $OUT_DIR/q8-180s-0swarm-100ms-src100ms/ $SCRIPT_DIR/q8_boki/mem/4src_2/180s_0swarm_100ms_src100ms/$i || true
done
