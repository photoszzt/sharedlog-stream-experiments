#!/bin/bash
set -euo pipefail
DIR=$1
f=$(find $1 -type f)
for i in $f; do
    basename=$(basename $i)
    parent=$(dirname $i)
    if [[ $basename = "sar_st" ]]; then
        sadf -j -t $i -- -P ALL > $parent/cpu_util.json
        sadf -j -t --iface=ens5 $i -- -n DEV > $parent/net_bandwidth.json
        sadf -j -t $i -- -r > $parent/mem_util.json
    fi
done
