#!/bin/bash
ins=(8 16 28 32)
for ((i=0; i < ${#ins[@]}; ++i)); do
  num_in=${ins[$i]}
  python3 parse_stats_single_exp.py \
    --dir ./q8_boki/mem_4node_${num_in}ins_4xlarge/${num_in}src_4node_${num_in}ins_0extra_kvrocks2/ --mode epoch --app q8 \
    --out_stats ../pub_data/micro/multi_instances_0extra_kvrocks_4xlarge2/q8_180s_0swarm_100ms_src100ms_stats
  python3 parse_stats_single_exp.py \
    --dir ./q8_boki/mem_4node_${num_in}ins_4xlarge/${num_in}src_4node_${num_in}ins_0extra_kvrocks2/ --mode 2pc --app q8 \
    --out_stats ../pub_data/micro/multi_instances_0extra_kvrocks_4xlarge2/q8_180s_0swarm_100ms_src100ms_stats
done
python3 parse_stats_single_exp.py \
  --dir ./q8_boki/mem_4xlarge/4src_4node_4ins_0extra_kvrocks2/ --mode epoch --app q8 \
  --out_stats ../pub_data/micro/multi_instances_0extra_kvrocks_4xlarge2/q8_180s_0swarm_100ms_src100ms_stats
python3 parse_stats_single_exp.py \
  --dir ./q8_boki/mem_4xlarge/4src_4node_4ins_0extra_kvrocks2/ --mode 2pc --app q8 \
  --out_stats ../pub_data/micro/multi_instances_0extra_kvrocks_4xlarge2/q8_180s_0swarm_100ms_src100ms_stats
