import argparse
import json
import numpy as np
from parse_epoch_mark_time import parse_single_topdir

extra=0

dirs = {
    4: f"./q8_boki/mem_4xlarge/4src_4node_4ins_{extra}extra_kvrocks",  
    8: f"./q8_boki/mem_4node_8ins_4xlarge/8src_4node_8ins_{extra}extra_kvrocks/",
    16: f"./q8_boki/mem_4node_16ins_4xlarge/16src_4node_16ins_{extra}extra_kvrocks/",
    32: f"./q8_boki/mem_4node_32ins_4xlarge/32src_4node_32ins_{extra}extra_kvrocks/",
}

tps_map = {
    4: 28000,
    8: 14000,
    16: 7000,
    32: 3500,
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
    ins = [4, 8, 16, 32]
    for i in dirs:
        stats[i] = {}
    for i in ins:
        d = dirs[i]
        epoch_stat = parse_single_topdir(d, "epoch")
        twopc_stat = parse_single_topdir(d, "2pc")
        stats[i]['epoch'] = epoch_stat
        stats[i]['2pc'] = twopc_stat
    with open(f"q8_multistream_stats_{extra}extra_4xlarge.json", "w") as f:
        json.dump(stats, f, cls=NpEncoder)


if __name__ == '__main__':
    main()
