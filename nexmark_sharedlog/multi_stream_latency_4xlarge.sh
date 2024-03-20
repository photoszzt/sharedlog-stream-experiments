#!/bin/bash
set -euo pipefail
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

extra=0
OUT_DIR=$SCRIPT_DIR/../pub_data/micro/multi_instances_${extra}extra_kvrocks_4xlarge/
mkdir -p $OUT_DIR
instances=(8 16 28 32 40)
for j in ${instances[@]}; do
  DIR=$OUT_DIR/${j}ins/q8-180s-0swarm-100ms-src100ms
  mkdir -p $DIR
  for ((i=0; i < 6; i++)); do
    INDIR=$SCRIPT_DIR/q8_boki/mem_4node_${j}ins_4xlarge/${j}src_4node_${j}ins_${extra}extra_kvrocks/180s_0swarm_100ms_src100ms/$i
    if [[ -d $INDIR ]]; then
      latency scan --prefix q8JoinStream --suffix .json.gz --output $DIR $INDIR
    fi
  done
done
DIR=$OUT_DIR/4ins/q8-180s-0swarm-100ms-src100ms
mkdir -p $DIR
for ((i=0; i < 6; i++)); do
  INDIR=$SCRIPT_DIR/q8_boki/mem_4xlarge/4src_4node_4ins_${extra}extra_kvrocks/180s_0swarm_100ms_src100ms/$i
  if [[ -d $INDIR ]]; then
    latency scan --prefix q8JoinStream --suffix .json.gz --output $DIR $INDIR
  fi
done

instances=(4 8 16 28 32 40)
for j in ${instances[@]}; do
  mkdir -p $OUT_DIR/2pc/${j}ins/q8-180s-0swarm-100ms-src100ms/
  mv $OUT_DIR/${j}ins/q8-180s-0swarm-100ms-src100ms/2pc* $OUT_DIR/2pc/${j}ins/q8-180s-0swarm-100ms-src100ms/ || true
  mkdir -p $OUT_DIR/impeller/${j}ins/q8-180s-0swarm-100ms-src100ms/
  mv $OUT_DIR/${j}ins/q8-180s-0swarm-100ms-src100ms/eo* $OUT_DIR/impeller/${j}ins/q8-180s-0swarm-100ms-src100ms/ || true
  mkdir -p $OUT_DIR/align_chkpt/${j}ins/q8-180s-0swarm-100ms-src100ms/
  mv $OUT_DIR/${j}ins/q8-180s-0swarm-100ms-src100ms/align_chkpt* $OUT_DIR/align_chkpt/${j}ins/q8-180s-0swarm-100ms-src100ms/ || true
  rmdir $OUT_DIR/${j}ins/q8-180s-0swarm-100ms-src100ms/ || true
  rmdir $OUT_DIR/${j}ins/ || true
done
