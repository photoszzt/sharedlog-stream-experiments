#!/bin/bash
set -euo pipefail
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
OUT_DIR=$SCRIPT_DIR/../pub_data/fig10_fig11/q38_rerun/50ms
mkdir -p $OUT_DIR

for ((i=1; i <= 2; i++)); do
  mkdir -p $OUT_DIR/q${i}-180s-0swarm-50ms-src10ms/
  mkdir -p $OUT_DIR/remote_2pc/q${i}-180s-0swarm-50ms-src10ms/
  mkdir -p $OUT_DIR/epoch/q${i}-180s-0swarm-50ms-src10ms/
done

for ((i=3; i <= 8; i++)); do
  mkdir -p $OUT_DIR/q${i}-180s-0swarm-50ms-src50ms/
  mkdir -p $OUT_DIR/remote_2pc/q${i}-180s-0swarm-50ms-src50ms/
  mkdir -p $OUT_DIR/epoch/q${i}-180s-0swarm-50ms-src50ms/
done

for ((i=0; i < 3; i++)); do
  echo "q1"
  INDIR=$SCRIPT_DIR/q1_boki/4src_1/180s_0swarm_50ms_src10ms/$i
  [[ -d $INDIR ]] && latency scan --prefix query1 --suffix .json.gz --output $OUT_DIR/q1-180s-0swarm-50ms-src10ms/ $INDIR
  echo "q2"
  INDIR=$SCRIPT_DIR/q2_boki/4src_2/180s_0swarm_50ms_src10ms/$i
  [[ -d $INDIR ]] && latency scan --prefix query2 --suffix .json.gz --output $OUT_DIR/q2-180s-0swarm-50ms-src10ms/ $INDIR
  echo "q3"
  INDIR=$SCRIPT_DIR/q3_boki/mem/4src_1/180s_0swarm_50ms_src50ms/$i/
  [[ -d $INDIR ]] && latency scan --prefix q3JoinTable --suffix .json.gz --output $OUT_DIR/q3-180s-0swarm-50ms-src50ms/ $INDIR
  echo "q4"
  INDIR=$SCRIPT_DIR/q4_boki/4src_1/180s_0swarm_50ms_src50ms/$i
  [[ -d $INDIR ]] && latency scan --prefix q4Avg --suffix .json.gz --output $OUT_DIR/q4-180s-0swarm-50ms-src50ms/ $INDIR
  echo "q5"
  INDIR=$SCRIPT_DIR/q5_boki/mem/4src_1/180s_0swarm_50ms_src50ms/$i
  [[ -d $INDIR ]] && latency scan --prefix q5maxbid --suffix .json.gz --output $OUT_DIR/q5-180s-0swarm-50ms-src50ms/ $INDIR
  echo "q6"
  INDIR=$SCRIPT_DIR/q6_boki/4src_1/180s_0swarm_50ms_src50ms/$i
  [[ -d $INDIR ]] && latency scan --prefix q6Avg --suffix .json.gz --output $OUT_DIR/q6-180s-0swarm-50ms-src50ms/ $INDIR
  echo "q7"
  INDIR=$SCRIPT_DIR/q7_boki/mem/4src_1/180s_0swarm_50ms_src50ms/$i
  [[ -d $INDIR ]] && latency scan --prefix q7JoinMaxBid --suffix .json.gz --output $OUT_DIR/q7-180s-0swarm-50ms-src50ms/ $INDIR
  echo "q8"
  INDIR=$SCRIPT_DIR/q8_boki/mem/4src_3/180s_0swarm_50ms_src50ms/$i
  [[ -d $INDIR ]] && latency scan --prefix q8JoinStream --suffix .json.gz --output $OUT_DIR/q8-180s-0swarm-50ms-src50ms/ $INDIR
done

for ((i=1; i <= 2; i++)); do
  mv $OUT_DIR/q${i}-180s-0swarm-50ms-src10ms/remote_2pc-* $OUT_DIR/remote_2pc/q${i}-180s-0swarm-50ms-src10ms/
  mv $OUT_DIR/q${i}-180s-0swarm-50ms-src10ms/eo-* $OUT_DIR/epoch/q${i}-180s-0swarm-50ms-src10ms/
done

for ((i=3; i <= 8; i++)); do
  mv $OUT_DIR/q${i}-180s-0swarm-50ms-src50ms/remote_2pc-* $OUT_DIR/remote_2pc/q${i}-180s-0swarm-50ms-src50ms/
  mv $OUT_DIR/q${i}-180s-0swarm-50ms-src50ms/eo-* $OUT_DIR/epoch/q${i}-180s-0swarm-50ms-src50ms/
done
