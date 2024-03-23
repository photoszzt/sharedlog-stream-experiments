import argparse
import matplotlib.pyplot as plt
import json
import numpy as np
from parse_epoch_mark_time import parse_single_topdir

extra=0

dirs = {
    4: f"./q8_boki/mem_4xlarge/4src_4node_4ins_{extra}extra_kvrocks2",  
    8: f"./q8_boki/mem_4node_8ins_4xlarge/8src_4node_8ins_{extra}extra_kvrocks2/",
    16: f"./q8_boki/mem_4node_16ins_4xlarge/16src_4node_16ins_{extra}extra_kvrocks2/",
    28: f"./q8_boki/mem_4node_28ins_4xlarge/28src_4node_28ins_{extra}extra_kvrocks2/",
    32: f"./q8_boki/mem_4node_32ins_4xlarge/32src_4node_32ins_{extra}extra_kvrocks2/",
    40: f"./q8_boki/mem_4node_40ins_4xlarge/40src_4node_40ins_{extra}extra_kvrocks2/",
}

tps_map = {
    4: 28000,
    8: 14000,
    16: 7000,
    28: 4000,
    32: 3500,
    40: 2800,
}


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


def main():
    stats = {}
    ins = [4, 8, 16, 28, 32, 40]
    for i in dirs:
        stats[i] = {}
    for i in ins:
        dir = dirs[i]
        epoch_stat = parse_single_topdir(dir, "epoch", "q8")
        twopc_stat = parse_single_topdir(dir, "2pc", "q8")
        stats[i]['epoch'] = epoch_stat
        stats[i]['2pc'] = twopc_stat
    print(stats)
    with open(f"../pub_data/micro/q8_multistream_stats_{extra}extra_4xlarge2.json", "w") as f:
        json.dump(stats, f, cls=NpEncoder)


if __name__ == '__main__':
    main()
