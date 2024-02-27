#!/bin/bash
set -euo pipefail
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

OUT_DIR=$SCRIPT_DIR/../pub_data/micro/multi_instances/
mkdir -p $OUT_DIR
instances=(8 16)
for j in ${instances[@]}; do
  DIR=$OUT_DIR/${j}ins/q8-180s-0swarm-100ms-src100ms
  mkdir -p $DIR
  for ((i=0; i < 3; i++)); do
    latency scan --prefix q8JoinStream --suffix .json.gz --output $DIR $SCRIPT_DIR/q8_boki/mem_4node_${j}ins/${j}src_4node_${j}ins/180s_0swarm_100ms_src100ms/$i
  done
done

for j in ${instances[@]}; do
  mkdir -p $OUT_DIR/2pc/${j}ins/q8-180s-0swarm-100ms-src100ms/
  mv $OUT_DIR/${j}ins/q8-180s-0swarm-100ms-src100ms/2pc* $OUT_DIR/2pc/${j}ins/q8-180s-0swarm-100ms-src100ms/
  mkdir -p $OUT_DIR/impeller/${j}ins/q8-180s-0swarm-100ms-src100ms/
  mv $OUT_DIR/${j}ins/q8-180s-0swarm-100ms-src100ms/eo* $OUT_DIR/impeller/${j}ins/q8-180s-0swarm-100ms-src100ms/
  mkdir -p $OUT_DIR/align_chkpt/${j}ins/q8-180s-0swarm-100ms-src100ms/
  mv $OUT_DIR/${j}ins/q8-180s-0swarm-100ms-src100ms/align_chkpt* $OUT_DIR/align_chkpt/${j}ins/q8-180s-0swarm-100ms-src100ms/
done
